"""Scan YouTube channel /videos pages and one watch page through ytInitialData (no API key). python yt_scan.py url..."""
import json, re, sys, urllib.request

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.8",
                                               "Cookie": "CONSENT=YES+cb; SOCS=CAISNQgDEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjMwODI5LjA3X3AxGgJlbiACGgYIgLC_pwY"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

def initial(html, key="ytInitialData"):
    m = re.search(key + r"\s*=\s*(\{.*?\});\s*</script>", html, re.S)
    return json.loads(m.group(1)) if m else None

def walk(o, key):
    if isinstance(o, dict):
        if key in o: yield o[key]
        for v in o.values(): yield from walk(v, key)
    elif isinstance(o, list):
        for v in o: yield from walk(v, key)

def txt(o):
    if not o: return ""
    if "simpleText" in o: return o["simpleText"]
    return "".join(r.get("text", "") for r in o.get("runs", []))

if __name__ == "__main__":
    import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    for url in sys.argv[1:]:
        print("=" * 80); print(url)
        try: html = fetch(url)
        except Exception as e: print("fetch failed:", e); continue
        d = initial(html)
        if not d: print("no ytInitialData"); continue
        if "/watch" in url:
            p = initial(html, "ytInitialPlayerResponse") or {}
            vd = p.get("videoDetails", {})
            print("title:", vd.get("title"), "| channel:", vd.get("author"), "| views:", vd.get("viewCount"), "| length s:", vd.get("lengthSeconds"))
            print("description:", (vd.get("shortDescription") or "")[:1500])
            continue
        hdr = next(walk(d, "pageHeaderViewModel"), None) or {}
        meta = " | ".join(t for t in re.findall(r'"content":"([^"]{2,60})"', json.dumps(hdr)) if "subscriber" in t or "video" in t or "abonn" in t)[:300]
        print("header:", meta)
        about = next(walk(d, "descriptionPreviewViewModel"), None)
        if about: print("about:", json.dumps(about)[:300])
        vids = list(walk(d, "videoRenderer")) + list(walk(d, "richItemRenderer"))
        seen = set()
        for v in list(walk(d, "videoRenderer")):
            vid = v.get("videoId")
            if vid in seen: continue
            seen.add(vid)
            print(f"- {txt(v.get('title'))} | {txt(v.get('viewCountText'))} | {txt(v.get('publishedTimeText'))} | {txt(v.get('lengthText'))}")
        print(len(seen), "videos listed")
