"""Number cards with hand-drawn icons, cream explainer style. Never ship a bare number in a box: every card gets an icon
that says what the number is (clock, calendar, fuel, thermometer...), and consecutive cards use different layouts.

  from cards import card
  card("clock", "3:47", "a.m.").save("c01.png")                      # icon left, number right
  card("calendar", "240 DAYS", "nothing lands", layout="top")        # icon above the number
  card("stamp", "DAY 68", "the hum stops")                           # calendar-page stamp
  card("compare", "10 L SNOW", "1 L WATER", icons=("snow", "water")) # A -> B
  card("gauge", "412 TABLETS", "of 730", value=0.56, icon="pills")   # number + progress bar
  python cards.py   -> writes cards_demo.jpg (all icons and layouts) for a visual check

Icons: clock, calendar, fuel, thermo, snow, water, food, pills, hourglass, key, radio, fire, plane, battery, wind, sun, moon, heart, people, hair, dna,
       check, cross, question, exclamation, arrow_loop, gift, bulb, lock, coin, envelope, magnifier, star, eye, flag, door
  symbol('check', 'verified')  -> one big centred icon with an optional caption: the insert Flow used to be asked for
"""
import math, pathlib, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
CREAM, INK, GREY, WHITE = (245, 239, 224), (30, 27, 22), (150, 145, 135), (255, 255, 255)
SAND, SAGE, BLUE, TERRA, ORANGE, SLATE = (232, 213, 176), (196, 210, 184), (168, 186, 204), (199, 123, 88), (240, 180, 120), (38, 48, 60)
LW = 7  # ink line width
BG = {False: None, True: None}   # optional background images (cream, dark) generated ONCE in Flow, so code inserts share the video's paper and light

def canvas(dark=False, colour=None):
    """The base 1920x1080 image of every code insert: the Flow background of the video if set (BG[dark]), else a flat colour."""
    src = BG[bool(dark)]
    if src and pathlib.Path(src).exists(): return Image.open(src).convert("RGB").resize((W, H))
    return Image.new("RGB", (W, H), colour or (SLATE if dark else CREAM))

def font(size, bold=False):
    for name in (("segoeprb.ttf" if bold else "segoepr.ttf"), "arial.ttf"):
        try: return ImageFont.truetype("C:/Windows/Fonts/" + name, size)
        except OSError: pass
    return ImageFont.load_default()

# ---------- icons: drawn in a box (x, y, s) with s = side ----------
def _ell(d, x, y, s, fill, k=1.0):
    m = s * (1 - k) / 2; d.ellipse([x + m, y + m, x + s - m, y + s - m], fill=fill, outline=INK, width=LW)

def ic_clock(d, x, y, s):
    _ell(d, x, y, s, WHITE); cx, cy = x + s / 2, y + s / 2
    for a in range(12):
        r1, r2 = s * 0.40, s * (0.46 if a % 3 else 0.44); t = math.radians(a * 30)
        d.line([cx + r1 * math.sin(t), cy - r1 * math.cos(t), cx + r2 * math.sin(t), cy - r2 * math.cos(t)], fill=INK, width=4)
    d.line([cx, cy, cx + s * 0.22 * math.sin(math.radians(105)), cy - s * 0.22 * math.cos(math.radians(105))], fill=INK, width=LW)
    d.line([cx, cy, cx + s * 0.34 * math.sin(math.radians(282)), cy - s * 0.34 * math.cos(math.radians(282))], fill=TERRA, width=LW)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=INK)

def ic_calendar(d, x, y, s):
    d.rounded_rectangle([x, y + s * 0.12, x + s, y + s], 18, fill=WHITE, outline=INK, width=LW)
    d.rectangle([x, y + s * 0.12, x + s, y + s * 0.32], fill=TERRA, outline=INK, width=LW)
    for rx in (0.28, 0.72): d.rounded_rectangle([x + s * rx - 10, y, x + s * rx + 10, y + s * 0.22], 6, fill=INK)
    for r in range(3):
        for c in range(4):
            cx, cy = x + s * (0.2 + c * 0.2), y + s * (0.47 + r * 0.17)
            d.rectangle([cx - 12, cy - 12, cx + 12, cy + 12], fill=SAND if (r, c) != (1, 2) else TERRA, outline=INK, width=3)

