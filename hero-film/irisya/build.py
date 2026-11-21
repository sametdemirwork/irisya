"""Irisya hero film: a fast-cut, effects-driven edit of the Kling clips, graded and encoded as the
looping hero background video.

Sources   raw/*.mp4  (1920x1080, 24 fps, 5 s, Kling 4.0 via Higgsfield; prompts in prompts.md,
          job ids and download links in SOURCES below)
Outputs   ../../irisya-clinic/assets/img/content/
            hero.{mp4,webm}            desktop, 1080p
            hero-720.{mp4,webm}        tablets / small laptops
            hero-portrait.{mp4,webm}   phones (608x1080, per-shot focus point)
            hero.webp, hero-portrait.webp              first paint = the frame playback starts on
            hero-still.webp, hero-still-portrait.webp  reduced-motion / data-saver still

Run       python -E build.py fetch           download any missing clip into raw/
          python -E build.py                 full render + encode
          python -E build.py 1.2 5.0 ...     preview stills at those times (build/preview-*.jpg)
          python -E build.py sheet           contact sheet of every raw clip (build/sheet-*.jpg)
Needs     pip install imageio-ffmpeg numpy pillow

The edit: 16 s, 17 cuts. Speed ramps (fast into and out of each shot, slow in the middle), zoom-blur
punch-ins, whip pans, a warm light leak over Galata, flash cuts with an ice-blue anamorphic flare, RGB
split cuts, a short recap montage and an iris that opens out of the patient's eye. No cut flashes the
whole frame more than once a second, and the montage cuts are colour splits, not flashes.

Frames are decoded once into cache/*.u8 (memory-mapped) so the edit runs in a few hundred MB
of RAM; delete cache/ and build/ afterwards if disk space matters.
"""
import json
import os
import subprocess
import sys
import urllib.request

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'raw')
CACHE = os.path.join(HERE, 'cache')
BUILD = os.path.join(HERE, 'build')
OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'irisya-clinic', 'assets', 'img', 'content'))
FF = imageio_ffmpeg.get_ffmpeg_exe()

FPS, W, H = 24, 1920, 1080
PW = 608                      # portrait crop width (9:16 out of 1080 rows)
LENGTH = 16.0                 # loop length, seconds
POSTER_T = 1.0                # playback starts here on first view, so the poster matches it
STILL_T = 15.0                # calm still for reduced motion / save-data

# The six Kling 4.0 clips in the Higgsfield account (generated 14-15 Nov 2026). The Higgsfield history
# no longer lists videos, but the jobs still answer `higgsfield generate get <id>`. 3-iris-green failed
# on Higgsfield and 7-hotel was never recorded, so the edit uses these six.
CDN = 'https://d8j0ntlcm91z4.cloudfront.net/user_3M6QeYEsYkpJnGzjpEWMIbA3iFT/'
SOURCES = {
    '1-iris-hazel': 'hf_20261114_235847_c7df7204-49d4-466e-8fff-bec49ad2b9a5.mp4',
    '2-iris-blue': 'hf_20261114_235533_5f2f5336-f6e3-44be-8384-24549528d15b.mp4',
    '4-bosphorus': 'hf_20261115_000307_7282ca5e-f2d2-4713-acf5-2f5d3564e4d0.mp4',
    '5-galata': 'hf_20261115_001848_0acc82d8-7a4b-454c-86c3-e134bd30ea9b.mp4',
    '6-transfer': 'hf_20261114_235533_7081cd10-a7b9-43b6-9607-03de40cf7daa.mp4',
    '8-clinic': 'hf_20261115_001628_9a8cd3cf-e315-4191-a46a-f5c5aa8a39f8.mp4',
}
CLIP_NAMES = tuple(SOURCES)
# 6-transfer holds three shots: the van (0-2.00 s), the chauffeur (2.04-3.54 s), the reflection (3.58-5.04 s)


def fetch():
    os.makedirs(RAW, exist_ok=True)
    for name, file in SOURCES.items():
        path = os.path.join(RAW, name + '.mp4')
        if os.path.exists(path):
            print(f'  {name}: already in raw/')
            continue
        print(f'  {name}: downloading', flush=True)
        urllib.request.urlretrieve(CDN + file, path + '.part')
        os.replace(path + '.part', path)


