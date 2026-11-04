"""Converts every image downloaded by batch.mjs (jpg / webp / png) into the <file>.png that build_slideshow.py loads.

  python scripts/flow/convert.py flow/<video>      (existing PNGs are kept; delete one to redo it)
"""
import pathlib, sys
from PIL import Image

d = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "flow/out"); n = 0
for f in sorted(d.iterdir()):
    if f.suffix.lower() not in (".jpg", ".jpeg", ".webp") or f.with_suffix(".png").exists(): continue
    Image.open(f).convert("RGB").save(f.with_suffix(".png")); n += 1
print(f"{n} converted in {d} | {len(list(d.glob('*.png')))} PNG total")
