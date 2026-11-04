"""Charts, gauges and timelines in the Apefully slideshow style, rendered by code (exact numbers, consistent look).
Every function returns a 1920x1080 PIL image: a cream rounded card with a black outline on a flat pale background,
handwritten capitals, one accent colour. Patterns measured on the channel's videos (see references/scene-catalogue.md).

  from charts import *
  bar_ratio("100x", "ROOM AIR", "5% CO2")                  # one tiny bar vs one huge bar, ratio label on top
  bars([("CO2", 40, GREY), ("O2", 42, GREEN), ("EXERCISE", 41, ORANGE)], ref=45)   # bars + dashed reference line
  pie(20, "CALORIES")                                      # pastel pie, one detached orange slice with "20%"
  line([0,1,1,3,3,8], "WEEK 1", "WEEK 12", shape="hockey") # stair / hockey stick / peak-then-flat
  lines2([...], [...], labels=("FAST", "SLOW"))            # two curves compared
  dots("86 BILLION", "neurons", n=60, icon="*")            # big number + pictogram grid
  scatter(points, "AGE", "RISK")                           # orange cloud on two named axes
  thermo("+0.5°", "brain")  /  thermo2(("BIRD", 0.8), ("MAMMAL", 0.5))
  hbar_gauge(0.72, ("LOW", "OK", "HIGH"))                  # 3-zone horizontal bar with round cursor
  dial(0.8)                                                # round 3-zone gauge with needle, no text
  timeline("6 MONTHS", start_dot=True)  /  timeline_marks(["BIRTH", "6 MO", "2 YR"], [0, .3, 1])
  daynight(["6 AM", "NOON", "10 PM"])                      # flat sun→moon curve with dotted markers
  compare(("FAST", "hare"), ("SLOW", "tortoise"), icons=(imgA, imgB))   # two sides split by a dotted line
  pills([("A", "YES"), ("B", "NO"), ("C", "YES")])          # table of aligned pills with a label under each
  python charts.py -> charts_demo.jpg
"""
import math, pathlib, sys, io
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

W, H = 1920, 1080
CREAM, CARD, INK, GREY, LIGHT = (245, 239, 224), (250, 246, 236), (30, 27, 22), (150, 145, 135), (225, 220, 205)
ORANGE, RED, BLUE, GREEN, SAND, PALEBLUE, PEACH = (236, 140, 60), (214, 72, 48), (110, 150, 200), (120, 170, 110), (232, 213, 176), (214, 228, 238), (246, 220, 200)
LW = 6

def font(size, bold=True):
    for n in (("segoeprb.ttf" if bold else "segoepr.ttf"), "arial.ttf"):
        try: return ImageFont.truetype("C:/Windows/Fonts/" + n, size)
        except OSError: pass
    return ImageFont.load_default()

BG = {False: None, True: None}   # optional Flow-generated backgrounds (cream, dark), set by build_slideshow.py

def canvas(bg=CREAM, card=(220, 150, 1700, 930)):
    """Background + rounded card. Returns (image, draw, card box)."""
    src = BG[bg != CREAM]
    im = Image.open(src).convert("RGB").resize((W, H)) if src and pathlib.Path(src).exists() else Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    if card: d.rounded_rectangle(card, 40, fill=CARD, outline=INK, width=LW)
    return im, d, card

