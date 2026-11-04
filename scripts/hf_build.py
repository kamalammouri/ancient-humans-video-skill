"""Build a HyperFrames project (HTML rendered to video) from shots.json + voice: animated captions and motion-design titles.

  python hf_build.py shots.json voice.wav timing.json <project_dir> [--flow flow/<video>] [--music music.mp3]
                     [--transcript assets/transcript.json] [--no-captions] [--accent "#F2C446"]
  then: npx hyperframes check <project_dir> --json ; npx hyperframes preview <project_dir> ; npx hyperframes render <project_dir>

What it writes (the HyperFrames contract, references/format.md of the hyperframes skill):
  index.html                 root composition: one scene host per chapter (data-track-kind="graphics"), one captions host
                             (data-track-kind="captions"), <audio id="voice">, optional <audio id="music">
  compositions/chN.html      one .clip per shot, hard cuts; the image sits in a .kb wrapper that GSAP zooms/pans by "frame"
                             (wide | zoom | zoom-out | pan-left | pan-right | left | right); "title" shots are kinetic
                             typography (words blur in 0.067 s apart, accent on the last word, dead still, blur out)
  compositions/captions.html one group of 3-5 words per .clip, active word popped in the accent colour, hard kill at the end
  assets/                    F###.png copied, cards/charts/html inserts rendered by build_slideshow.render, voice.wav, music
Word timings: --transcript (hyperframes transcribe / whisper: [{text,start,end}]) ; else derived from an ElevenLabs
timing.json ({"chars","end"} per character) ; else words spread evenly inside each sentence. Shot starts: shots[].start,
else timing.json as a list of sentence starts.
"""
import json, os, pathlib, re, shutil, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import build_slideshow as bs

W, H = 1920, 1080
FRAMES = {   # (scale from, scale to, x from, x to) in px of the 1920 canvas; y stays centred
    "wide": (1.00, 1.07, 0, 0), "zoom": (1.15, 1.30, 0, 0), "zoom-out": (1.30, 1.10, 0, 0),
    "pan-left": (1.20, 1.20, 192, -192), "pan-right": (1.20, 1.20, -192, 192),
    "left": (1.25, 1.29, 240, 240), "right": (1.25, 1.29, -240, -240),
}

def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def words_from_eleven(timing):
    """ElevenLabs with-timestamps: one end time per character of the voiced text -> word timings."""
    chars, end = timing["chars"], timing["end"]; out = []; k = 0
    while k < len(chars):
        if chars[k].isspace(): k += 1; continue
        j = k
        while j < len(chars) and not chars[j].isspace(): j += 1
        out.append({"text": chars[k:j], "start": end[k - 1] if k else 0.0, "end": end[j - 1]}); k = j
    return out

def words_even(shots, starts, ends):
    out = []
    for s, a, b in zip(shots, starts, ends):
        ws = s["sentence"].split(); step = (b - a) / max(1, len(ws))
        for n, w in enumerate(ws): out.append({"text": w, "start": a + n * step, "end": a + (n + 1) * step - 0.02})
    return out

def groups(words, max_words=4):
    """3-5 words per group: break at sentence end, a pause >= 150 ms, or max_words."""
    gs, cur = [], []
    for w in words:
        if cur and (len(cur) >= max_words or (w["start"] - cur[-1]["end"]) >= 0.15 or re.search(r"[.!?]$", cur[-1]["text"])):
            gs.append(cur); cur = []
        cur.append(w)
    if cur: gs.append(cur)
    return gs

def kb_tween(sel, frame, start, dur):
    s0, s1, x0, x1 = FRAMES.get(frame, FRAMES["wide"])
    return f'tl.fromTo("{sel}", {{scale: {s0}, x: {x0}, y: 0}}, {{scale: {s1}, x: {x1}, y: 0, duration: {dur:.3f}, ease: "none"}}, {start:.3f});'