def ic_fuel(d, x, y, s):
    d.rounded_rectangle([x + s * 0.15, y + s * 0.08, x + s * 0.85, y + s], 24, fill=BLUE, outline=INK, width=LW)
    for ry in (0.3, 0.55, 0.8): d.line([x + s * 0.15, y + s * ry, x + s * 0.85, y + s * ry], fill=INK, width=4)
    d.ellipse([x + s * 0.15, y, x + s * 0.85, y + s * 0.18], fill=SAND, outline=INK, width=LW)
    d.rectangle([x + s * 0.42, y + s * 0.02, x + s * 0.58, y + s * 0.1], fill=INK)

def ic_thermo(d, x, y, s):
    cx = x + s / 2
    d.rounded_rectangle([cx - s * 0.11, y, cx + s * 0.11, y + s * 0.72], 40, fill=WHITE, outline=INK, width=LW)
    d.ellipse([cx - s * 0.2, y + s * 0.6, cx + s * 0.2, y + s], fill=TERRA, outline=INK, width=LW)
    d.rectangle([cx - s * 0.04, y + s * 0.42, cx + s * 0.04, y + s * 0.72], fill=TERRA)
    for ry in (0.15, 0.27, 0.39): d.line([cx + s * 0.11, y + s * ry, cx + s * 0.2, y + s * ry], fill=INK, width=4)

def ic_snow(d, x, y, s):
    cx, cy, r = x + s / 2, y + s / 2, s * 0.42
    for a in range(0, 360, 60):
        t = math.radians(a); ex, ey = cx + r * math.cos(t), cy + r * math.sin(t)
        d.line([cx, cy, ex, ey], fill=BLUE, width=LW)
        for k in (0.55, 0.78):
            px, py = cx + r * k * math.cos(t), cy + r * k * math.sin(t)
            for b in (35, -35):
                tb = math.radians(a + b); d.line([px, py, px + r * 0.16 * math.cos(tb), py + r * 0.16 * math.sin(tb)], fill=BLUE, width=5)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=BLUE)

def ic_water(d, x, y, s):
    cx = x + s / 2
    d.polygon([(cx, y), (x + s * 0.18, y + s * 0.6), (cx, y + s * 0.6), (x + s * 0.82, y + s * 0.6)], fill=BLUE, outline=INK)
    d.ellipse([x + s * 0.18, y + s * 0.36, x + s * 0.82, y + s], fill=BLUE, outline=INK, width=LW)
    d.line([(cx, y), (x + s * 0.2, y + s * 0.62)], fill=INK, width=LW); d.line([(cx, y), (x + s * 0.8, y + s * 0.62)], fill=INK, width=LW)
    d.ellipse([x + s * 0.3, y + s * 0.6, x + s * 0.4, y + s * 0.72], fill=WHITE)

def ic_food(d, x, y, s):
    d.ellipse([x, y + s * 0.3, x + s, y + s * 0.85], fill=WHITE, outline=INK, width=LW)
    d.ellipse([x + s * 0.12, y + s * 0.38, x + s * 0.88, y + s * 0.77], fill=SAND, outline=INK, width=4)
    for k in range(3):
        px = x + s * (0.35 + k * 0.15); d.line([px, y + s * 0.05, px - 10, y + s * 0.3], fill=GREY, width=4)

def ic_pills(d, x, y, s):
    d.rounded_rectangle([x + s * 0.18, y + s * 0.2, x + s * 0.82, y + s], 26, fill=ORANGE, outline=INK, width=LW)
    d.rectangle([x + s * 0.12, y, x + s * 0.88, y + s * 0.26], fill=WHITE, outline=INK, width=LW)
    d.rectangle([x + s * 0.28, y + s * 0.45, x + s * 0.72, y + s * 0.8], fill=WHITE, outline=INK, width=4)
    d.line([x + s * 0.5, y + s * 0.52, x + s * 0.5, y + s * 0.73], fill=TERRA, width=6); d.line([x + s * 0.38, y + s * 0.625, x + s * 0.62, y + s * 0.625], fill=TERRA, width=6)

def ic_hourglass(d, x, y, s):
    d.polygon([(x + s * 0.2, y), (x + s * 0.8, y), (x + s * 0.5, y + s * 0.5), (x + s * 0.8, y + s), (x + s * 0.2, y + s), (x + s * 0.5, y + s * 0.5)], fill=WHITE, outline=INK)
    d.polygon([(x + s * 0.3, y + s * 0.72), (x + s * 0.7, y + s * 0.72), (x + s * 0.78, y + s * 0.96), (x + s * 0.22, y + s * 0.96)], fill=SAND)
    d.polygon([(x + s * 0.36, y + s * 0.1), (x + s * 0.64, y + s * 0.1), (x + s * 0.5, y + s * 0.4)], fill=SAND)
    d.line([(x + s * 0.2, y), (x + s * 0.8, y), (x + s * 0.5, y + s * 0.5), (x + s * 0.8, y + s), (x + s * 0.2, y + s), (x + s * 0.5, y + s * 0.5), (x + s * 0.2, y)], fill=INK, width=LW)

