"""Labelled contact sheets of Flow images: python sheets.py <flowdir> <outdir> [cols rows]"""
import sys, pathlib, json
from PIL import Image, ImageDraw, ImageFont
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]); out.mkdir(exist_ok=True)
cols, rows = 4, 3; W, H = 480, 270
files = sorted(src.glob("*.jpg")) + sorted(src.glob("*.png"))
f = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 30)
for n in range(0, len(files), cols*rows):
    chunk = files[n:n+cols*rows]
    sheet = Image.new("RGB", (cols*W, rows*(H+40)), "white"); d = ImageDraw.Draw(sheet)
    for k, p in enumerate(chunk):
        im = Image.open(p).convert("RGB"); im.thumbnail((W, H))
        x, y = (k % cols)*W, (k // cols)*(H+40)
        sheet.paste(im, (x + (W-im.width)//2, y + 40)); d.text((x+8, y+4), p.stem, font=f, fill="black")
    name = out / f"sheet_{chunk[0].stem}_{chunk[-1].stem}.jpg"; sheet.save(name, quality=85); print(name.name, len(chunk))