# ---------------------------------------------------------------- sources
class Clip:
    def __init__(self, name):
        os.makedirs(CACHE, exist_ok=True)
        path = os.path.join(CACHE, name + '.u8')
        meta_path = path + '.json'
        if not os.path.exists(meta_path):
            reader = imageio_ffmpeg.read_frames(os.path.join(RAW, name + '.mp4'))
            meta = next(reader)
            w, h = meta['size']
            n = 0
            with open(path, 'wb') as fh:
                for f in reader:
                    if (w, h) != (W, H):   # normalise odd sizes to the 1920x1080 canvas (cover)
                        img = Image.frombytes('RGB', (w, h), f)
                        s = max(W / w, H / h)
                        img = img.resize((round(w * s), round(h * s)), Image.LANCZOS)
                        x0, y0 = (img.width - W) // 2, (img.height - H) // 2
                        f = img.crop((x0, y0, x0 + W, y0 + H)).tobytes()
                    fh.write(f)
                    n += 1
            with open(meta_path, 'w') as fh:
                json.dump({'w': W, 'h': H, 'n': n, 'fps': meta.get('fps', FPS)}, fh)
        with open(meta_path) as fh:
            m = json.load(fh)
        self.n, self.fps = m['n'], m.get('fps', FPS)
        self.frames = np.memmap(path, np.uint8, 'r', shape=(m['n'], m['h'], m['w'], 3))

    def at(self, t):
        """uint8 frame at source time t; neighbouring frames are blended for sub-frame times."""
        f = min(max(t * self.fps, 0.0), self.n - 1.0)
        i = int(f)
        a = f - i
        if a < 0.04 or i + 1 >= self.n:
            return np.asarray(self.frames[i])
        mix = self.frames[i].astype(np.float32) * (1 - a) + self.frames[i + 1].astype(np.float32) * a
        return mix.astype(np.uint8)


_clips = {}


def clip(name):
    if name not in _clips:
        _clips[name] = Clip(name)
    return _clips[name]


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def ease_in(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * u


def ease_out(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def bell(t, c, sigma):
    return float(np.exp(-((t - c) / sigma) ** 2))


def crop_zoom(img, s, center):
    """Scale an RGB uint8 frame by s around center (fractions of the frame), keeping W x H."""
    if s <= 1.001 and center == (.5, .5):
        return img
    cw, ch = W / s, H / s
    x0 = min(max(center[0] * W - cw / 2, 0), W - cw)
    y0 = min(max(center[1] * H - ch / 2, 0), H - ch)
    return np.asarray(Image.fromarray(img).resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)))


# camera shake on the hardest cuts: (cut time, amplitude as a fraction of the frame)
IMPACTS = [(1.75, .006), (4.75, .003), (8.625, .005), (13.0, .004)]


def shake(t):
    dx = dy = 0.0
    for tc, amp in IMPACTS:
        u = t - tc
        if 0 <= u < .45:
            k = amp * np.exp(-u / .11)
            dx += k * np.sin(2 * np.pi * 17 * u)
            dy += k * .7 * np.cos(2 * np.pi * 13 * u)
    return dx, dy


