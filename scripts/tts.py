"""Voice track of the slideshow: one audio clip per shot, concatenated, with exact start times.

  python tts.py shots.json [--engine gemini|edge] [--voice NAME] [--style "..."] [--rate +0%] [--model ID] [--gap 0.35]
                           [--brief brief.json] [--out voice.wav] [--timing timing.json] [--cache tts] [--pace 2000] [--only 1,2,3]

Engine, voice, style, rate and language come from brief.json ("voice": {"engine", "name", "style", "rate", "model"}, "voice_language"),
each overridable by a flag. The engine is chosen by the user at the pre-production brief (references/brief.md); nothing is assumed.

Each shot's "sentence" is synthesised to <cache>/<engine>/S<i>.wav, next to a .txt with the text that produced it: a clip whose text
has not changed is skipped (the run is resumable; delete a clip or change its sentence to redo it). The clips are then concatenated
with --gap seconds of silence into voice.wav, and timing.json receives the list of start times, one per shot, in shot order (the
second format build_slideshow.py accepts). A shot without a sentence takes the start time of the next clip.

gemini : pip install "google-genai>=2.25" ; GEMINI_API_KEY in the environment or in a local .env (never in the repo) ; 24 kHz WAV ;
         model gemini-3.8-flash-tts by default (gemini-2.5-*-preview-tts models go through generate_content) ; the style sentence
         is sent with every call so the clips match ; --pace ms between calls keeps under the quota ; 429 and 5xx are retried.
edge   : pip install edge-tts ; free, no key ; mp3 converted to 24 kHz mono WAV with the ffmpeg of imageio_ffmpeg (already needed
         by build_slideshow.py) ; --rate like "-5%" ; no style control, the voice name carries the tone.
Several voices: brief.json "voices": {"NARRATOR": "en-US-GuyNeural", "MOM": "en-US-JennyNeural", ...} and, on a shot, "speaker": "MOM".
         A shot without "speaker" uses the main voice; a speaker missing from the table falls back to it too (and is listed at the end).
         Gemini: the table gives the voice name; the style sentence stays the brief's one, so put the tone in the sentence itself.
Always test on three shots first: --only 1,2,3 , listen, then run the full list.
"""
import json, sys, os, time, wave, pathlib, subprocess, base64, io, shutil

SR = 24000
DEFAULT_MODEL = "gemini-3.8-flash-tts"
DEFAULT_VOICE = {"gemini": {"en": "Kore", "fr": "Kore"}, "edge": {"en": "en-US-GuyNeural", "fr": "fr-FR-HenriNeural"},
                 "eleven": {"en": "Brian", "fr": "Brian"}, "voicebox": {"en": "Narrator Ryan (qwen)", "fr": "Narrator Ryan (qwen)"}}
VOICEBOX_URL = os.environ.get("VOICEBOX_URL", "http://127.0.0.1:17493")   # local Voicebox app (jamiepine/voicebox), free, CPU or GPU
VOICEBOX_ENGINE = "qwen_custom_voice"                                       # kokoro = 5 s per sentence on CPU, qwen_custom_voice = 95 s but far more natural
# Rhythm control (29 Oct 2026, after the snoring episode): Qwen draws a different tempo for every sentence (1.3 to 3.6 words/s measured on
# 64 clips) when each clip is generated alone with a random seed. So: one fixed seed for the whole video (--seed, default 42), a pace hint
# appended to the instruct, and every voicebox clip is measured (words per second of voiced audio); outside --rate-min..--rate-max
# (1.8..2.8) it is regenerated with the next seed of VOICEBOX_SEEDS, up to --tries times, keeping the clip closest to the middle.
VOICEBOX_SEEDS = [42, 7, 1234, 99, 2024]
PACE_HINT = "steady even pace, no rushing, no dramatic pauses"
ELEVEN_MODEL = "eleven_multilingual_v2"
DEFAULT_STYLE = "calm, slow, low-pitched documentary narration, no enthusiasm"

def arg_value(args, flag, default=None):
    return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else default

def load_env():
    """Read KEY=VALUE lines of a .env in the working directory or its parents (3 levels) into os.environ, without overriding."""
    here = pathlib.Path.cwd()
    for d in [here, *here.parents[:3]]:
        f = d / ".env"
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return

def ffmpeg():
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return shutil.which("ffmpeg") or sys.exit("ffmpeg not found: pip install imageio-ffmpeg")

