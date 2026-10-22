#!/usr/bin/env python3
"""Render a data-driven knowledge film with semantic diagrams and a single timeline.

Episode facts belong in the input JSON. No cloud services or private assets are used.
The four capsule presets define visual and narrative grammar; this is their drawing kit,
not an automatic topic-to-script generator. Requires Pillow, numpy, PyYAML and FFmpeg.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'capsules/dark_gold_knowledge_film.capsule/assets/kit/gold_kit.py'
spec = importlib.util.spec_from_file_location('vibe_drawing_kit', KIT)
k = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = k
spec.loader.exec_module(k)

CAPSULES = ('vibe_probability_lab', 'vibe_decision_poem',
            'vibe_system_blueprint', 'vibe_learning_workbench')
KINDS = {'doors', 'matrix', 'bars', 'sequence', 'curve', 'network', 'recall', 'loop', 'statement'}
EXTRA_DRAWERS = {}
SCENE_VALIDATORS = {}
# Fixed, local component modules; never execute a module path from episode input.
for component_name in ('probability', 'decision', 'system', 'learning'):
    component_path = ROOT / 'scripts' / 'vibe_scenes' / (component_name + '.py')
    if not component_path.exists():
        continue
    component_spec = importlib.util.spec_from_file_location('vibe_component_' + component_name, component_path)
    component = importlib.util.module_from_spec(component_spec)
    sys.modules[component_spec.name] = component
    component_spec.loader.exec_module(component)
    for kind, drawer in component.DRAWERS.items():
        if kind in KINDS or not callable(drawer):
            raise ValueError(f'duplicate or invalid scene component: {kind}')
        KINDS.add(kind)
        EXTRA_DRAWERS[kind] = drawer
        if hasattr(component, 'validate_scene'):
            SCENE_VALIDATORS[kind] = component.validate_scene


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def validate(episode, style):
    if not isinstance(episode, dict) or not episode.get('title') or not episode.get('sources'):
        raise ValueError('title and sources are required')
    if not isinstance(episode.get('scenes'), list) or not episode['scenes']:
        raise ValueError('scenes must be a nonempty list')
    for i, s in enumerate(episode['scenes']):
        if s.get('kind') not in KINDS:
            raise ValueError(f'scene {i}: unsupported diagram kind')
        if not isinstance(s.get('duration'), (int, float)) or not 3 <= s['duration'] <= 30:
            raise ValueError(f'scene {i}: duration must be 3–30 seconds')
        if not s.get('heading') or not isinstance(s.get('captions'), list) or not s['captions']:
            raise ValueError(f'scene {i}: heading and timed captions required')
        previous = 0.0
        for cap in s['captions']:
            start, end = cap['start'], cap['end']
            if not (previous <= start < end <= s['duration']):
                raise ValueError(f'scene {i}: overlapping or out-of-range caption')
            if not cap.get('text') or len(cap['text']) > 46:
                raise ValueError(f'scene {i}: caption must have 1–46 characters')
            previous = end
        data = s.get('data', {})
        if not isinstance(data, dict):
            raise ValueError(f'scene {i}: data must be an object')
        if s['kind'] in SCENE_VALIDATORS:
            SCENE_VALIDATORS[s['kind']](s)
        if s['kind'] == 'curve':
            pts = data.get('points', [])
            if len(pts) < 2 or any(not isinstance(p,list) or len(p)!=2 or
                    any(not isinstance(v,(int,float)) or not 0<=v<=1 for v in p) for p in pts):
                raise ValueError('curve requires normalized points in [0, 1]')
            if any(b[0]<a[0] for a,b in zip(pts,pts[1:])):
                raise ValueError('curve x coordinates must be monotonic')
        if s['kind'] in ('bars', 'matrix'):
            values = data.get('values', [])
            if not values or any(not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0 for v in values):
                raise ValueError('bars/matrix require finite nonnegative values')
            if len(data.get('labels', [])) != len(values):
                raise ValueError('each value requires a label')
            if 'display' in data and len(data['display'])!=len(values):
                raise ValueError('each value requires a display label')
            if s['kind']=='bars' and len(values)>6:
                raise ValueError('bars support at most six values')
            if s['kind']=='matrix':
                if data.get('cases'):
                    if len(data['cases'])>4 or len(data.get('columns',[]))!=3 or any(len(row)!=3 for row in data['cases']):
                        raise ValueError('case tables support three columns and at most four rows')
                elif len(values)!=2 or not 0<sum(values) or not isinstance(data.get('dots',120),int) or not 1<=data.get('dots',120)<=160:
                    raise ValueError('dot matrix requires two positive-total values and 1–160 dots')
        if s['kind'] == 'network':
            nodes = data.get('nodes', [])
            if not nodes or not data.get('edges'):
                raise ValueError('network requires nodes and edges')
            for node in nodes:
                xy=node.get('xy',[])
                if len(xy)!=2 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in xy) or not (100<=xy[0]<=1180 and 240<=xy[1]<=500):
                    raise ValueError('network node outside diagram safe area')
            for edge in data.get('edges', []):
                if not all(isinstance(edge.get(key),int) and 0<=edge[key]<len(nodes) for key in ('a','b')):
                    raise ValueError('network edge references missing node')
        if s['kind'] == 'sequence':
            values=data.get('values',[])
            if not 2<=len(values)<=16 or any(not isinstance(v,(int,float)) or not 0<=v<=1 for v in values):
                raise ValueError('sequence requires 2–16 normalized values')
            if not isinstance(data.get('cutoff',0),int) or not 0<=data.get('cutoff',0)<=len(values) or not 0<=data.get('threshold',0)<=1:
                raise ValueError('invalid sequence cutoff or threshold')
        if s['kind']=='recall' and not 1<=len(data.get('items',[]))<=6:
            raise ValueError('recall requires 1–6 items')
        if s['kind']=='loop' and not 3<=len(data.get('items',[]))<=6:
            raise ValueError('loop requires 3–6 items')
        if s['kind']=='statement' and not 1<=len(data.get('lines',[]))<=3:
            raise ValueError('statement requires 1–3 lines')
        if s['kind']=='doors':
            count=data.get('count',3)
            if not isinstance(count,int) or not 2<=count<=4 or ('labels' in data and len(data['labels'])!=count):
                raise ValueError('doors support 2–4 doors with matching labels')
    if not all(field in style for field in ('background', 'ink', 'accent', 'secondary', 'muted', 'grid', 'label')):
        raise ValueError('incomplete style palette')


class Frame:
    def __init__(self, palette, t, width):
        self.p = palette
        self.im = background(tuple(palette[c] for c in ('background', 'grid')), width).copy()
        self.a = k.Canvas(self.im)
        if palette.get('particles'):
            for n in range(38):
                x = 65 + ((n * 149.3 + t * (2 + n % 3)) % 1150)
                y = 105 + ((n * 87.1 + math.sin(t * .25 + n) * 7) % 480)
                self.a.ellipse(x, y, .65 + n % 3 * .3, color=palette['grid'], fill=True)

    def text(self, text, x, y, size=28, color=None, anchor='center', alpha=1, latin=False, max_width=1120):
        if not text:
            return
        # Latin-only fonts generally lack CJK glyphs, including mixed eyebrow labels.
        latin = latin and not any('\u2e80' <= c <= '\uffef' for c in str(text))
        size = min(size, 94)
        while k.glyph(str(text), size, color or self.p['ink'], latin).width > max_width * k.SCALE and size > 15:
            size -= 1
        if k.glyph(str(text), size, color or self.p['ink'], latin).width > max_width * k.SCALE:
            raise ValueError(f'text exceeds layout: {text}')
        self.a.text(str(text), x, y, size, color or self.p['ink'], anchor, alpha, latin)

    def line(self, pts, color=None, width=1.5):
        self.a.line(pts, color or self.p['grid'], width)


@lru_cache(8)
def background(colors, width):
    base, grid = colors
    im = Image.new('RGB', (width, round(width * 9 / 16)), base)
    a = k.Canvas(im)
    for x in range(60, 1280, 40):
        for y in range(100, 610, 40):
            a.ellipse(x, y, .65, color=grid, fill=True)
    return im


def doors(f, s, t):
    d, a, p = s['data'], f.a, f.p
    n = d.get('count', 3)
    opened = d.get('opened', []) if t >= d.get('reveal_at', 1) else []
    for j in range(n):
        x = 640 + (j - (n - 1) / 2) * 260
        chosen = j == d.get('selected', -1)
        color = p['accent'] if chosen else p['muted']
        a.rect((x-88,240,x+88,475), p['grid'], fill=True, r=42)
        a.rect((x-88,240,x+88,475), color, width=2, r=42)
        if j in opened:
            a.rect((x-78,250,x+78,464), p['background'], fill=True, r=34)
            f.text(d.get('revealed_label', '空'),x,357,44,p['secondary'])
            a.line([(x-85,253),(x-120,276),(x-120,496),(x-85,474)],p['muted'],2)
        else:
            f.text(str(j+1).zfill(2),x,333,68,color,latin=True)
            a.ellipse(x+55,383,4,color=color,fill=True)
        f.text(d.get('labels',['']*n)[j],x,516,23,color,max_width=245)
        if chosen:
            f.text(d.get('selection_label','你的选择'),x,207,22,p['accent'])
    if d.get('switch') and t>2:
        a.arrow((440,555),(800,555),p['accent'],3)
        f.text(d.get('switch_label','改变选择'),640,575,20,p['accent'])


def matrix(f, s, t):
    d,p,a=s['data'],f.p,f.a
    values=d['values']; labels=d['labels']; total=sum(values)
    if d.get('cases'):
        for j,heading in enumerate(d['columns']):
            f.text(heading,290+j*330,260,23,p['muted'])
        for i,row in enumerate(d['cases']):
            y=330+i*76
            active=min(len(d['cases'])-1,int(t/2.5))==i
            if active:a.rect((110,y-30,1170,y+30),p['grid'],fill=True,r=5)
            for j,cell in enumerate(row):
                f.text(cell,290+j*330,y,29,p['accent'] if j==2 else p['ink'],max_width=310)
        f.text(d.get('note',''),640,570,23,p['muted'])
        return
    count=d.get('dots',120); shown=round(count*k.ease(t/3))
    cols=20; step=26; x0=100; y0=280
    split=round(values[0]/total*count)
    for i in range(count):
        color=(p['secondary'] if i<split else p['accent']) if i<shown else p['grid']
        a.ellipse(x0+(i%cols)*step,y0+(i//cols)*step,6,color=color,fill=True)
    for j,(label,val) in enumerate(zip(labels,values)):
        y=280+j*133
        f.text(label,840,y,26,p['muted'],anchor='left',max_width=330)
        f.text(d.get('display',[str(v) for v in values])[j],840,y+60,64,p['secondary'] if j==0 else p['accent'],anchor='left',latin=True,max_width=330)
    f.text(d.get('note',''),360,515,24,p['muted'],max_width=580)


def bars(f,s,t):
    d,p,a=s['data'],f.p,f.a
    values=d['values']; maxv=max(values)*1.15 or 1
    n=len(values); slot=900/n
    for i,v in enumerate(values):
        x=190+i*slot; h=230*v/maxv*k.ease((t-i*.25)/1.7)
        color=p['accent'] if i==d.get('highlight',n-1) else p['secondary']
        a.rect((x,505-h,x+slot*.57,505),color,fill=True,r=3)
        f.text(d.get('display',[str(v) for v in values])[i],x+slot*.285,480-h,48,color,latin=True,max_width=slot*.8)
        f.text(d['labels'][i],x+slot*.285,542,24,p['ink'],max_width=slot*.86)
    f.line([(160,508),(1120,508)],p['muted'])
    f.text(d.get('note',''),640,594,19,p['muted'])


def sequence(f,s,t):
    d,p,a=s['data'],f.p,f.a
    values=d['values']; n=len(values); slot=1040/n
    upto=min(n, int(n*k.clamp(t/max(2,s['duration']-2)))+1)
    threshold=d.get('threshold',0); cutoff=d.get('cutoff',0)
    chosen=next((i for i,v in enumerate(values) if i>=cutoff and v>threshold),None) if d.get('stop_on_record') else None
    if chosen is not None:upto=min(upto,chosen+1)
    for i,v in enumerate(values):
        x=120+i*slot; h=v*235
        col=p['accent'] if i>=cutoff else p['muted']
        if i>=upto: col=p['grid']
        a.rect((x,500-h,x+slot*.57,500),col,fill=True,r=3)
        if chosen==i and upto>i:
            a.rect((x-6,494-h,x+slot*.57+6,506),p['accent'],width=2,r=5)
            f.text(d.get('chosen_label','选择'),x+slot*.28,470-h,22,p['accent'],max_width=slot)
        f.text(str(i+1),x+slot*.28,526,17,p['muted'],latin=True)
    if threshold:
        y=500-threshold*235
        for x in range(112,1160,14): f.line([(x,y),(x+6,y)],p['secondary'])
        f.text(d.get('threshold_label','比较标准'),1138,y-20,20,p['secondary'],anchor='right')
    f.text(d.get('left_label','观察'),120+cutoff*slot/2,568,25,p['muted'])
    f.text(d.get('right_label','选择'),120+(n+cutoff)*slot/2,568,25,p['accent'])
    f.line([(120+cutoff*slot-10,235),(120+cutoff*slot-10,540)],p['secondary'])


def curve(f,s,t):
    d,p,a=s['data'],f.p,f.a
    pts=[(170+x*900,520-y*280) for x,y in d['points']]
    for y in (240,310,380,450,520): f.line([(170,y),(1100,y)])
    if d.get('percent_axes'):
        for q in (0,.25,.5,.75,1):
            f.text(f'{q*100:.0f}%',170+q*900,541,16,p['muted'],latin=True)
            f.text(f'{q*d.get("y_max",1)*100:.1f}%',150,520-q*280,16,p['muted'],anchor='right',latin=True)
    f.line([(170,230),(170,520),(1110,520)],p['muted'])
    q=k.ease(t/3)
    a.path(pts,q,p['accent'],3.5,glow=p.get('particles',False))
    idx=min(len(pts)-1,max(1,int(len(pts)*q)-1))
    a.ellipse(*pts[idx],6,color=p['accent'],fill=True)
    if d.get('marker') and t>2.2:
        mx,my=d['marker'];x,y=170+mx*900,520-my*280
        f.line([(x,y),(x,520)],p['secondary'])
        a.ellipse(x,y,8,color=p['accent'],fill=True)
        f.text(d['marker_label'],x,y-38,42,p['accent'],latin=True)
    f.text(d.get('x_label',''),640,573,22,p['muted'])
    f.text(d.get('y_label',''),175,205,22,p['muted'],anchor='left')
    f.text(d.get('note',''),640,595,18,p['muted'])


def network(f,s,t):
    d,p,a=s['data'],f.p,f.a
    nodes=d['nodes']
    for edge in d['edges']:
        x1,y1=nodes[edge['a']]['xy'];x2,y2=nodes[edge['b']]['xy']
        special=edge.get('accent',False)
        if special and t<d.get('reveal_at',0):continue
        col=p['secondary'] if special else p['accent']
        f.line([(x1,y1),(x2,y2)],p['grid'],16)
        f.line([(x1,y1),(x2,y2)],col,2.3)
        for j in range(edge.get('flow',8)):
            u=(t*edge.get('speed',.13)+j/edge.get('flow',8))%1
            x,y=x1+(x2-x1)*u,y1+(y2-y1)*u
            a.ellipse(x,y,3.5,color=col,fill=True)
        dx,dy=edge.get('label_offset',[0,-24])
        f.text(edge.get('label',''),(x1+x2)/2+dx,(y1+y2)/2+dy,22,col,max_width=240)
    for n in nodes:
        x,y=n['xy'];a.ellipse(x,y,28,color=p['background'],fill=True)
        a.ellipse(x,y,28,color=p['muted'],width=2)
        f.text(n['label'],x,y,22,p['ink'])
    f.text(d.get('badge',''),640,555,38,p['secondary'])
    f.text(d.get('note',''),640,595,18,p['muted'])


def recall(f,s,t):
    d,p,a=s['data'],f.p,f.a
    hide=d.get('hide_at',1000); reveal=d.get('reveal_at',1000)
    items=d.get('items',[]); columns=3; w=290
    for i,word in enumerate(items):
        x=350+(i%columns)*w;y=310+(i//columns)*100
        a.rect((x-125,y-37,x+125,y+37),p['grid'],width=2,r=7)
        hidden=hide<=t<reveal
        f.text('？' if hidden else word,x,y,34,p['accent'] if not hidden else p['muted'],max_width=235)
    if hide<=t<reveal:
        remaining=max(0,math.ceil(reveal-t))
        f.text(d.get('prompt','在脑中回忆'),640,498,30,p['ink'])
        a.d.arc((603*k.SCALE,528*k.SCALE,677*k.SCALE,602*k.SCALE),-90,-90+359*remaining/max(1,reveal-hide),fill=p['accent'],width=round(3*k.SCALE))
        f.text(str(remaining),640,563,28,p['accent'],latin=True)
    else:f.text(d.get('note',''),640,555,25,p['muted'])


def loop(f,s,t):
    d,p,a=s['data'],f.p,f.a
    items=d['items'];n=len(items)
    radius=200
    points=[(640+radius*math.cos(-math.pi/2+i*2*math.pi/n),405+radius*.65*math.sin(-math.pi/2+i*2*math.pi/n)) for i in range(n)]
    for i,(x,y) in enumerate(points):
        nx,ny=points[(i+1)%n];vx,vy=nx-x,ny-y;l=math.hypot(vx,vy)
        a.arrow((x+vx/l*75,y+vy/l*35),(nx-vx/l*75,ny-vy/l*35),p['muted'],2)
    active=int(t/1.7)%n
    for i,(x,y) in enumerate(points):
        col=p['accent'] if i==active else p['muted']
        a.rect((x-98,y-36,x+98,y+36),p['background'],fill=True,r=10)
        a.rect((x-98,y-36,x+98,y+36),col,width=2,r=10)
        f.text(items[i],x,y,26,col,max_width=185)
    f.text(d.get('center',''),640,405,30,p['ink'],max_width=190)
    f.text(d.get('note',''),640,590,22,p['muted'])


def statement(f,s,t):
    d,p,a=s['data'],f.p,f.a
    for j in range(3):
        r=100+j*38+math.sin(t*.45+j)*5
        a.ellipse(640,390,r,r*.62,color=p['grid'],width=1)
    lines=d.get('lines',[])
    for i,line in enumerate(lines):
        alpha=k.ease((t-i*.45)/.7)
        f.text(line,640,330+i*75,54 if len(lines)<3 else 43,p['accent'] if i==len(lines)-1 else p['ink'],alpha=alpha,max_width=1080)
    f.text(d.get('note',''),640,565,24,p['muted'])


DRAWERS={name:globals()[name] for name in KINDS if name not in EXTRA_DRAWERS}
DRAWERS.update(EXTRA_DRAWERS)


def render_frame(episode,style,timeline,frame,width):
    index,t,duration=timeline.at_frame(frame)
    scene=episode['scenes'][index];global_t=frame/timeline.fps
    f=Frame(style,global_t,width)
    f.text(style['label'],70,50,18,style['accent'],anchor='left',latin=True,max_width=600)
    f.text(f'{index+1:02d} / {len(episode["scenes"]):02d}',1210,50,18,style['muted'],anchor='right',latin=True)
    f.line([(70,78),(1210,78)])
    f.text(scene.get('eyebrow',''),640,114,18,style['muted'],latin=True)
    f.text(scene['heading'],640,169,43,style['ink'],max_width=1120)
    DRAWERS[scene['kind']](f,scene,t)
    for cap in scene['captions']:
        if cap['start']<=t<cap['end']:
            txt=cap['text'];lines=[txt] if len(txt)<=30 else [txt[:len(txt)//2],txt[len(txt)//2:]]
            for n,line in enumerate(lines):
                f.text(line,640,646+n*32-(16 if len(lines)>1 else 0),27,style['ink'])
    f.line([(70,696),(1210,696)])
    f.line([(70,696),(70+1140*global_t/timeline.duration,696)],style['accent'],2)
    # Brief dissolves retain a visible composition rather than inserting black frames.
    transition=min(k.ease(t/.28),k.ease((duration-t)/.28))
    if transition<1:
        f.im=Image.blend(background(tuple(style[c] for c in ('background','grid')),width),f.im,.28+.72*transition)
    return f.im


def srt_time(t):
    ms=round(t*1000);sec,ms=divmod(ms,1000);minute,sec=divmod(sec,60);hour,minute=divmod(minute,60)
    return f'{hour:02}:{minute:02}:{sec:02},{ms:03}'


def write_run_contract(out, capsule, episode, timeline):
    """Describe the actual continuous render and audio, without inventing scene clips."""
    paths = [('final_video','release/final.mp4'), ('code_rendered_video','release/final.mp4'),
             ('cover_image','release/cover.jpg'), ('copywriting','release/copywriting.txt'),
             ('publishing_package','release/copywriting.txt'), ('subtitle','release/subtitles.srt'),
             ('bgm','work/score.wav'), ('source_project','work/episode.json'),
             ('contact_sheet','qa/review_contact_sheet.jpg'),
             ('reference_analysis','work/reference_analysis.json')]
    dump(out/'artifact_manifest.json', {
        'schema_version':'vibe.render.manifest.v1', 'capsule_name':capsule,
        'delivery_promise':{'promise_type':'reference_remake'},
        'artifacts':[{'category':c,'path':str(out/p)} for c,p in paths]})
    tracks = [{'type':kind, 'clips':[{'id':kind+'-master', 'source_path':str(out/path),
               'start':0, 'duration':timeline.duration, 'source_duration':timeline.duration}]}
              for kind,path in [('video','work/picture.mp4'), ('audio','work/score.wav')]]
    dump(out/'work/edit_plan.json', {'schema':'capsule_cinema.edit_plan.v1',
        'timeline':{'duration':timeline.duration, 'fps':timeline.fps, 'tracks':tracks},
        'scene_map':[{'scene_id':i+1, 'start':start, 'duration':scene['duration'],
                      'heading':scene['heading'], 'component':scene['kind']}
                     for i,(start,scene) in enumerate(zip(timeline.starts,episode['scenes']))]})


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--capsule',choices=CAPSULES,required=True)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True,help='new run folder under output/')
    ap.add_argument('--font',type=Path,required=True,help='Chinese font file')
    ap.add_argument('--latin-font',type=Path,required=True)
    ap.add_argument('--width',type=int,default=1920,choices=(1280,1920))
    ap.add_argument('--fps',type=int,default=30,choices=(24,30))
    ap.add_argument('--preview',action='store_true',help='only scene contact sheet; no video or score')
    args=ap.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(ROOT/'output'):
        ap.error('--out must be inside this project output/')
    style_path=ROOT/'capsules'/f'{args.capsule}.capsule'/'assets/style.json'
    style=json.loads(style_path.read_text())
    episode=json.loads(args.input.read_text())
    validate(episode,style)
    if not args.preview and (out/'release/final.mp4').exists():
        ap.error('output already contains final.mp4; choose a new run folder')
    for cmd in ('ffmpeg','ffprobe'):
        if not shutil.which(cmd):ap.error(f'{cmd} not found')
    k.configure(args.font,args.latin_font,args.width/1280)
    timeline=k.Timeline.from_durations([s['duration'] for s in episode['scenes']],args.fps)
    for sub in ('work','release','qa'):(out/sub).mkdir(parents=True,exist_ok=True)
    dump(out/'work/episode.json',episode)
    dump(out/'work/style.json',style)
    thumbs=[]
    for i,start in enumerate(timeline.starts):
        second=start+min(episode['scenes'][i]['duration']*.55,5.5)
        im=render_frame(episode,style,timeline,round(second*args.fps),args.width)
        im.save(out/'qa'/f'scene-{i+1:02}.jpg',quality=93)
        thumbs.append(im.resize((640,360),Image.Resampling.LANCZOS))
    sheet=Image.new('RGB',(1280,360*math.ceil(len(thumbs)/2)),style['background'])
    for i,thumb in enumerate(thumbs):sheet.paste(thumb,((i%2)*640,(i//2)*360))
    sheet.save(out/'qa/review_contact_sheet.jpg',quality=93)
    if args.preview:
        print(out/'qa/review_contact_sheet.jpg');return
    caption_blocks=[]
    for start,scene in zip(timeline.starts,episode['scenes']):
        for cap in scene['captions']:
            caption_blocks.append(f'{len(caption_blocks)+1}\n{srt_time(start+cap["start"])} --> {srt_time(start+cap["end"])}\n{cap["text"]}\n')
    (out/'release/subtitles.srt').write_text('\n'.join(caption_blocks),encoding='utf-8')
    cover=render_frame(episode,style,timeline,round(2.8*args.fps),args.width)
    cover.save(out/'release/cover.jpg',quality=96)
    k.write_score(out/'work/score.wav',timeline.duration,timeline.starts,style.get('bpm',100),episode.get('seed',73))
    video=out/'work/picture.mp4'
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{args.width}x{round(args.width*9/16)}','-framerate',str(args.fps),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-threads','4',str(video)]
    with (out/'qa/encode.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for i in range(sum(timeline.frames)):
                proc.stdin.write(render_frame(episode,style,timeline,i,args.width).tobytes())
                if i% (args.fps*10)==0:print(f'{args.capsule}: {i/args.fps:.0f}/{timeline.duration:.0f}s',flush=True)
        except BaseException:
            proc.kill();proc.wait();raise
        finally:
            proc.stdin.close()
        if proc.wait():raise RuntimeError('FFmpeg encoding failed; inspect qa/encode.log')
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-i',str(out/'work/score.wav'),'-map','0:v','-map','1:a','-c:v','copy','-af','loudnorm=I=-18:TP=-1.5:LRA=9','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',str(timeline.duration),str(out/'release/final.mp4')],check=True)
    copy=episode['title']+'\n\n'+episode.get('description','')+'\n\n'+episode.get('tags','#Vibe知识大赏 #知识科普')+'\n'
    (out/'release/copywriting.txt').write_text(copy,encoding='utf-8')
    dump(out/'work/decision_log.json',{'route':'procedural_2d_render','resolution':[args.width,round(args.width*9/16)],'fps':args.fps,'audio':'original procedural instrumental, no narration','capsule':args.capsule,'duration':timeline.duration})
    dump(out/'work/reference_analysis.json',episode.get('reference_analysis',{}))
    write_run_contract(out,args.capsule,episode,timeline)
    dump(out/'work/timeline.json',{'fps':args.fps,'frames':list(timeline.frames),'starts':timeline.starts,'duration':timeline.duration})
    print(out/'release/final.mp4')


if __name__=='__main__':
    main()