def chapter_scene(cid, shots_in, t0, assets_rel, accent):
    """One scene file: local clock starts at the chapter's first shot."""
    clips, tw = [], []
    for z, (s, a, b) in enumerate(shots_in, 1):
        st, du = a - t0, max(b - a, 0.4); sid = f"{cid}-s{s['i']}"
        if s["family"] == "title":
            ws = s["title"].split()
            spans = "".join(f'<span class="w">{esc(w)}</span> ' for w in ws[:-1]) + f'<span class="w acc">{esc(ws[-1])}</span>'
            clips.append(f'<div id="{sid}" class="clip title" data-start="{st:.3f}" data-duration="{du:.3f}" style="z-index:{z}"><div class="tt"><h1>{spans}</h1></div></div>')
            tw.append(f'tl.fromTo("#{sid} .w", {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power4.out", stagger: 0.067}}, {st + 0.1:.3f});')
            tw.append(f'tl.to("#{sid} .tt", {{opacity: 0, filter: "blur(6px)", duration: 0.15, ease: "power3.in"}}, {st + du - 0.16:.3f});')
        else:
            clips.append(f'<div id="{sid}" class="clip" data-start="{st:.3f}" data-duration="{du:.3f}" style="z-index:{z}"><div class="kb"><img src="{assets_rel[s["i"]]}" alt=""></div></div>')
            if s["family"] not in ("card", "chart", "html"): tw.append(kb_tween(f"#{sid} .kb", s.get("frame", "wide"), st, du))
    return f"""<template>
<style>
#root {{ position: absolute; inset: 0; background: #0b0f1a; overflow: hidden; }}
.clip {{ position: absolute; inset: 0; }}
.kb {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
.kb img {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
.title .tt {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; text-align: center; padding: 0 160px; }}
.title h1 {{ font-family: Oswald, Inter, sans-serif; font-weight: 700; font-size: 128px; line-height: 1.05; color: #fff; letter-spacing: 0.02em; text-transform: uppercase; text-shadow: 0 6px 24px rgba(0,0,0,.6); margin: 0; }}
.title .acc {{ color: {accent}; }}
</style>
<div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
{chr(10).join(clips)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tw)}
window.__timelines["{cid}"] = tl;
</script>
</template>
"""

def captions_scene(gs, accent):
    clips, tw = [], []
    for n, g in enumerate(gs, 1):
        a, b = max(0.1, g[0]["start"]), g[-1]["end"] + 0.08; gid = f"cap{n}"
        spans = " ".join(f'<span class="cw" id="{gid}w{k}">{esc(w["text"])}</span>' for k, w in enumerate(g))
        clips.append(f'<div id="{gid}" class="clip cg" data-start="{a:.3f}" data-duration="{b - a:.3f}" style="z-index:{n}"><p>{spans}</p></div>')
        tw.append(f'tl.fromTo("#{gid} p", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.14, ease: "power3.out"}}, {a:.3f});')
        for k, w in enumerate(g):
            tw.append(f'tl.fromTo("#{gid}w{k}", {{scale: 1, color: "#ffffff"}}, {{scale: 1.08, color: "{accent}", duration: 0.08, ease: "power2.out"}}, {max(a, w["start"]):.3f});')
        tw.append(f'tl.to("#{gid} p", {{opacity: 0, duration: 0.12, ease: "power2.in"}}, {b - 0.12:.3f});')
        tw.append(f'tl.set("#{gid} p", {{opacity: 0, visibility: "hidden"}}, {b:.3f});')   # hard kill on the inner block, never on the .clip
    return f"""<template>
<style>
#root {{ position: absolute; inset: 0; }}
.cg {{ position: absolute; left: 0; right: 0; bottom: 96px; text-align: center; overflow: visible; }}
.cg p {{ display: inline-block; margin: 0; padding: 10px 28px; border-radius: 14px; background: rgba(0,0,0,.35); font-family: Inter, sans-serif; font-weight: 800; font-size: 56px; line-height: 1.2; color: #fff; text-shadow: 0 2px 0 #000, 0 0 12px rgba(0,0,0,.8); }}
.cw {{ display: inline-block; margin: 0 0.14em; transform-origin: 50% 80%; }}
</style>
<div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}">
{chr(10).join(clips)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tw)}
window.__timelines["captions"] = tl;
</script>
</template>
"""

