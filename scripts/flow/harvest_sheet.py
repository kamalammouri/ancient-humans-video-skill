"""Contact sheets of the images harvest.mjs could not match, labelled H-number + Flow caption, to map them to prompts.json by eye.
  python scripts/flow/harvest_sheet.py flow/<video>     -> flow/<video>/harvest/sheet1.jpg, sheet2.jpg… (20 per sheet)
"""
import json, pathlib, sys
from PIL import Image, ImageDraw
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "flow/out"); h = out / "harvest"
inv = [r for r in json.load(open(h / "inventory.json")) if not r["known"]]
W, H, C, N = 384, 216, 5, 20
for s in range(0, len(inv), N):
    part = inv[s:s + N]; rows = (len(part) + C - 1) // C
    sheet = Image.new("RGB", (C * W, rows * (H + 22)), "white"); d = ImageDraw.Draw(sheet)
    for k, r in enumerate(part):
        x, y = (k % C) * W, (k // C) * (H + 22)
        sheet.paste(Image.open(r["file"]).resize((W, H)), (x, y + 22)); d.text((x + 4, y + 5), f"H{r['n']:03d}  {r['caption'][:44]}", fill="black")
    sheet.save(h / f"sheet{s // N + 1}.jpg", quality=85)
print(f"{len(inv)} unmatched images, {(len(inv) + N - 1) // N} sheet(s) in {h}")
