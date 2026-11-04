"""Assemble the slideshow video: one image per shot, held until the next shot's sentence starts, on the voice track.

  python build_slideshow.py shots.json voice.wav timing.json out.mp4 [--flow flow/my-video] [--caption] [--motion | --motion-all]
  --motion: slow zoom (in, then out, alternating) on two Flow images out of three; cards, charts and titles stay still. Measured on an
            animated reference channel (Ifverse): 2 shots in 3 move. Every shot becomes a clip, so the build takes a few minutes longer.
  --motion-all: every Flow shot moves (the ancient-humans-video reference: 100 % of images in motion, a cut every 2 s). A shot may carry
            "frame": wide | zoom | zoom-out | pan-left | pan-right | left | right, so 2-3 consecutive shots can reuse one "file" with
            different framings (one generated image = several cuts). Without "frame", zoom in and out alternate as with --motion.
  card with "fn": {"family": "card", "card": {"fn": "scoreboard", "args": ["21", "0", "YOU", "THEM"]}} or {"fn": "phone", "args": ["MOM", ["3 missed calls"]]}

shots.json  = the same list as for prompts.py, one entry per shot, in order:
  {"i": 1, "sentence": "...", "family": "scene", "file": "F001"}                       -> flow/<dir>/F001.png (or .jpg)
  {"i": 2, "sentence": "...", "family": "card",  "card": {"icon": "clock", "big": "3:47", "small": "a.m.", "layout": "left"}}
  {"i": 3, "sentence": "...", "family": "chart", "chart": {"fn": "bar_ratio", "args": ["100x", "ROOM AIR", "5% CO2"]}}
  {"i": 4, "sentence": "...", "family": "title", "title": "THE HIDDEN COST"}
  {"i": 5, "sentence": "...", "family": "html",  "html": {"type": "symbol", "icon": "check", "caption": "verified"}}   -> flow/<dir>/html/H0005.png
      (hand-drawn inserts drawn in a browser by the hand-drawn-visuals skill: run its render.mjs with --shots before building)
  optional on any shot: "start": seconds (overrides timing), "day": "DAY 68" (corner label), "dark": true (cards/charts dark variant)
timing.json = either {"chars": "...", "end": [t0, t1, ...]} (ElevenLabs with-timestamps, per character)
              or a list of sentence start times [0.0, 4.2, ...] (one per shot)
Missing Flow images fall back to a cream caption card so the build never stops; the list of missing files is printed.
If flow/<dir>/BG.jpg (and BG_DARK.jpg) exist, generated once in Flow by prompts.py's two extra prompts, every card, chart, title and
symbol is drawn on them instead of a flat colour, so code inserts share the video's paper texture and light.
"""
import json, os, pathlib, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import cards, charts

W, H = 1920, 1080
CREAM, INK, GREY = (245, 239, 224), (30, 27, 22), (150, 145, 135)
def font(size, bold=False):
    try: return ImageFont.truetype("C:/Windows/Fonts/" + ("segoeprb.ttf" if bold else "segoepr.ttf"), size)
    except OSError: return ImageFont.load_default()

def starts_from_timing(shots, timing):
    if isinstance(timing, list): return [float(t) for t in timing]
    chars, end = timing["chars"], timing["end"]; pos, out = 0, []
    for s in shots:
        if "start" in s: out.append(float(s["start"])); continue
        k = chars.find(s["sentence"][:25], pos)          # locate the sentence in the voiced text
        out.append(end[k - 1] if k > 0 else (out[-1] if out else 0.0)); pos = max(pos, k)
    return out

