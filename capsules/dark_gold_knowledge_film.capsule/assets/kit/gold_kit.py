"""Topic-neutral drawing and score helpers. Requires Pillow and numpy.

Call configure with user-provided Chinese and Latin font files before drawing.
Write episode scripts separately; no topic copy or fixed scene sequence is stored here.
"""
from __future__ import annotations
import bisect
import math
import wave
from pathlib import Path
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W,H=1280,720
GOLD='#e5c581'
WHITE='#eee7d5'
RED='#e87d60'
TEAL='#91b9ac'
MUTED='#aca18d'
DIM='#514a3c'
SCALE=1.5
SERIF=None
LATIN=None

def configure(serif_font, latin_font, scale=1.5):
    global SERIF,LATIN,SCALE
    if scale<=0: raise ValueError('scale must be positive')
    for path in [serif_font,latin_font]:
        if not Path(path).is_file(): raise FileNotFoundError(path)
    SERIF=str(serif_font);LATIN=str(latin_font);SCALE=float(scale)
    font.cache_clear();glyph.cache_clear();background.cache_clear()

@dataclass(frozen=True)
class Timeline:
    fps: int
    frames: tuple[int,...]

    @classmethod
    def from_durations(cls, durations, fps=30):
        if not isinstance(fps,int) or fps<=0: raise ValueError('fps must be a positive integer')
        durations=tuple(durations)
        if not durations or any(not math.isfinite(d) or d<=0 for d in durations):
            raise ValueError('durations must be finite and positive')
        return cls(fps,tuple(max(1,round(d*fps)) for d in durations))

    @property
    def starts(self):
        result=[];elapsed=0
        for length in self.frames:
            result.append(elapsed/self.fps);elapsed+=length
        return result

    @property
    def duration(self): return sum(self.frames)/self.fps

    def at_frame(self, frame_index):
        if not isinstance(frame_index,int) or not 0<=frame_index<sum(self.frames):
            raise IndexError('frame outside the timeline')
        start=0
        for index,length in enumerate(self.frames):
            if frame_index<start+length:
                return index,(frame_index-start)/self.fps,length/self.fps
            start+=length
        raise IndexError(frame_index)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def rgb(c):
    return tuple((int(c[i:i + 2], 16) for i in (1, 3, 5)))

def shade(c, value):
    return tuple((round(v * value) for v in rgb(c)))

def lerp(a, b, x):
    return a + (b - a) * x

@lru_cache(128)
def font(size, latin=False):
    return ImageFont.truetype(LATIN if latin else SERIF, round(size * SCALE))

@lru_cache(2048)
def glyph(text, size, color, latin):
    f = font(size, latin)
    b = f.getbbox(text)
    im = Image.new('RGBA', (max(1, b[2] - b[0] + 8), max(1, b[3] - b[1] + 8)))
    ImageDraw.Draw(im).text((4 - b[0], 4 - b[1]), text, font=f, fill=color)
    return im

