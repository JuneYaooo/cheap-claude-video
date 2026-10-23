"""Read constant-frame-rate edit sources without codec-dependent random seeks."""

import math
from pathlib import Path

import cv2


class SequentialVideoReader:
    """Decode forward; reopen and decode from the start for backward requests.

    Some files report a successful frame seek while returning an earlier decoded
    frame. Never use CAP_PROP_POS_FRAMES as proof of the returned frame's identity.
    Returned arrays are copies so compositing cannot alter the cached source.
    This reader is for constant-frame-rate sources; normalize VFR sources first.
    """

    def __init__(self, path):
        self.path = str(Path(path))
        self._cap = None
        self._frame = None
        self._index = -1
        self._open()
        self.fps = self._cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if not math.isfinite(self.fps) or self.fps <= 0 or self.frame_count <= 0:
            self.close()
            raise ValueError(f"Invalid constant-frame-rate video metadata: {self.path}")

    def _open(self):
        self.close()
        self._cap = cv2.VideoCapture(self.path)
        if not self._cap.isOpened():
            self.close()
            raise OSError(f"Cannot open video: {self.path}")
        self._index = -1
        self._frame = None

    def frame(self, index):
        if not isinstance(index, int) or not 0 <= index < self.frame_count:
            raise IndexError(f"Frame {index} outside 0..{self.frame_count - 1}")
        if self._cap is None:
            raise RuntimeError("Video reader is closed")
        if index < self._index:
            self._open()
        while self._index < index:
            ok, frame = self._cap.read()
            if not ok:
                raise OSError(f"Decode failed at frame {self._index + 1}: {self.path}")
            self._frame = frame
            self._index += 1
        return self._frame.copy()

    def at(self, seconds):
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError("Video time must be finite and nonnegative")
        return self.frame(math.floor(seconds * self.fps + 1e-7))

    def close(self):
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