def ic_key(d, x, y, s):
    d.ellipse([x, y + s * 0.25, x + s * 0.5, y + s * 0.75], fill=ORANGE, outline=INK, width=LW)
    d.ellipse([x + s * 0.15, y + s * 0.4, x + s * 0.35, y + s * 0.6], fill=CREAM, outline=INK, width=4)
    d.rectangle([x + s * 0.48, y + s * 0.44, x + s, y + s * 0.56], fill=ORANGE, outline=INK, width=5)
    for px in (0.78, 0.92): d.rectangle([x + s * px, y + s * 0.56, x + s * px + 18, y + s * 0.7], fill=ORANGE, outline=INK, width=4)

def ic_radio(d, x, y, s):
    d.rounded_rectangle([x, y + s * 0.3, x + s, y + s], 22, fill=SAGE, outline=INK, width=LW)
    d.ellipse([x + s * 0.12, y + s * 0.45, x + s * 0.5, y + s * 0.85], fill=WHITE, outline=INK, width=5)
    d.line([x + s * 0.31, y + s * 0.65, x + s * 0.42, y + s * 0.55], fill=TERRA, width=5)
    for ry in (0.5, 0.62, 0.74): d.line([x + s * 0.6, y + s * ry, x + s * 0.9, y + s * ry], fill=INK, width=4)
    d.line([x + s * 0.8, y + s * 0.3, x + s * 0.95, y], fill=INK, width=LW); d.ellipse([x + s * 0.72, y + s * 0.36, x + s * 0.78, y + s * 0.42], fill=TERRA)

def ic_fire(d, x, y, s):
    cx = x + s / 2
    d.polygon([(cx, y), (x + s * 0.85, y + s * 0.45), (x + s * 0.8, y + s * 0.85), (cx, y + s), (x + s * 0.2, y + s * 0.85), (x + s * 0.15, y + s * 0.45), (x + s * 0.4, y + s * 0.35)], fill=ORANGE, outline=INK)
    d.line([(cx, y), (x + s * 0.85, y + s * 0.45), (x + s * 0.8, y + s * 0.85), (cx, y + s), (x + s * 0.2, y + s * 0.85), (x + s * 0.15, y + s * 0.45), (x + s * 0.4, y + s * 0.35), (cx, y)], fill=INK, width=LW)
    d.polygon([(cx, y + s * 0.45), (x + s * 0.65, y + s * 0.75), (cx, y + s * 0.95), (x + s * 0.35, y + s * 0.75)], fill=TERRA)

def ic_plane(d, x, y, s):
    cy = y + s * 0.5
    d.polygon([(x, cy), (x + s * 0.85, cy - s * 0.12), (x + s, cy), (x + s * 0.85, cy + s * 0.12)], fill=WHITE, outline=INK)
    d.polygon([(x + s * 0.35, cy - s * 0.05), (x + s * 0.55, cy - s * 0.45), (x + s * 0.68, cy - s * 0.45), (x + s * 0.55, cy - s * 0.05)], fill=BLUE, outline=INK)
    d.polygon([(x + s * 0.35, cy + s * 0.05), (x + s * 0.55, cy + s * 0.45), (x + s * 0.68, cy + s * 0.45), (x + s * 0.55, cy + s * 0.05)], fill=BLUE, outline=INK)
    d.polygon([(x + s * 0.02, cy - s * 0.02), (x + s * 0.1, cy - s * 0.3), (x + s * 0.2, cy - s * 0.3), (x + s * 0.15, cy - s * 0.02)], fill=BLUE, outline=INK)
    d.line([(x, cy), (x + s * 0.85, cy - s * 0.12), (x + s, cy), (x + s * 0.85, cy + s * 0.12), (x, cy)], fill=INK, width=LW)

def ic_battery(d, x, y, s):
    d.rounded_rectangle([x, y + s * 0.2, x + s * 0.88, y + s * 0.8], 16, fill=WHITE, outline=INK, width=LW)
    d.rectangle([x + s * 0.88, y + s * 0.38, x + s, y + s * 0.62], fill=INK)
    d.rectangle([x + s * 0.06, y + s * 0.27, x + s * 0.3, y + s * 0.73], fill=TERRA)