class Canvas:

    def __init__(self, image):
        self.im = image
        self.d = ImageDraw.Draw(image)

    def line(self, pts, color=GOLD, width=1):
        self.d.line([(round(x * SCALE), round(y * SCALE)) for x, y in pts], fill=color, width=max(1, round(width * SCALE)), joint='curve')

    def ellipse(self, x, y, rx, ry=None, color=GOLD, fill=False, width=1):
        ry = rx if ry is None else ry
        box = ((x - rx) * SCALE, (y - ry) * SCALE, (x + rx) * SCALE, (y + ry) * SCALE)
        self.d.ellipse(box, fill=color if fill else None, outline=None if fill else color, width=max(1, round(width * SCALE)))

    def rect(self, box, color=GOLD, fill=False, width=1, r=0):
        b = tuple((v * SCALE for v in box))
        self.d.rounded_rectangle(b, radius=r * SCALE, fill=color if fill else None, outline=None if fill else color, width=max(1, round(width * SCALE)))

    def text(self, text, x, y, size=26, color=WHITE, anchor='center', alpha=1, latin=False):
        if alpha <= 0:
            return
        p = glyph(text, size, color, latin)
        if alpha < 0.999:
            p = p.copy()
            p.putalpha(p.getchannel('A').point(lambda v: round(v * alpha)))
        px = x * SCALE - (p.width / 2 if anchor == 'center' else p.width if anchor == 'right' else 0)
        self.im.paste(p, (round(px), round(y * SCALE - p.height / 2)), p)

    def glow(self, x, y, r=4, color=GOLD):
        for k, v in [(5, 0.06), (3, 0.12), (1.8, 0.3)]:
            self.ellipse(x, y, r * k, color=shade(color, v), fill=True)
        self.ellipse(x, y, r, color=color, fill=True)

    def path(self, pts, p=1, color=GOLD, width=1.4, glow=False):
        q = pts[:max(2, int(len(pts) * clamp(p)))]
        if glow:
            self.line(q, shade(color, 0.09), width + 8)
            self.line(q, shade(color, 0.2), width + 3)
        self.line(q, color, width)

    def arrow(self, a, b, color=GOLD, width=1):
        self.line([a, b], color, width)
        theta = math.atan2(b[1] - a[1], b[0] - a[0])
        self.line([(b[0] - 10 * math.cos(theta - 0.45), b[1] - 10 * math.sin(theta - 0.45)), b, (b[0] - 10 * math.cos(theta + 0.45), b[1] - 10 * math.sin(theta + 0.45))], color, width)

@lru_cache(1)
def background():
    h, w = (round(H * SCALE), round(W * SCALE))
    yy, xx = np.mgrid[:h, :w]
    u = xx / w
    v = yy / h
    glow = np.exp(-((u - 0.45) ** 2 / 0.12 + (v - 0.43) ** 2 / 0.3))
    blue = np.exp(-((u - 0.9) ** 2 / 0.12 + (v - 0.65) ** 2 / 0.2))
    noise = np.random.default_rng(42).normal(0, 0.85, (h, w))
    arr = np.stack([9 + 9 * glow + noise, 11 + 7 * glow + noise, 14 + 4 * glow + 5 * blue + noise], axis=-1)
    return Image.fromarray(np.uint8(np.clip(arr, 0, 255)))

def bezier(a, b, c, d, n=140):
    return [((1 - t) ** 3 * a[0] + 3 * (1 - t) ** 2 * t * b[0] + 3 * (1 - t) * t * t * c[0] + t ** 3 * d[0], (1 - t) ** 3 * a[1] + 3 * (1 - t) ** 2 * t * b[1] + 3 * (1 - t) * t * t * c[1] + t ** 3 * d[1]) for t in np.linspace(0, 1, n)]

def orbit(a, t, center=(640, 360), r=220, flatten=0.42, color=DIM):
    pts = []
    for z in np.linspace(0, 2 * math.pi, 180):
        x, y = (r * math.cos(z), r * flatten * math.sin(z))
        pts.append((center[0] + x * 0.94 - y * 0.34, center[1] + x * 0.34 + y * 0.94))
    a.path(pts, color=color, width=0.65)
    pos = pts[int(t * 0.04 % 1 * 179)]
    a.glow(*pos, 2.6)

def node(a, x, y, label, color=GOLD, r=30):
    a.ellipse(x, y, r, color=color)
    a.text(label, x, y, 22, color)

