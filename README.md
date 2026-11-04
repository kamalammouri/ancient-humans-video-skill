# ancient-humans-video — Claude Code skill

A [Claude Code](https://claude.com/claude-code) skill that produces faceless YouTube videos in the
"How did ancient humans…? And what happened when…?" format: a daily gesture of the viewer
(salt, sugar, a locked door, a pill) taken back 200,000 years, the chain of civilisations that
invented the answer, and a modern twist. The format was measured on the Arabic channel
« المهووس - الإنسان قبلنا » (@Mahoos-beforeUs); the skill holds the method, not a topic.

It covers the whole pipeline: brief → fact-check → script (one sentence per line) → shot list →
voice (ElevenLabs, per-character timings) → images (Google Flow driven by Playwright) → edit
(ffmpeg slideshow or HyperFrames with animated captions) → thumbnail → title/description/tags.
Orchestration runs through named sub-agents (`references/agents.md`). The docs are in French;
the scripts produce an American-English video.

## Layout

- `SKILL.md` — the skill itself (channel norms, formula, workflow, agents).
- `references/` — brief, script template, visual style, voice, Flow automation, publishing/SEO,
  the measured reference study of the channel.
- `scripts/` — Python tools: `prompts.py` (shot-list lint + Flow prompts), `tts.py` (ElevenLabs /
  Gemini / edge-tts with word timings), `build_slideshow.py`, `hf_build.py` (HyperFrames project),
  `thumb.py`, `sheets.py`, `make_shots.py` (shot-list template), `styles.json`.
- `scripts/flow/` — Playwright scripts that drive flow.google.com in a real Chrome (`browser.mjs`,
  `login.mjs`, `qbatch.mjs`, `harvest.mjs`, `convert.py`).
- `scripts/yt/` — channel and video analysis (yt-dlp, faster-whisper, librosa, scenedetect,
  script metrics, keyword research).

## Install

Copy (or clone) this folder into your Claude Code skills directory:

```bash
git clone https://github.com/kamalammouri/ancient-humans-video-skill ~/.claude/skills/ancient-humans-video
```

Claude Code picks it up on the next session. Trigger it by asking for a video "like Mahoos" /
"how did cavemen…", or run `/ancient-humans-video`.

## Requirements

- **Python 3.13** with `pip install edge-tts imageio-ffmpeg pillow numpy matplotlib faster-whisper librosa scenedetect yt-dlp`
  (`google-genai` only if you use the Gemini TTS engine).
- **Node 18+** with the `playwright` package installed in some folder; point the Flow scripts at
  it with `PLAYWRIGHT_DIR=/path/to/that/folder`. Google Chrome must be installed (the scripts use
  `channel: 'chrome'`).
- **ElevenLabs**: put `ELEVENLABS_API_KEY=...` in a `.env` file of your *working* folder
  (never in this repo; `.gitignore` excludes it). `tts.py` reads it itself.
- **HyperFrames CLI** (`npx hyperframes`) and the `hyperframes` Claude Code skill for the
  animated-captions edit path; ffmpeg via `imageio-ffmpeg` is enough for the plain slideshow.
- Optional: [Hermes Agent](https://github.com/NousResearch/hermes-agent) on the PATH for one-command
  image QC and transcript analysis.

## Settings to adapt

The docs mention the author's machine; change these to your own paths:

- `PLAYWRIGHT_DIR` — set to the folder where you ran `npm i playwright`
  (docs show `C:/Users/kamalAmmouri/Desktop/nastro`).
- `FLOW_PROFILE` — Chrome profile used for the Google session, default `~/.flow-profile`
  (created on first run of `scripts/flow/browser.mjs`).
- `references/voice.md` names a WhisperX venv under `C:/Users/kamalAmmouri/.venvs/`; install
  WhisperX wherever you like, it is only used for word-level re-alignment.

## License

MIT — see `LICENSE`.