def ic_wind(d, x, y, s):
    for k, ry in enumerate((0.25, 0.5, 0.75)):
        ex = x + s * (0.75 if k == 1 else 0.9); d.line([x, y + s * ry, ex, y + s * ry], fill=BLUE, width=LW)
        d.arc([ex - s * 0.12, y + s * ry - s * 0.14, ex + s * 0.12, y + s * ry + s * 0.1], 90, 360, fill=BLUE, width=LW)

def ic_sun(d, x, y, s):
    cx, cy = x + s / 2, y + s / 2; _ell(d, x, y, s, ORANGE, 0.55)
    for a in range(0, 360, 45):
        t = math.radians(a); d.line([cx + s * 0.33 * math.cos(t), cy + s * 0.33 * math.sin(t), cx + s * 0.48 * math.cos(t), cy + s * 0.48 * math.sin(t)], fill=INK, width=LW)

def ic_moon(d, x, y, s):
    _ell(d, x, y, s, SAND, 0.9); d.ellipse([x + s * 0.3, y - s * 0.02, x + s * 1.05, y + s * 0.78], fill=CREAM)
    d.arc([x + s * 0.05, y + s * 0.05, x + s * 0.95, y + s * 0.95], 40, 320, fill=INK, width=LW)

def ic_people(d, x, y, s):
    for k, (cx, cy, r) in enumerate(((0.25, 0.42, 0.14), (0.75, 0.42, 0.14), (0.5, 0.36, 0.17))):
        px, py, rr = x + s * cx, y + s * cy, s * r
        d.rounded_rectangle([px - rr * 1.5, py + rr * 0.9, px + rr * 1.5, y + s], 30, fill=BLUE if k == 2 else SAGE, outline=INK, width=LW)
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=WHITE, outline=INK, width=LW)
        d.ellipse([px - rr * 0.35 - 5, py - 5, px - rr * 0.35 + 5, py + 5], fill=INK); d.ellipse([px + rr * 0.35 - 5, py - 5, px + rr * 0.35 + 5, py + 5], fill=INK)

def ic_heart(d, x, y, s):
    cx = x + s / 2
    d.ellipse([x, y, cx + 6, y + s * 0.62], fill=TERRA, outline=INK, width=LW); d.ellipse([cx - 6, y, x + s, y + s * 0.62], fill=TERRA, outline=INK, width=LW)
    d.polygon([(x + s * 0.03, y + s * 0.42), (x + s * 0.97, y + s * 0.42), (cx, y + s)], fill=TERRA)
    d.line([(x + s * 0.04, y + s * 0.42), (cx, y + s), (x + s * 0.96, y + s * 0.42)], fill=INK, width=LW)
    d.ellipse([x + s * 0.2, y + s * 0.3, x + s * 0.8, y + s * 0.5], fill=TERRA)

def ic_hair(d, x, y, s):
    """A round head seen from the front with a thin horseshoe of hair and a bare crown."""
    cx, cy = x + s / 2, y + s * 0.55
    d.ellipse([x + s * 0.12, y + s * 0.12, x + s * 0.88, y + s * 0.98], fill=WHITE, outline=INK, width=LW)
    for k in range(7):                                                               # side hairs, left and right
        t = math.radians(150 + k * 10); r = s * 0.40
        d.line([cx - r * math.cos(t) * 0.95, cy - r * math.sin(t) * 0.95, cx - r * math.cos(t) * 1.15, cy - r * math.sin(t) * 1.15], fill=INK, width=5)
        d.line([cx + r * math.cos(t) * 0.95, cy - r * math.sin(t) * 0.95, cx + r * math.cos(t) * 1.15, cy - r * math.sin(t) * 1.15], fill=INK, width=5)
    for k in (-1, 0, 1):                                                             # three lonely hairs on top
        d.line([cx + k * s * 0.08, y + s * 0.13, cx + k * s * 0.14, y - s * 0.02], fill=INK, width=4)
    d.ellipse([cx - s * 0.2 - 6, cy - 6, cx - s * 0.2 + 6, cy + 6], fill=INK); d.ellipse([cx + s * 0.2 - 6, cy - 6, cx + s * 0.2 + 6, cy + 6], fill=INK)

