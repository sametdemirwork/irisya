"""Local stand-ins for the GPT Image 2.6 eye-colour edits (story-N-before, story-3-after, story-5-after, tx-4-after).

The edits were lost with the project folder on 2026-11-20 and the Higgsfield history does not list them, so this
script redoes them on the raw portraits: it finds each iris (a circle fit on the iris / sclera edge), masks out the
eyelid skin that covers it, and recolours only those pixels. The iris texture (its luminance) is kept, the colour
comes from the target shade. Everything outside the irises stays byte-identical, so ba.py registers the result at
scale 1, offset 0, and its colour-difference mask picks up exactly the recoloured irises.

Writes raw/<name>.png next to the sources, plus raw/<name>-mask.png (the recoloured pixels, read by ba.py). Usage:
  python recolour.py                 # every job
  python recolour.py story-1-before  # only these
  python recolour.py --sheet DIR     # also write a check sheet per job (iris circle + mask + result)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"

# rough eye centres (image left, image right) in the raw files; the circle fit refines them
STORY_EYES = {
    1: ((475, 850), (772, 828)),
    2: ((540, 659), (852, 636)),
    3: ((557, 775), (860, 785)),
    4: ((555, 735), (930, 735)),
    5: ((522, 590), (790, 575)),
}
TX4_EYES = ((523, 718), (1547, 767))  # dark brown (image left), light blue (image right)

# target colours as (Cb, Cr) slopes per unit of luma, plus the luma the iris median is moved to.
# brown: "a very dark, deep espresso brown, almost black-brown, a natural ordinary dark brown eye"
# silver: IR-04 Silver Grey, "cool soft silver grey with a faint blue cast, clearly grey rather than blue"
# bosphorus: IR-02 Bosphorus Blue, "clear bright medium blue like the Bosphorus on a sunny day"
SHADES = {
    "brown": {"luma": 46, "cb": -.20, "cr": .25, "contrast": .9},
    "silver": {"luma": 132, "cb": .045, "cr": -.02, "contrast": 1.0},
    "bosphorus": {"luma": 104, "cb": .27, "cr": -.21, "contrast": 1.05},
}

# name: (source, eye centres, shade or ("match", eye), options)
#   open: the visible part of the iris between the lids, as fractions of the radius above and below the centre
#         (only where the lids are as warm as the iris, so the colour test cannot tell them apart)
#   luma: override of the shade's iris brightness
OPTS = {"story-1-before": {"open": (.36, .68), "luma": 30}}
JOBS = {f"story-{i}-before": (f"story-{i}", STORY_EYES[i], "brown") for i in STORY_EYES}
JOBS["story-3-after"] = ("story-3", STORY_EYES[3], "silver")
JOBS["story-5-after"] = ("story-5", STORY_EYES[5], "bosphorus")
JOBS["tx-4-after"] = ("tx-4", TX4_EYES[:1], ("match", TX4_EYES[1]))


def ycc(im):
    return np.asarray(im.convert("YCbCr"), np.float32)


def fit_iris(Y, c, rmin, rmax, search):
    """Circle with the strongest dark-to-bright step along its lower and side arcs (the upper lid usually covers the top)."""
    th = np.radians(np.r_[np.arange(-25, 50, 5), np.arange(130, 206, 5)])  # sides + lower arc, y points down
    rs = np.arange(rmin, rmax + 1, 1.0)
    best = (-1e9, c[0], c[1], rmin)
    Yb = np.asarray(Image.fromarray(Y.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)), np.float32)
    H, W = Y.shape
    for cy in range(c[1] - search, c[1] + search + 1, 2):
        for cx in range(c[0] - search, c[0] + search + 1, 2):
            xs = np.clip(np.round(cx + rs[:, None] * np.cos(th)), 0, W - 1).astype(int)
            ys = np.clip(np.round(cy + rs[:, None] * np.sin(th)), 0, H - 1).astype(int)
            ring = Yb[ys, xs].mean(1)
            step = ring[2:] - ring[:-2]
            k = int(np.argmax(step))
            if step[k] > best[0]:
                best = (float(step[k]), cx, cy, float(rs[k + 1]))
    return best[1], best[2], best[3]


def iris_mask(a, cx, cy, r, opening=None):
    """Soft disc of the iris without the eyelid skin that hangs over it and without the sclera."""
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot(xx - cx, yy - cy)
    disc = np.clip((r - d) / 2.0 + .5, 0, 1)
    if opening:
        top, bottom = opening
        disc *= np.clip((yy - (cy - top * r)) / 2.0 + .5, 0, 1) * np.clip(((cy + bottom * r) - yy) / 2.0 + .5, 0, 1)
    Y, Cb, Cr = a[..., 0], a[..., 1], a[..., 2]
    inner = d < r * .85
    ring = (d > r * 1.6) & (d < r * 2.4) & (yy < cy - r * .6)  # the lid skin above the eye
    yi = np.median(Y[inner])
    skin_y, skin_cr = np.median(Y[ring]), np.median(Cr[ring])
    # skin: brighter than the iris and as warm as the lid; sclera: brighter still and neutral
    t = (yi + skin_y) / 2
    skin = (Y > t) & (Cr > skin_cr - 6) & (yy < cy)
    sclera = (Y > yi + .55 * (255 - yi)) & (np.abs(Cr - 128) < 10) & (np.abs(Cb - 128) < 12)
    out = disc * ~(skin | sclera)
    m = Image.fromarray((out * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    return np.asarray(m, np.float32) / 255 * disc


def recolour(a, m, shade, ref=None, luma=None):
    """a: YCbCr float array, m: 0..1 mask. Keeps the iris texture (luma), swaps the colour."""
    Y = a[..., 0]
    sel = m > .5
    med = np.median(Y[sel])
    out = a.copy()
    if ref is not None:  # match another iris: its luma distribution, and its colour at the same place in the iris
        ry, rcb, rcr = ref["y"], ref["cb"], ref["cr"]
        ranks = np.argsort(np.argsort(Y[sel]))
        q = np.sort(ry)[np.clip((ranks / max(1, sel.sum() - 1) * (len(ry) - 1)).astype(int), 0, len(ry) - 1)]
        Yn = Y.copy()
        Yn[sel] = q
        Yn = np.where(sel, Yn, np.clip(Y - med + np.median(ry), 0, 255))
        pb, pr = np.polyfit(ry, rcb, 1), np.polyfit(ry, rcr, 1)
        Cb, Cr = np.polyval(pb, Yn), np.polyval(pr, Yn)
        # the other eye mirrored onto this one at the same relative radius (keeps e.g. a warm ring round the pupil)
        (tx, ty, tr), (rx, rcy, rr) = ref["target"], ref["circle"]
        H, W = Y.shape
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        sx = np.clip(np.round(rx - (xx - tx) * rr / tr), 0, W - 1).astype(int)
        sy = np.clip(np.round(rcy + (yy - ty) * rr / tr), 0, H - 1).astype(int)
        ok = ref["valid"][sy, sx] * (m > 0)
        Cb = np.where(ok > .5, ref["cb_map"][sy, sx], Cb)
        Cr = np.where(ok > .5, ref["cr_map"][sy, sx], Cr)
    else:
        s = dict(SHADES[shade], **({"luma": luma} if luma else {}))
        Yn = np.clip(s["luma"] + (Y - med) * s["contrast"] * s["luma"] / max(med, 1), 0, 255)
        Cb = 128 + s["cb"] * Yn
        Cr = 128 + s["cr"] * Yn
    # window reflections and the shadowed sclera at the rim are much brighter than the iris:
    # they keep their brightness and turn neutral instead of taking the new colour
    hl = np.clip((Y - max(med + 45, 150)) / 45, 0, 1)
    Yn = Yn * (1 - hl) + Y * hl
    Cb = Cb * (1 - hl) + 128 * hl
    Cr = Cr * (1 - hl) + 128 * hl
    k = m[..., None]
    new = np.stack([Yn, Cb, Cr], -1)
    out = a * (1 - k) + new * k
    return out


def to_rgb(a):
    return Image.fromarray(np.clip(a + .5, 0, 255).astype(np.uint8), "YCbCr").convert("RGB")


def run(name, sheet=None):
    src, eyes, shade = JOBS[name]
    opts = OPTS.get(name, {})
    im = Image.open(RAW / f"{src}.png").convert("RGB")
    a = ycc(im)
    Y = a[..., 0]
    span = abs(eyes[-1][0] - eyes[0][0]) if len(eyes) > 1 else 1024
    rmin, rmax = (round(span * .075), round(span * .125)) if len(eyes) > 1 else (60, 130)
    m = np.zeros(Y.shape, np.float32)
    fits = []
    for c in eyes:
        cx, cy, r = fit_iris(Y, c, rmin, rmax, 14 if len(eyes) > 1 else 24)
        fits.append((cx, cy, r))
        m = np.maximum(m, iris_mask(a, cx, cy, r * .97, opts.get("open")))
    ref = None
    if isinstance(shade, tuple):  # ("match", eye): copy that iris's colour; both irises are the same size
        r0 = fits[0][2]
        rx, ry, rr = fit_iris(Y, shade[1], round(r0 * .9), round(r0 * 1.1), 30)
        print(f"  reference iris ({rx},{ry}) r{rr:.0f}")
        H, W = Y.shape
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.hypot(xx - rx, yy - ry)
        rmask = iris_mask(a, rx, ry, rr * .97)
        sel = (rmask > .5) & (d > rr * .3)  # iris ring without the pupil
        blur = lambda ch: np.asarray(Image.fromarray(np.clip(ch, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32)
        ref = {"y": Y[sel], "cb": a[..., 1][sel], "cr": a[..., 2][sel], "circle": (rx, ry, rr), "target": fits[0],
               "valid": (rmask > .5) & (d > rr * .25), "cb_map": blur(a[..., 1]), "cr_map": blur(a[..., 2])}
    out = to_rgb(recolour(a, m, shade, ref, opts.get("luma")))
    # outside the masks the pixels must not move at all
    keep = Image.fromarray((m > 0).astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(5))
    out = Image.composite(out, im, keep)
    out.save(RAW / f"{name}.png")
    # the exact pixels that were recoloured: ba.py uses this instead of guessing them from colour differences
    Image.fromarray((m * 255).astype(np.uint8)).save(RAW / f"{name}-mask.png")
    print(f"{name:16s} from {src}: irises " + ", ".join(f"({x},{y}) r{r:.0f}" for x, y, r in fits))
    if sheet:
        Path(sheet).mkdir(parents=True, exist_ok=True)
        tiles = []
        for cx, cy, r in fits:
            box = (int(cx - r * 2.2), int(cy - r * 1.4), int(cx + r * 2.2), int(cy + r * 1.4))
            t1 = im.crop(box).copy()
            ImageDraw.Draw(t1).ellipse((cx - r - box[0], cy - r - box[1], cx + r - box[0], cy + r - box[1]), outline=(255, 0, 0))
            t2 = Image.fromarray((m * 255).astype(np.uint8)).crop(box).convert("RGB")
            t3 = out.crop(box)
            tiles += [t.resize((300, round(300 * t.height / t.width))) for t in (t1, t2, t3)]
        h = tiles[0].height
        s = Image.new("RGB", (900, h * len(fits)), "white")
        for i, t in enumerate(tiles):
            s.paste(t, ((i % 3) * 300, (i // 3) * h))
        s.save(Path(sheet) / f"{name}.png")


def main():
    args = sys.argv[1:]
    sheet = None
    if "--sheet" in args:
        sheet = args[args.index("--sheet") + 1]
        del args[args.index("--sheet"):args.index("--sheet") + 2]
    for name in args or JOBS:
        run(name, sheet)


if __name__ == "__main__":
    main()
