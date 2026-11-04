# Standalone audio-system acceptance fixture

This is technical verification, not a Dino episode. Generated colour-card video, synthetic detector tones and original procedural effects exercise the complete production pipeline without touching Episode 1 or inventing Episode 2 dialogue/actions.

Run tools/verify_audio_system.py to generate versioned ignored media. Results and final checks are recorded below.

## Acceptance results — 2026-10-27

Generated and fully decoded three12.000-second H264/AAC MP4s, each with288 original diagnostic-card frames and a48kHz stereo soundtrack. Every output retained the same picture-packet hash. All three reference exactly the same ducked music/SFX hashes; only the diagnostic dialogue signals differ. Encoded integrated loudness is EN -16.31, ZH -16.22, MS -16.15 LUFS, within1LU of target; true peaks -11.94/-11.96/-11.27dBTP leave ample headroom. Thirty-three library WAV variants passed exact sample-count/format/checksum/non-silence/peak checks. The decoded label frame was visually inspected.

Independent synthetic verification only: no real episode footage, TTS, paid API, GPU, upload or publishing. Source generation and reports remain editable and reproducible. Detailed ignored audit: reports/acceptance-summary.json and media/derived/fixture-v001/acceptance.json.
