"""Contact sheet of raw images for review: python sheet.py out.jpg name1 name2 ... (or a glob like 'shade-*')."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

RAW = Path(__file__).resolve().parent / "raw"
out, pats = sys.argv[1], sys.argv[2:]
files = []
for p in pats:
    files += sorted(RAW.glob(p + ".png")) if "*" in p else [RAW / f"{p}.png"]
files = [f for f in files if f.exists()]
cols = 3 if len(files) > 4 else max(1, len(files))
cw, ch = 520, 400
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cw, rows * (ch + 24)), "white")
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB")
    im.thumbnail((cw - 8, ch - 8))
    x, y = (i % cols) * cw, (i // cols) * (ch + 24)
    sheet.paste(im, (x + (cw - im.width) // 2, y + 4))
    d.text((x + 6, y + ch + 4), f"{f.stem}  {Image.open(f).size}", fill="black")
sheet.save(out, quality=82)
print(out, len(files))
