"""Channel /videos pages in the lockupViewModel layout. python yt_scan2.py url..."""
import json, re, sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from yt_scan import fetch, initial, walk

for url in sys.argv[1:]:
    print("=" * 70); print(url)
    d = initial(fetch(url))
    sub = [t for t in re.findall(r'"content":\s*"([^"]{2,40})"', json.dumps(next(walk(d, "pageHeaderViewModel"), {}))) if "subscriber" in t or "abonn" in t or "video" in t]
    print("header:", " | ".join(sub[:3]))
    n = 0
    for l in walk(d, "lockupViewModel"):
        vid = l.get("contentId"); meta = l.get("metadata", {}).get("lockupMetadataViewModel", {})
        title = meta.get("title", {}).get("content", "")
        parts = [p.get("text", {}).get("content", "") for row in meta.get("metadata", {}).get("contentMetadataViewModel", {}).get("metadataRows", []) for p in row.get("metadataParts", [])]
        dur = next((b.get("thumbnailBadgeViewModel", {}).get("text", "") for o in l.get("contentImage", {}).get("thumbnailViewModel", {}).get("overlays", []) for b in o.get("thumbnailBottomOverlayViewModel", {}).get("badges", [])), "")
        if title: n += 1; print(f"- {title} | {' | '.join(p for p in parts if p)} | {dur} | {vid}")
    print(n, "videos")