def ic_dna(d, x, y, s):
    """Double helix: two sine strands with rungs."""
    n = 40; pts_a, pts_b = [], []
    for i in range(n + 1):
        t = i / n; yy = y + s * t; ph = t * math.pi * 2
        pts_a.append((x + s / 2 + s * 0.3 * math.sin(ph), yy)); pts_b.append((x + s / 2 - s * 0.3 * math.sin(ph), yy))
    for i in range(0, n + 1, 5):
        if abs(pts_a[i][0] - pts_b[i][0]) > s * 0.12: d.line([pts_a[i], pts_b[i]], fill=TERRA, width=5)
    d.line(pts_a, fill=INK, width=LW); d.line(pts_b, fill=BLUE, width=LW)

# ---------- generic symbols (the inserts Flow used to draw: a check mark, a gift box, an arrow bent in a loop...) ----------
def ic_check(d, x, y, s):
    d.line([(x + s * 0.12, y + s * 0.55), (x + s * 0.4, y + s * 0.85), (x + s * 0.9, y + s * 0.2)], fill=SAGE, width=int(s * 0.16), joint="curve")
    d.line([(x + s * 0.12, y + s * 0.55), (x + s * 0.4, y + s * 0.85), (x + s * 0.9, y + s * 0.2)], fill=INK, width=LW, joint="curve")

def ic_cross(d, x, y, s):
    for a, b in (((0.15, 0.15), (0.85, 0.85)), ((0.85, 0.15), (0.15, 0.85))):
        d.line([(x + s * a[0], y + s * a[1]), (x + s * b[0], y + s * b[1])], fill=TERRA, width=int(s * 0.16))
        d.line([(x + s * a[0], y + s * a[1]), (x + s * b[0], y + s * b[1])], fill=INK, width=LW)

def ic_question(d, x, y, s):
    f = font(int(s * 1.1), True); d.text((x + s / 2, y + s / 2), "?", font=f, fill=BLUE, anchor="mm", stroke_width=LW, stroke_fill=INK)

def ic_exclamation(d, x, y, s):
    f = font(int(s * 1.1), True); d.text((x + s / 2, y + s / 2), "!", font=f, fill=TERRA, anchor="mm", stroke_width=LW, stroke_fill=INK)

def ic_arrow_loop(d, x, y, s):
    """An arrow bent back on itself: a loop with an arrowhead (repeat, cycle, 'back to square one')."""
    d.arc([x + s * 0.12, y + s * 0.12, x + s * 0.88, y + s * 0.88], 20, 330, fill=SAND, width=int(s * 0.13))
    d.arc([x + s * 0.12, y + s * 0.12, x + s * 0.88, y + s * 0.88], 20, 330, fill=INK, width=LW)
    d.arc([x + s * 0.25, y + s * 0.25, x + s * 0.75, y + s * 0.75], 20, 330, fill=INK, width=LW)
    ax, ay = x + s * 0.86, y + s * 0.5 - s * 0.38 * 0.34
    d.polygon([(ax - s * 0.12, ay - s * 0.16), (ax + s * 0.1, ay), (ax - s * 0.12, ay + s * 0.16)], fill=SAND, outline=INK)

def ic_gift(d, x, y, s):
    d.rectangle([x + s * 0.1, y + s * 0.4, x + s * 0.9, y + s * 0.95], fill=SAGE, outline=INK, width=LW)
    d.rectangle([x + s * 0.05, y + s * 0.3, x + s * 0.95, y + s * 0.45], fill=SAGE, outline=INK, width=LW)
    d.rectangle([x + s * 0.42, y + s * 0.3, x + s * 0.58, y + s * 0.95], fill=TERRA, outline=INK, width=LW)
    for k in (-1, 1): d.ellipse([x + s * 0.5 + k * s * 0.2 - s * 0.14, y + s * 0.1, x + s * 0.5 + k * s * 0.2 + s * 0.14, y + s * 0.32], fill=TERRA, outline=INK, width=LW)

def ic_bulb(d, x, y, s):
    d.ellipse([x + s * 0.2, y, x + s * 0.8, y + s * 0.65], fill=ORANGE, outline=INK, width=LW)
    d.rectangle([x + s * 0.38, y + s * 0.6, x + s * 0.62, y + s * 0.85], fill=WHITE, outline=INK, width=LW)
    d.line([x + s * 0.38, y + s * 0.93, x + s * 0.62, y + s * 0.93], fill=INK, width=LW)
    for a in (-30, 0, 30):
        t = math.radians(-90 + a); d.line([x + s / 2 + math.cos(t) * s * 0.36, y + s * 0.33 + math.sin(t) * s * 0.36, x + s / 2 + math.cos(t) * s * 0.5, y + s * 0.33 + math.sin(t) * s * 0.5], fill=INK, width=5)