def to_wav24(src, dst):
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", str(SR), "-sample_fmt", "s16", str(dst)], check=True)

def pcm_to_wav_bytes(pcm, sr=SR):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm)
    return buf.getvalue()

def read_frames(path):
    """Return the 16-bit mono 24 kHz frames of a WAV, converting through ffmpeg when the format differs."""
    with wave.open(str(path), "rb") as w:
        if w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getframerate() == SR: return w.readframes(w.getnframes())
    tmp = path.with_suffix(".24k.wav"); to_wav24(path, tmp)
    with wave.open(str(tmp), "rb") as w: frames = w.readframes(w.getnframes())
    tmp.unlink(); return frames

# ---------- engines ----------
def tts_gemini(text, voice, style, model, dst):
    from google import genai
    client = genai.Client()  # reads GEMINI_API_KEY
    if "2.5" in model:  # preview models: generate_content with AUDIO modality, raw PCM back
        from google.genai import types
        r = client.models.generate_content(model=model, contents=(f"Say in a {style} voice: " if style else "") + text,
            config=types.GenerateContentConfig(response_modalities=["AUDIO"], speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)))))
        pcm = r.candidates[0].content.parts[0].inline_data.data
        dst.write_bytes(pcm_to_wav_bytes(pcm if isinstance(pcm, bytes) else base64.b64decode(pcm))); return
    content = {"type": "text", "text": text}
    if style: content["annotations"] = [{"type": "speech_metadata", "style": style}]
    it = client.interactions.create(model=model, input=[{"type": "user_input", "content": [content]}],
                                    response_format={"type": "audio"}, generation_config={"speech_config": [{"voice": voice}]})
    data = it.output_audio.data
    dst.write_bytes(base64.b64decode(data) if isinstance(data, str) else data)

def tts_edge(text, voice, rate, dst):
    import asyncio, edge_tts
    mp3 = dst.with_suffix(".mp3")
    asyncio.run(edge_tts.Communicate(text, voice, rate=rate).save(str(mp3)))
    to_wav24(mp3, dst); mp3.unlink()

# eleven : ELEVENLABS_API_KEY in the environment or .env ; voice = a premade name ("Brian", "Daniel"...) or a voice_id ; model
#          eleven_multilingual_v2 by default ; the remaining character quota is checked BEFORE the first call and the script
#          exits with code 3 when it is short, so the caller can fall back to --engine edge for the whole video (never mix voices).
def eleven_req(path, data=None, headers=None):
    import urllib.request
    req = urllib.request.Request("https://api.elevenlabs.io/v1" + path, data=data,
                                 headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], **(headers or {})})
    return urllib.request.urlopen(req, timeout=180).read()

def eleven_voice_id(name):
    if len(name) >= 20 and " " not in name: return name
    voices = json.loads(eleven_req("/voices"))["voices"]
    for v in voices:
        if v["name"].split(" - ")[0].strip().lower() == name.lower(): return v["voice_id"]   # library names read "Brian - Deep, Resonant..."
    sys.exit(f"ElevenLabs voice '{name}' not found; available: {[v['name'] for v in voices]}")

def eleven_quota():
    s = json.loads(eleven_req("/user/subscription")); return s["character_limit"] - s["character_count"]

