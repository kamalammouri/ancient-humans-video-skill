"""Thumbnail text by code (never by the image generator): python thumb.py flow/snoring/THUMB.png thumbnail.jpg "WHY DO WE SNORE?"
Same template as the Goosebumps thumbnail: 1280 x 720, a dark navy band across the top, yellow Impact capitals with a thick black outline.
The text is checked first (SKILL.md, norm 4): 2 to 4 words, no duration-like number, none of the known English mistakes.
This lint only catches known patterns; the English copy editor agent still reads every text. --force skips the lint."""
import re, sys
from PIL import Image, ImageDraw, ImageFont

def lint(text):
    t, words = text.upper().strip(), text.split()
    errors = []
    if not 2 <= len(words) <= 4: errors.append(f"{len(words)} words, 2 to 4 expected")
    if re.search(r"\b\d{1,2}:\d{2}\b", t): errors.append("duration-like number (3:47) looks like YouTube's timer")
    if re.match(r"WHY \w+ING\b", t) and not re.match(r"WHY (EVERYTHING|NOTHING|SOMETHING|ANYTHING)\b", t):
        errors.append('"WHY + -ing" is not English: "WHY DO WE SNORE?" or "WHY WE SNORE"')
    if re.fullmatch(r"WHY (WE|YOU|I|THEY|HUMANS|PEOPLE) \w+( \w+)?\?!?", t):
        errors.append('"WHY WE/YOU + verb?" is not a question: "WHY DO WE SNORE?" or drop the "?"')
    return errors   # "WHY APPENDIX?" (singular noun) is left to the copy editor: "WHY BALD?!" is fine and a regex can't tell them apart

if __name__ == "__main__":
    # --square[=x]: 1080x1080 image for a YouTube post, square cut centred at x (0 = left edge, 1 = right, default 0.5);
    # text "" = no band (python thumb.py flow/period/F027.png posts/P1.jpg "" --square=0.3)
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    src, dst, text = [a for a in sys.argv[1:] if not a.startswith("--")][:3]
    sq = next((float(a.split("=", 1)[1]) if "=" in a else 0.5 for a in flags if a.startswith("--square")), None)
    # "LINE ONE|LINE TWO" = two lines; --noband = yellow text straight on the image (the scene keeps its top third empty)
    if text and "--force" not in flags and (errs := lint(text.replace("|", " "))): sys.exit("thumbnail text refused: " + "; ".join(errs))
    im = Image.open(src).convert("RGB")
    if sq is None:
        im = im.resize((1280, 720), Image.LANCZOS)
    else:
        w, h = im.size; s = min(w, h); x0 = round(min(max(sq * w - s / 2, 0), w - s))
        im = im.crop((x0, 0, x0 + s, s)).resize((1080, 1080), Image.LANCZOS)
    W = im.size[0]
    d = ImageDraw.Draw(im)
    if text:
        lines = text.split("|"); bh = 200 if len(lines) == 1 else 300
        if "--noband" not in flags: d.rectangle([0, 0, W, bh], fill=(26, 40, 78))   # navy band
        f = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 150 if len(lines) == 1 else 125)
        while max(d.textlength(l, font=f) for l in lines) > W - 100: f = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", f.size - 6)
        for n, l in enumerate(lines):
            d.text((W // 2, bh * (2 * n + 1) // (2 * len(lines))), l, font=f, fill=(242, 196, 70), anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0))
    im.save(dst, quality=92, optimize=True)
    import os; print(dst, im.size, f"{os.path.getsize(dst) / 1e6:.2f} MB")