def ic_lock(d, x, y, s):
    d.rounded_rectangle([x + s * 0.15, y + s * 0.42, x + s * 0.85, y + s * 0.95], 24, fill=SAND, outline=INK, width=LW)
    d.arc([x + s * 0.28, y + s * 0.05, x + s * 0.72, y + s * 0.6], 180, 360, fill=INK, width=LW + 4)
    d.ellipse([x + s * 0.44, y + s * 0.58, x + s * 0.56, y + s * 0.7], fill=INK); d.line([x + s * 0.5, y + s * 0.66, x + s * 0.5, y + s * 0.82], fill=INK, width=6)

def ic_coin(d, x, y, s):
    d.ellipse([x + s * 0.08, y + s * 0.08, x + s * 0.92, y + s * 0.92], fill=ORANGE, outline=INK, width=LW)
    d.ellipse([x + s * 0.22, y + s * 0.22, x + s * 0.78, y + s * 0.78], outline=INK, width=4)

def ic_envelope(d, x, y, s):
    d.rectangle([x + s * 0.05, y + s * 0.2, x + s * 0.95, y + s * 0.8], fill=WHITE, outline=INK, width=LW)
    d.line([(x + s * 0.05, y + s * 0.2), (x + s * 0.5, y + s * 0.55), (x + s * 0.95, y + s * 0.2)], fill=INK, width=LW)

def ic_magnifier(d, x, y, s):
    d.ellipse([x + s * 0.05, y + s * 0.05, x + s * 0.65, y + s * 0.65], fill=BLUE, outline=INK, width=LW + 3)
    d.line([x + s * 0.58, y + s * 0.58, x + s * 0.92, y + s * 0.92], fill=INK, width=int(s * 0.12))

def ic_star(d, x, y, s):
    pts = []
    for k in range(10):
        r = s * (0.48 if k % 2 == 0 else 0.2); t = math.radians(-90 + k * 36)
        pts.append((x + s / 2 + r * math.cos(t), y + s / 2 + r * math.sin(t)))
    d.polygon(pts, fill=ORANGE, outline=INK, width=LW)

def ic_eye(d, x, y, s):
    d.polygon([(x + s * 0.05, y + s * 0.5), (x + s * 0.5, y + s * 0.2), (x + s * 0.95, y + s * 0.5), (x + s * 0.5, y + s * 0.8)], fill=WHITE, outline=INK, width=LW)
    d.ellipse([x + s * 0.36, y + s * 0.36, x + s * 0.64, y + s * 0.64], fill=BLUE, outline=INK, width=LW)
    d.ellipse([x + s * 0.45, y + s * 0.45, x + s * 0.55, y + s * 0.55], fill=INK)

def ic_flag(d, x, y, s):
    d.line([x + s * 0.2, y + s * 0.05, x + s * 0.2, y + s * 0.95], fill=INK, width=LW + 2)
    d.polygon([(x + s * 0.22, y + s * 0.08), (x + s * 0.9, y + s * 0.25), (x + s * 0.22, y + s * 0.45)], fill=TERRA, outline=INK, width=LW)

def ic_door(d, x, y, s):
    d.rectangle([x + s * 0.2, y + s * 0.05, x + s * 0.8, y + s * 0.95], fill=SAND, outline=INK, width=LW)
    d.ellipse([x + s * 0.64, y + s * 0.48, x + s * 0.72, y + s * 0.56], fill=INK)

ICONS = {n[3:]: f for n, f in globals().items() if n.startswith("ic_")}

def draw_icon(d, name, x, y, s):
    ICONS[name](d, x, y, s)

# ---------- layouts ----------
def _fit(d, text, maxw, size, bold=True):
    f = font(size, bold)
    while d.textlength(text, font=f) > maxw and size > 40: size -= 8; f = font(size, bold)
    return f

