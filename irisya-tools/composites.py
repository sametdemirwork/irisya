"""İrisya — composed illustrations built from the iris renders and the logo's eyelids.

Every file here is an illustration (no fake photos): an iris from iris.py set in
the logo's eyelid strokes on a navy field, a corneal map, a shade palette.
Replace any of them with a real photo of the same name and aspect when you have one.

Run       python -E irisya-tools/composites.py   (after iris.py; needs numpy, pillow)
Outputs   irisya-clinic/assets/img/
            journey-plan.webp     1200x600   step 01, shade preview from a photo
            journey-exam.webp     1200x600   step 03, corneal map
            journey-colour.webp   1200x600   step 04, the pigment ring
            tx-kerato.webp        1200x900   treatment tab 01
            tx-lighten.webp       1200x900   treatment tab 02
            tx-bespoke.webp       1200x900   treatment tab 03
            tx-hetero-today.webp / tx-hetero-matched.webp   1200x900   treatment tab 04
            eye-photo.webp        960x411    colour library "send your photos" card
            why-eye.webp          1000x1500  Why İrisya visual
            og-image.jpg          1200x630   social sharing image
Also prints the eyelid outline as an SVG path (used as #lids in index.html).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iris  # noqa: E402

IMG = os.path.normpath(os.path.join(HERE, '..', 'irisya-clinic', 'assets', 'img'))
IRIS_DIR = os.path.join(IMG, 'iris')
BRAND = os.path.join(IMG, 'brand')

# ---------------------------------------------------------------- eyelids (logo geometry, px on the 2000 px source)
# (x, top edge, bottom edge) sampled from the logo mask
UPPER = [(607, 372, 374), (640, 340, 352), (680, 303, 325), (720, 269, 298), (760, 240, 274), (800, 217, 253),
         (840, 198, 236), (880, 183, 223), (920, 173, 213), (960, 166, 207), (1000, 164, 205), (1040, 166, 208),
         (1080, 172, 217), (1120, 183, 230), (1160, 199, 248), (1200, 220, 272), (1240, 246, 300), (1280, 276, 329),
         (1320, 309, 352), (1360, 339, 366), (1400, 361, 373), (1420, 368, 374), (1439, 373.5, 374)]
LOWER = [(577, 398, 399), (588, 390, 398), (600, 386, 396), (640, 384, 405), (680, 393, 425), (720, 410, 452),
         (760, 435, 482), (800, 463, 509), (840, 489, 531), (880, 511, 549), (920, 528, 561), (960, 538, 567),
         (1000, 542, 570), (1040, 540, 567), (1080, 533, 559), (1120, 522, 547), (1160, 505, 530), (1200, 484, 507),
         (1240, 458, 477), (1280, 428, 439), (1305, 410, 412)]
EYE_C = (999.5, 373.5)       # iris centre
EYE_W = 1439 - 577           # lid span
IRIS_R = 152                 # iris radius in the logo


def catmull(pts, n=10):
    pts = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = (np.array(p, float) for p in pts[i - 1:i + 3])
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(np.array(pts[-2], float))
    return out


def lid_polys():
    polys = []
    for lid in (UPPER, LOWER):
        top = catmull([(x, a) for x, a, b in lid])
        bot = catmull([(x, b) for x, a, b in lid])
        polys.append([tuple(p) for p in top] + [tuple(p) for p in bot[::-1]])
    return polys


def svg_path(origin=(560, 150), scale=1.0):
    d = []
    for lid in (UPPER, LOWER):
        for edge, rev in ((1, False), (2, True)):
            pts = [(x, row[edge]) for row in lid for x in [row[0]]]
            if rev:
                pts = pts[::-1]
            pts = [((x - origin[0]) * scale, (y - origin[1]) * scale) for x, y in pts]
            # Catmull-Rom -> cubic Bezier
            P = [pts[0]] + pts + [pts[-1]]
            seg = [] if edge == 2 else [f'M{pts[0][0]:.1f} {pts[0][1]:.1f}']
            if edge == 2:
                seg.append(f'L{pts[0][0]:.1f} {pts[0][1]:.1f}')
            for i in range(1, len(P) - 2):
                p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
                c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
                c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
                seg.append(f'C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}')
            d.append(''.join(seg))
        d.append('Z')
    return ''.join(d)


def draw_lids(img, cx, cy, width, color=(255, 255, 255), alpha=1.0, ss=4):
    """Draw the logo's eyelids so that the iris centre lands on (cx, cy) and the span is `width` px."""
    s = width / EYE_W
    W, H = img.size
    mask = Image.new('L', (W * ss, H * ss), 0)
    dr = ImageDraw.Draw(mask)
    for poly in lid_polys():
        pts = [((x - EYE_C[0]) * s * ss + cx * ss, (y - EYE_C[1]) * s * ss + cy * ss) for x, y in poly]
        dr.polygon(pts, fill=255)
    mask = mask.resize((W, H), Image.LANCZOS)
    if alpha < 1:
        mask = mask.point(lambda v: int(v * alpha))
    layer = Image.new('RGBA', (W, H), color + (0,))
    layer.putalpha(mask)
    img.alpha_composite(layer)
    return s