class Shot:
    """A source clip placed on the timeline: speed (or ramp), push-in, framing and portrait focus.

    speed  1.2           constant
           (0.8, 2.4)    linear ramp from the first to the second value
           ('v', 2.2, .9)  fast in, slow in the middle, fast out (the edge speed, then the middle one)
    """

    def __init__(self, key, name, t0, t1, src, speed=1.0, zoom=(1.0, 1.05), center=(.5, .5),
                 focus=.5, gain=1.0, sat=.92, flip=False):
        self.key, self.name = key, name
        self.t0, self.t1, self.src, self.speed = t0, t1, src, speed
        self.zoom, self.center, self.focus = zoom, center, focus
        self.gain, self.sat, self.flip = gain, sat, flip

    def scale(self, t):
        return self.zoom[0] + (self.zoom[1] - self.zoom[0]) * ease((t - self.t0) / (self.t1 - self.t0))

    def source(self, t):
        """(source time, playback speed) at timeline time t."""
        d, dur = t - self.t0, self.t1 - self.t0
        u = d / dur
        sp = self.speed
        if isinstance(sp, (int, float)):
            return self.src + d * sp, sp
        if sp[0] == 'v':
            edge, mid = sp[1], sp[2]
            v = mid + (edge - mid) * (2 * u - 1) ** 2
            return self.src + mid * d + (edge - mid) * dur * ((2 * u - 1) ** 3 + 1) / 6, v
        v0, v1 = sp
        return self.src + d * (v0 + (v1 - v0) * u / 2), v0 + (v1 - v0) * u

    def last_source(self):
        return self.source(self.t1)[0]

    def raw(self, t, extra=1.0):
        c = clip(self.name)
        s, v = self.source(t)
        img = c.at(s)
        if v > 1.5:   # fast playback: blend in a step back for motion blur, so the ramp reads smooth
            img = ((img.astype(np.uint16) + c.at(s - v / (2 * FPS))) // 2).astype(np.uint8)
        dx, dy = shake(t)
        img = crop_zoom(img, self.scale(t) * extra, (self.center[0] + dx, self.center[1] + dy))
        if self.flip:
            img = img[:, ::-1]
        return img

    def frame(self, t, extra=1.0):
        return grade(self.raw(t, extra).astype(np.float32) / 255, self.gain, self.sat)


# ---------------------------------------------------------------- grade (Irisya navy)
LUMA = np.array([.2126, .7152, .0722], np.float32)
SHADOW = np.array([.004, .016, .044], np.float32)    # deep shadows fall to Irisya night-navy, not grey
HIGH = np.array([.968, .984, 1.0], np.float32)       # highlights lean cool porcelain-white
ICE = np.array([.55, .75, 1.0], np.float32)
WARM = np.array([1.0, .66, .32], np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
VIGNETTE = (1 - .40 * _r ** 2.2)[..., None].astype(np.float32)
DITHER = (np.random.default_rng(7).random((H, W, 1), np.float32) - .5) * (1.6 / 255)
# synthetic lens flare for flash cuts: soft core + anamorphic streak, Irisya ice-blue
_fx = (xx - W * .5) / W
_fy = (yy - H * .46) / H
FLARE = (np.exp(-(_fx ** 2 + _fy ** 2) / .045)[..., None] * np.array([.62, .76, 1.0], np.float32)
         + np.exp(-(_fy ** 2) / .0009 - (_fx ** 2) / .5)[..., None] * np.array([.55, .72, 1.0], np.float32) * .9
         ).astype(np.float32)
del yy, xx, _r, _fx, _fy
LX = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
LY = np.linspace(-1, 1, H, dtype=np.float32)[:, None]


def luma(x):
    return x @ LUMA


def grade(x, gain=1.0, sat=.92):
    x = x * gain
    L = luma(x)[..., None]
    x = np.clip(L + (x - L) * sat, 0, 1)
    x = x + (x * x * (3 - 2 * x) - x) * .38                   # filmic S-curve
    L = luma(x)[..., None]
    x = x * (1 + (HIGH - 1) * L * L) + SHADOW * (1 - L) ** 6   # split tone
    return x


def small(x, f):
    h, w = x.shape[0] // f, x.shape[1] // f
    return x[:h * f, :w * f].reshape(h, f, w, f, 3).mean((1, 3))


def upscale(s):
    u8 = Image.fromarray((np.clip(s, 0, 1) * 255).astype(np.uint8))
    return np.asarray(u8.resize((W, H), Image.BILINEAR)).astype(np.float32) / 255


def box_x(x, r):
    """Horizontal box blur of radius r (pixels) along axis 1."""
    if r < 1:
        return x
    r = int(r)
    p = np.pad(x, ((0, 0), (r + 1, r), (0, 0)), mode='edge')
    c = np.cumsum(p, axis=1, dtype=np.float32)
    return (c[:, 2 * r + 1:] - c[:, :-2 * r - 1]) / (2 * r + 1)


def bloom(x, amount=.30):
    hl = np.clip(luma(x) - .58, 0, None)[..., None] * x
    s = Image.fromarray((np.clip(small(hl, 4), 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9))
    glow = np.asarray(s.resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    return x + glow * np.array([.84, .92, 1.0], np.float32) * amount


def streak(x, k):
    """Anamorphic flare: highlights smeared horizontally, tinted ice-blue."""
    hl = np.clip(luma(x) - .72, 0, None)[..., None] * np.ones(3, np.float32)
    s = box_x(small(hl, 8), 38)
    s = box_x(s, 20)
    return upscale(s * 4) * np.array([.6, .76, 1.0], np.float32) * k


def screen(a, b):
    return 1 - (1 - np.clip(a, 0, 1)) * (1 - np.clip(b, 0, 1))


def rgb_split(x, px):
    """Chromatic split: red pushed right, blue pushed left by px pixels, green stays."""
    s = int(round(px))
    if s < 1:
        return x
    out = x.copy()
    out[:, s:, 0] = x[:, :-s, 0]
    out[:, :-s, 2] = x[:, s:, 2]
    return out


def leak(pos, color, width=.38, tilt=.3):
    """A soft, slightly tilted band of light centred at horizontal position pos (-1 left edge, 1 right)."""
    band = np.exp(-((LX - pos - tilt * LY) / width) ** 2) * (1 - .4 * LY ** 2)
    return band[..., None] * color


def zoom_blur(shot, t, strength, center):
    """Radial zoom blur: average of progressively larger copies around center."""
    acc = np.zeros((H, W, 3), np.float32)
    n = 9
    for i in range(n):
        acc += crop_zoom(shot.raw(t), 1 + strength * i / (n - 1), center).astype(np.float32)
    acc = acc / n
    if strength > .02:   # melt the copies together so the steps never read
        acc = np.asarray(Image.fromarray(acc.astype(np.uint8)).filter(ImageFilter.GaussianBlur(strength * 60))).astype(np.float32)
    return grade(acc / 255, shot.gain, shot.sat)


# ---------------------------------------------------------------- transitions
def flash_cut(a, b, tc, strength=.85):
    def render(t):
        x = (a if t < tc else b).frame(t)
        k = bell(t, tc, .085) * strength
        x = x * (1 + 1.3 * k)
        x = screen(x, FLARE * 1.05 * k)
        x = x + streak(x, 1.1 * k)
        return rgb_split(x, 14 * k)
    return render


def whip_cut(a, b, tc, direction=1):
    def render(t):
        k = bell(t, tc, .07)
        out = t < tc
        x = (a if out else b).frame(t)
        shift = int(direction * (-1 if out else 1) * 140 * k)
        x = np.roll(x, shift, axis=1)
        x = box_x(box_x(x, 90 * k), 60 * k)
        return rgb_split(x * (1 + .35 * k), 10 * k)
    return render


def punch_cut(a, b, tc, ca=(.5, .5), cb=(.5, .5)):
    """Fast push into a, radial zoom blur through the cut, b settles out of the same blur."""
    def render(t):
        if t < tc:
            k = ease_in(1 - (tc - t) / .22)
            x = zoom_blur(a, t, .22 * k, ca) * (1 + .2 * k)
        else:
            k = 1 - ease_out((t - tc) / .26)
            x = zoom_blur(b, t, .18 * k, cb) * (1 + .18 * k)
        x = x + streak(x, .7 * bell(t, tc, .08))
        return rgb_split(x, 16 * bell(t, tc, .07))
    return render


def leak_cut(a, b, tc, color=WARM, half=.24):
    """A warm band of light sweeps across the frame and hides the cut at its brightest."""
    def render(t):
        u = (t - (tc - half)) / (2 * half)
        x = (a if t < tc else b).frame(t)
        k = np.sin(np.pi * min(max(u, 0), 1))
        x = screen(x * (1 + .12 * k), leak(-1.7 + 3.4 * ease(u), color, .42) * .95 * k)
        return x
    return render


def split_cut(a, b, tc, px=24, sigma=.045):
    """Hard cut with an RGB split and a few frame bands slipping sideways around it."""
    def render(t):
        x = (a if t < tc else b).frame(t)
        k = bell(t, tc, sigma)
        x = rgb_split(x, px * k)
        if k > .5:
            rng = np.random.default_rng(int(tc * 1000) * 7 + int(round(t * FPS)))
            for _ in range(3):
                y0, h = int(rng.integers(0, H - 80)), int(rng.integers(10, 60))
                x[y0:y0 + h] = np.roll(x[y0:y0 + h], int(rng.integers(-70, 70) * k), axis=1)
        return x * (1 + .08 * k)
    return render


_ring_cache = {}


def iris_open(a, b, t0, t1, center=(.5, .5)):
    """b opens out of a's pupil: a pushes into its centre, b grows in a soft-edged circle with a thin
    ice-blue rim, like an iris diaphragm opening."""
    cx, cy = center[0] * W, center[1] * H
    if center not in _ring_cache:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        _ring_cache[center] = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    dist = _ring_cache[center]
    rmax = float(dist.max()) + 40

    def render(t):
        u = (t - t0) / (t1 - t0)
        r = rmax * ease_in(u) ** .9
        xa = a.frame(t, extra=1 + .55 * ease_in(u)) * (1 - .35 * u)
        xb = b.frame(t, extra=1.18 - .18 * ease_out(u))
        m = smoothstep(r - 2 - .06 * r, r + 2, dist)[..., None]        # 0 inside the circle → b
        x = xb * (1 - m) + xa * m
        rim = np.exp(-((dist - r) / (6 + .02 * r)) ** 2)[..., None] * ICE
        return screen(x, rim * .55 * np.sin(np.pi * min(u * 1.1, 1)))
    return render


# ---------------------------------------------------------------- edit
# key, clip, t0, t1, source-in, speed, zoom (from, to), zoom centre, portrait focus, gain, sat
S = {s.key: s for s in [
    # 01 the brown iris warms to hazel, speeding up into the punch through the pupil
    Shot('hazel',  '1-iris-hazel', 0.000,  1.750, 1.40, (1.4, 2.6), (1.02, 1.18), (.46, .40), focus=.46, gain=1.2, sat=1.05),
    # 02 Istanbul: the Bosphorus by night, Galata tower, the Golden Horn catching the sun
    Shot('bosph',  '4-bosphorus',  1.750,  3.000, 0.50, ('v', 2.4, .9), (1.06, 1.14), (.55, .45), focus=.70, gain=1.12, sat=.95),
    Shot('tower',  '5-galata',     3.000,  3.875, 0.10, ('v', 2.2, .9), (1.04, 1.10), (.35, .42), focus=.20, sat=.9),
    Shot('glint',  '5-galata',     3.875,  4.750, 3.50, ('v', 2.0, .8), (1.04, 1.10), (.60, .45), focus=.62, sat=.9),
    # 03 the pickup: van, chauffeur, reflection (the three shots inside 6-transfer)
    Shot('van',    '6-transfer',   4.750,  5.625, 0.30, ('v', 2.0, .9), (1.00, 1.06), (.5, .5), focus=.60, gain=1.10),
    Shot('chauf',  '6-transfer',   5.625,  6.500, 2.12, ('v', 1.8, .9), (1.02, 1.08), (.55, .5), focus=.70, gain=1.10),
    Shot('refl',   '6-transfer',   6.500,  7.375, 3.66, ('v', 1.8, .9), (1.04, 1.10), (.5, .5), focus=.50, gain=1.10),
    # 04 the exam, then a punch-in to the patient's eye in the slit-lamp light
    Shot('clinic', '8-clinic',     7.375,  8.625, 0.30, 1.1, (1.00, 1.08), (.42, .40), focus=.40, gain=1.0),
    Shot('close',  '8-clinic',     8.625,  9.625, 1.90, 1.0, (1.55, 1.65), (.36, .38), focus=.50, gain=1.04),
    # 05 the iris opens out of that eye and turns hazel to ice blue, slowing down through the change
    Shot('blue',   '2-iris-blue',  9.625, 12.333, 1.30, ('v', 1.5, .75), (1.00, 1.10), (.5, .48), focus=.50, sat=1.02),
    # recap: four quick shots, four frames each, bright to dark, so the only jump in brightness is the
    # flash from the brown iris to the blue one
    Shot('m1',     '8-clinic',     12.333, 12.500, 3.60, 1.0, (1.75, 1.60), (.36, .38), gain=1.04),
    Shot('m2',     '6-transfer',   12.500, 12.667, 2.90, 1.0, (1.20, 1.10), (.62, .45), gain=1.10),
    Shot('m3',     '4-bosphorus',  12.667, 12.833, 3.60, 1.0, (1.25, 1.15), (.72, .42), gain=1.12, sat=.95),
    Shot('m4',     '1-iris-hazel', 12.833, 13.000, 4.30, 1.0, (1.30, 1.22), (.45, .38), gain=1.2, sat=1.05),
    # 01 again: the finished ice-blue iris, mirrored so it reads as the other eye, slow push-in
    Shot('final',  '2-iris-blue',  13.000, LENGTH, 3.00, 0.55, (1.00, 1.14), (.5, .47), focus=.50, sat=1.04, flip=True),
]}
ORDER = list(S.values())

TRANSITIONS = [
    (1.530, 2.010, punch_cut(S['hazel'], S['bosph'], 1.750, (.46, .40), (.55, .45))),
    (2.850, 3.150, whip_cut(S['bosph'], S['tower'], 3.000)),
    (3.635, 4.115, leak_cut(S['tower'], S['glint'], 3.875)),
    (4.570, 4.930, flash_cut(S['glint'], S['van'], 4.750, .6)),
    (5.475, 5.775, whip_cut(S['van'], S['chauf'], 5.625)),
    (6.400, 6.600, split_cut(S['chauf'], S['refl'], 6.500, 30, .06)),
    (7.195, 7.555, flash_cut(S['refl'], S['clinic'], 7.375, .38)),   # the clinic is bright already
    (8.405, 8.885, punch_cut(S['clinic'], S['close'], 8.625, (.36, .38), (.36, .38))),
    (9.400, 9.950, iris_open(S['close'], S['blue'], 9.400, 9.950)),
    (12.273, 12.393, split_cut(S['blue'], S['m1'], 12.333)),
    (12.440, 12.560, split_cut(S['m1'], S['m2'], 12.500)),
    (12.607, 12.727, split_cut(S['m2'], S['m3'], 12.667)),
    (12.773, 12.873, split_cut(S['m3'], S['m4'], 12.833)),
    (12.875, 13.180, flash_cut(S['m4'], S['final'], 13.000, .5)),
]

CUES = [  # chapter changes the page syncs its caption to (CUES in irisya-clinic/assets/js/main.js)
    [0, 'Laser eye colour change'],
    [1.75, 'Istanbul'],
    [4.75, 'Airport pickup'],
    [7.375, 'Eye exam first'],
    [9.625, 'Your shade, planned'],
    [13, 'Laser eye colour change'],
]

FINAL_SWEEP = (13.45, 14.65)   # an ice-blue light band crosses the finished iris once


def shot_at(t):
    for s in ORDER:
        if s.t0 <= t < s.t1:
            return s
    return ORDER[-1]


def render(t):
    for t0, t1, fn in TRANSITIONS:
        if t0 <= t < t1:
            x = fn(t)
            break
    else:
        x = shot_at(t).frame(t)
    a, b = FINAL_SWEEP
    if a <= t < b:
        u = (t - a) / (b - a)
        x = screen(x, leak(-1.8 + 3.6 * ease(u), ICE, .3, .45) * .32 * np.sin(np.pi * u))
    x = bloom(np.clip(x, 0, 1.4)) * VIGNETTE
    x = x * ease(t / .4) * (1 - ease((t - (LENGTH - .45)) / .45))   # breathe through black at the loop point
    return np.clip(x * 255 + DITHER * 255 + .5, 0, 255).astype(np.uint8)


def focus_at(t):
    """Portrait crop centre; eases between shots so cuts inside transitions do not jump."""
    s = shot_at(t)
    i = ORDER.index(s)
    if i + 1 < len(ORDER) and t > s.t1 - .2:
        return s.focus + (ORDER[i + 1].focus - s.focus) * ease((t - (s.t1 - .2)) / .4)
    if i > 0 and t < s.t0 + .2:
        prev = ORDER[i - 1]
        return prev.focus + (s.focus - prev.focus) * ease((t - (s.t0 - .2)) / .4)
    return s.focus


def portrait(img, t):
    x0 = int(round(min(max(focus_at(t) * W - PW / 2, 0), W - PW)))
    return np.ascontiguousarray(img[:, x0:x0 + PW])


def check_edit():
    """Every shot stays inside its source clip (and inside its part of 6-transfer)."""
    parts = {'van': 2.0, 'chauf': 3.54, 'm2': 3.54, 'refl': 5.0}
    for s in ORDER:
        end = s.last_source()
        limit = parts.get(s.key, clip(s.name).n / clip(s.name).fps - .05)
        if end > limit or s.src < 0:
            sys.exit(f'shot {s.key}: source {s.src:.2f}-{end:.2f} s runs past {limit:.2f} s')


# ---------------------------------------------------------------- review helpers
def contact_sheets():
    """One sheet per raw clip: 12 evenly spaced frames with timestamps, for picking in-points."""
    os.makedirs(BUILD, exist_ok=True)
    for name in CLIP_NAMES:
        if not os.path.exists(os.path.join(RAW, name + '.mp4')):
            continue
        c = clip(name)
        dur = c.n / c.fps
        tw, th = 480, 270
        sheet = Image.new('RGB', (tw * 4, th * 3), 'black')
        d = ImageDraw.Draw(sheet)
        for i in range(12):
            t = dur * (i + .5) / 12
            im = Image.fromarray(c.at(t)).resize((tw, th), Image.BILINEAR)
            sheet.paste(im, ((i % 4) * tw, (i // 4) * th))
            d.text(((i % 4) * tw + 8, (i // 4) * th + 6), f'{t:.2f}s', fill='yellow')
        sheet.save(os.path.join(BUILD, f'sheet-{name}.jpg'), quality=82)
        print(f'  {name}: {c.n} frames @ {c.fps} fps = {dur:.2f}s')


# ---------------------------------------------------------------- encode
def pipe(path, w, h):
    return subprocess.Popen(
        [FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS),
         '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '9', '-pix_fmt', 'yuv420p', path],
        stdin=subprocess.PIPE)


def run(args):
    print(' ', os.path.basename(args[-1]), flush=True)
    subprocess.run([FF, '-y', '-loglevel', 'error'] + args, check=True)


def deliver(master, name, vf, crf_mp4=23, crf_webm=33):
    common_mp4 = ['-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf_mp4), '-profile:v', 'high', '-pix_fmt', 'yuv420p',
                  '-x264-params', 'aq-mode=3:aq-strength=0.9', '-g', '48', '-movflags', '+faststart', '-an']
    common_webm = ['-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', str(crf_webm), '-row-mt', '1', '-tile-columns', '2',
                   '-deadline', 'good', '-cpu-used', '2', '-aq-mode', '2', '-g', '48', '-pix_fmt', 'yuv420p', '-an']
    vf_args = ['-vf', vf] if vf else []
    run(['-i', master] + vf_args + common_mp4 + [os.path.join(OUT, name + '.mp4')])
    run(['-i', master] + vf_args + common_webm + [os.path.join(OUT, name + '.webm')])


def save_webp(img, name, q=74):
    Image.fromarray(img).save(os.path.join(OUT, name), 'WEBP', quality=q, method=6)


def main():
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    args = sys.argv[1:]
    if args == ['fetch']:
        fetch()
        return
    if args == ['sheet']:
        contact_sheets()
        return
    check_edit()
    if args:   # preview stills at the given times instead of rendering
        for t in map(float, args):
            img = render(t)
            Image.fromarray(img).save(os.path.join(BUILD, f'preview-{t:05.2f}.jpg'), quality=88)
            Image.fromarray(portrait(img, t)).save(os.path.join(BUILD, f'preview-{t:05.2f}-p.jpg'), quality=88)
        return
    land, port = os.path.join(BUILD, 'master.mp4'), os.path.join(BUILD, 'master-portrait.mp4')
    n = int(round(LENGTH * FPS))
    pl, pp = pipe(land, W, H), pipe(port, PW, H)
    stills = {int(round(POSTER_T * FPS)): 'hero', int(round(STILL_T * FPS)): 'hero-still'}
    for i in range(n):
        t = i / FPS
        img = render(t)
        por = portrait(img, t)
        pl.stdin.write(img.tobytes())
        pp.stdin.write(por.tobytes())
        if i in stills:
            save_webp(img, stills[i] + '.webp')
            save_webp(por, stills[i] + '-portrait.webp')
        if i % 24 == 0:
            print(f'  frame {i}/{n}', flush=True)
    for p in (pl, pp):
        p.stdin.close()
        p.wait()
    print('encoding deliverables')
    deliver(land, 'hero', None, crf_mp4=25)   # the fast cuts cost bitrate; 25 keeps the Safari file near 5.7 MB
    deliver(land, 'hero-720', 'scale=1280:720:flags=lanczos')
    deliver(port, 'hero-portrait', None)
    print(json.dumps(CUES, ensure_ascii=False))


if __name__ == '__main__':
    main()
