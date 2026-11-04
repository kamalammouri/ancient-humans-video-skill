"""Measure one reference video: speech rhythm, pauses, voice pitch/energy, cut rate, frame contact sheet.
Usage: python analyze_video.py <video.mp4|voice.wav> <out_dir> [--subs captions.json3] [--whisper small] [--lang ar] [--audio-only]
Writes <out_dir>/<id>.json (measures) and <out_dir>/<id>_sheet.jpg (one frame per scene, max 48).
"""
import json, os, subprocess, sys, math

FFMPEG = "ffmpeg"

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def extract_wav(video, wav):
    if not os.path.exists(wav):
        run([FFMPEG, "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav])

def speech_stats(wav):
    import librosa, numpy as np
    y, sr = librosa.load(wav, sr=16000, mono=True)
    dur = len(y) / sr
    hop = 320  # 20 ms
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=hop)[0]
    db = librosa.amplitude_to_db(rms, ref=np.max)
    thr = -35.0
    voiced = db > thr
    # pauses = runs of unvoiced >= 300 ms
    pauses = []
    i = 0
    n = len(voiced)
    while i < n:
        if not voiced[i]:
            j = i
            while j < n and not voiced[j]:
                j += 1
            L = (j - i) * hop / sr
            if L >= 0.3:
                pauses.append((i * hop / sr, L))
            i = j
        else:
            i += 1
    plens = [p[1] for p in pauses]
    # pitch on 3 windows of 60 s (start / middle / end) to keep it cheap
    f0s = []
    for start in (30, dur / 2, max(30, dur - 90)):
        s = int(start * sr); e = int(min(len(y), s + 60 * sr))
        seg = y[s:e]
        if len(seg) < sr:
            continue
        f0, vflag, _ = librosa.pyin(seg, fmin=60, fmax=400, sr=sr, frame_length=2048, hop_length=512)
        f0 = f0[~np.isnan(f0)]
        if len(f0):
            f0s.append(f0)
    f0all = np.concatenate(f0s) if f0s else np.array([])
    # loudness dynamics per 10 s (music swells, dramatic rises)
    seg_db = [float(np.mean(db[k:k + 500])) for k in range(0, len(db), 500)]
    return {
        "duration_s": round(dur, 1),
        "speech_ratio": round(float(voiced.mean()), 3),
        "pauses_over_300ms": len(pauses),
        "pauses_per_min": round(len(pauses) / (dur / 60), 1),
        "pause_mean_s": round(float(np.mean(plens)), 2) if plens else 0,
        "pause_p90_s": round(float(np.percentile(plens, 90)), 2) if plens else 0,
        "pause_max_s": round(float(max(plens)), 2) if plens else 0,
        "long_pauses_over_1s": [round(p[0], 1) for p in pauses if p[1] >= 1.0][:40],
        "f0_median_hz": round(float(np.median(f0all)), 1) if len(f0all) else None,
        "f0_p10_hz": round(float(np.percentile(f0all, 10)), 1) if len(f0all) else None,
        "f0_p90_hz": round(float(np.percentile(f0all, 90)), 1) if len(f0all) else None,
        "loudness_db_per_10s": [round(v, 1) for v in seg_db],
    }

def caption_stats(json3_path, dur):
    """YouTube json3 auto captions: words with timings."""
    d = json.load(open(json3_path, encoding="utf-8"))
    words = []
    for ev in d.get("events", []):
        t0 = ev.get("tStartMs", 0)
        for s in ev.get("segs", []) or []:
            w = (s.get("utf8") or "").strip()
            if w and w != "\n":
                words.append((t0 + s.get("tOffsetMs", 0), w))
    nw = len(words)
    text = " ".join(w for _, w in words)
    buckets = {}
    for t, _ in words:
        buckets[int(t // 60000)] = buckets.get(int(t // 60000), 0) + 1
    wpm_series = [buckets.get(k, 0) for k in range(int(math.ceil(dur / 60)))]
    return {"words": nw, "wpm": round(nw / (dur / 60), 1), "wpm_per_minute": wpm_series,
            "first_200_words": " ".join(text.split()[:200]), "last_120_words": " ".join(text.split()[-120:]),
            "transcript": text}

def whisper_transcribe(wav, model="small", lang="ar"):
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device="cpu", compute_type="int8")
    segs, info = m.transcribe(wav, language=lang, vad_filter=True, word_timestamps=False)
    return [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segs]

def scenes(video, out_sheet):
    from scenedetect import open_video, SceneManager, ContentDetector
    import numpy as np, cv2
    v = open_video(video)
    sm = SceneManager(); sm.add_detector(ContentDetector(threshold=27.0, min_scene_len=12))
    sm.detect_scenes(video=v)
    sl = sm.get_scene_list()
    lens = [(e - s).get_seconds() for s, e in sl]
    stats = {"shots": len(sl), "shot_mean_s": round(float(np.mean(lens)), 2) if lens else 0,
             "shot_median_s": round(float(np.median(lens)), 2) if lens else 0,
             "shot_p10_s": round(float(np.percentile(lens, 10)), 2) if lens else 0,
             "shot_p90_s": round(float(np.percentile(lens, 90)), 2) if lens else 0,
             "shots_under_1s": int(sum(1 for L in lens if L < 1.0))}
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    picks = sl if len(sl) <= 48 else [sl[int(i * len(sl) / 48)] for i in range(48)]
    thumbs = []
    for s, e in picks:
        mid = (s.get_seconds() + e.get_seconds()) / 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(mid * fps))
        ok, fr = cap.read()
        if ok:
            fr = cv2.resize(fr, (320, 180))
            cv2.putText(fr, f"{int(mid)//60}:{int(mid)%60:02d}", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            thumbs.append(fr)
    if thumbs:
        cols = 6; rows = math.ceil(len(thumbs) / cols)
        while len(thumbs) < rows * cols:
            thumbs.append(np.zeros_like(thumbs[0]))
        grid = np.vstack([np.hstack(thumbs[r * cols:(r + 1) * cols]) for r in range(rows)])
        cv2.imwrite(out_sheet, grid, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return stats

if __name__ == "__main__":
    video, out_dir = sys.argv[1], sys.argv[2]
    subs = sys.argv[sys.argv.index("--subs") + 1] if "--subs" in sys.argv else None
    wmodel = sys.argv[sys.argv.index("--whisper") + 1] if "--whisper" in sys.argv else None
    lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "ar"
    os.makedirs(out_dir, exist_ok=True)
    vid = os.path.splitext(os.path.basename(video))[0]
    wav = os.path.join(out_dir, vid + ".wav")
    extract_wav(video, wav)
    res = {"id": vid}
    res["audio"] = speech_stats(wav)
    if subs and os.path.exists(subs):
        res["captions"] = caption_stats(subs, res["audio"]["duration_s"])
    if wmodel:
        res["whisper"] = whisper_transcribe(wav, wmodel, lang)
    audio_only = "--audio-only" in sys.argv or video.lower().endswith((".wav", ".mp3", ".m4a"))
    res["video"] = {"shots": 0, "shot_mean_s": 0, "shot_median_s": 0} if audio_only else scenes(video, os.path.join(out_dir, vid + "_sheet.jpg"))
    json.dump(res, open(os.path.join(out_dir, vid + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    a, v = res["audio"], res["video"]
    print(f"{vid}: {a['duration_s']}s speech {a['speech_ratio']} pauses/min {a['pauses_per_min']} mean {a['pause_mean_s']}s max {a['pause_max_s']}s "
          f"f0 {a['f0_p10_hz']}-{a['f0_median_hz']}-{a['f0_p90_hz']}Hz | shots {v['shots']} mean {v['shot_mean_s']}s med {v['shot_median_s']}s"
          + (f" | wpm {res['captions']['wpm']}" if 'captions' in res else ""))