# ---------------------------------------------------------------- canvas helpers
def navy_field(w, h, cx=0.5, cy=0.5, inner=(14, 46, 92), outer=(2, 10, 24), seed=1):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.hypot((xx / w - cx) * (w / h), yy / h - cy) / 0.95
    k = np.clip(d, 0, 1) ** 1.25
    a = np.array(inner, np.float32) * (1 - k[..., None]) + np.array(outer, np.float32) * k[..., None]
    a += np.random.default_rng(seed).normal(0, 1.4, a.shape)   # dither against banding
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')


def glow(img, cx, cy, r, color, strength=0.5):
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.hypot(xx - cx, yy - cy) / r
    a = np.clip(1 - d, 0, 1) ** 2 * strength
    layer = np.zeros((h, w, 4), np.float32)
    layer[..., :3] = color
    layer[..., 3] = a * 255
    img.alpha_composite(Image.fromarray(layer.astype(np.uint8), 'RGBA'))


def iris_img(slug, size=1600):
    return Image.open(os.path.join(IRIS_DIR, f'iris-{slug}-{size}.webp')).convert('RGBA')


def put_iris(img, im, cx, cy, r, shadow=True):
    d = int(round(r * 2 / iris.R_IRIS))          # the disc fills R_IRIS of the image
    ir = im.resize((d, d), Image.LANCZOS)
    if shadow:
        sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse((cx - r * 1.02, cy - r * 1.02 + r * .04, cx + r * 1.02, cy + r * 1.02 + r * .04), fill=(0, 6, 16, 150))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(r * .06)))
    img.alpha_composite(ir, (int(round(cx - d / 2)), int(round(cy - d / 2))))


def catchlight(img, cx, cy, r, s=1.0):
    """Soft window reflection on the cornea, upper right of the pupil (as in the logo)."""
    w, h = img.size
    hx, hy = cx + r * 0.27, cy - r * 0.27
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.hypot(xx - hx, yy - hy) / (r * 0.085 * s)
    a = np.clip(1.25 - d, 0, 1) ** 1.4
    d2 = np.hypot(xx - (cx - r * .34), yy - (cy + r * .3)) / (r * 0.04 * s)
    a = np.maximum(a, np.clip(1 - d2, 0, 1) ** 2 * 0.45)
    layer = np.zeros((h, w, 4), np.float32)
    layer[..., :3] = 255
    layer[..., 3] = a * 235
    img.alpha_composite(Image.fromarray(layer.astype(np.uint8), 'RGBA'))


