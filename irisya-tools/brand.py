"""İrisya — brand assets cut from the supplied logo files.

Sources   irisya-tools/logo-src/irisya-logo-navy.webp   (navy + colour iris, transparent)
          irisya-tools/logo-src/irisya-logo-white.webp  (white, transparent)
Outputs   irisya-clinic/assets/img/brand/
            logo-navy.webp / logo-white.webp   stacked logo (eye, IRISYA, CLINIC)
            mark-navy.webp                     eye mark, navy lids + colour iris (light backgrounds)
            mark-light.webp                    eye mark, white lids + colour iris (dark backgrounds)
            mark-white.webp                    eye mark, all white (official mono)
            wordmark-navy.webp / wordmark-white.webp   IRISYA letters only
            favicon-32.png, favicon-192.png, apple-touch-icon.png

Run       python -E irisya-tools/brand.py      (needs: numpy, pillow)
"""
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'logo-src')
OUT = os.path.normpath(os.path.join(HERE, '..', 'irisya-clinic', 'assets', 'img', 'brand'))

NAVY = (2, 30, 68)
# geometry measured on the 2000 x 1333 source files
BOX_LOGO = (290, 150, 1710, 1010)
BOX_MARK = (565, 154, 1449, 580)
BOX_WORD = (296, 619, 1704, 876)
IRIS_C, IRIS_R = (999.5, 373.5), 154


def save_webp(im, name, h=None, w=None):
    if h:
        im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    elif w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(os.path.join(OUT, name), 'WEBP', quality=92, method=6)
    print(name, im.size)
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    navy = Image.open(os.path.join(SRC, 'irisya-logo-navy.webp')).convert('RGBA')
    white = Image.open(os.path.join(SRC, 'irisya-logo-white.webp')).convert('RGBA')

    save_webp(navy.crop(BOX_LOGO), 'logo-navy.webp', w=720)
    save_webp(white.crop(BOX_LOGO), 'logo-white.webp', w=720)
    save_webp(navy.crop(BOX_MARK), 'mark-navy.webp', h=160)
    save_webp(white.crop(BOX_MARK), 'mark-white.webp', h=160)
    save_webp(navy.crop(BOX_WORD), 'wordmark-navy.webp', h=96)
    save_webp(white.crop(BOX_WORD), 'wordmark-white.webp', h=96)

    # white lids + the colour iris of the full-colour logo
    yy, xx = np.mgrid[0:navy.height, 0:navy.width]
    d = np.hypot(xx - IRIS_C[0], yy - IRIS_C[1])
    k = np.clip((IRIS_R + 1.5 - d) / 3.0, 0, 1)[..., None]
    a = np.asarray(white, np.float32)
    b = np.asarray(navy, np.float32)
    mixed = Image.fromarray((a * (1 - k) + b * k + 0.5).astype(np.uint8), 'RGBA')
    light = save_webp(mixed.crop(BOX_MARK), 'mark-light.webp', h=160)

    # favicons: the colour iris on a navy tile
    iris = navy.crop((int(IRIS_C[0] - IRIS_R - 2), int(IRIS_C[1] - IRIS_R - 2),
                      int(IRIS_C[0] + IRIS_R + 2), int(IRIS_C[1] + IRIS_R + 2)))
    for size, name, rounded in ((32, 'favicon-32.png', True), (192, 'favicon-192.png', True), (180, 'apple-touch-icon.png', False)):
        s = size * 4
        tile = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        dr = ImageDraw.Draw(tile)
        if rounded:
            dr.rounded_rectangle((0, 0, s - 1, s - 1), radius=int(s * 0.22), fill=NAVY + (255,))
        else:
            dr.rectangle((0, 0, s, s), fill=NAVY + (255,))
        if size >= 180:
            m = mixed.crop(BOX_MARK)
            mw = int(s * 0.78)
            m = m.resize((mw, round(m.height * mw / m.width)), Image.LANCZOS)
            tile.alpha_composite(m, ((s - m.width) // 2, (s - m.height) // 2))
        else:
            iw = int(s * 0.8)
            ic = iris.resize((iw, iw), Image.LANCZOS)
            # thin light ring so the iris reads on the navy tile
            dr.ellipse(((s - iw) // 2 - 6, (s - iw) // 2 - 6, (s + iw) // 2 + 6, (s + iw) // 2 + 6), fill=(214, 228, 240, 255))
            tile.alpha_composite(ic, ((s - iw) // 2, (s - iw) // 2))
        tile.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, name))
        print(name)


if __name__ == '__main__':
    main()
