"""Crop + resize the Higgsfield raw images into the files the site expects (irisya-clinic/assets/img/content/).

Each entry: out file -> (raw name, width, height, focus_x, focus_y, zoom)
The crop is the largest box with the target aspect ratio, shrunk by `zoom`, centred on (focus_x, focus_y)
(fractions of the source) and clamped inside the image.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "irisya-clinic" / "assets" / "img" / "content"
BRAND = OUT.parent / "brand"

S = {}
# patient stories, their trip moments and the avatar crops of the same people
FACES = {1: (.40, .43), 2: (.47, .37), 3: (.47, .38), 4: (.48, .44), 5: (.46, .36)}
for i in range(1, 6):
    S[f"story-{i}"] = (f"story-{i}", 1100, 1467, .5, .5, 1)
    S[f"moment-{i}"] = (f"moment-{i}", 600, 750, .5, .5, 1)
    S[f"face-{i}"] = (f"story-{i}", 200, 200, *FACES[i], 1.6)
for i in range(1, 10):
    S[f"review-{i}"] = (f"review-{i}", 200, 200, .5, .42, 1.25)
S["team-1"] = ("team-1", 400, 400, .5, .38, 1.35)
S["team-2"] = ("team-2", 400, 400, .5, .38, 1.35)
S["team-3"] = ("team-3", 400, 400, .55, .4, 1.35)
S["why"] = ("why-shade-c", 1500, 2000, .5, .5, 1)  # black and white, colour kept in the eyes and the shade disc
# ellipses (x, y, rx, ry) in the raw why-shade-c.png: "keep" stay in colour (her two irises and the IR-07 Hazel disc),
# "drop" are cut back out (the clinician's thumb tip over the disc's edge)
COLOUR_SPOTS = {"why": {
    "keep": [(859, 657, 28, 28), (566, 710, 28, 28), (1077, 757, 82, 82)],
    "drop": [(1185, 757, 41, 36)],
}}
for i in range(1, 6):
    S[f"journey-{i}"] = (f"journey-{i}", 1680, 840, .5, .5, 1)
S["riders"] = ("riders", 1200, 1800, .5, .5, 1)
S["vision-bg"] = ("vision-bg", 1600, 1000, .5, .5, 1)
S["package-procedure"] = ("package-procedure", 600, 300, .5, .5, 1.15)
S["package-hotel"] = ("package-hotel", 600, 300, .5, .55, 1)
S["package-transfer"] = ("package-transfer", 600, 300, .47, .53, 1.6)
S["bento-procedure"] = ("bento-procedure", 600, 320, .52, .55, 1.1)
S["bento-aftercare"] = ("bento-aftercare", 600, 400, .5, .5, 1)
for i in range(1, 4):
    S[f"tx-{i}"] = (f"tx-{i}", 1400, 1050, .5, .5, 1)
    S[f"tx-{i}-detail"] = (f"tx-{i}-detail", 520, 650, .5, .5, 1)
S["tx-4"] = ("tx-4", 1400, 1050, .5, .5, 1)
S["tx-4-after"] = ("tx-4-after", 1400, 1050, .5, .5, 1)  # aligned to tx-4 separately below
S["tx-4-detail"] = ("tx-4-after", 520, 650, .27, .5, 2.2)
S["send-photos"] = ("send-photos", 960, 411, .5, .5, 1)
for i in range(1, 9):
    S[f"shade-{i}"] = (f"shade-{i}", 800, 500, .5, .5, 1)
    S[f"shade-{i}-detail"] = (f"shade-{i}-detail", 800, 500, .5, .5, 1)
# shade-preview tiles: square crops around the eye in three shade photos (Glacier · Hazel · Aegean)
S["shade-preview-1"] = ("shade-1", 300, 300, .40, .5, 1.6)
S["shade-preview-2"] = ("shade-7", 300, 300, .64, .55, 1.6)
S["shade-preview-3"] = ("shade-5", 300, 300, .50, .55, 1.6)
# review strip photo cards (312x410 on screen): the quote covers the lower ~45%, so faces must sit in the upper half
for i in range(1, 10):
    S[f"quote-{i}"] = (f"quote-{i}", 640, 840, .5, .5, 1)
# every review photo is about the eye colour itself: black and white, the reviewer's two irises kept in colour (their shade)
QUOTE_EYES = {  # (x, y, r) of each iris in the raw 1536x2048 quote-N.png
    1: [(565, 833, 35), (912, 733, 35)], 2: [(565, 545, 37), (890, 540, 37)], 3: [(675, 520, 25), (865, 505, 25)],
    4: [(600, 575, 50), (944, 630, 50)], 5: [(675, 480, 25), (865, 475, 25)], 6: [(600, 770, 30), (900, 765, 30)],
    7: [(610, 595, 30), (830, 620, 30)], 8: [(640, 630, 25), (900, 625, 25)], 9: [(635, 730, 30), (850, 740, 30)],
}
WARM = {2, 8, 9}  # honey / hazel irises share the skin's hue: smaller circles instead of the skin filter
for i, eyes in QUOTE_EYES.items():
    k = .85 if i in WARM else 1
    COLOUR_SPOTS[f"quote-{i}"] = {"keep": [(x, y, r * k, r * k) for x, y, r in eyes], "skin_out": i not in WARM,
                                  "boost": {1: 1.5, 5: 1.45, 6: 1.4, 7: 1.2, 3: 1.15}.get(i, 1)}  # pale shades read at card size
S["footer"] = ("footer", 2400, 1030, .5, .5, 1)
S["footer-portrait"] = ("footer-portrait", 900, 1125, .5, .7, 1)
S["clinic"] = ("clinic", 600, 375, .5, .5, 1)


def crop(im, w, h, fx, fy, zoom):
    W, H = im.size
    ar = w / h
    cw, ch = (W, W / ar) if W / H < ar else (H * ar, H)
    cw, ch = cw / zoom, ch / zoom
    x = min(max(fx * W - cw / 2, 0), W - cw)
    y = min(max(fy * H - ch / 2, 0), H - ch)
    return im.crop((round(x), round(y), round(x + cw), round(y + ch))).resize((w, h), Image.LANCZOS)


def aligned_after():
    """GPT edits come back at a slightly different size: rescale tx-4-after onto tx-4's frame."""
    a = Image.open(RAW / "tx-4.png").convert("RGB")
    b = Image.open(RAW / "tx-4-after.png").convert("RGB")
    return b.resize(a.size, Image.LANCZOS)


