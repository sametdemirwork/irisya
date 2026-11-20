"""Irisya hero film, stand-in: build.py's edit made from Higgsfield stills while the Kling clips are missing.

The eight Kling clips (raw/*.mp4) were lost with the project folder on 2026-11-20 and the Higgsfield history does
not list them. This script replaces each clip with a still from the site's own Higgsfield set (irisya-tools/hf/raw,
see irisya-tools/hf/sources.json) and a slow camera move, then runs build.py unchanged: same 16 s edit, grade,
transitions, chapter cuts, portrait crop, posters and encodes, written to the same files.

When the clips are back, put them in raw/ and run build.py: it overwrites everything this script made.

Run       python -E stills.py              full render + encode (needs irisya-tools/hf/raw, see fetch.py there)
          python -E stills.py 1.0 9.5 ...  preview stills at those times (build/preview-*.jpg)
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

import build

HF_RAW = os.path.normpath(os.path.join(build.HERE, '..', '..', 'irisya-tools', 'hf', 'raw'))
W, H = build.W, build.H

# clip -> list of (from source time, raw still, zoom start, zoom end, centre start, centre end, mirror)
# The motions follow the Kling prompts in prompts.md (push-ins on the irises, a glide over the water,
# a lateral move past Galata, a dolly toward the hotel window). Centres are fractions of the 16:9 frame.
PLAN = {
    '1-iris-hazel': [(0, 'shade-7-detail', 1.00, 1.16, (.50, .50), (.50, .49), False)],
    '2-iris-blue': [(0, 'shade-1-detail', 1.02, 1.16, (.47, .50), (.53, .49), False)],
    '4-bosphorus': [(0, 'footer', 1.02, 1.14, (.47, .62), (.53, .60), False)],
    '5-galata': [(0, 'riders', 1.10, 1.14, (.30, .62), (.48, .60), False)],
    # the van arrives, then the chauffeur waits at arrivals (build.py cuts to source 2.25 s for that shot)
    '6-transfer': [(0, 'package-transfer', 1.04, 1.12, (.44, .55), (.48, .55), False),
                   (2.0, 'journey-2', 1.00, 1.08, (.62, .45), (.66, .43), False)],
    '7-hotel': [(0, 'package-hotel', 1.00, 1.14, (.55, .48), (.62, .45), False)],
    # mirrored so the patient's eye sits where the punch-in transitions aim (.33, .37)
    '8-clinic': [(0, 'journey-3', 1.00, 1.10, (.40, .42), (.36, .40), True)],
}
LENGTH = 5.0  # seconds per stand-in clip, like the 5 s Kling clips
# boxes (x0, y0, x1, y1, blur radius) softened in the raw stills: invented text and brand badges
# (the Kling prompts asked for an unbadged car and no text)
BLUR = {
    'package-transfer': [(1082, 606, 1206, 658, 9), (1126, 568, 1164, 608, 7), (1018, 580, 1082, 608, 7)],
    'journey-2': [(1368, 730, 1560, 836, 6)],
}


def cover(im, scale=1.25):
    """The still resized to cover a canvas `scale` times the frame, so zoom and pan never leave the picture."""
    cw, ch = round(W * scale), round(H * scale)
    s = max(cw / im.width, ch / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0, y0 = (im.width - cw) // 2, (im.height - ch) // 2
    return im.crop((x0, y0, x0 + cw, y0 + ch))


class StillClip:
    fps = build.FPS

    def __init__(self, name):
        self.parts = []
        for t0, raw, z0, z1, c0, c1, mirror in PLAN[name]:
            im = Image.open(os.path.join(HF_RAW, raw + '.png')).convert('RGB')
            for x0, y0, x1, y1, r in BLUR.get(raw, []):
                box = (x0, y0, x1, y1)
                im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(r)), box[:2])
            if mirror:
                im = im.transpose(Image.FLIP_LEFT_RIGHT)
            if im.height > im.width:  # portrait still: take a 16:9 band around the subject first
                band = round(im.width * 9 / 16)
                cy = round(c0[1] * im.height)
                y0 = min(max(cy - band // 2, 0), im.height - band)
                im = im.crop((0, y0, im.width, y0 + band))
                c0, c1 = (c0[0], .5), (c1[0], .5)
            self.parts.append((t0, cover(im), z0, z1, c0, c1))
        self.n = int(LENGTH * self.fps)

    def at(self, t):
        t = min(max(t, 0.0), LENGTH)
        t0, im, z0, z1, c0, c1 = [p for p in self.parts if p[0] <= t][-1]
        t1 = next((p[0] for p in self.parts if p[0] > t0), LENGTH)
        u = (t - t0) / (t1 - t0)
        z = z0 + (z1 - z0) * u
        cx = (c0[0] + (c1[0] - c0[0]) * u) * im.width
        cy = (c0[1] + (c1[1] - c0[1]) * u) * im.height
        # the canvas is 1.25x the frame, so zoom 1.0 shows the whole still
        bw, bh = im.width / z, im.height / z
        x = min(max(cx - bw / 2, 0), im.width - bw)
        y = min(max(cy - bh / 2, 0), im.height - bh)
        return np.asarray(im.resize((W, H), Image.BILINEAR, box=(x, y, x + bw, y + bh)))


_clips = {}


def clip(name):
    if name not in _clips:
        _clips[name] = StillClip(name)
    return _clips[name]


build.clip = clip

if __name__ == '__main__':
    missing = [p[1] for parts in PLAN.values() for p in parts if not os.path.exists(os.path.join(HF_RAW, p[1] + '.png'))]
    if missing:
        sys.exit('missing Higgsfield stills in irisya-tools/hf/raw (run fetch.py there): ' + ', '.join(missing))
    build.main()