def card(icon, big, small="", layout="left", dark=False, icons=None, value=None, accent=None):
    """icon: an ICONS key (or 'stamp' / 'compare' / 'gauge' as layout shortcuts). big: the number. small: 2-4 words.
    layout: 'left' (icon left, number right), 'top' (icon above), 'stamp' (calendar page for DAY n),
            'compare' (big -> small with two icons), 'gauge' (number + bar, value 0..1)."""
    if icon in ("stamp", "compare", "gauge"): layout, icon = icon, icon if icon in ICONS else None
    bg, ink, sub = (SLATE, CREAM, (190, 196, 204)) if dark else (CREAM, INK, GREY)
    im = canvas(dark, bg); d = ImageDraw.Draw(im); acc = accent or TERRA
    if layout == "left":
        d.rounded_rectangle([200, 260, 1720, 820], 44, fill=WHITE if not dark else (50, 62, 76), outline=ink, width=6)
        draw_icon(d, icon, 300, 380, 320)
        f = _fit(d, big, 940, 170); d.text((1120, 500 if small else 540), big, font=f, fill=acc if big[:1].isdigit() and layout == "left" and small == "a.m." else ink, anchor="mm")
        if small: d.text((1120, 660), small, font=font(52), fill=sub, anchor="mm")
    elif layout == "top":
        draw_icon(d, icon, 960 - 130, 150, 260)
        f = _fit(d, big, 1500, 190); d.text((960, 600), big, font=f, fill=ink, anchor="mm")
        if small: d.text((960, 760), small, font=font(56), fill=sub, anchor="mm")
    elif layout == "stamp":
        x, y, s = 660, 160, 600
        d.rounded_rectangle([x, y + 70, x + s, y + s + 120], 30, fill=WHITE if not dark else (50, 62, 76), outline=ink, width=8)
        d.rectangle([x, y + 70, x + s, y + 190], fill=acc, outline=ink, width=8)
        for rx in (0.25, 0.75): d.rounded_rectangle([x + s * rx - 16, y + 20, x + s * rx + 16, y + 120], 10, fill=ink)
        word, num = (big.split(" ", 1) + [""])[:2]
        d.text((x + s / 2, y + 130), word, font=font(60, True), fill=WHITE, anchor="mm")
        d.text((x + s / 2, y + 440), num, font=_fit(d, num, 520, 230), fill=ink, anchor="mm")
        if small: d.text((960, 960), small, font=font(56), fill=sub, anchor="mm")
    elif layout == "compare":
        a, b = icons or ("snow", "water")
        for k, (ic, txt, cx) in enumerate(((a, big, 480), (b, small, 1440))):
            draw_icon(d, ic, cx - 140, 230, 280)
            d.text((cx, 700), txt, font=_fit(d, txt, 760, 120), fill=ink, anchor="mm")
        d.text((960, 520), "=", font=font(200, True), fill=acc, anchor="mm")
        d.polygon([(880, 470), (1040, 520), (880, 570)], fill=bg)  # keep the '=' crisp on cream
        d.text((960, 520), "=", font=font(200, True), fill=acc, anchor="mm")
    elif layout == "gauge":
        if icon: draw_icon(d, icon, 240, 300, 260)
        f = _fit(d, big, 1100, 170); d.text((1100, 400), big, font=f, fill=ink, anchor="mm")
        d.rounded_rectangle([240, 620, 1680, 720], 50, fill=WHITE if not dark else (50, 62, 76), outline=ink, width=6)
        v = max(0.0, min(1.0, value or 0)); d.rounded_rectangle([246, 626, 246 + int(1428 * v), 714], 44, fill=acc)
        if small: d.text((960, 820), small, font=font(56), fill=sub, anchor="mm")
    return im

def symbol(icon, caption="", dark=False):
    """One big centred icon (a check mark, a gift box, a bent arrow), optional caption below: replaces a Flow 'single isolated object'."""
    bg, ink, sub = (SLATE, CREAM, (190, 196, 204)) if dark else (CREAM, INK, GREY)
    im = canvas(dark, bg); d = ImageDraw.Draw(im)
    draw_icon(d, icon, 960 - 250, 220 if caption else 290, 500)
    if caption: d.text((960, 860), caption, font=font(64), fill=sub, anchor="mm")
    return im

def scoreboard(left, right, left_name="", right_name="", dark=True, accent=None):
    """Two big numbers on a flip-board, 'VICTORY x30' style: scoreboard("21", "0", "YOU", "THEM")."""
    bg, ink = (SLATE, CREAM) if dark else (CREAM, INK)
    im = canvas(dark, bg); d = ImageDraw.Draw(im); acc = accent or TERRA
    for k, (num, name, cx) in enumerate(((left, left_name, 640), (right, right_name, 1280))):
        d.rounded_rectangle([cx - 260, 300, cx + 260, 760], 36, fill=(28, 30, 34), outline=ink, width=6)
        d.line([cx - 260, 530, cx + 260, 530], fill=bg, width=6)
        d.text((cx, 530), num, font=_fit(d, num, 480, 300), fill=CREAM if k else acc, anchor="mm")
        if name: d.text((cx, 860), name, font=font(60, True), fill=ink, anchor="mm")
    d.text((960, 530), ":", font=font(200, True), fill=ink, anchor="mm")
    return im

