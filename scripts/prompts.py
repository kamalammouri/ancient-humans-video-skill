"""Build Google Flow prompts from a shot list, and lint the shot list for the channel's rhythm rules.

  python prompts.py shots.json [--brief brief.json] [--style ID] [--setting "..."] [--flow-per-min 5] [--ref] [--strict]
      --ref: every prompt with the character also says "the same character as in the reference image": run batch.mjs with REF="<caption>"
      -> prompts.json (for scripts/flow/batch.mjs) + lint report on stdout ; --strict exits 1 on a lint error
  python prompts.py --styles        -> lists the character styles of styles.json

Where the style comes from (first found wins):
  1. --style ID                       (an id of scripts/styles.json)
  2. brief.json                       (written at the pre-production brief, references/brief.md ; "--brief path" to point elsewhere)
       {"style": "stickman-meme", "setting": "a small Antarctic station of three plywood modules on a white plateau",
        "character": {"costume": "wearing a torn parka", "sheet": null}}
       character.sheet, when given, REPLACES the style's character sentence (custom character from the Character designer agent).
  3. "default" of styles.json
Never edit a prompt by hand: the full prefix + character sheet must be in EVERY prompt, Flow has no memory between generations.

shots.json = [ {"i": 1, "sentence": "...", "family": "scene", "scene": "the character stands at a frosted window, back to viewer",
                "composition": "wide", "dark": false, "file": "F01"}, ... ]
  family: scene | icon | schema | metaphor | map | card | chart | title | html   (card/chart/title/html are rendered by code: no prompt;
          html = a hand-drawn insert spec for the hand-drawn-visuals skill, the best-looking option for symbols, numbers, charts, timelines)
  composition (optional, rotated automatically if missing): wide | medium | close | cutaway | overhead | pov
  nochar: true  -> the recurring character sheet is not added (a scene with other people only)
  withchar: true -> adds the character sheet to a metaphor (by default only scenes carry it)
  costume: "..." -> overrides the brief's costume for this shot only (rank or season changes)
  Flow prompts are built only for scene / icon / schema / metaphor / map.
  file: two consecutive shots may share the same "file": one Flow image held over several sentences (built once).
  start (optional, seconds): used for the Flow budget; without it a shot counts 4.5 s.

Render routing: an insert that is one simple symbol (check mark, gift box, arrow bent in a loop, question mark, padlock, coin...)
is refused by the lint (CODE_ICONS): cards.symbol draws it by code. The Render router agent (references/agents.md) makes the same call
for what the word list cannot catch. Flow is for scenes with the character and for objects with texture and light.

Backgrounds: prompts.json ends with BG and BG_DARK (an empty page in the style's insert backgrounds); generated once, they are
the canvas of every code insert (build_slideshow.py reads flow/<dir>/BG.* and BG_DARK.*). --no-bg skips them.

Flow budget (the slow, rate-limited part of production): at most FLOW_PER_MIN Flow images per minute of video
(default 5, i.e. one scene per moment of about 12 s), the other shots rendered by code (card / chart / title) or held.
163 Flow images for 16 min took a whole evening; 80 take 40 minutes. --flow-per-min N changes the budget.
"""
import json, re, sys, itertools, pathlib

HERE = pathlib.Path(__file__).parent
COMPOSITIONS = {
    "wide": "Wide shot, the whole set visible, horizon line low,",
    "medium": "Medium shot, waist up, the set suggested behind,",
    "close": "Close-up on hands and one object, the face out of frame,",
    "cutaway": "Cutaway view as if one wall were removed, the inside drawn like a dollhouse,",
    "overhead": "Overhead view looking straight down,",
    "pov": "First-person point of view, {pov_hands},",
}
FAMILY_TEMPLATE = {
    "scene": "{comp} {scene}. {scene_bg}",
    "icon": "A single isolated object: {scene}. {insert_bg} Thick clean outline, flat fill.",
    "schema": "Simple explanatory diagram: {scene}. {insert_bg} Thin outlines, two or three flat colours, thick coloured arrows where motion matters.",
    "metaphor": "Visual metaphor, drawn literally: {scene}. {insert_bg}",
    "map": "Simple flat map silhouette: {scene}. {insert_bg} One red pin, no place names.",
}
BANNED = ["talking", "talks", "calling", "says", "saying", "speaks", "speaking", "conversation", "sign ", "signs", "label", "poster", "screen showing",
          "reads ", "written", "writing", "text", "clock showing", "gauge reading", "number", "digits", "letters", "caption", "subtitle"]
