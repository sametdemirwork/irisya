"""Before / after eye strips for the Patient stories cards.

story-N.png is the published portrait (after: the patient's shade). story-N-before.png is an edit of it with natural
dark-brown irises: first GPT Image 2.6 edits, since 2026-11-20 recolour.py. GPT returned a slightly different size, so
such an edit is registered onto the portrait around the eyes and only the irises (where the two images differ in colour)
are taken from it; recolour.py edits in place and saves the exact iris mask, which is used as is. Everything else in the
"before" strip is the very same pixels as the "after" strip, so the slider only moves the eye colour.

Both strips follow the site rule (people in black and white, colour only in the eyes).

Usage: python ba.py [--sheet DIR] [1 2 ...]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "irisya-clinic" / "assets" / "img" / "content"

# rough eye centres (left, right) in the 1536x2048 portraits; the iris masks refine them
EYES = {
    1: ((475, 850), (772, 828)),
    2: ((540, 659), (852, 636)),
    3: ((557, 775), (860, 785)),
    4: ((555, 735), (930, 735)),
    5: ((522, 590), (790, 575)),
}
W, H = 1120, 400  # strip size (shown at up to 560x200)
# (brightness, saturation) applied to the edited brown irises where the edit came back too light or too orange.
# The GPT Image edits needed {1: (.62, .8), 5: (.7, .72)}; recolour.py, which replaced them on 2026-11-20, sets the
# brown directly, so nothing is corrected here any more.
BEFORE_TONE = {}


def grey(a):
    return a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114


def register(A, B, box):
    """Find scale + offset that maps B (already resized to A's size) onto A inside box. Returns warped B (PIL)."""
    x0, y0, x1, y1 = box
    ga = grey(np.asarray(A, np.float32))[y0:y1:2, x0:x1:2]
    ga = (ga - ga.mean()) / ga.std()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    best = None
    for s in np.arange(.97, 1.031, .005):
        # scale B about the box centre
        Bs = B.transform(B.size, Image.AFFINE, (1 / s, 0, cx - cx / s, 0, 1 / s, cy - cy / s), Image.BILINEAR)
        gb = grey(np.asarray(Bs, np.float32))
        for dy in range(-30, 31, 2):
            for dx in range(-30, 31, 2):
                p = gb[y0 + dy:y1 + dy:2, x0 + dx:x1 + dx:2]
                p = (p - p.mean()) / p.std()
                e = float(((ga - p) ** 2).mean())
                if best is None or e < best[0]:
                    best = (e, s, dx, dy)
    e, s, dx, dy = best
    # refine the offset at full resolution
    Bs = B.transform(B.size, Image.AFFINE, (1 / s, 0, cx - cx / s, 0, 1 / s, cy - cy / s), Image.BILINEAR)
    gb = grey(np.asarray(Bs, np.float32))
    ga1 = grey(np.asarray(A, np.float32))[y0:y1, x0:x1]
    ga1 = (ga1 - ga1.mean()) / ga1.std()
    for ddy in range(dy - 2, dy + 3):
        for ddx in range(dx - 2, dx + 3):
            p = gb[y0 + ddy:y1 + ddy, x0 + ddx:x1 + ddx]
            p = (p - p.mean()) / p.std()
            e2 = float(((ga1 - p) ** 2).mean())
            if e2 <= e:
                e, dx, dy = e2, ddx, ddy
    print(f"  scale {s:.3f} offset {dx:+d},{dy:+d} err {e:.3f}")
    return Bs.transform(B.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), Image.BILINEAR)


def iris_mask(A, Bw, eyes, r):
    """Pixels whose colour changed between portrait and edit, limited to discs around each eye."""
    ya = np.asarray(A.convert("YCbCr"), np.float32)
    yb = np.asarray(Bw.convert("YCbCr"), np.float32)
    d = np.hypot(ya[..., 1] - yb[..., 1], ya[..., 2] - yb[..., 2]) + .35 * np.abs(ya[..., 0] - yb[..., 0])
    yy, xx = np.mgrid[0:A.height, 0:A.width]
    near = np.zeros(d.shape, bool)
    for ex, ey in eyes:
        near |= (xx - ex) ** 2 + (yy - ey) ** 2 < r ** 2
    m = Image.fromarray(np.where(near, np.clip((d - 9) * 12, 0, 255), 0).astype(np.uint8))
    # close small holes (pupil reflections, lash gaps), then soften the edge
    m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(2.2))
    return m


