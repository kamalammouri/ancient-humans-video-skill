"""Details of watch pages: title, views, length, description, chapters, caption transcript (word count + first words). python yt_video.py id..."""
import json, re, sys, urllib.request
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from yt_scan import fetch, initial

for vid in sys.argv[1:]:
    print("=" * 70)
    h = fetch("https://www.youtube.com/watch?v=" + vid)
    p = initial(h, "ytInitialPlayerResponse") or {}
    d = p.get("videoDetails", {})
    print(f"{d.get('title')} | {d.get('author')} | views {d.get('viewCount')} | {int(d.get('lengthSeconds', 0)) // 60}:{int(d.get('lengthSeconds', 0)) % 60:02d}")
    desc = d.get("shortDescription", "")
    print("DESC:", desc[:1600].replace("\n", " / "))
    tracks = p.get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])
    en = next((t for t in tracks if t.get("languageCode", "").startswith("en")), tracks[0] if tracks else None)
    if en:
        try:
            xml = urllib.request.urlopen(urllib.request.Request(en["baseUrl"] + "&fmt=json3", headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode()
            ev = json.loads(xml).get("events", [])
            words = " ".join(s.get("utf8", "") for e in ev for s in e.get("segs", [])).replace("\n", " ")
            n = len(words.split()); L = int(d.get("lengthSeconds", 1))
            print(f"TRANSCRIPT: {n} words, {n * 60 // L} wpm, kind={en.get('kind', 'manual')}")
            print("FIRST 120 WORDS:", " ".join(words.split()[:120]))
            print("LAST 60 WORDS:", " ".join(words.split()[-60:]))
        except Exception as e: print("transcript failed:", e)
    else: print("no captions")