DATA = {"card", "chart", "map", "html"}; INSERT = {"icon", "schema", "metaphor", "map", "card", "chart", "title", "html"}
# Simple symbols Flow should never be asked for: cards.symbol(icon) draws them exactly, instantly, with no credits.
CODE_ICONS = {"check mark": "check", "checkmark": "check", "tick": "check", "cross mark": "cross", "crossed out": "cross", "red cross": "cross",
              "question mark": "question", "exclamation": "exclamation", "arrow bent": "arrow_loop", "looping arrow": "arrow_loop", "arrow in a loop": "arrow_loop",
              "circular arrow": "arrow_loop", "gift box": "gift", "present box": "gift", "light bulb": "bulb", "lightbulb": "bulb", "padlock": "lock", " lock ": "lock",
              "coin": "coin", "envelope": "envelope", "magnifying glass": "magnifier", "magnifier": "magnifier", "star shape": "star", "single star": "star",
              "an eye": "eye", "open eye": "eye", "flag": "flag", "door": "door", "clock": "clock", "calendar": "calendar", "heart shape": "heart", "key": "key",
              "thermometer": "thermo", "battery": "battery", "hourglass": "hourglass", "flame": "fire", "candle": "fire", "sun": "sun", "moon": "moon", "pill": "pills"}

def code_candidate(s):
    """A Flow insert that a code symbol replaces: short text, no character, one object among CODE_ICONS. Returns the icon name or None."""
    if s["family"] not in ("icon", "metaphor", "schema") or s.get("withchar"): return None
    low = " " + s.get("scene", "").lower() + " "
    if len(low.split()) > 14 or " character" in low or " figure" in low or " hand" in low: return None
    hits = [v for k, v in CODE_ICONS.items() if k in low]
    return hits[0] if len(set(hits)) == 1 else None

def tokens(s): return set(re.findall(r"[a-z]{4,}", s.lower()))

def arg_value(args, flag):
    return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else None

def load_styles(): return json.load(open(HERE / "styles.json", encoding="utf-8"))

def resolve_style(args=()):
    """Merge styles.json + brief.json + command line into one STYLE dict (see module doc)."""
    cfg = load_styles(); brief = {}
    bp = pathlib.Path(arg_value(args, "--brief") or "brief.json")
    if bp.exists(): brief = json.load(open(bp, encoding="utf-8"))
    sid = arg_value(args, "--style") or brief.get("style") or cfg["default"]
    if sid not in cfg["styles"]: sys.exit(f"unknown style '{sid}'. Known: {', '.join(cfg['styles'])}  (python prompts.py --styles)")
    st = dict(cfg["styles"][sid]); st["id"] = sid
    ch = brief.get("character") or {}
    if ch.get("sheet"): st["character"] = ch["sheet"]
    st["costume"] = ch.get("costume") or st.get("costume", "")
    setting = arg_value(args, "--setting") or brief.get("setting") or ""
    st["setting"] = ("Setting: " + setting.rstrip(". ") + ".") if setting and not setting.lower().startswith("setting:") else setting
    return st

def character_sentence(st, costume=None):
    return re.sub(r"\s+", " ", st["character"].replace("{costume}", costume if costume is not None else st["costume"])).replace(" ,", ",").strip()

FLOW_PER_MIN = 10

def flow_budget(shots, per_min=FLOW_PER_MIN):
    """(flow images, minutes, budget): a Flow image is one distinct file among scene/icon/schema/metaphor/map shots."""
    files = {s.get("file") or f"F{s['i']:03d}" for s in shots if s["family"] in FAMILY_TEMPLATE}
    starts = [s["start"] for s in shots if isinstance(s.get("start"), (int, float))]
    minutes = ((max(starts) + 5) if starts else len(shots) * 4.5) / 60
    return len(files), minutes, int(per_min * minutes)

def lint(shots, data_every=14, per_min=FLOW_PER_MIN):
    errs, warns = [], []
    n, minutes, budget = flow_budget(shots, per_min)
    if n > budget: errs.append(f"{n} Flow images for {minutes:.1f} min, budget {budget} ({per_min}/min): hold one scene over consecutive sentences (same \"file\"), or turn icons and schemas into code cards/charts")
    elif n > budget * 0.8: warns.append(f"{n} Flow images for {minutes:.1f} min, close to the budget of {budget}")
    run, prev = 0, None
    for k, s in enumerate(shots):
        fam = s["family"]
        if fam == "scene": run += 0 if s.get("file") and s.get("file") == prev else 1   # 2-3 framings of one image are one scene, not three
        else: run = 0
        prev = s.get("file")
        if run == 4: errs.append(f"#{s['i']}: 4 distinct scene images in a row, insert an icon, schema or data visual before")
        if fam in FAMILY_TEMPLATE:
            low = " " + s.get("scene", "").lower() + " "
            hit = [b for b in BANNED if b in low]
            if hit: errs.append(f"#{s['i']}: banned words {hit} in scene text (they trigger bubbles or text)")
            if not s.get("scene"): errs.append(f"#{s['i']}: empty scene description")
        if k > 0 and fam in DATA and shots[k - 1]["family"] in DATA: warns.append(f"#{s['i']}: two data visuals in a row, put a scene between")
        for j in range(max(0, k - 10), k):
            o = shots[j]
            if o.get("file") and o.get("file") == s.get("file"): continue      # same image, another "frame": not a duplicate
            if o["family"] == fam and fam in FAMILY_TEMPLATE and o.get("composition") == s.get("composition"):
                a, b = tokens(o.get("scene", "")), tokens(s.get("scene", ""))
                if a and b and len(a & b) / len(a | b) > 0.6: warns.append(f"#{s['i']}: near-duplicate of #{o['i']} (same composition, same words)")
    last = -1
    for k, s in enumerate(shots):
        if s["family"] in DATA | {"chart"}: last = k
        elif k - last > data_every: warns.append(f"#{s['i']}: {k - last} shots since the last data visual (max {data_every})"); last = k
    simple = [(s["i"], code_candidate(s)) for s in shots if code_candidate(s)]
    for i, ic in simple: errs.append(f"#{i}: a simple symbol, render it by code instead of Flow: {{\"family\": \"card\", \"card\": {{\"fn\": \"symbol\", \"args\": [\"{ic}\", \"<caption or empty>\"]}}}}")
    cards_without = [s["i"] for s in shots if s["family"] == "card" and not s.get("card", {}).get("icon")]
    if cards_without: errs.append(f"cards without an icon: {cards_without} (use cards.card with an icon)")
    return errs, warns

