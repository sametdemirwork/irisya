"""İrisya — procedural iris renderer.

Renders the shade library used across the site (hero, stories, colour library,
package cards) as transparent WebP discs. No photos are involved: every iris is
built from filtered noise in polar space (radial fibres, collarette, crypts,
contraction furrows, limbal ring, pupillary ruff), then coloured per shade.

Run        python -E irisya-tools/iris.py [sheet_dir] [slug ...] [--preview]
             sheet_dir   optional folder for a review contact sheet (iris-sheet.jpg)
             slug ...    only these shades (default: all)
             --preview   render the sheet only (640 px), write no site files
Output     irisya-clinic/assets/img/iris/iris-<slug>-<size>.webp
             1600  hero (desktop)
             800   hero (phones), stories, colour-library tiles, cards
             360   thumbnails, avatars, swatches

Change a shade: edit SHADES and run again. The seed per shade keeps the fibre
pattern stable, so only the colour changes.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'irisya-clinic', 'assets', 'img', 'iris'))
SIZES = (1600, 800, 360)

NU, NT = 384, 3072          # polar texture: radial x angular samples
R_IRIS = 0.985              # iris radius (image half-size = 1)
PUPIL = 0.355               # pupil radius


def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], dtype=np.float32)


# Shade library. Codes and names are shown on the site.
#   pup  pupillary zone (inside the collarette)   col  collarette ring
#   mid  main stroma                               out  outer ciliary zone
#   lim  limbal ring                               hi   bright fibres
#   lo   deep stroma between fibres                cry  crypts
#   fl   optional pigment flecks (colour, amount)
SHADES = [
    dict(slug='glacier', code='IR-01', name='Glacier Blue', seed=11,
         pup='#8DA1AF', col='#DCE5EC', mid='#9EBBD3', out='#7E9DBA', lim='#2A3D52',
         hi='#F4F9FC', lo='#4C6A86', cry='#3A546E'),
    dict(slug='bosphorus', code='IR-02', name='Bosphorus Blue', seed=23,
         pup='#5F7E9B', col='#B9D0E4', mid='#4F8BC4', out='#3B74B0', lim='#0F2848',
         hi='#D6EAFA', lo='#1E4C80', cry='#173C66'),
    dict(slug='sapphire', code='IR-03', name='Sapphire', seed=37,
         pup='#3D5675', col='#8FAACA', mid='#2B5994', out='#1F467E', lim='#081631',
         hi='#A9C4E4', lo='#132F58', cry='#0E2445'),
    dict(slug='silver', code='IR-04', name='Silver Grey', seed=41,
         pup='#7F878E', col='#D3D7DA', mid='#9EA8B1', out='#838D97', lim='#2C3238',
         hi='#F3F5F6', lo='#58616A', cry='#454C53'),
    dict(slug='aegean', code='IR-05', name='Aegean Green', seed=53,
         pup='#8A8656', col='#CDCFA3', mid='#56968F', out='#417D78', lim='#11292B',
         hi='#D5EDE6', lo='#285B57', cry='#1F4744', fl=('#B39446', .16)),
    dict(slug='emerald', code='IR-06', name='Emerald', seed=67,
         pup='#83703C', col='#C9BC85', mid='#558C4E', out='#40733B', lim='#10230F',
         hi='#D4E9BC', lo='#2E5729', cry='#23421F', fl=('#B08A40', .26)),
    dict(slug='hazel', code='IR-07', name='Hazel', seed=71,
         pup='#6C4626', col='#B58F5C', mid='#7F7D45', out='#61703F', lim='#1D1F10',
         hi='#E2D3A4', lo='#47462A', cry='#382C18', fl=('#9A6A36', .32)),
    dict(slug='honey', code='IR-08', name='Honey', seed=83,
         pup='#7C4A1B', col='#DCA85E', mid='#B47C35', out='#956127', lim='#2E1B08',
         hi='#F5D9A2', lo='#673F16', cry='#4F3011'),
    dict(slug='brown', code='IR-00', name='Natural Brown', seed=97,
         pup='#3A2315', col='#6F4B2C', mid='#563820', out='#462C19', lim='#150D07',
         hi='#94704A', lo='#2C1A0E', cry='#1C1109'),
]


# ---------------------------------------------------------------- helpers
def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def blur(a, su, st):
    """Gaussian blur of a polar texture: periodic along angle (axis 1), padded along radius."""
    pad = int(3 * su) + 2
    a2 = np.pad(a, ((pad, pad), (0, 0)), mode='reflect')
    ku = np.fft.fftfreq(a2.shape[0])[:, None]
    kt = np.fft.fftfreq(a2.shape[1])[None, :]
    g = np.exp(-2.0 * np.pi ** 2 * ((su * ku) ** 2 + (st * kt) ** 2))
    out = np.real(np.fft.ifft2(np.fft.fft2(a2) * g))[pad:-pad]
    out -= out.mean()
    out /= out.std() + 1e-8
    return out.astype(np.float32)


def blur1(n, s, rng):
    """Smooth periodic 1D noise (angle), unit std."""
    a = rng.standard_normal(n)
    k = np.fft.fftfreq(n)
    out = np.real(np.fft.ifft(np.fft.fft(a) * np.exp(-2.0 * np.pi ** 2 * (s * k) ** 2)))
    out -= out.mean()
    return (out / (out.std() + 1e-8)).astype(np.float32)


def sample(tex, u, t):
    """Bilinear lookup in a polar texture; u in [0,1] (clamped), t in [0,1) (wrapped)."""
    nu, nt = tex.shape
    fu = np.clip(u, 0.0, 1.0) * (nu - 1)
    ft = np.mod(t, 1.0) * nt
    u0 = np.floor(fu).astype(np.int32)
    t0 = np.floor(ft).astype(np.int32)
    du = (fu - u0).astype(np.float32)
    dt = (ft - t0).astype(np.float32)
    u1 = np.minimum(u0 + 1, nu - 1)
    t1 = (t0 + 1) % nt
    t0 = t0 % nt
    return (tex[u0, t0] * (1 - du) * (1 - dt) + tex[u1, t0] * du * (1 - dt)
            + tex[u0, t1] * (1 - du) * dt + tex[u1, t1] * du * dt)


def sample1(arr, t):
    n = arr.shape[0]
    ft = np.mod(t, 1.0) * n
    i0 = np.floor(ft).astype(np.int32) % n
    i1 = (i0 + 1) % n
    d = (ft - np.floor(ft)).astype(np.float32)
    return arr[i0] * (1 - d) + arr[i1] * d


def ridge(n, width=1.5, power=2.0):
    """Thin bright lines along the zero crossings of a noise field."""
    return (1.0 - np.minimum(np.abs(n), width) / width) ** power


# ---------------------------------------------------------------- structure
_cache = {}


def build_structure(seed):
    """Shade-independent fields (one set per seed)."""
    if seed in _cache:
        return _cache[seed]
    rng = np.random.default_rng(seed)
    s = {}
    s['r1'] = blur(rng.standard_normal((NU, NT)), 64, 1.05)     # fine fibres
    s['r2'] = blur(rng.standard_normal((NU, NT)), 46, 1.8)      # second, crossing layer
    s['r3'] = blur(rng.standard_normal((NU, NT)), 30, 3.4)      # thicker trabeculae
    s['bundle'] = blur(rng.standard_normal((NU, NT)), 26, 6.5)  # fibre bundles with dark gaps
    s['spoke'] = blur(rng.standard_normal((NU, NT)), 34, 10)    # radial wedges
    s['coarse'] = blur(rng.standard_normal((NU, NT)), 16, 30)   # patches
    s['warp'] = blur(rng.standard_normal((NU, NT)), 60, 70)
    s['crypt'] = blur(rng.standard_normal((NU, NT)), 11, 13)
    s['fleck'] = blur(rng.standard_normal((NU, NT)), 2.6, 3.8)
    s['coll'] = blur1(NT, NT / 75.0, rng)          # collarette wander (~14 lobes)
    s['coll2'] = blur1(NT, NT / 300.0, rng)        # collarette zig-zag
    s['ruff'] = blur1(NT, NT / 260.0, rng)         # pupillary ruff crenellation
    s['pupil'] = blur1(NT, NT / 300.0, rng)
    s['furrow'] = [(blur1(NT, NT / 90.0, rng), blur1(NT, NT / 26.0, rng)) for _ in range(4)]
    _cache[seed] = s
    return s


def render(shade, size):
    s = build_structure(shade['seed'])
    c = {k: hexrgb(shade[k]) for k in ('pup', 'col', 'mid', 'out', 'lim', 'hi', 'lo', 'cry')}

    n = size
    ax = (np.arange(n, dtype=np.float32) + 0.5) / n * 2.0 - 1.0
    x, y = np.meshgrid(ax, ax)
    r = np.hypot(x, y)
    th = np.arctan2(y, x)
    t = (th + np.pi) / (2 * np.pi)

    inside = r < R_IRIS + 0.02
    ri = r[inside]
    ti = t[inside]
    thi = th[inside]

    def mix(a, b, k):
        k = np.clip(k, 0, 1)[..., None]
        return a * (1 - k) + b * k

    # pupil edge wanders very slightly
    p_r = PUPIL * (1.0 + 0.006 * sample1(s['pupil'], ti))
    u = (ri - p_r) / (R_IRIS - p_r)
    uc = np.clip(u, 0.0, 1.0)

    # fibres: thin ridges, two layers crossing at a slight angle, gently undulating
    w = sample(s['warp'], uc, ti) * 0.0013
    n1 = sample(s['r1'], uc, ti + w + 0.0032 * uc)
    n2 = sample(s['r2'], uc, ti + 1.3 * w - 0.0028 * uc)
    n3 = sample(s['r3'], uc, ti + 0.7 * w)
    f1 = ridge(n1, 1.5, 2.4)
    f2 = ridge(n2, 1.5, 2.0)
    f3 = ridge(n3, 1.6, 1.5)
    sp = sample(s['spoke'], uc, ti + w)
    cs = sample(s['coarse'], uc, ti)
    nb = sample(s['bundle'], uc, ti + 0.8 * w)
    fb = ridge(nb, 1.7, 1.3)
    fib = np.clip(0.30 * f1 + 0.24 * f2 + 0.36 * f3 + 0.42 * fb, 0, 1.15) / 1.15
    dens = np.clip(0.12 + 0.88 * fib + 0.12 * sp + 0.07 * cs, 0, 1)
    gap = smoothstep(0.25, -0.6, nb) * smoothstep(0.08, 0.3, u)   # dark clefts between bundles

    # collarette: wavy ring ~30% out from the pupil
    ucoll = 0.29 + 0.03 * sample1(s['coll'], ti) + 0.009 * sample1(s['coll2'], ti)
    coll = np.exp(-((u - ucoll) / 0.026) ** 2)
    pz = smoothstep(ucoll + 0.03, ucoll - 0.025, u)    # 1 = pupillary zone

    # radial base colour
    base = mix(c['mid'], c['out'], smoothstep(0.42, 0.9, u))
    base = mix(base, c['pup'], pz * 0.9)
    deep = mix(base * 0.42, c['lo'], 0.55)

    col = mix(deep, base, dens)
    col *= (1.0 - 0.22 * gap)[..., None]
    hi_amt = (0.5 - 0.28 * smoothstep(0.65, 1.0, u)) * (0.75 + 0.25 * (sp > 0))
    col = mix(col, c['hi'], smoothstep(0.5, 0.95, fib) * hi_amt)
    col *= (0.86 + 0.2 * np.clip(sp * 0.5 + 0.5, 0, 1))[..., None]

    # collarette: raised, lighter, with the fibre texture still showing
    col = mix(col, c['col'], coll * (0.14 + 0.34 * dens))
    # pupillary zone: a touch darker and finer
    col *= (1.0 - 0.10 * pz * (1 - f1))[..., None]

    # crypts: dark lacunae near the collarette and in the mid ciliary zone, crossed by fibres
    cr = sample(s['crypt'], uc, ti + w)
    cw = smoothstep(0.26, 0.36, u) * smoothstep(0.8, 0.52, u)
    crypt = smoothstep(0.8, 1.65, cr) * cw * (1 - 0.45 * f1) * (0.7 + 0.3 * (1 - fib))
    col = mix(col, mix(c['cry'], deep, 0.3), crypt * 0.88)

    # contraction furrows: broken concentric arcs near the edge
    for k, (wob, gate) in enumerate(s['furrow']):
        uk = (0.70, 0.78, 0.855, 0.92)[k] + 0.01 * sample1(wob, ti)
        ring = np.exp(-((u - uk) / 0.009) ** 2) * smoothstep(0.0, 0.9, sample1(gate, ti))
        col *= (1.0 - 0.17 * ring)[..., None]

    # pigment flecks (green / hazel shades)
    if 'fl' in shade:
        fcol, famt = hexrgb(shade['fl'][0]), shade['fl'][1]
        fk = sample(s['fleck'], uc, ti)
        fmask = smoothstep(1.9, 2.6, fk) * smoothstep(0.06, 0.18, u) * smoothstep(0.78, 0.42, u)
        col = mix(col, fcol * (0.85 + 0.3 * dens[..., None]), fmask * famt * 2.2)

    # limbal ring: a defined dark band at the edge
    lim = smoothstep(0.84, 1.0, u)
    col = mix(col, c['lim'], lim ** 1.25 * 0.92)
    col *= (1.0 - 0.35 * smoothstep(0.965, 1.0, u))[..., None]

    # pupillary ruff: thin, dark, crenellated border around the pupil
    ruff_edge = np.maximum(0.024 + 0.006 * sample1(s['ruff'], ti), 0.012)
    ruff = smoothstep(ruff_edge, ruff_edge * 0.3, u)
    col = mix(col, np.array([0.09, 0.06, 0.045], np.float32), ruff * 0.85)

    # soft key light from the upper right + a little dome falloff
    light = 1.0 + 0.08 * np.cos(thi + np.pi / 4) * smoothstep(0.0, 0.9, uc)
    col *= light[..., None]

    # pupil
    pupil = smoothstep(p_r + 0.0035, p_r - 0.0035, ri)
    pcol = np.array([0.016, 0.018, 0.024], np.float32)
    col = mix(col, pcol, pupil)

    col = np.clip(col, 0, 1) ** 1.03
    alpha = smoothstep(R_IRIS + 0.0035, R_IRIS - 0.0035, ri)

    out = np.zeros((n, n, 4), np.float32)
    out[inside, :3] = col
    out[inside, 3] = alpha
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    preview = '--preview' in sys.argv
    sheet_dir = args[0] if args else None
    only = args[1:]
    if not preview:
        os.makedirs(OUT, exist_ok=True)
    thumbs = []
    for sh in SHADES:
        if only and sh['slug'] not in only:
            continue
        if preview:
            thumbs.append((sh, render(sh, 640)))
            print('preview', sh['slug'])
            continue
        big = render(sh, SIZES[0])
        for sz in SIZES:
            im = big if sz == SIZES[0] else big.resize((sz, sz), Image.LANCZOS)
            path = os.path.join(OUT, f"iris-{sh['slug']}-{sz}.webp")
            im.save(path, 'WEBP', quality=86 if sz > 400 else 90, method=6)
        thumbs.append((sh, big.resize((640, 640), Image.LANCZOS)))
        print('rendered', sh['slug'], os.path.getsize(os.path.join(OUT, f"iris-{sh['slug']}-1600.webp")) // 1024, 'KB @1600')
    if sheet_dir and thumbs:
        cols = min(len(thumbs), 3)
        rows = (len(thumbs) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * 660, rows * 660), (4, 19, 43))
        for i, (sh, im) in enumerate(thumbs):
            sheet.paste(im, ((i % cols) * 660 + 10, (i // cols) * 660 + 10), im)
        sheet.save(os.path.join(sheet_dir, 'iris-sheet.jpg'), quality=90)


if __name__ == '__main__':
    main()
