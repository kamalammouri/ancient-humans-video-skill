"""Builds shots.json from script.md for the Ancient Humans Video format: one line of script.md = one shot, zipped with SPECS below.
Copy this file next to script.md, fill SPECS (one list per "## Chapter N — title" block, same number of entries as lines), then:
  python make_shots.py  -> shots.json + chapters.json (first shot of each chapter) + files.json (key -> Flow file F001, F002...)
  python <skill>/scripts/prompts.py shots.json --flow-per-min 10   (lint + Flow prompts)

The reference channel cuts every 2 s with every image moving: a sentence that must carry two shots is split over two lines of
script.md, and one generated image serves 2-3 consecutive shots with different framings:
  S("door", "the character in a modern bedroom at night, hand on the door key, one warm lamp, blue window light", "medium", dark=True)
  R("door", "zoom")        # same image, tighter framing       R("door", "pan-left")   # same image, the frame slides
Helpers: S(key, scene, composition, dark, nochar, costume, frame) scene with the hero (nochar=True: without him);
         M(key, kind, scene, composition, dark) kind = metaphor | icon | schema | map (no hero);   R(key, frame) reuse of a key;
         H(spec, dark) hand-drawn insert for hand-drawn-visuals (card, timeline, title, symbol, compare, list);   T(title, sub) title card.
frame = wide | zoom | zoom-out | pan-left | pan-right | left | right (build_slideshow.py --motion-all).
"""
import json, re, pathlib
HERE = pathlib.Path(__file__).parent

def S(key, scene, comp="wide", dark=False, nochar=False, costume=None, frame="wide"):
    d = {"family": "scene", "key": key, "scene": scene, "composition": comp, "dark": dark, "frame": frame}
    if nochar: d["nochar"] = True
    if costume: d["costume"] = costume
    return d
def M(key, kind, scene, comp=None, dark=False, frame="wide"):
    d = {"family": kind, "key": key, "scene": scene, "dark": dark, "frame": frame}
    if comp: d["composition"] = comp
    return d
def R(key, frame="zoom"): return {"family": "reuse", "key": key, "frame": frame}
def H(spec, dark=False): return {"family": "html", "html": spec, "dark": dark}
def T(title, sub=None): return H({"type": "title", "title": title, **({"sub": sub} if sub else {})})

BEDROOM = "the character standing in a small modern bedroom at night, one hand on the door key, one warm bedside lamp, blue window light"

SPECS = {   # example: chapter 1 of the reference video "privacy" (parts 1 + 2 of the script template); replace with your own
 1: [
  S("door", BEDROOM, "medium", dark=True),                     # Try getting up right now, closing your door, turning the key in the lock twice, and turning off the light.
  R("door", "zoom"),                                           # Listen closely to the sound of that lock clicking and feel the quiet and isolation that follows.
  S("alone", "the character alone in the dark bedroom seen from above, a thin line of light under the door", "overhead", dark=True),   # In this moment, you have done something almost impossible.
  M("void", "metaphor", "a tiny glowing bedroom floating alone in a vast black void, the rest of the planet fading to dark around it"),   # You have wiped out the entire world with a flick of your hand.
  R("void", "zoom-out"),                                       # No eyes are watching you, no ears are hearing how you breathe.
  S("walls", "the same bedroom with its four walls dissolving into dust, revealing a dark cave behind", "wide", dark=True),   # But if we go back in time, and remove these four walls, and remove the door and the key.
  R("walls", "pan-right"),                                     # You will be shocked by a terrifying truth.
  H({"type": "card", "icon": "hourglass", "big": "200,000", "small": "years without a door", "layout": "left", "colour": "terra"}),   # For more than two hundred thousand years, isolation was not a luxury.
  T("ISOLATION MEANT DEATH"),                                  # Isolation meant. Death.
  S("cave-night", "the character at the mouth of a cave at night, a tribe huddled around a fire behind him, pairs of yellow eyes shining in the dark forest", "wide", dark=True),   # So, how was it before we invented bricks, doors, and locks?
  R("cave-night", "zoom"),                                     # Where would ancient humans escape to, when they needed just five minutes to themselves?
 ],
}

def chapters():
    text = (HERE / "script.md").read_text(encoding="utf-8")
    out = []
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        head, *lines = block.strip().splitlines()
        if not head.lower().startswith("chapter"): continue      # "## Sources for the description" and other notes are not spoken
        m = re.match(r"Chapter (\d+) — (.+)", head)
        assert m, f"bad chapter header: {head!r} (expected '## Chapter N — title')"
        lines = [l for l in lines if not l.strip().startswith("<!--")]   # reviewer comments are not spoken
        out.append((int(m.group(1)), m.group(2).strip(), [l.strip() for l in lines if l.strip()]))
    return out

def main():
    shots, chap_index, files, last = [], [], {}, {}
    for num, title, lines in chapters():
        specs = SPECS[num]
        assert len(specs) == len(lines), f"chapter {num}: {len(lines)} lines but {len(specs)} specs"
        chap_index.append({"chapter": num, "title": title, "shot": len(shots) + 1})
        for line, spec in zip(lines, specs):
            if spec["family"] == "reuse":                                   # another framing of an image already described
                s = {**last[spec["key"]], "i": len(shots) + 1, "sentence": line, "frame": spec["frame"]}
            else:
                s = {"i": len(shots) + 1, "sentence": line, "family": spec["family"]}
                if "key" in spec:
                    files.setdefault(spec["key"], f"F{len(files) + 1:03d}")
                    s["file"] = files[spec["key"]]; s["scene"] = spec["scene"]; s["frame"] = spec.get("frame", "wide")
                    for k in ("composition", "nochar", "costume"):
                        if spec.get(k): s[k] = spec[k]
                    last[spec["key"]] = s
                if spec["family"] == "html": s["html"] = spec["html"]
                if spec.get("dark"): s["dark"] = True
            shots.append(s)
    (HERE / "shots.json").write_text(json.dumps(shots, indent=1, ensure_ascii=False), encoding="utf-8")
    (HERE / "files.json").write_text(json.dumps(files, indent=1), encoding="utf-8")
    (HERE / "chapters.json").write_text(json.dumps(chap_index, indent=1, ensure_ascii=False), encoding="utf-8")
    fam = {}
    for s in shots: fam[s["family"]] = fam.get(s["family"], 0) + 1
    reused = sum(1 for s in shots if s.get("file")) - len(files)
    print(f"{len(shots)} shots, {len(files)} Flow images (+{reused} reused framings), families {fam}")

if __name__ == "__main__":
    main()