def ring(img, cx, cy, r, width, color, alpha, dash=None, ss=3):
    W, H = img.size
    m = Image.new('L', (W * ss, H * ss), 0)
    dr = ImageDraw.Draw(m)
    if dash:
        n = dash
        for k in range(n):
            a0 = 360 * k / n
            dr.arc((cx * ss - r * ss, cy * ss - r * ss, cx * ss + r * ss, cy * ss + r * ss), a0, a0 + 360 / n * 0.55, fill=255, width=int(width * ss))
    else:
        dr.ellipse((cx * ss - r * ss, cy * ss - r * ss, cx * ss + r * ss, cy * ss + r * ss), outline=255, width=int(width * ss))
    m = m.resize((W, H), Image.LANCZOS).point(lambda v: int(v * alpha))
    layer = Image.new('RGBA', (W, H), color + (0,))
    layer.putalpha(m)
    img.alpha_composite(layer)


def annulus_glow(img, cx, cy, r0, r1, color, alpha):
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.hypot(xx - cx, yy - cy)
    mid, half = (r0 + r1) / 2, (r1 - r0) / 2
    a = np.clip(1 - np.abs(d - mid) / half, 0, 1) ** 0.7 * alpha
    layer = np.zeros((h, w, 4), np.float32)
    layer[..., :3] = color
    layer[..., 3] = a * 255
    img.alpha_composite(Image.fromarray(layer.astype(np.uint8), 'RGBA'))


