# EP2 English integrated revision v002

This revision uses the existing166.5s clean picture and the verified English Puck/Leda dialogue stem. It does not regenerate scenes, call a generation API, change approved voices/styles, modify v001, or render other languages. Picture includes the existing2s opening and accepted4.5s ending exactly once.

Run from the repository root after restoring ignored media and the licensed FluidR3 soundfont/fonts:

```sh
.venv/bin/python tools/review_audio.py episodes/rainbow-bridge/review-en-v002.json
.venv/bin/python -m unittest discover -s tests -v
```

Dependencies are the existing production/transcription environment, NumPy, Pillow, FFmpeg with libass/libx264, and FluidSynth. No GPU, network or API key is used. The helper reuses `audio_production.timeline`, `scene_score`, `subtitles`, `dub.master_audio` and the waveform reviewer. Its frozen configuration lists source hashes, per-line pitch-preserving tempo/gain/entry edits, independent bus ducking, music and SFX decisions. The English review intentionally bypasses the three-language export controller: it does not generate placeholder ZH/MS finals to satisfy that controller.

Outputs are individual files in `exports/Review_EN_v002/`: complete integrated MP4; independent dialogue, BGM, ambience and SFX WAVs; final-spoken-audio timeline JSON/MD; SRT/ASS; music/automation manifest; change log and QA report. Media and diagnostic caches remain ignored by Git. The clean intermediate preserves encoded picture packets; only the caption pass re-encodes video. Full frame,24fps and166.5s length are retained.

Subtitle timing is remeasured conservatively from final dialogue PCM energy:25ms leading and45ms trailing guard. This is not word-level forced alignment. Existing white, dark outlined/shadowed full-picture style is retained. A source cutaway during the triangle discovery intentionally has offscreen Dino speech. No original Flow guide track is mixed into the final audio.

BGM, ambience and SFX delivery WAVs already include their own phrase ducking:8,2 and5dB respectively,150ms lead-in and300ms release. Do not duck them again. The final two-pass loudness master targets−16LUFS /−2.5dBTP. Reusing the composition and effect marks in later languages is supported; recompute duck automation from the localized final dialogue, rather than copying English intervals.

All outputs are versioned. The helper refuses changed input metadata or conflicting JSON at a frozen work location. To change decisions after review, use a new config, work directory and delivery directory; retain the existing review and sources. The original take metadata and ASR verification records remain in the original production directory. New clip files are offline edits, not new TTS generations and not evidence of re-acted emotion.

QA includes complete FFmpeg decoding, duration/frame count, loudness/true peak, dialogue waveform presence in actual AAC, and sampled picture/caption/action checks. These cannot establish human listening approval of acting, pronunciation or music taste. Owner review remains required, particularly for previously flagged emotional delivery; new TTS acting is outside the current no-new-generation authorization.
