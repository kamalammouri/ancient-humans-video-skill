"""YouTube keyword and packaging research for a US audience, with free sources only.
  python keywords.py "how did cavemen sleep" "ancient humans sleep" [--n 25] [--out keywords.md]
Sources: (1) YouTube autocomplete (gl=US, hl=en): the seed, then seed + " " + each modifier (why, how, what, first, before,
ancient, history, explained, documentary, facts, vs, a..z); (2) YouTube search results via yt-dlp ("ytsearchN:<query>"),
with views, duration, channel -> which titles the niche rewards right now.
Output (markdown): suggestions ranked by how many queries produced them, the top results by views with their title
patterns, and a ready list of tag candidates. yt-dlp needs a JS runtime: --js-runtimes node is passed.
"""
import json, re, subprocess, sys, urllib.parse, urllib.request, datetime, collections

UA = {"User-Agent": "Mozilla/5.0"}
MODS = ["why", "how", "what", "when", "first", "before", "ancient", "history", "explained", "documentary", "facts", "secret",
        "real", "actually", "vs", "night", "every day"] + list("abcdefghijklmnopqrstuvwxyz")

def suggest(q):
    url = "https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&gl=US&hl=en&q=" + urllib.parse.quote(q)
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=10).read().decode("utf-8", "replace")
        return json.loads(raw)[1]
    except Exception:
        return []

def search(q, n):
    r = subprocess.run(["yt-dlp", "--js-runtimes", "node", "--flat-playlist", "-J", f"ytsearch{n}:{q}"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    try: return json.loads(r.stdout).get("entries", [])
    except Exception: return []

def main():
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 25
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    skip = {str(n), out}
    seeds = [a for a in sys.argv[1:] if not a.startswith("--") and a not in skip]
    lines = [f"# Keyword research (US) — {', '.join(seeds)} — {datetime.date.today()}"]
    counter, examples = collections.Counter(), {}
    for s in seeds:
        for q in [s] + [f"{s} {m}" for m in MODS]:
            for sug in suggest(q):
                if re.search(r"(hindi|urdu|tamil|telugu|bangla|bengali|malayalam|kannada|marathi|punjabi|arabic|reaction|reacts?|shorts?|zenn|mr\.? hell)", sug.lower()): continue   # other languages, reaction videos, channel names
                counter[sug.lower()] += 1; examples.setdefault(sug.lower(), q)
    lines.append("\n## 1. What Americans type (YouTube autocomplete, gl=US)\n\n| Suggestion | Queries that produce it |\n|---|---|")
    for sug, c in counter.most_common(60): lines.append(f"| {sug} | {c} |")
    lines.append("\n## 2. What the search page rewards (sorted by views)\n")
    rows = []
    for s in seeds:
        for e in search(s, n):
            v = e.get("view_count") or 0; d = e.get("duration") or 0; t = e.get("title") or ""
            rows.append({"seed": s, "title": t, "views": v, "dur": int(d), "channel": e.get("channel") or e.get("uploader") or "", "id": e.get("id")})
    seen = set(); rows = [r for r in rows if not (r["id"] in seen or seen.add(r["id"]))]
    rows.sort(key=lambda r: -r["views"])
    lines.append("| Views | Length | Channel | Title |\n|---|---|---|---|")
    for r in rows[:40]: lines.append(f"| {r['views']:,} | {r['dur']//60}:{r['dur']%60:02d} | {r['channel'][:28]} | {r['title']} |")
    tt = [r["title"] for r in rows[:40]]
    openers = collections.Counter(" ".join(t.split()[:2]).lower() for t in tt)
    qs = sum(1 for t in tt if "?" in t); nums = sum(1 for t in tt if re.search(r"\d", t)); avg = sum(len(t) for t in tt) / max(1, len(tt))
    lines.append(f"\n## 3. Title patterns in the top 40\n\n- questions: {qs}/{len(tt)} · with a number: {nums}/{len(tt)} · average length: {avg:.0f} characters")
    lines.append("- most common openers: " + ", ".join(f"« {o} » ×{c}" for o, c in openers.most_common(8)))
    tags = [s for s, _ in counter.most_common(40)][:20]
    lines.append("\n## 4. Tag candidates (≤ 500 characters in Studio)\n\n" + ", ".join(tags))
    lines.append(f"\n(total: {len(', '.join(tags))} characters)")
    text = "\n".join(lines)
    if out: open(out, "w", encoding="utf-8").write(text); print(f"-> {out}")
    else: print(text)

if __name__ == "__main__":
    main()
