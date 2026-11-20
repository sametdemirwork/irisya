"""İrisya — re-grades the reusable photos of the previous site into the İrisya palette.

Only neutral photos are reused (Istanbul, hotel, transfer, flight, stock doctor
portraits). Nothing dental and nothing carrying another brand's sign.

Grade     purple / magenta hues are pulled to the brand's iris blue, saturation is
          eased and shadows lean toward the logo navy, so every photo sits in the
          same cool, calm family as the logo.
Sources   vors-dental-clinic/assets/img/   (left untouched)
Outputs   irisya-clinic/assets/img/
Run       python -E irisya-tools/photos.py
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', 'vors-dental-clinic', 'assets', 'img'))
OUT = os.path.normpath(os.path.join(HERE, '..', 'irisya-clinic', 'assets', 'img'))

NAVY = np.array([2, 30, 68], np.float32) / 255


def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rc = np.where(m, (mx - r) / np.where(m, d, 1), 0)
    gc = np.where(m, (mx - g) / np.where(m, d, 1), 0)
    bc = np.where(m, (mx - b) / np.where(m, d, 1), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
    h = np.where(m, (h / 6.0) % 1.0, 0.0)
    s = np.where(mx > 1e-6, d / np.where(mx > 1e-6, mx, 1), 0)
    return np.stack([h, s, mx], -1)


def hsv_to_rgb(hsv):
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = np.floor(h * 6.0)
    f = h * 6.0 - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    i = i.astype(np.int32) % 6
    conds = [i == k for k in range(6)]
    r = np.select(conds, [v, q, p, p, t, v])
    g = np.select(conds, [t, v, v, q, p, p])
    b = np.select(conds, [p, p, t, v, v, q])
    return np.stack([r, g, b], -1)


def grade(im, strength=1.0, warm_keep=0.85, shadow=0.16):
    a = np.asarray(im.convert('RGB'), np.float32) / 255
    hsv = rgb_to_hsv(a)
    hdeg = hsv[..., 0] * 360
    # purple / magenta band (245..335 deg) -> iris blue (212 deg)
    w = np.clip(1 - np.abs(hdeg - 288) / 58, 0, 1) ** 0.8 * strength
    hdeg = hdeg + (212 - hdeg) * w
    hsv[..., 0] = (hdeg % 360) / 360
    sat = hsv[..., 1]
    # warm tones keep most of their colour, everything else eases off a little
    warm = np.clip(1 - np.abs(((hsv[..., 0] * 360 + 180) % 360) - 210) / 40, 0, 1)  # around 30 deg
    hsv[..., 1] = sat * (0.86 + (warm_keep - 0.86) * warm) * (1 - 0.18 * w)
    out = hsv_to_rgb(hsv)
    lum = (out @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    out = out + (NAVY - out) * ((1 - lum) ** 2.2 * shadow)
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGB')


def crop_to(im, ar, fx=0.5, fy=0.5):
    """Crop to aspect ratio ar (w/h) around focus point (fx, fy)."""
    w, h = im.size
    if w / h > ar:
        nw = round(h * ar)
        x = round((w - nw) * fx)
        return im.crop((x, 0, x + nw, h))
    nh = round(w / ar)
    y = round((h - nh) * fy)
    return im.crop((0, y, w, y + nh))


def save(im, name, width=None, q=84):
    if width and im.width != width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(os.path.join(OUT, name), 'WEBP', quality=q, method=6)
    print(name, im.size)


def main():
    os.makedirs(OUT, exist_ok=True)
    src = lambda n: Image.open(os.path.join(SRC, n))

    # full-frame photos
    for n in ('istanbul-galata', 'istanbul-mosque', 'istanbul-dusk', 'hotel-room', 'hotel-room-2',
              'hotel-pool', 'vip-car', 'driver', 'plane'):
        save(grade(src(n + '.webp')), n + '.webp')
    for n in ('footer-bosphorus-2400', 'footer-bosphorus-1200', 'footer-bosphorus-portrait-900'):
        save(grade(src(n + '.webp'), shadow=0.1), n + '.webp', q=82)
    # stock portraits used as team placeholders: only a light, cool grade
    for n in ('doctor-woman', 'doctor-man', 'doctor-smile'):
        save(grade(src(n + '.webp'), strength=0.6, shadow=0.08), n + '.webp', q=86)

    # story "moment" polaroids (4:5)
    moments = [('moment-galata', 'istanbul-galata', .55, .5), ('moment-mosque', 'istanbul-mosque', .5, .5),
               ('moment-transfer', 'driver', .62, .5), ('moment-pool', 'hotel-pool', .3, .5),
               ('moment-dusk', 'istanbul-dusk', .5, .55)]
    for out, n, fx, fy in moments:
        save(crop_to(grade(src(n + '.webp')), 4 / 5, fx, fy), out + '.webp', width=600)

    # journey cards (2:1)
    save(crop_to(grade(src('vip-car.webp')), 2.0, .5, .55), 'journey-arrive.webp', width=1200)
    save(crop_to(grade(src('plane.webp')), 2.0, .5, .5), 'journey-home.webp', width=900)


if __name__ == '__main__':
    main()
