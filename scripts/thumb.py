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
    args = [a for a in sys.argv[1:] if a != "--force"]
    src, dst, text = args[0], args[1], args[2]
    if "--force" not in sys.argv and (errs := lint(text)): sys.exit("thumbnail text refused: " + "; ".join(errs))
    im = Image.open(src).convert("RGB").resize((1280, 720), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1280, 200], fill=(26, 40, 78))                       # navy band
    f = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 150)
    while d.textlength(text, font=f) > 1180: f = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", f.size - 6)
    d.text((640, 100), text, font=f, fill=(242, 196, 70), anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0))
    im.save(dst, quality=92, optimize=True)
    import os; print(dst, im.size, f"{os.path.getsize(dst) / 1e6:.2f} MB")