def edit_and_mask(A, B, name, box, eyes, r):
    """The edit aligned to the portrait, and the pixels it changed.
    recolour.py edits in place and saves the exact mask (raw/<name>-mask.png); a generated edit (GPT Image) is
    registered first and its mask is read from the colour differences."""
    mp = RAW / f"{name}-mask.png"
    if mp.exists():
        return B, Image.open(mp).convert("L")
    Bw = register(A, B, box)
    return Bw, iris_mask(A, Bw, eyes, r)


def bw_with_colour(im, mask):
    g = ImageEnhance.Contrast(ImageOps.grayscale(im)).enhance(1.08).convert("RGB")
    return Image.composite(im, g, mask)


def strip(im, eyes):
    (lx, ly), (rx, ry) = eyes
    cx, cy = (lx + rx) / 2, (ly + ry) / 2
    span = rx - lx
    cw = span * 2.05
    ch = cw * H / W
    box = (round(cx - cw / 2), round(cy - ch * .52), round(cx + cw / 2), round(cy + ch * .48))
    return im.crop(box).resize((W, H), Image.LANCZOS)


def build(i, sheet=None):
    A = Image.open(RAW / f"story-{i}.png").convert("RGB")
    B = Image.open(RAW / f"story-{i}-before.png").convert("RGB").resize(A.size, Image.LANCZOS)
    eyes = EYES[i]
    span = eyes[1][0] - eyes[0][0]
    box = (eyes[0][0] - span // 2, min(e[1] for e in eyes) - span // 3, eyes[1][0] + span // 2, max(e[1] for e in eyes) + span // 3)
    print(f"story-{i}")
    r = span * .12
    Bw, m = edit_and_mask(A, B, f"story-{i}-before", box, eyes, r)
    # refine the eye centres from the mask, so the strip is centred on the real irises
    ma = np.asarray(m, np.float32)
    yy, xx = np.mgrid[0:A.height, 0:A.width]
    cs = []
    for ex, ey in eyes:
        w = ma * (((xx - ex) ** 2 + (yy - ey) ** 2) < r ** 2)
        cs.append((float((w * xx).sum() / w.sum()), float((w * yy).sum() / w.sum())) if w.sum() > 500 else (ex, ey))
    print("  eyes", [(round(x), round(y)) for x, y in cs])
    bri, sat = BEFORE_TONE.get(i, (1, 1))
    Bt = ImageEnhance.Brightness(ImageEnhance.Color(Bw).enhance(sat)).enhance(bri)
    before = Image.composite(Bt, A, m)
    after, keep = A, m
    # optional story-N-after.png: an edit that corrects the portrait's eyes to the story's shade
    if (RAW / f"story-{i}-after.png").exists():
        C = Image.open(RAW / f"story-{i}-after.png").convert("RGB").resize(A.size, Image.LANCZOS)
        Cw, mc = edit_and_mask(A, C, f"story-{i}-after", box, eyes, r)
        after = Image.composite(Cw, A, mc)
        keep = Image.fromarray(np.maximum(np.asarray(m), np.asarray(mc)))
    after_s = strip(bw_with_colour(after, keep), cs)
    before_s = strip(bw_with_colour(before, keep), cs)
    if sheet:
        Path(sheet).mkdir(parents=True, exist_ok=True)
        s = Image.new("RGB", (W, H * 3 + 20), "white")
        s.paste(before_s, (0, 0)); s.paste(after_s, (0, H + 10)); s.paste(strip(m.convert("RGB"), cs), (0, 2 * H + 20))
        s.save(Path(sheet) / f"ba-{i}.png")
    before_s.save(OUT / f"story-{i}-before.webp", "WEBP", quality=84, method=6)
    after_s.save(OUT / f"story-{i}-after.webp", "WEBP", quality=84, method=6)


def main():
    args = sys.argv[1:]
    sheet = None
    if "--sheet" in args:
        sheet = args[args.index("--sheet") + 1]
        del args[args.index("--sheet"):args.index("--sheet") + 2]
    for i in [int(a) for a in args] or EYES:
        build(i, sheet)


if __name__ == "__main__":
    main()