def tts_eleven(text, voice_id, model, dst):
    """with-timestamps endpoint: the audio plus one end time per character, saved next to the clip (<name>.align.json) so that
    timing.json can carry the per-character format ({"chars", "end"}) that build_slideshow.py and hf_build.py read for word timings."""
    import urllib.error
    body = json.dumps({"text": text, "model_id": model, "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.0}}).encode()
    try: raw = eleven_req(f"/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128", body, {"Content-Type": "application/json"})
    except urllib.error.HTTPError as e:
        if e.code in (401, 402): print(f"ElevenLabs refused ({e.code}): {e.read()[:200]} -> fall back to --engine edge"); sys.exit(3)
        raise
    r = json.loads(raw); audio = base64.b64decode(r["audio_base64"]); al = r.get("alignment") or r.get("normalized_alignment")
    if al: dst.with_suffix(".align.json").write_text(json.dumps({"chars": "".join(al["characters"]), "end": al["character_end_times_seconds"]}), encoding="utf-8")
    mp3 = dst.with_suffix(".mp3"); mp3.write_bytes(audio); to_wav24(mp3, dst); mp3.unlink()

def eleven_char_timing(shots, starts, cache, gap, cuts=None):
    """Global per-character timing from the clips' align files: sentences joined by one space, end times offset by each clip's start
    (minus the lead silence trim_edges removed from that clip). Returns None when a clip has no alignment (then timing.json stays the list of starts)."""
    chars, end = "", []
    for s, st in zip(shots, starts):
        if not (s.get("sentence") or "").strip(): continue
        al = cache / f"S{s['i']:04d}.align.json"
        if not al.exists(): return None
        a = json.load(open(al, encoding="utf-8"))
        if not a["end"]: return None
        cut, top = (cuts or {}).get(s["i"], (0.0, 1e9))   # (lead removed, trimmed clip length): an engine may stamp the last character at the end of its trailing silence
        fix = lambda e: round(st + min(top, max(0.0, e - cut)), 3)
        chars += a["chars"] + " "; end += [fix(e) for e in a["end"]] + [round(fix(a["end"][-1]) + gap, 3)]
    return {"chars": chars, "end": end, "starts": starts} if chars else None

def trim_edges(frames, keep_lead=0.05, keep_trail=0.10, thr_db=-40.0):
    """Cut the silence an engine leaves around a clip (ElevenLabs: ~0.1 s lead, ~0.4 s trail, up to 2.6 s on a one-word line, measured
    4 Nov 2026) so the pause between sentences is the --gap and nothing else. Returns (frames, seconds removed at the start)."""
    import array
    a = array.array("h"); a.frombytes(frames); n = len(a); win = int(SR * 0.02); thr = 32768 * 10 ** (thr_db / 20)
    def quiet(seg): return (sum(x * x for x in seg) / max(1, len(seg))) ** 0.5 < thr
    lead = 0
    while lead + win < n and quiet(a[lead:lead + win]): lead += win
    trail = 0
    while trail + win < n - lead and quiet(a[n - trail - win:n - trail]): trail += win
    lo, hi = max(0, lead - int(SR * keep_lead)), n - max(0, trail - int(SR * keep_trail))
    return a[lo:hi].tobytes(), lo / SR

# voicebox : the Voicebox desktop app running locally (its API on VOICEBOX_URL). voice = a profile NAME (or id) created in the app or
#          by POST /profiles (voice_type preset: engine kokoro / qwen_custom_voice + preset_voice_id) ; model = the engine name ;
#          style = the "instruct" sentence. /generate/stream returns a 24 kHz mono WAV. Measured 28 Oct 2026 on CPU: kokoro 4.7 s
#          per sentence, qwen_custom_voice 95 s. Several voices in one run: use --cache / --out / --timing per voice.
_vb_profiles = {}
def voicebox_profile_id(name):
    import urllib.request
    if not _vb_profiles:
        for p in json.loads(urllib.request.urlopen(VOICEBOX_URL + "/profiles", timeout=30).read()): _vb_profiles[p["name"].lower()] = p["id"]; _vb_profiles[p["id"]] = p["id"]
    pid = _vb_profiles.get(name.lower()) or _vb_profiles.get(name)
    if not pid: sys.exit(f"Voicebox profile '{name}' not found; existing: {sorted(k for k in _vb_profiles if k != _vb_profiles[k])}")
    return pid

def speech_rate(path, words):
    """Words per second of voiced audio (leading and trailing silence under -40 dBFS removed), 0 if unreadable."""
    import struct
    with wave.open(str(path), "rb") as w: n, sr, raw = w.getnframes(), w.getframerate(), w.readframes(w.getnframes())
    a = struct.unpack("<%dh" % (len(raw) // 2), raw); win = max(1, int(sr * 0.02)); thr = 32768 * 10 ** (-40 / 20)
    rms = lambda seg: (sum(x * x for x in seg) / max(1, len(seg))) ** 0.5
    lead = 0
    while lead + win < len(a) and rms(a[lead:lead + win]) < thr: lead += win
    trail = 0
    while trail + win < len(a) and rms(a[len(a) - trail - win:len(a) - trail]) < thr: trail += win
    speech = (len(a) - lead - trail) / sr
    return words / speech if speech > 0.2 else 0.0

def tts_voicebox(text, profile, engine, instruct, lang, dst, seed=None):
    import urllib.request
    body = {"profile_id": voicebox_profile_id(profile), "text": text, "language": lang, "engine": engine}
    if instruct: body["instruct"] = instruct[:500]
    if seed is not None: body["seed"] = int(seed)
    req = urllib.request.Request(VOICEBOX_URL + "/generate/stream", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    dst.write_bytes(urllib.request.urlopen(req, timeout=1800).read())

def synth(engine, text, cfg, dst, attempts=4):
    for n in range(attempts):
        try:
            if engine == "gemini": tts_gemini(text, cfg["voice"], cfg["style"], cfg["model"], dst)
            elif engine == "eleven": tts_eleven(text, cfg["voice_id"], cfg["model"], dst)
            elif engine == "voicebox": tts_voicebox(text, cfg["voice"], cfg["model"], cfg["style"], cfg["lang"], dst, cfg.get("seed"))
            else: tts_edge(text, cfg["voice"], cfg["rate"], dst)
            return True
        except Exception as e:  # quota (429), transient 5xx, network: wait and retry
            wait = 10 * (3 ** n)
            print(f"  retry in {wait}s after: {str(e)[:160]}")
            if dst.exists(): dst.unlink()
            time.sleep(wait)
    return False

# ---------- main ----------
def main(args):
    load_env()
    src = next((a for a in args if a.endswith(".json") and (args.index(a) == 0 or not args[args.index(a) - 1].startswith("--"))), "shots.json")
    shots = json.load(open(src, encoding="utf-8"))
    bp = pathlib.Path(arg_value(args, "--brief", "brief.json")); brief = json.load(open(bp, encoding="utf-8")) if bp.exists() else {}
    bv = brief.get("voice") or {}
    engine = arg_value(args, "--engine", bv.get("engine") or "edge")
    if engine not in DEFAULT_VOICE: sys.exit(f"unknown engine '{engine}': gemini | edge | eleven | voicebox")
    lang = (brief.get("voice_language") or "en")[:2].lower()
    cfg = {"voice": arg_value(args, "--voice", bv.get("name") or DEFAULT_VOICE[engine].get(lang, DEFAULT_VOICE[engine]["en"])),
           "style": arg_value(args, "--style", bv.get("style") if bv.get("style") is not None else DEFAULT_STYLE),
           "rate": arg_value(args, "--rate", bv.get("rate") or "+0%"),
           "model": arg_value(args, "--model", bv.get("model") or DEFAULT_MODEL)}
    gap, pace = float(arg_value(args, "--gap", 0.35)), int(arg_value(args, "--pace", 2000 if engine == "gemini" else 300))
    only = {int(x) for x in arg_value(args, "--only", "").split(",") if x.strip()}
    cache = pathlib.Path(arg_value(args, "--cache", "tts")) / engine; cache.mkdir(parents=True, exist_ok=True)
    if engine == "gemini" and not os.environ.get("GEMINI_API_KEY"): sys.exit("GEMINI_API_KEY missing: put it in the environment or in a local .env")
    cfg["lang"] = lang
    if engine == "voicebox":
        cfg["seed"] = int(arg_value(args, "--seed", bv.get("seed", VOICEBOX_SEEDS[0])))
        if cfg["style"] and PACE_HINT not in cfg["style"]: cfg["style"] = cfg["style"].rstrip(". ") + ", " + PACE_HINT
        cfg["rate_min"], cfg["rate_max"] = float(arg_value(args, "--rate-min", bv.get("rate_min", 1.8))), float(arg_value(args, "--rate-max", bv.get("rate_max", 2.8)))
        cfg["tries"] = int(arg_value(args, "--tries", bv.get("tries", 3)))
    if engine == "voicebox":
        if cfg["model"] == DEFAULT_MODEL: cfg["model"] = VOICEBOX_ENGINE
        voicebox_profile_id(cfg["voice"])
    if engine == "eleven":
        if not os.environ.get("ELEVENLABS_API_KEY"): print("ELEVENLABS_API_KEY missing: put it in the environment or in a local .env -> fall back to --engine edge"); sys.exit(3)
        if cfg["model"] == DEFAULT_MODEL: cfg["model"] = ELEVEN_MODEL
        cfg["voice_id"] = eleven_voice_id(cfg["voice"])
        need = sum(len((s.get("sentence") or "").strip()) for s in shots if (s.get("sentence") or "").strip() and (not only or s["i"] in only)
                   and not ((cache / f"S{s['i']:04d}.txt").exists() and (cache / f"S{s['i']:04d}.txt").read_text(encoding="utf-8") == f"{cfg['voice']}|{(s.get('sentence') or '').strip()}"))
        left = eleven_quota(); print(f"ElevenLabs quota: {left} characters left, {need} needed")
        if left < need: print("quota too short -> fall back to --engine edge"); sys.exit(3)
    print(f"engine {engine} | voice {cfg['voice']} | {'model ' + cfg['model'] + ' | style ' + repr(cfg['style']) if engine == 'gemini' else 'model ' + cfg['model'] if engine in ('eleven', 'voicebox') else 'rate ' + cfg['rate']} | lang {lang}")

    voices = brief.get("voices") or {}; unknown = set()
    made = skipped = failed = 0
    for s in shots:
        text = (s.get("sentence") or "").strip()
        if not text or (only and s["i"] not in only): continue
        spk = s.get("speaker"); vcfg = dict(cfg)
        if spk and spk in voices: vcfg["voice"] = voices[spk]
        elif spk: unknown.add(spk)
        name = f"S{s['i']:04d}"; dst, txt = cache / f"{name}.wav", cache / f"{name}.txt"   # by shot, not by image: one image may carry several sentences
        key = f"{vcfg['voice']}|{text}"
        if dst.exists() and txt.exists() and txt.read_text(encoding="utf-8") == key: skipped += 1; continue
        print(f"#{s['i']:>3} {name} [{spk or 'narrator'} / {vcfg['voice']}]: {text[:60]}")
        ok = synth(engine, text, vcfg, dst)
        words = len(text.split())
        if ok and engine == "voicebox" and vcfg["model"] != "kokoro" and words >= 6:   # kokoro is deterministic; a short line is naturally slow
            r = speech_rate(dst, words); mid = (vcfg["rate_min"] + vcfg["rate_max"]) / 2
            best = (abs(r - mid), dst.read_bytes(), r, vcfg["seed"]); k = 0
            while not (vcfg["rate_min"] <= r <= vcfg["rate_max"]) and k < vcfg["tries"]:
                k += 1; seed = VOICEBOX_SEEDS[(VOICEBOX_SEEDS.index(vcfg["seed"]) + k) % len(VOICEBOX_SEEDS)] if vcfg["seed"] in VOICEBOX_SEEDS else VOICEBOX_SEEDS[k % len(VOICEBOX_SEEDS)]
                print(f"      rate {r:.2f} words/s outside {vcfg['rate_min']}..{vcfg['rate_max']}: retry {k} with seed {seed}")
                if not synth(engine, text, dict(vcfg, seed=seed), dst): print("      retry failed (server?), keeping the best clip so far"); break
                r = speech_rate(dst, words)
                if abs(r - mid) < best[0]: best = (abs(r - mid), dst.read_bytes(), r, seed)
            if not dst.exists() or dst.read_bytes() != best[1]: dst.write_bytes(best[1])
            print(f"      kept {best[2]:.2f} words/s (seed {best[3]})")
        if ok: txt.write_text(key, encoding="utf-8"); made += 1; time.sleep(pace / 1000)
        else: failed += 1
    print(f"clips: {made} made, {skipped} unchanged, {failed} failed" + (f" | speakers without a voice in brief.voices (main voice used): {sorted(unknown)}" if unknown else ""))

    # concatenate in shot order, exact start times
    silence = b"\x00\x00" * int(gap * SR); frames, starts, missing, t, cuts = [], [], [], 0.0, {}
    for s in shots:
        starts.append(round(t, 3))
        name = f"S{s['i']:04d}"; clip = cache / f"{name}.wav"
        if not (s.get("sentence") or "").strip(): continue
        if not clip.exists(): missing.append(s["i"]); continue
        fr, cut = trim_edges(read_frames(clip)); cuts[s["i"]] = (cut, len(fr) / 2 / SR); frames.append(fr); frames.append(silence); t += (len(fr) // 2 + len(silence) // 2) / SR
    out, timing = pathlib.Path(arg_value(args, "--out", "voice.wav")), pathlib.Path(arg_value(args, "--timing", "timing.json"))
    with wave.open(str(out), "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(b"".join(frames))
    ct = eleven_char_timing(shots, starts, cache, gap, cuts) if engine == "eleven" and not missing else None
    json.dump(ct if ct else starts, open(timing, "w", encoding="utf-8"))
    print(f"{out} {t / 60:.1f} min | {timing} {len(starts)} starts{' + per-character timestamps' if ct else ''} | missing clips: {missing or 'none'}"
          + (" (run again without --only for the full track)" if only else ""))

if __name__ == "__main__":
    main(sys.argv[1:])