def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--") and (sys.argv[sys.argv.index(x) - 1] not in ("--flow", "--music", "--transcript", "--accent"))]
    opt = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    shots_f, voice, timing_f, proj = a[0], a[1], a[2], pathlib.Path(a[3])
    flow_dir = pathlib.Path(opt("--flow", "flow")); music = opt("--music"); accent = opt("--accent", "#F2C446")
    shots = json.load(open(shots_f, encoding="utf-8")); timing = json.load(open(timing_f, encoding="utf-8"))
    starts = bs.starts_from_timing(shots, timing)
    FF = bs.imageio_ffmpeg.get_ffmpeg_exe()
    hh, mm, ss = subprocess.run([FF, "-i", voice], capture_output=True, text=True).stderr.split("Duration: ")[1].split(",")[0].split(":")
    dur = 3600 * int(hh) + 60 * int(mm) + float(ss); ends = starts[1:] + [dur]
    (proj / "compositions").mkdir(parents=True, exist_ok=True); (proj / "assets").mkdir(exist_ok=True)
    shutil.copy(voice, proj / "assets" / "voice.wav")
    # images: Flow files copied once, inserts rendered by build_slideshow.render (cards/charts/html on the paper background)
    assets_rel, done, missing = {}, {}, []
    for s in shots:
        if s["family"] == "title": continue
        key = s.get("file") or f"i{s['i']}"
        if key not in done:
            im = bs.render(s, flow_dir)
            if im is None: missing.append(key); im = bs.fallback(s["sentence"])
            name = f"{key}.png"; im.convert("RGB").resize((W, H)).save(proj / "assets" / name, compress_level=1); done[key] = f"assets/{name}"
        assets_rel[s["i"]] = done[key]
    # chapters: split at "title" shots (a title opens a chapter), else every ~60 s, so each scene stays small
    chapters, cur, t_open = [], [], 0.0
    for s, a_, b_ in zip(shots, starts, ends):
        if cur and (s["family"] == "title" or a_ - t_open >= 60): chapters.append(cur); cur = []
        if not cur: t_open = a_
        cur.append((s, a_, b_))
    if cur: chapters.append(cur)
    hosts = []
    for n, ch in enumerate(chapters, 1):
        cid = f"ch{n}"; t0, t1 = ch[0][1], ch[-1][2]
        (proj / "compositions" / f"{cid}.html").write_text(chapter_scene(cid, ch, t0, assets_rel, accent), encoding="utf-8")
        hosts.append(f'<div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:1"></div>')
    # captions
    cap_host = ""
    if "--no-captions" not in sys.argv:
        tr = opt("--transcript")
        if tr: words = [w for w in json.load(open(tr, encoding="utf-8")) if re.search(r"\w", w.get("text", ""))]
        elif isinstance(timing, dict) and "chars" in timing: words = words_from_eleven(timing)
        else: words = words_even(shots, starts, ends)
        words = [w for w in words if w["start"] < dur - 0.3]
        (proj / "compositions" / "captions.html").write_text(captions_scene(groups(words), accent), encoding="utf-8")
        cap_host = f'<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{dur:.3f}" data-track-index="2" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:5"></div>'
    audio = [f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{dur:.3f}" data-track-index="3" data-volume="1"></audio>']
    if music:
        subprocess.run([FF, "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", music, "-t", f"{dur:.3f}", "-c:a", "aac", "-b:a", "160k", str(proj / "assets" / "music.m4a")], check=True)
        audio.append(f'<audio id="music" class="clip" src="assets/music.m4a" data-start="0" data-duration="{dur:.3f}" data-track-index="4" data-volume="0.08" data-fade-out="3"></audio>')
    (proj / "index.html").write_text(f"""<!doctype html>
<html data-composition-variables='[{{"id":"accent","type":"color","label":"Accent","default":"{accent}"}}]'>
<head><meta charset="utf-8"><title>ancient-humans-video</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script></head>
<body style="margin:0;background:#000">
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.3f}" data-width="{W}" data-height="{H}">
{chr(10).join(hosts)}
{cap_host}
{chr(10).join(audio)}
</div>
<script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
</body></html>
""", encoding="utf-8")
    if not (proj / "hyperframes.json").exists():          # project files the CLI expects (what `hyperframes init` writes)
        (proj / "hyperframes.json").write_text(json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": True}}, indent=2), encoding="utf-8")
        (proj / "meta.json").write_text(json.dumps({"id": proj.name, "name": proj.name}, indent=2), encoding="utf-8")
        (proj / "package.json").write_text(json.dumps({"name": proj.name, "private": True, "type": "module", "scripts": {
            "dev": "npx --yes hyperframes preview", "check": "npx --yes hyperframes check", "render": "npx --yes hyperframes render"}}, indent=2), encoding="utf-8")
    print(f"HyperFrames project -> {proj} | {len(shots)} shots, {len(chapters)} scenes, {len(done)} images, captions {'off' if cap_host == '' else 'on'}, {dur:.1f} s | missing Flow images: {missing}")
    print(f"next: npx hyperframes check {proj} --json && npx hyperframes render {proj}")

if __name__ == "__main__":
    main()