def colour_only_in(im, spots, feather=3):
    """Site rule: people in black and white, colour only in eyes and shades. Keeps colour inside the "keep" ellipses."""
    grey = ImageEnhance.Contrast(ImageOps.grayscale(im)).enhance(1.06).convert("RGB")
    mask = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(mask)
    for key, fill in (("keep", 255), ("drop", 0)):
        for x, y, rx, ry in spots.get(key, []):
            d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=fill)
    if spots.get("skin_out"):  # cool irises: drop the warm eyelid / skin pixels that fall inside the circles
        h, sat, _ = im.convert("HSV").split()
        skin = Image.eval(h, lambda v: 255 if v < 36 or v > 245 else 0)
        skin = Image.composite(skin, Image.new("L", im.size, 0), Image.eval(sat, lambda v: 255 if v > 45 else 0))
        mask = Image.composite(Image.new("L", im.size, 0), mask, skin.filter(ImageFilter.MaxFilter(3)))
    if spots.get("boost", 1) != 1:
        im = ImageEnhance.Color(im).enhance(spots["boost"])
    return Image.composite(im, grey, mask.filter(ImageFilter.GaussianBlur(feather)))


def save(img, name):
    path = OUT / f"{name}.webp"
    img.save(path, "WEBP", quality=82, method=6)
    return path


def og_image():
    base = crop(Image.open(RAW / "og.png").convert("RGB"), 1200, 630, .5, .5, 1)
    shade = Image.new("L", base.size, 0)
    d = ImageDraw.Draw(shade)
    for x in range(base.width):
        d.line([(x, 0), (x, base.height)], fill=int(235 * max(0, 1 - x / 760) ** 1.4))
    navy = Image.new("RGB", base.size, (2, 30, 68))
    base = Image.composite(navy, base, shade)
    logo = Image.open(BRAND / "logo-white.webp").convert("RGBA")
    logo.thumbnail((330, 330))
    base.paste(logo, (84, 315 - logo.height // 2 - 40), logo)
    d = ImageDraw.Draw(base)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 34)
        small = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
    except OSError:
        font = small = ImageFont.load_default()
    y = 315 + logo.height // 2 - 10
    d.text((88, y), "Your eyes, reimagined.", font=font, fill=(255, 255, 255))
    d.text((88, y + 48), "Eye colour change in Istanbul", font=small, fill=(168, 199, 227))
    base.save(OUT / "og-image.jpg", "JPEG", quality=86, optimize=True, progressive=True)


def main():
    only = set(sys.argv[1:])
    OUT.mkdir(parents=True, exist_ok=True)
    cache = {}
    for name, (src, w, h, fx, fy, zoom) in S.items():
        if only and name not in only:
            continue
        if src not in cache:
            cache[src] = aligned_after() if src == "tx-4-after" else Image.open(RAW / f"{src}.png").convert("RGB")
        base = colour_only_in(cache[src], COLOUR_SPOTS[name]) if name in COLOUR_SPOTS else cache[src]
        img = crop(base, w, h, fx, fy, zoom)
        if name == "package-transfer":  # soften the invented licence plate
            box = (356, 148, 414, 172)
            img.paste(img.crop(box).filter(ImageFilter.GaussianBlur(5)), box[:2])
        p = save(img, name)
        print(f"{name:20s} {w}x{h}  {p.stat().st_size // 1024} KB")
    if not only or "og-image" in only:
        og_image()
        print("og-image.jpg         1200x630")


if __name__ == "__main__":
    main()