def title_card(text, dark=False):
    im = cards.canvas(dark); d = ImageDraw.Draw(im); f = font(120, True)
    if d.textlength(text, font=f) > 1600:                       # wrap long titles on two balanced lines
        w = text.split(); k = len(w) // 2; lines = [" ".join(w[:k]), " ".join(w[k:])]
        while max(d.textlength(l, font=f) for l in lines) > 1600 and f.size > 60: f = font(f.size - 8, True)
    else: lines = [text]
    for i, l in enumerate(lines): d.text((W // 2, H // 2 + (i - (len(lines) - 1) / 2) * f.size * 1.25), l, font=f, fill=CREAM if dark else INK, anchor="mm")
    return im

def fallback(text):
    im = cards.canvas(False); d = ImageDraw.Draw(im); words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font(64)) <= 1500: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); y = H // 2 - 40 * len(lines)
    for i, ln in enumerate(lines): d.text((W // 2, y + i * 80), ln, font=font(64), fill=INK, anchor="mm")
    return im

def overlay(im, sentence, day, caption):
    d = ImageDraw.Draw(im, "RGBA"); f = font(40)
    if caption:
        tw = d.textlength(sentence, font=f); lines = [sentence]
        if tw > 1700:
            words, l1 = sentence.split(), ""
            while words and d.textlength(l1 + " " + words[0], font=f) < 1600: l1 = (l1 + " " + words.pop(0)).strip()
            lines = [l1, " ".join(words)]
        y = H - 70 - 50 * (len(lines) - 1)
        for i, ln in enumerate(lines):
            w = d.textlength(ln, font=f); d.rounded_rectangle([W // 2 - w // 2 - 24, y + i * 50 - 26, W // 2 + w // 2 + 24, y + i * 50 + 26], 14, fill=(245, 239, 224, 215))
            d.text((W // 2, y + i * 50), ln, font=f, fill=INK, anchor="mm")
    if day: d.text((50, 44), day, font=font(30, True), fill=(30, 27, 22, 170), anchor="lm")
    d.text((W - 50, 44), os.environ.get("SUBSCRIBE_LABEL", "SUBSCRIBE"), font=font(26), fill=(30, 27, 22, 110), anchor="rm")
    return im

def render(s, flow_dir):
    fam = s["family"]
    if fam == "card":
        c = dict(s["card"])
        if "fn" in c: return getattr(cards, c["fn"])(*c.get("args", []), **c.get("kwargs", {}))   # scoreboard, phone
        return cards.card(c.pop("icon"), c.pop("big"), c.pop("small", ""), dark=s.get("dark", False), **c)
    if fam == "chart": c = s["chart"]; return getattr(charts, c["fn"])(*c.get("args", []), **c.get("kwargs", {}))
    if fam == "title": return title_card(s["title"], s.get("dark", False))
    if fam == "html":                                  # rendered beforehand by the hand-drawn-visuals skill: node render.mjs shots.json flow/<dir>/html --shots
        f = flow_dir / "html" / f"H{s['i']:04d}.png"
        return Image.open(f).convert("RGB").resize((W, H)) if f.exists() else None
    for ext in (".png", ".jpg", ".webp"):
        f = flow_dir / f"{s.get('file') or f'F{s['i']:03d}'}{ext}"
        if f.exists(): return Image.open(f).convert("RGB").resize((W, H))
    return None

def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    shots_f, voice, timing_f, out = a[0], a[1], a[2], a[3] if len(a) > 3 else "slideshow.mp4"
    flow_dir = pathlib.Path(sys.argv[sys.argv.index("--flow") + 1]) if "--flow" in sys.argv else pathlib.Path("flow")
    caption, motion_all = "--caption" in sys.argv, "--motion-all" in sys.argv
    motion = motion_all or "--motion" in sys.argv
    shots = json.load(open(shots_f, encoding="utf-8")); timing = json.load(open(timing_f, encoding="utf-8"))
    for dark, name in ((False, "BG"), (True, "BG_DARK")):     # backgrounds generated once in Flow: every code insert is drawn on them
        bg = next((flow_dir / f"{name}{e}" for e in (".png", ".jpg", ".webp") if (flow_dir / f"{name}{e}").exists()), None)
        if bg: cards.BG[dark] = charts.BG[dark] = str(bg)
    if cards.BG[False] or cards.BG[True]: print("backgrounds:", cards.BG)
    starts = starts_from_timing(shots, timing)
    FF = imageio_ffmpeg.get_ffmpeg_exe()
    hh, mm, ss = subprocess.run([FF, "-i", voice], capture_output=True, text=True).stderr.split("Duration: ")[1].split(",")[0].split(":")
    dur = 3600 * int(hh) + 60 * int(mm) + float(ss)
    ends = starts[1:] + [dur]
    fr = pathlib.Path("build_slideshow/frames"); fr.mkdir(parents=True, exist_ok=True); missing, lines, moving = [], [], 0
    enc = ["-c:v", "libx264", "-preset", "fast", "-crf", "20"]
    for k, s in enumerate(shots):
        im = render(s, flow_dir); is_flow = s["family"] not in ("card", "chart", "title", "html")
        if im is None: missing.append(s.get("file") or s["i"]); im = fallback(s["sentence"]); is_flow = False
        else: im = overlay(im, s["sentence"], s.get("day"), caption)
        p = fr / f"f{k:04d}.png"; im.save(p, compress_level=1); d = max(ends[k] - starts[k], 0.4)
        if not motion: lines.append(f"file '{p.resolve().as_posix()}'\nduration {d:.3f}\n"); continue
        seg = fr / f"s{k:04d}.mp4"                       # --motion: every shot becomes a clip, concatenated without re-encoding
        if is_flow and (motion_all or k % 3 != 2):        # --motion: two Flow shots out of three move; --motion-all: every Flow shot moves
            n = int(round(d * 30)); z = f"1+0.07*on/{n}" if moving % 2 == 0 else f"1.07-0.07*on/{n}"; moving += 1
            cx, cy = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
            z, x, y = {                                   # "frame": one Flow image reused by 2-3 consecutive shots with different framings
                "wide": (f"1+0.07*on/{n}", cx, cy), "zoom": (f"1.15+0.15*on/{n}", cx, cy), "zoom-out": (f"1.30-0.20*on/{n}", cx, cy),
                "pan-left": ("1.2", f"(iw-iw/zoom)*(1-on/{n})", cy), "pan-right": ("1.2", f"(iw-iw/zoom)*on/{n}", cy),
                "left": (f"1.25+0.04*on/{n}", "0", cy), "right": (f"1.25+0.04*on/{n}", "iw-iw/zoom", cy),
            }.get(s.get("frame"), (z, cx, cy))
            vf = f"scale=2400:1350,zoompan=z='{z}':x='{x}':y='{y}':d={n}:s=1920x1080:fps=30,format=yuv420p"
            subprocess.run([FF, "-y", "-loglevel", "error", "-loop", "1", "-i", str(p), "-vf", vf, "-frames:v", str(n), *enc, str(seg)], check=True)
        else:
            subprocess.run([FF, "-y", "-loglevel", "error", "-loop", "1", "-i", str(p), "-t", f"{d:.3f}", "-vf", "fps=30,format=yuv420p", *enc, str(seg)], check=True)
        lines.append(f"file '{seg.resolve().as_posix()}'\n")
    lst = pathlib.Path("build_slideshow/frames.txt")
    lst.write_text("".join(lines) + ("" if motion else f"file '{(fr / f'f{len(shots) - 1:04d}.png').resolve().as_posix()}'\n"))
    video = ["-c:v", "copy"] if motion else ["-vf", "fps=30,format=yuv420p", *enc]
    subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", voice, *video,
                    "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)
    print(f"done -> {out} | {len(shots)} shots | missing Flow images: {missing}")

if __name__ == "__main__": main()