def save(img, name, q=86):
    path = os.path.join(IMG, name)
    if name.endswith('.jpg'):
        img.convert('RGB').save(path, 'JPEG', quality=q, optimize=True, progressive=True)
    else:
        img.convert('RGB').save(path, 'WEBP', quality=q, method=6)
    print(name, img.size, os.path.getsize(path) // 1024, 'KB')


def eye(img, slug, cx, cy, width, lid_color=(236, 243, 249), lid_alpha=0.92, iris_scale=1.0, light=True):
    s = width / EYE_W
    r = IRIS_R * s * iris_scale
    put_iris(img, iris_img(slug), cx, cy, r)
    if light:
        catchlight(img, cx, cy, r)
    draw_lids(img, cx, cy, width, lid_color, lid_alpha)
    return r


# ---------------------------------------------------------------- corneal map
TOPO = [(36.0, (20, 24, 120)), (39.0, (30, 70, 200)), (41.0, (30, 150, 230)), (42.5, (40, 200, 190)),
        (43.5, (60, 200, 90)), (44.5, (200, 220, 60)), (45.5, (250, 190, 40)), (47.0, (240, 110, 30)),
        (49.0, (210, 30, 40)), (52.0, (150, 20, 60))]


def topo_color(k):
    ks = np.array([t[0] for t in TOPO])
    cs = np.array([t[1] for t in TOPO], np.float32)
    k = np.clip(k, ks[0], ks[-1])
    out = np.zeros(k.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(k, ks, cs[:, c])
    return out


def corneal_map(img, cx, cy, r, axis=0.35, seed=3):
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x = (xx - cx) / r
    y = (yy - cy) / r
    rho = np.hypot(x, y)
    th = np.arctan2(y, x)
    rng = np.random.default_rng(seed)
    noise = sum(rng.normal(0, .12) * np.cos(k * th + rng.uniform(0, 6.28)) * rho ** (k * .5) for k in range(3, 7))
    K = 44.2 - 2.4 * rho ** 2 + 1.25 * np.cos(2 * (th - axis)) * np.minimum(rho, 1) ** .9 + noise
    Kq = np.floor(K / 0.5) * 0.5 + 0.25                       # 0.5 D bands
    col = topo_color(Kq) * 0.92
    edge = np.abs(K / 0.5 - np.round(K / 0.5)) < 0.06            # thin contour lines
    col[edge] *= 0.72
    a = np.clip((1.0 - rho) * r / 1.5, 0, 1)
    layer = np.zeros((h, w, 4), np.float32)
    layer[..., :3] = col
    layer[..., 3] = a * 255
    img.alpha_composite(Image.fromarray(layer.astype(np.uint8), 'RGBA'))
    # reticle
    dr = ImageDraw.Draw(img)
    for f in (0.33, 0.66, 1.0):
        dr.ellipse((cx - r * f, cy - r * f, cx + r * f, cy + r * f), outline=(255, 255, 255, 70), width=1)
    dr.line((cx - r * 1.08, cy, cx + r * 1.08, cy), fill=(255, 255, 255, 60), width=1)
    dr.line((cx, cy - r * 1.08, cx, cy + r * 1.08), fill=(255, 255, 255, 60), width=1)
    for k in range(36):
        a0 = k * np.pi / 18
        r0, r1 = r * 1.03, r * (1.07 if k % 3 == 0 else 1.05)
        dr.line((cx + r0 * np.cos(a0), cy + r0 * np.sin(a0), cx + r1 * np.cos(a0), cy + r1 * np.sin(a0)), fill=(255, 255, 255, 110), width=1)


def scale_bar(img, x, y0, y1, wbar=14):
    dr = ImageDraw.Draw(img)
    steps = 26
    for i in range(steps):
        k = 52 - (52 - 36) * (i + .5) / steps
        c = tuple(int(v) for v in topo_color(np.array(k)))
        ya = y0 + (y1 - y0) * i / steps
        yb = y0 + (y1 - y0) * (i + 1) / steps
        dr.rectangle((x, ya, x + wbar, yb), fill=c + (235,))
    dr.rectangle((x - 1, y0 - 1, x + wbar + 1, y1 + 1), outline=(255, 255, 255, 90), width=1)


# ---------------------------------------------------------------- builds
def build():
    W, H = 1200, 600
    # 01 plan: an eye with a shade preview, overlays sit on the left
    im = navy_field(W, H, .7, .5)
    glow(im, W * .7, H * .5, 420, (70, 130, 200), .35)
    eye(im, 'hazel', W * .69, H * .5, 640)
    save(im, 'journey-plan.webp')

    # 03 exam: corneal map + colour scale
    im = navy_field(W, H, .68, .5, inner=(10, 34, 70), outer=(2, 9, 22), seed=2)
    corneal_map(im, W * .67, H * .5, 228)
    scale_bar(im, int(W * .9), int(H * .16), int(H * .84))
    save(im, 'journey-exam.webp')

    # 04 colour day: iris with the ring-shaped tunnel lit up
    im = navy_field(W, H, .68, .5, seed=3)
    glow(im, W * .68, H * .5, 380, (90, 150, 220), .3)
    cx, cy, r = W * .68, H * .5, 236
    put_iris(im, iris_img('bosphorus'), cx, cy, r)
    annulus_glow(im, cx, cy, r * .47, r * .86, (150, 200, 245), .2)
    ring(im, cx, cy, r * .47, 1.6, (205, 230, 250), .85, dash=72)
    ring(im, cx, cy, r * .86, 1.6, (205, 230, 250), .85, dash=96)
    glow(im, cx + r * .86 * np.cos(-.9), cy + r * .86 * np.sin(-.9), 26, (220, 240, 255), .95)
    catchlight(im, cx, cy, r)
    save(im, 'journey-colour.webp')

    # treatments (4:3)
    W, H = 1200, 900
    im = navy_field(W, H, .5, .46, seed=4)
    glow(im, W * .5, H * .46, 520, (80, 140, 210), .3)
    cx, cy, r = W * .5, H * .46, 330
    put_iris(im, iris_img('bosphorus'), cx, cy, r)
    ring(im, cx, cy, r * .47, 2, (215, 235, 252), .8, dash=80)
    ring(im, cx, cy, r * .86, 2, (215, 235, 252), .8, dash=110)
    catchlight(im, cx, cy, r)
    save(im, 'tx-kerato.webp')

    # laser lightening: same fibres, brown on the left easing to a lighter tone on the right
    im = navy_field(W, H, .5, .46, seed=5)
    glow(im, W * .5, H * .46, 520, (90, 120, 160), .25)
    brown = next(s for s in iris.SHADES if s['slug'] == 'brown')
    lighter = dict(brown, pup='#6E5A45', col='#B9AF9C', mid='#8E9AA0', out='#7C8B95', lim='#26303A',
                   hi='#E6E9E8', lo='#4F5A62', cry='#3A4148')
    a = iris.render(brown, 900)
    b = iris.render(lighter, 900)
    aa, bb = np.asarray(a, np.float32), np.asarray(b, np.float32)
    xs = np.linspace(0, 1, 900)[None, :, None]
    k = np.clip((xs - .3) / .4, 0, 1)
    k = k * k * (3 - 2 * k)
    mix = Image.fromarray((aa * (1 - k) + bb * k).astype(np.uint8), 'RGBA')
    cx, cy, r = W * .5, H * .46, 330
    put_iris(im, mix, cx, cy, r)
    catchlight(im, cx, cy, r)
    save(im, 'tx-lighten.webp')

    # bespoke: the shade library as a palette
    im = navy_field(W, H, .5, .5, seed=6)
    glow(im, W * .5, H * .5, 560, (70, 120, 190), .28)
    order = ['glacier', 'bosphorus', 'sapphire', 'silver', 'aegean', 'emerald', 'hazel', 'honey']
    for i, slug in enumerate(order):
        col, row = i % 4, i // 4
        cx = W * (.17 + col * .22)
        cy = H * (.33 + row * .36)
        put_iris(im, iris_img(slug, 800), cx, cy, 112)
        catchlight(im, cx, cy, 112, .9)
    save(im, 'tx-bespoke.webp')

    # heterochromia: two eyes, today and matched
    for name, pair in (('tx-hetero-today.webp', ('brown', 'glacier')), ('tx-hetero-matched.webp', ('glacier', 'glacier'))):
        im = navy_field(W, H, .5, .46, seed=7)
        glow(im, W * .5, H * .46, 560, (80, 130, 200), .25)
        for side, slug in zip((-1, 1), pair):
            ex = W * (.5 + side * .225)
            e = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            eye(e, slug, W * .5, H * .44, 470)
            if side < 0:
                e = e.transpose(Image.FLIP_LEFT_RIGHT)
            im.alpha_composite(e, (int(ex - W * .5), 0))
        save(im, name)

    # colour library card: "send us a photo of your eyes"
    W, H = 960, 411
    im = navy_field(W, H, .5, .5, inner=(16, 40, 74), outer=(4, 12, 26), seed=8)
    glow(im, W * .5, H * .5, 380, (90, 140, 200), .25)
    eye(im, 'brown', W * .5, H * .52, 600)
    save(im, 'eye-photo.webp')

    # why İrisya visual (2:3); the white card covers the lower ~40%
    W, H = 1000, 1500
    im = navy_field(W, H, .5, .3, seed=9)
    glow(im, W * .5, H * .33, 620, (80, 140, 210), .35)
    eye(im, 'hazel', W * .5, H * .33, 860)
    save(im, 'why-eye.webp', q=84)

    # social sharing image
    W, H = 1200, 630
    im = navy_field(W, H, .74, .5, seed=10)
    glow(im, W * .78, H * .5, 520, (80, 140, 210), .35)
    cx, cy, r = W * .8, H * .5, 280
    put_iris(im, iris_img('bosphorus'), cx, cy, r)
    catchlight(im, cx, cy, r)
    fade = np.zeros((H, W, 4), np.float32)
    fade[..., :3] = (2, 12, 28)
    xs = np.linspace(0, 1, W)[None, :]
    fade[..., 3] = np.clip((0.66 - xs) / 0.2, 0, 1) * 200
    im.alpha_composite(Image.fromarray(fade.astype(np.uint8), 'RGBA'))
    logo = Image.open(os.path.join(BRAND, 'logo-white.webp')).convert('RGBA')
    lw = 470
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    im.alpha_composite(logo, (90, (H - logo.height) // 2))
    save(im, 'og-image.jpg', q=88)


if __name__ == '__main__':
    if '--svg' in sys.argv:
        print(svg_path())
    else:
        build()
        print('lids path:', svg_path()[:120], '...')