def phone(title, lines=(), dark=True, accent=None):
    """A phone screen with a short title and up to 4 lines: phone("MOM", ["3 missed calls"]), phone("MY BANK", ["$31,240.00", "SEND"])."""
    bg, ink = (SLATE, CREAM) if dark else (CREAM, INK)
    im = canvas(dark, bg); d = ImageDraw.Draw(im); acc = accent or TERRA
    x0, y0, x1, y1 = 700, 90, 1220, 990
    d.rounded_rectangle([x0, y0, x1, y1], 70, fill=(28, 30, 34), outline=ink, width=8)
    d.rounded_rectangle([x0 + 24, y0 + 24, x1 - 24, y1 - 24], 54, fill=WHITE if not dark else (236, 240, 244))
    d.rounded_rectangle([880, y0 + 40, 1040, y0 + 70], 15, fill=(28, 30, 34))
    d.text((960, 300), title, font=_fit(d, title, 420, 72), fill=INK, anchor="mm")
    for k, t in enumerate(list(lines)[:4]):
        d.rounded_rectangle([x0 + 70, 400 + k * 130, x1 - 70, 500 + k * 130], 24, fill=acc if k == len(lines) - 1 and len(lines) > 1 else (220, 224, 228))
        d.text((960, 450 + k * 130), t, font=_fit(d, t, 360, 48), fill=WHITE if (k == len(lines) - 1 and len(lines) > 1) else INK, anchor="mm")
    return im

if __name__ == "__main__":
    demo = [("clock", "3:47", "a.m.", "left", {}), ("calendar", "240 DAYS", "nothing lands", "top", {}),
            ("fuel", "14,000 L", "arctic diesel", "left", {}), ("thermo", "-58 °C", "tonight", "top", {}),
            ("stamp", "DAY 68", "the hum stops", "stamp", {}), ("compare", "10 L SNOW", "1 L WATER", "compare", {"icons": ("snow", "water")}),
            ("gauge", "412 TABLETS", "of 730", "gauge", {"value": 0.56, "icon": "pills"}), ("hourglass", "2 H 40", "before the pipes freeze", "left", {}),
            ("key", "HEAT IS THE KEY", "", "top", {}), ("radio", "291", "days of silence", "left", {}),
            ("fire", "DAY 248", "the smoke", "top", {"dark": True}), ("plane", "DAY 365", "wheels down", "left", {}),
            ("battery", "4,100 L", "left in the tank", "gauge", {"value": 0.29, "icon": "battery"}), ("wind", "91 KNOTS", "and climbing", "top", {}),
            ("sun", "146 DAYS", "of darkness", "left", {"icon": "moon"}), ("heart", "2,200 KCAL", "a day", "left", {"icon": "food"})]
    sheet = Image.new("RGB", (480 * 4, 270 * 5), "white")
    for i, (ic, big, small, lay, kw) in enumerate(demo):
        kw = dict(kw); ic = kw.pop("icon", ic)
        im = card(ic, big, small, layout=lay, **kw).resize((480, 270)); sheet.paste(im, ((i % 4) * 480, (i // 4) * 270))
    for i, im in enumerate((scoreboard("21", "0", "YOU", "THEM"), phone("MOM", ["3 missed calls"]), phone("MY BANK", ["$31,240.00", "SEND"]), scoreboard("9", "10", "SAVED", "SHOTS", dark=False))):
        sheet.paste(im.resize((480, 270)), (i * 480, 4 * 270))
    gen = ["check", "cross", "question", "exclamation", "arrow_loop", "gift", "bulb", "lock", "coin", "envelope", "magnifier", "star", "eye", "flag", "door"]
    sheet2 = Image.new("RGB", (480 * 4, 270 * 4), "white")
    for i, ic in enumerate(gen):
        sheet2.paste(symbol(ic, ic.replace("_", " "), dark=(i % 5 == 4)).resize((480, 270)), ((i % 4) * 480, (i // 4) * 270))
    out2 = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "cards_symbols.jpg"); sheet2.save(out2, quality=85); print(out2)
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "cards_demo.jpg"); sheet.save(out, quality=85); print(out)
