# EP2 English v004 — performance review

Owner-authorized changes: excited Leda retake of the existing under-foot clue, and short Puck reactions at clearly smiling poses. Keep v003 picture, timing, music and magic effects. Compact English review only; no ZH/MS or final-quality export.

```sh
.venv/bin/python tools/review_audio.py episodes/rainbow-bridge/review-en-v004.json
```

The existing take generator was used for two successful unbilled requests. Exact prompts/style, model/approved preset, provider PCM WAV and fingerprints are preserved under media/derived/retakes-v004/en. The Bunny transcript including Dino and foot was verified with cached CPU medium ASR. The Puck take is a0.533s padded nonverbal chuckle, technically verified separately rather than pretending a laughter sound has ordinary dialogue ASR certification. One take is reused at83.000 and123.167s, with different restrained gains. No new story words or forced laughter at every smile. Original voices/styles/presets and previous outputs are unchanged.

New source_take entries must match the transcript, character, voice/model/version, request fingerprint, WAV SHA and verification record. Retakes are trimmed conservatively with the existing speech-bound function. Vocal reactions are separate JSON events, mixed into the dialogue/vocal stem, included in ducking but omitted from spoken learning subtitles. All events remain independently editable.

Direct compact rendering reuses dub.master_audio loudness and full decode checks while burning/scaling captions once; it avoids writing another full-resolution intermediate. The usual production path still copies/compares original video packets. Inputs include source voice/metadata/check hashes; use a new work/output version for future changes. Existing outputs made by older tool revisions are retained, not silently revalidated or overwritten.

69 regression tests pass, including actual retake loading with wrong transcript/voice/hash rejection and an actual filtered compact master. Complete review:540x960,24fps,3996frames/166.5s;35,058,144bytes. Actual audio−16.15LUFS /−2.22dBTP. Minimum27-dialogue waveform correlation0.982344; the two reactions correlate0.988737/0.989946 with the encoded mix. These checks do not establish human approval of emotional acting or laugh naturalness.

Delivery: Review_EN_v004 under EP2/02_After_Editing, including individually uploaded standalone new voice WAVs and metadata for easy listening/recovery. Creative approval remains pending.