REF = False   # set by --ref: the batch attaches the character image as an ingredient, the prompt points to it

def build(shots, st):
    out, comps, seen = [], itertools.cycle(["wide", "medium", "close", "cutaway", "overhead", "pov"]), set()
    for s in shots:
        fam = s["family"]
        if fam not in FAMILY_TEMPLATE: continue
        f = s.get("file") or f"F{s['i']:03d}"
        if f in seen: continue                      # the same image held over several sentences
        seen.add(f)
        comp = s.get("composition") or (next(comps) if fam == "scene" else "")
        dark = bool(s.get("dark"))
        body = FAMILY_TEMPLATE[fam].format(comp=COMPOSITIONS.get(comp, "").format(pov_hands=st["pov_hands"]), scene=s["scene"].rstrip("."),
                                           scene_bg=st["dark_scene_bg"] if dark else (st.get("scene_bg_nochar", st["scene_bg"]) if s.get("nochar") else st["scene_bg"]),
                                           insert_bg=st["dark_insert_bg"] if dark else st["insert_bg"])
        with_char = (fam == "scene" and not s.get("nochar")) or (fam == "metaphor" and s.get("withchar"))
        ref = "The same character as in the reference image, exactly the same design, same head, same clothes." if (with_char and REF) else ""
        prefix = st["prefix"] if fam == "scene" else st.get("insert_prefix", st["prefix"])
        parts = [prefix, character_sentence(st, s.get("costume")) if with_char else "", ref, st["setting"] if fam == "scene" else "", body,
                 st["dark"] if dark else "", st["suffix"]]
        out.append({"file": s.get("file") or f"F{s['i']:03d}", "i": s["i"], "family": fam, "prompt": re.sub(r"\s+", " ", " ".join(p for p in parts if p)).strip()})
    return out

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--styles" in args:
        cfg = load_styles()
        for sid, st in cfg["styles"].items(): print(f"{sid:18s} {'(default) ' if sid == cfg['default'] else ''}{st['label']}")
        sys.exit(0)
    src = next((a for a in args if not a.startswith("--") and (args.index(a) == 0 or args[args.index(a) - 1] not in ("--brief", "--style", "--setting"))), "shots.json")
    shots = json.load(open(src, encoding="utf-8"))
    for k, s in enumerate(shots):                 # a shot that reuses the previous shot's "file" (another "frame" of the same image)
        if k and s.get("file") and s.get("file") == shots[k - 1].get("file") and not s.get("scene"):   # inherits its description
            for key in ("scene", "composition", "dark", "nochar", "withchar", "costume"):
                if key in shots[k - 1] and key not in s: s[key] = shots[k - 1][key]
    st = resolve_style(args)
    per_min = float(arg_value(args, "--flow-per-min") or FLOW_PER_MIN)
    globals()["REF"] = "--ref" in args
    errs, warns = lint(shots, per_min=per_min)
    for e in errs: print("ERROR ", e)
    for w in warns: print("warn  ", w)
    prompts = build(shots, st)
    if "--no-bg" not in args:           # two backgrounds, generated once: the code inserts are drawn on them (build_slideshow.py)
        for f, bg, dark in (("BG", st["insert_bg"], ""), ("BG_DARK", st["dark_insert_bg"], st["dark"])):
            prompts.append({"file": f, "i": 0, "family": "background", "prompt": re.sub(r"\s+", " ", " ".join(x for x in (
                st.get("insert_prefix", st["prefix"]), "An empty page: " + bg, "nothing drawn at all, no object, no character, only the paper and its light.", dark, st["suffix"]) if x)).strip()})
    json.dump(prompts, open("prompts.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    fams = {}
    for s in shots: fams[s["family"]] = fams.get(s["family"], 0) + 1
    print(f"{len(prompts)} Flow prompts written to prompts.json | style: {st['id']} | setting: {st['setting'] or '(none)'} | families: {fams} | {len(errs)} errors, {len(warns)} warnings")
    if "--strict" in args and errs: sys.exit(1)