def write_score(out, seconds, scene_starts, bpm=104, seed=73):
    """Original chamber-electronic score with accents at actual scene changes."""
    if seconds <= 0 or not scene_starts or scene_starts[0] != 0 or list(scene_starts) != sorted(set(scene_starts)) or scene_starts[-1] >= seconds or bpm <= 0:
        raise ValueError("Invalid score duration, starts or tempo")
    out = Path(out)
    sr = 48000
    n = int(sr * seconds)
    mix = np.zeros((n, 2), dtype=np.float32)
    rng = np.random.default_rng(seed)

    def note(start, dur, midi, gain, pan=0, tone='piano'):
        k = round(start * sr)
        length = min(round(dur * sr), n - k)
        if length <= 0 or k < 0:
            return
        tt = np.arange(length, dtype=np.float32) / sr
        f = 440 * 2 ** ((midi - 69) / 12)
        if tone == 'pad':
            sig = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 1.002 * tt) + 0.18 * np.sin(2 * np.pi * f * 2 * tt)
            env = np.minimum(1, tt / 0.8) * np.minimum(1, (dur - tt) / 1.5) * 0.45
        elif tone == 'bass':
            sig = np.sin(2 * np.pi * f * tt) + 0.15 * np.sin(2 * np.pi * f * 2 * tt)
            env = (1 - np.exp(-tt * 30)) * np.exp(-tt * 1.3)
        elif tone == 'tick':
            sig = rng.normal(0, 1, length) * 0.18 + np.sin(2 * np.pi * f * tt) * 0.4
            env = np.exp(-tt * 44)
        else:
            sig = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 1.1)
            sig += 0.3 * np.sin(2 * np.pi * f * 2.003 * tt) * np.exp(-tt * 2.1)
            sig += 0.12 * np.sin(2 * np.pi * f * 3.99 * tt) * np.exp(-tt * 3.5)
            env = (1 - np.exp(-tt * 180)) * np.minimum(1, (dur - tt) / 0.12)
        sig = (sig * env * gain).astype(np.float32)
        mix[k:k + length, 0] += sig * math.sqrt((1 - pan) / 2)
        mix[k:k + length, 1] += sig * math.sqrt((1 + pan) / 2)
    chords = [(50, 57, 62, 65), (46, 53, 58, 62), (41, 48, 57, 60), (48, 55, 60, 64)]
    beat = 60 / bpm
    for bar in range(math.ceil(seconds / (beat * 4))):
        start = bar * beat * 4
        section = min(len(scene_starts)-1, max(0, bisect.bisect_right(scene_starts, start)-1))
        chord = chords[bar // 3 % 4]
        if start >= scene_starts[-1]:
            chord = (50, 57, 62, 66)
        dynamic = 0.7 if section in (0, 2, 7, 15) else 1
        for m in chord:
            note(start, 4.4, m, 0.05 * dynamic, (m % 3 - 1) * 0.4, 'pad')
        note(start, 2.4, chord[0] - 12, 0.13 * dynamic, 0, 'bass')
        for step in range(8):
            m = chord[[0, 2, 1, 3, 2, 1, 3, 2][step]] + 12
            note(start + step * beat / 2, 2.1, m, 0.065 * dynamic, -0.35 if step % 2 else 0.35)
        if scene_starts[min(2, len(scene_starts)-1)] <= start < scene_starts[-1]:
            for step in (0, 2):
                note(start + step * beat, 0.2, 37, 0.07, 0, 'tick')
        if scene_starts[min(5, len(scene_starts)-1)] <= start < scene_starts[max(0, len(scene_starts)-2)]:
            for step in (1, 3):
                note(start + step * beat, 0.12, 90, 0.035, 0.15, 'tick')
    melody = [74, 77, 81, 79, 77, 74, 72, 69, 70, 74, 77, 76, 72, 69, 67, 69]
    for j, m in enumerate(melody * 3):
        start = scene_starts[min(1, len(scene_starts)-1)] + j * 3.6 * beat
        if start >= seconds - 7:
            break
        note(start, 3.6, m, 0.075, 0.15)
    for i, s in enumerate(scene_starts[1:], 1):
        note(s, 0.25, 42 if i < 9 else 74, 0.085, 0, 'tick')
    dry = mix.copy()
    for delay, gain in [(0.19, 0.16), (0.37, 0.13), (0.61, 0.085), (0.89, 0.045)]:
        d = round(delay * sr)
        mix[d:] += dry[:-d, ::-1] * gain
    fade = np.minimum(1, np.arange(n) / sr / 2) * np.minimum(1, (n - np.arange(n)) / sr / 4)
    mix *= fade[:, None]
    mix *= 0.78 / max(0.01, float(np.max(np.abs(mix))))
    with wave.open(str(out), 'wb') as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(np.int16(mix * 32767).tobytes())
