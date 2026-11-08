"""Event list for Real SFX (~/.claude/skills/real-sfx) from shots.json: few sounds, only where the picture changes kind.
  python sfx_cues.py shots.json > work/sfx_events.json
  kinetic title card -> whoosh (0.7 s) on the cut; number card, comparison, bar, timeline -> hit; symbol card -> pop.
Scenes get nothing: the voice carries them, and one sound every 2 s turns a documentary into a game show.
Real SFX then picks real recordings from the library (openverse.py --kit) and places them frame-exact (SKILL.md §5)."""
import json, sys

KIND = {"title": ("whoosh", 0.7), "card": ("hit", None), "compare": ("hit", None), "bar": ("hit", None),
        "timeline": ("hit", None), "list": ("pop", None), "symbol": ("pop", None)}

shots = json.load(open(sys.argv[1], encoding="utf-8")); shots = shots["shots"] if isinstance(shots, dict) else shots
ev, last = [], -9.0
for s in shots:
    k = KIND.get((s.get("html") or {}).get("type")) if s.get("family") == "html" else None
    if not k or "start" not in s or s["start"] - last < 4: continue   # at most one sound per 4 s
    e = {"t": round(s["start"] + (0 if k[0] == "whoosh" else 0.12), 3), "type": k[0]}
    if k[1]: e["len"] = k[1]
    ev.append(e); last = s["start"]
json.dump(ev, sys.stdout); print(f"\n{len(ev)} events", file=sys.stderr)
