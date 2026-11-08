"""Free music bed and real sound effects from Openverse (api.openverse.org: Freesound, Jamendo, Wikimedia...), no key needed.
  python openverse.py "dark ambient drone" --out audio/music --n 4 --length medium    # 2-10 min candidates for music.mp3 (looped; listen, pick one)
  python openverse.py --kit --out ~/sfx-library                                        # the format's SFX kit, one folder per sound kind
  python openverse.py "torch fire crackle" --out ~/sfx-library/fire --n 6               # one more kind
Licence: CC0 by default (no credit, safe for a monetized channel). --license by also takes CC BY: then the credit lines of
credits.csv must go in the description. Never NC or ND (monetized channel, a mixed bed is a modification).
Every download is listed in <out>/credits.csv (file, title, creator, licence, page, attribution sentence).
Anonymous limit measured 7 Nov 2026: 20 requests a minute, 200 a day: the script waits 3.2 s between calls."""
import csv, json, pathlib, re, sys, time, urllib.parse, urllib.request

API = "https://api.openverse.org/v1/audio/"
UA = {"User-Agent": "ancient-humans-video/1.0"}
# kinds of sound this format needs (folder name = the kind Real SFX reads from the path)
KIT = {"whoosh": "whoosh", "hit": "deep impact hit", "riser": "riser", "fire": "fire crackle", "wind": "cave wind howl",
       "rain": "rain on leaves", "thunder": "thunder rumble", "crowd": "crowd murmur", "footsteps": "footsteps dirt",
       "stone": "stone hit rock", "wood": "wooden door creak", "water": "water drip cave", "heartbeat": "heartbeat",
       "paper": "paper scroll unroll", "coin": "coins drop", "animals": "wolf howl night"}

def call(url):
    for wait in (0, 30, 65):
        time.sleep(wait or 3.2)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
    sys.exit("Openverse: rate limit (20/min, 200/day) reached, try again later")

def fetch(query, out, n=5, length=None, license="cc0", max_s=None):
    out.mkdir(parents=True, exist_ok=True)
    q = {"q": query, "license": license, "page_size": min(n * 3, 20), "mature": "false"}   # anonymous Openverse answers 401 above 20 (7 Nov 2026, --kit --n 8)
    if length: q["length"] = length   # shortest <30 s, short 30 s-2 min, medium 2-10 min, long >10 min
    res = json.loads(call(API + "?" + urllib.parse.urlencode(q)))["results"]
    credits = out / "credits.csv"; new = not credits.exists(); got = []
    with open(credits, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new: w.writerow(["file", "title", "creator", "license", "page", "attribution"])
        for r in res:
            if len(got) >= n: break
            if max_s and (r.get("duration") or 0) > max_s * 1000: continue
            if (r.get("filesize") or 0) > 12e6: continue   # the Freesound CDN serves ~75 KB/s: a 37 MB drone took 8 min (7 Nov 2026)
            ext = (r.get("filetype") or "mp3").lower(); name = re.sub(r"[^a-z0-9]+", "-", r["title"].lower()).strip("-")[:40]
            dst = out / f"{name}-{r['id'][:8]}.{ext}"
            if not dst.exists():
                time.sleep(1); dst.write_bytes(urllib.request.urlopen(urllib.request.Request(r["url"], headers=UA), timeout=120).read())
                w.writerow([dst.name, r["title"], r["creator"], f"{r['license']} {r.get('license_version') or ''}".strip(), r["foreign_landing_url"], r["attribution"]]); f.flush()
            got.append(dst); print(f"  {dst.name}  {(r.get('duration') or 0) / 1000:.1f} s  {r['license']}  {r['creator']}")
    print(f"{query!r}: {len(got)} file(s) in {out}"); return got

if __name__ == "__main__":
    a = sys.argv[1:]
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    out = pathlib.Path(opt("--out", "audio")).expanduser(); lic = opt("--license", "cc0")
    if lic not in ("cc0", "by", "cc0,by"): sys.exit("--license: cc0 (default) or by; NC/ND are never safe for a monetized video")
    if "--kit" in a:
        for kind, q in KIT.items(): fetch(q, out / kind, int(opt("--n", 4)), "shortest", lic, max_s=20)
    else:
        query = next(x for x in a if not x.startswith("--") and a[a.index(x) - 1] not in ("--out", "--n", "--length", "--license", "--max-s"))
        fetch(query, out, int(opt("--n", 5)), opt("--length"), lic, float(opt("--max-s")) if "--max-s" in a else None)