def title(d, text, y=870, size=52, fill=INK):
    d.text((W // 2, y), text, font=font(size), fill=fill, anchor="mm")

def _mpl(fig_w=12, fig_h=6.2):
    plt.rcdefaults(); plt.xkcd(scale=0.6, length=80, randomness=1.5)
    plt.rcParams.update({"font.family": "Segoe Print", "font.size": 22, "axes.edgecolor": "#1e1b16", "axes.linewidth": 3,
                         "figure.facecolor": "none", "axes.facecolor": "none", "path.effects": []})
    return plt.subplots(figsize=(fig_w, fig_h), dpi=100)

def _paste_fig(im, fig, box):
    buf = io.BytesIO(); fig.savefig(buf, format="png", transparent=True, bbox_inches="tight"); plt.close(fig)
    pic = Image.open(buf).convert("RGBA"); x0, y0, x1, y1 = box
    pic.thumbnail((x1 - x0, y1 - y0)); im.paste(pic, (x0 + (x1 - x0 - pic.width) // 2, y0 + (y1 - y0 - pic.height) // 2), pic)

def _hex(c): return "#%02x%02x%02x" % c

# ---------------- bars ----------------
def bar_ratio(ratio, small_label, big_label="", bg=CREAM):
    im, d, _ = canvas(bg)
    d.rectangle([700, 760, 820, 800], fill=GREY, outline=INK, width=4)                     # tiny bar
    d.rectangle([1000, 280, 1220, 800], fill=INK)                                          # huge bar
    d.line([560, 800, 1360, 800], fill=INK, width=LW)
    d.text((1110, 230), ratio, font=font(70), fill=INK, anchor="mm")
    d.text((760, 850), small_label, font=font(36, False), fill=GREY, anchor="mm")
    if big_label: d.text((1110, 850), big_label, font=font(36, False), fill=GREY, anchor="mm")
    return im

def bars(items, ref=None, ylabel="", bg=CREAM):
    """items = [(label, value, colour)], ref = dashed horizontal reference value."""
    im, d, _ = canvas(bg); n = len(items); vmax = max(v for _, v, _ in items) * 1.25
    x0, x1, y0, y1 = 420, 1500, 760, 260; bw = (x1 - x0) / (n * 2)
    for i, (lab, v, col) in enumerate(items):
        col = tuple(col); cx = x0 + bw * (2 * i + 1); h = (y0 - y1) * v / vmax
        d.rounded_rectangle([cx - bw * 0.42, y0 - h, cx + bw * 0.42, y0], 14, fill=col, outline=INK, width=4)
        d.text((cx, y0 + 50), lab, font=font(38), fill=INK, anchor="mm")
        d.text((cx, y0 - h - 44), f"{v:g}", font=font(48), fill=INK, anchor="mm")
    d.line([x0, y0, x1, y0], fill=INK, width=LW)
    if ref is not None:
        yr = y0 - (y0 - y1) * ref / vmax
        for x in range(x0, x1, 40): d.line([x, yr, x + 22, yr], fill=INK, width=4)
    if ylabel: title(d, ylabel)
    return im

# ---------------- pie ----------------
def pie(percent, label, bg=CREAM, accent=ORANGE):
    im, d, _ = canvas(bg); cx, cy, r = 900, 520, 240
    d.pieslice([cx - r, cy - r, cx + r, cy + r], -90 + 360 * percent / 100, 270, fill=SAND, outline=INK, width=LW)
    rest = 360 * (100 - percent) / 100
    for k in range(1, 4):   # faint divisions in the rest
        a = math.radians(-90 + 360 * percent / 100 + rest * k / 4); d.line([cx, cy, cx + r * math.cos(a), cy + r * math.sin(a)], fill=LIGHT, width=4)
    a0 = -90 + 360 * percent / 100; am = math.radians((a0 - 90) / 2); off = 30
    ox, oy = off * math.cos(am), off * math.sin(am)
    d.pieslice([cx - r + ox, cy - r + oy, cx + r + ox, cy + r + oy], -90, a0, fill=accent, outline=INK, width=LW)
    d.text((cx + r + 130, cy - r + 40), f"{percent:g}%", font=font(72), fill=INK, anchor="mm")
    title(d, label)
    return im

# ---------------- lines ----------------
def line(values, x0_label="", x1_label="", shape=None, color=RED, bg=CREAM, ylabel=""):
    """values: list of y; shape 'stair' draws steps, otherwise a smooth-ish line (xkcd wobble)."""
    im, d, _ = canvas(bg); fig, ax = _mpl()
    xs = list(range(len(values)))
    if shape == "stair": ax.step(xs, values, where="post", color=_hex(color), linewidth=6)
    else: ax.plot(xs, values, color=_hex(color), linewidth=6)
    ax.set_xticks([0, len(values) - 1]); ax.set_xticklabels([x0_label, x1_label]); ax.set_yticks([])
    ax.spines[["top", "right"]].set_visible(False); ax.set_ylabel(ylabel)
    _paste_fig(im, fig, (260, 190, 1660, 900)); return im

def lines2(a, b, labels=("A", "B"), colors=(RED, BLUE), bg=CREAM):
    im, d, _ = canvas(bg); fig, ax = _mpl()
    for vals, lab, col in ((a, labels[0], colors[0]), (b, labels[1], colors[1])):
        ax.plot(range(len(vals)), vals, color=_hex(col), linewidth=6, label=lab)
    ax.set_xticks([]); ax.set_yticks([]); ax.spines[["top", "right"]].set_visible(False); ax.legend(frameon=False, fontsize=24)
    _paste_fig(im, fig, (260, 190, 1660, 900)); return im

def scatter(points, xlabel, ylabel, color=ORANGE, bg=CREAM):
    im, d, _ = canvas(bg); fig, ax = _mpl()
    ax.scatter([p[0] for p in points], [p[1] for p in points], s=260, color=_hex(color), edgecolor="#1e1b16", linewidth=2)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.spines[["top", "right"]].set_visible(False)
    _paste_fig(im, fig, (260, 190, 1660, 900)); return im

# ---------------- counts ----------------
def dots(big, small, n=60, icon="●", cols=15, color=BLUE, bg=CREAM, highlight=0):
    """Big number on top, a grid of n identical pictograms under it; the first `highlight` are drawn in accent colour."""
    im, d, _ = canvas(bg); d.text((W // 2, 270), big, font=font(110), fill=INK, anchor="mm")
    if n <= 12: cols = n
    rows = math.ceil(n / cols); sx = min(96, 1320 / cols); sy = min(96, 440 / rows)        # grid always fits the card
    f = font(max(18, int(min(sx, sy) * 0.85)), False)
    x0 = W // 2 - (cols - 1) * sx / 2; y0 = 400 + (440 - rows * sy) / 2 + sy / 2
    for i in range(n):
        d.text((x0 + (i % cols) * sx, y0 + (i // cols) * sy), icon, font=f, fill=ORANGE if i < highlight else color, anchor="mm")
    if small: title(d, small, y=890, size=44, fill=GREY)
    return im

# ---------------- gauges ----------------
def _thermo(d, cx, top, bottom, level, value="", label="", color=RED):
    d.rounded_rectangle([cx - 36, top, cx + 36, bottom - 40], 36, fill=CARD, outline=INK, width=LW)
    d.ellipse([cx - 70, bottom - 110, cx + 70, bottom + 30], fill=color, outline=INK, width=LW)
    lv = bottom - 60 - (bottom - 60 - top - 30) * max(0, min(1, level))
    d.rectangle([cx - 14, lv, cx + 14, bottom - 60], fill=color)
    for k in range(6): y = top + 40 + k * (bottom - 120 - top) / 5; d.line([cx + 36, y, cx + 62, y], fill=INK, width=4)
    if value: d.text((cx + 150, lv), value, font=font(60), fill=INK, anchor="lm")
    if label: d.text((cx, bottom + 80), label, font=font(40), fill=INK, anchor="mm")

def thermo(value, label="", level=0.65, bg=CREAM):
    im, d, _ = canvas(bg); _thermo(d, 820, 230, 760, level, value, label); return im

def thermo2(a, b, bg=CREAM):
    """a, b = (label, level 0..1). Dotted line joins the two levels."""
    im, d, _ = canvas(bg); _thermo(d, 700, 230, 740, a[1], label=a[0]); _thermo(d, 1220, 230, 740, b[1], label=b[0], color=BLUE)
    ya, yb = [740 - 60 - (740 - 60 - 230 - 30) * l for l in (a[1], b[1])]
    for t in range(0, 100, 6): x = 740 + (1180 - 740) * t / 100; y = ya + (yb - ya) * t / 100; d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=GREY)
    return im

def hbar_gauge(value, zones=("LOW", "OK", "HIGH"), colors=(BLUE, GREEN, RED), bg=CREAM, label=""):
    im, d, _ = canvas(bg); x0, x1, y0, y1 = 360, 1560, 520, 620; n = len(zones)
    for i, (z, c) in enumerate(zip(zones, colors)):
        xa, xb = x0 + (x1 - x0) * i / n, x0 + (x1 - x0) * (i + 1) / n
        d.rectangle([xa, y0, xb, y1], fill=c); d.text(((xa + xb) / 2, y1 + 60), z, font=font(38), fill=INK, anchor="mm")
    d.rounded_rectangle([x0, y0, x1, y1], 30, outline=INK, width=LW)
    cx = x0 + (x1 - x0) * max(0, min(1, value)); d.ellipse([cx - 44, y0 - 110, cx + 44, y0 - 22], fill=CARD, outline=INK, width=LW)
    d.polygon([(cx - 18, y0 - 30), (cx + 18, y0 - 30), (cx, y0 - 4)], fill=INK)
    if label: title(d, label)
    return im

def dial(value, colors=(GREEN, ORANGE, RED), bg=CREAM, label=""):
    im, d, _ = canvas(bg); cx, cy, r = 960, 640, 330
    for i, c in enumerate(colors):
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 180 + 60 * i, 240 + 60 * i, fill=c, outline=INK, width=LW)
    d.pieslice([cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6], 180, 360, fill=CARD, outline=INK, width=LW)
    a = math.radians(180 + 180 * max(0, min(1, value))); d.line([cx, cy, cx + r * 0.85 * math.cos(a), cy + r * 0.85 * math.sin(a)], fill=INK, width=10)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=INK)
    if label: title(d, label)
    return im

# ---------------- time ----------------
def timeline(label, start_dot=True, end_arrow=False, bg=CREAM, sub=""):
    im, d, _ = canvas(bg); x0, x1, y = 360, 1560, 600
    d.line([x0, y, x1, y], fill=INK, width=8)
    if start_dot: d.ellipse([x0 - 18, y - 18, x0 + 18, y + 18], fill=INK)
    if end_arrow: d.polygon([(x1, y), (x1 - 40, y - 22), (x1 - 40, y + 22)], fill=INK)
    d.text((W // 2, 470), label, font=font(80), fill=INK, anchor="mm")
    if sub: title(d, sub, y=720, size=44, fill=GREY)
    return im

def timeline_marks(labels, positions, highlight=None, bg=CREAM):
    """labels under tick marks placed at positions 0..1; highlight = index drawn in accent."""
    im, d, _ = canvas(bg); x0, x1, y = 340, 1580, 560
    d.line([x0, y, x1, y], fill=INK, width=8)
    for i, (lab, p) in enumerate(zip(labels, positions)):
        x = x0 + (x1 - x0) * p; col = ORANGE if i == highlight else INK
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=col, outline=INK, width=4)
        d.text((x, y + 80), lab, font=font(40), fill=col, anchor="mm")
    return im

def daynight(labels, bg=PALEBLUE):
    im, d, _ = canvas(bg); x0, x1, y = 340, 1580, 600; pts = []
    for t in range(0, 101): x = x0 + (x1 - x0) * t / 100; pts.append((x, y - 200 * math.sin(math.pi * t / 100)))
    d.line(pts, fill=INK, width=8)
    d.ellipse([x0 - 50, y - 50, x0 + 50, y + 50], fill=ORANGE, outline=INK, width=LW); d.ellipse([x1 - 50, y - 50, x1 + 50, y + 50], fill=SAND, outline=INK, width=LW)
    for i, lab in enumerate(labels):
        x = x0 + (x1 - x0) * i / max(1, len(labels) - 1)
        for yy in range(int(y - 200 * math.sin(math.pi * i / max(1, len(labels) - 1))), y, 18): d.line([x, yy, x, yy + 9], fill=GREY, width=3)
        d.text((x, y + 80), lab, font=font(40), fill=INK, anchor="mm")
    return im

# ---------------- comparisons ----------------
def compare(left, right, icons=(None, None), bg=CREAM, accent_side=None):
    """left/right = (big label, small label). icons = PIL images (any size) pasted in each half, optional."""
    im, d, _ = canvas(bg)
    for yy in range(180, 900, 24): d.line([960, yy, 960, yy + 12], fill=GREY, width=4)
    for k, ((big, small), ic, cx) in enumerate(zip((left, right), icons, (590, 1330))):
        if ic is not None:
            ic = ic.convert("RGBA"); ic.thumbnail((520, 380)); im.paste(ic, (cx - ic.width // 2, 230), ic)
        col = ORANGE if accent_side == k else INK
        d.text((cx, 700), big, font=font(72), fill=col, anchor="mm")
        if small: d.text((cx, 790), small, font=font(40, False), fill=GREY, anchor="mm")
    return im

def pills(items, bg=CREAM, accent_value="YES"):
    """items = [(label, value)]: aligned grey pills (accent when value == accent_value), label under each."""
    im, d, _ = canvas(bg); n = len(items); step = 1200 / n
    for i, (lab, val) in enumerate(items):
        cx = 360 + step * (i + 0.5); col = ORANGE if val == accent_value else LIGHT
        d.rounded_rectangle([cx - 110, 380, cx + 110, 640], 110, fill=col, outline=INK, width=LW)
        d.text((cx, 510), val, font=font(44), fill=INK, anchor="mm"); d.text((cx, 730), lab, font=font(40), fill=INK, anchor="mm")
    return im

# ---------------- timelines and schemas measured on the channel (2nd pass, 30 videos) ----------------
def timeline_bar(label, pos=0.75, sub="", bg=CREAM, marker="tri"):
    """Thick tan bar with a marker at pos (0..1) and the label above it: '8,500 YEARS AGO', '850,000 YEARS AGO'."""
    im, d, _ = canvas(bg); x0, x1, y = 340, 1580, 600
    d.rounded_rectangle([x0, y - 36, x1, y + 36], 20, fill=SAND, outline=INK, width=LW)
    for t in range(1, 10): x = x0 + (x1 - x0) * t / 10; d.line([x, y + 12, x, y + 36], fill=INK, width=3)
    x = x0 + (x1 - x0) * pos
    if marker == "tri": d.polygon([(x, y - 44), (x - 26, y - 90), (x + 26, y - 90)], fill=GREEN if pos < 0.5 else RED, outline=INK)
    else: d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=RED, outline=INK, width=4)
    d.text((x, y - 150), label, font=font(64), fill=INK, anchor="mm")
    if sub: title(d, sub, y=740, size=44, fill=GREY)
    return im

def timeline_arrow(label, direction="right", ticks=8, bg=CREAM, end_label="TODAY"):
    """Thick tan arrow with ticks and the duration above: '2,000,000 YEARS ->' or '<- TODAY'."""
    im, d, _ = canvas(bg); x0, x1, y = 360, 1560, 600; h = 46
    if direction == "right":
        d.rectangle([x0, y - h, x1 - 120, y + h], fill=SAND, outline=INK, width=LW); d.polygon([(x1 - 130, y - 100), (x1, y), (x1 - 130, y + 100)], fill=SAND, outline=INK)
        d.line([x1 - 130, y - 100, x1 - 130, y - h], fill=SAND, width=8); d.line([x1 - 130, y + 100, x1 - 130, y + h], fill=SAND, width=8)
    else:
        d.rectangle([x0 + 120, y - h, x1, y + h], fill=SAND, outline=INK, width=LW); d.polygon([(x0 + 130, y - 100), (x0, y), (x0 + 130, y + 100)], fill=SAND, outline=INK)
        d.line([x0 + 130, y - 100, x0 + 130, y - h], fill=SAND, width=8); d.line([x0 + 130, y + 100, x0 + 130, y + h], fill=SAND, width=8)
    for t in range(1, ticks): x = x0 + 120 + (x1 - x0 - 240) * t / ticks; d.line([x, y + 10, x, y + h], fill=INK, width=4)
    d.text((W // 2, 440), label, font=font(72), fill=INK, anchor="mm")
    if end_label: d.text((x1 - 40 if direction == "right" else x0 + 40, 720), end_label, font=font(44), fill=INK, anchor="rm" if direction == "right" else "lm")
    return im

def timeline_segment(label, a=0.3, b=0.55, bg=CREAM, color=RED, ends=("", "")):
    """Tan bar with one highlighted segment between a and b, bracket + label above: '8 WEEKS'."""
    im, d, _ = canvas(bg); x0, x1, y = 340, 1580, 600
    d.rounded_rectangle([x0, y - 34, x1, y + 34], 34, fill=SAND, outline=INK, width=LW)
    xa, xb = x0 + (x1 - x0) * a, x0 + (x1 - x0) * b
    d.rectangle([xa, y - 30, xb, y + 30], fill=color)
    d.line([xa, y - 70, xa, y - 90, xb, y - 90, xb, y - 70], fill=INK, width=5)
    d.text(((xa + xb) / 2, y - 160), label, font=font(64), fill=INK, anchor="mm")
    for lab, x, anc in ((ends[0], x0, "lm"), (ends[1], x1, "rm")):
        if lab: d.text((x, y + 90), lab, font=font(36), fill=GREY, anchor=anc)
    return im

def arrow_ab(a_img, b_img, top=("", ""), bottom=("", ""), bg=CREAM, color=RED):
    """A -> B with two pictures (PIL images), optional numbers above ('200', '0') and words below."""
    im, d, _ = canvas(bg, card=None)
    for ic, cx in ((a_img, 560), (b_img, 1360)):
        if ic is not None: ic = ic.convert("RGBA"); ic.thumbnail((460, 460)); im.paste(ic, (cx - ic.width // 2, 540 - ic.height // 2), ic)
    d.polygon([(850, 500), (1010, 500), (1010, 450), (1110, 540), (1010, 630), (1010, 580), (850, 580)], fill=color, outline=INK)
    for k, cx in enumerate((560, 1360)):
        if top[k]: d.text((cx, 230), top[k], font=font(84), fill=INK, anchor="mm")
        if bottom[k]: d.text((cx, 860), bottom[k], font=font(44), fill=INK, anchor="mm")
    return im

def balance(left, right, tilt=0.0, bg=CREAM, left_img=None, right_img=None):
    """Balance scale with two labels under the pans; tilt -1..1 (negative = left pan down)."""
    im, d, _ = canvas(bg, card=None); cx, top = 960, 260
    d.rectangle([cx - 14, top, cx + 14, 820], fill=INK); d.rectangle([cx - 160, 820, cx + 160, 850], fill=INK)
    dy = 90 * tilt
    for sx, lab, ic in ((-1, left, left_img), (1, right, right_img)):
        px = cx + sx * 420; py = top + 60 + sx * dy
        d.line([cx, top, px, py], fill=INK, width=8)
        for k in (-110, 110): d.line([px, py, px + k, py + 160], fill=INK, width=5)
        d.chord([px - 150, py + 110, px + 150, py + 230], 0, 180, fill=SAND, outline=INK, width=LW)
        if ic is not None: ic = ic.convert("RGBA"); ic.thumbnail((150, 150)); im.paste(ic, (int(px - ic.width / 2), int(py + 150 - ic.height)), ic)
        d.text((px, py + 300), lab, font=font(56), fill=INK, anchor="mm")
    return im

def cycle(imgs, labels=(), bg=CREAM):
    """Circular arrows with 3 to 5 pictures placed around: a loop, a life cycle, a feedback."""
    im, d, _ = canvas(bg, card=None); cx, cy, r = 960, 560, 300; n = len(imgs)
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=INK, width=12)
    for k in range(n):
        a = math.radians(-90 + 360 * (k + 0.5) / n); ax, ay = cx + r * math.cos(a), cy + r * math.sin(a)
        t = a + math.pi / 2; d.polygon([(ax + 28 * math.cos(t), ay + 28 * math.sin(t)), (ax + 22 * math.cos(a), ay + 22 * math.sin(a)), (ax - 22 * math.cos(a), ay - 22 * math.sin(a))], fill=INK)
    for k, ic in enumerate(imgs):
        a = math.radians(-90 + 360 * k / n); px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([px - 90, py - 90, px + 90, py + 90], fill=CARD, outline=INK, width=LW)
        if ic is not None: ic = ic.convert("RGBA"); ic.thumbnail((130, 130)); im.paste(ic, (int(px - ic.width / 2), int(py - ic.height / 2)), ic)
        if k < len(labels): d.text((px, py + 130), labels[k], font=font(36), fill=INK, anchor="mm")
    return im

def equation(a_n, a_img, b_n, b_img, text, bg=CREAM):
    """Pictogram equation: a_n copies of picture A over b_n copies of picture B, caption '1 STRIDE = 1 BREATH'."""
    im, d, _ = canvas(bg, card=None)
    for row, (n, ic) in enumerate(((a_n, a_img), (b_n, b_img))):
        y = 300 + row * 260; step = min(200, 1400 // max(1, n)); x0 = W // 2 - step * (n - 1) / 2
        for k in range(n):
            if ic is not None: p = ic.convert("RGBA"); p.thumbnail((150, 150)); im.paste(p, (int(x0 + k * step - p.width / 2), int(y - p.height / 2)), p)
    d.text((W // 2, 880), text, font=font(72), fill=INK, anchor="mm")
    return im

def split_compare(left_img, right_img, labels=("", ""), bg=CREAM):
    """Two pictures side by side split by a vertical dotted line (the channel's most frequent schema)."""
    return compare((labels[0], ""), (labels[1], ""), icons=(left_img, right_img), bg=bg)

if __name__ == "__main__":
    from PIL import Image as _I
    _blob = _I.new("RGBA", (200, 200), (0, 0, 0, 0)); ImageDraw.Draw(_blob).ellipse([10, 10, 190, 190], fill=ORANGE, outline=INK, width=8)
    demo = [timeline_bar("8,500 YEARS AGO", 0.8), timeline_arrow("2,000,000 YEARS"), timeline_segment("8 WEEKS", 0.3, 0.55, ends=("BIRTH", "ADULT")),
            arrow_ab(_blob, _blob, top=("200", "0"), bottom=("CALORIES", "LEFT")), balance("RISK", "REWARD", tilt=0.4, left_img=_blob, right_img=_blob),
            cycle([_blob] * 4, ("SLEEP", "EAT", "MOVE", "REST")), equation(4, _blob, 2, _blob, "1 STRIDE = 1 BREATH"), split_compare(_blob, _blob, ("APE", "HUMAN")),bar_ratio("100x", "ROOM AIR", "5% CO2"), bars([("CO2", 40, GREY), ("O2", 42, GREEN), ("EXERCISE", 41, ORANGE)], ref=45),
            pie(20, "CALORIES"), line([0, 1, 1, 2, 2, 5, 9], "WEEK 1", "WEEK 12", color=RED), lines2([9, 7, 4, 2, 1], [9, 8, 7, 6, 5], ("FAST", "SLOW")),
            dots("86 BILLION", "neurons", n=60, icon="*", highlight=12), scatter([(1, 1), (2, 2.2), (3, 2.8), (4, 4.1), (5, 4.8), (6, 6.3), (3.5, 3.2)], "AGE", "RISK"),
            thermo("+0.5°", "brain", 0.7), thermo2(("BIRD", 0.8), ("MAMMAL", 0.5)), hbar_gauge(0.72, label="BODY TEMPERATURE"), dial(0.8),
            timeline("6 MONTHS", sub="before the first word"), timeline_marks(["BIRTH", "6 MO", "2 YR", "ADULT"], [0, 0.25, 0.55, 1], highlight=1),
            daynight(["6 AM", "NOON", "10 PM"]), compare(("FAST", "hare"), ("SLOW", "tortoise"), accent_side=0), pills([("A", "YES"), ("B", "NO"), ("C", "YES")])]
    sheet = Image.new("RGB", (480 * 4, 270 * math.ceil(len(demo) / 4)), "white")
    for i, im in enumerate(demo): sheet.paste(im.resize((480, 270)), ((i % 4) * 480, (i // 4) * 270))
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "charts_demo.jpg"); sheet.save(out, quality=85); print(out)
