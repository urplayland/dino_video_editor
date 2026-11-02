# Dino and the Broken Rainbow Bridge — production

Current release: EN finalv001, BC/ZH finalv002 and BM/MS finalv002, with localized ending cards. See final-production-v001.md and [series release list](../../docs/series-release-list.md). Historical v001 build notes below describe earlier staging; use the pinned distribution-selection.json for publishing. The website addition remains pending.

The owner approved the production plan on2026-11-01, including differentiated dramatic music comparable to Dino Saves the Moon. Preserve Episode1 and all source footage. Working plan: production-plan-2026-11-01.md; review log: edit-plan.md.

## Sources and picture

The latest HQ handoff supersedes the older178.96s cut. Original silent picture is162s/3888frames/24fps/720x1280 and already has a2s FLH opening. The reference AAC container is162.021333s and is mixed guide audio, not a clean dialogue/background stem. Reconstruct the eight byte chunks using the supplied ASSEMBLY_MANIFEST.json and verify SHA256 before use. Inputs are retained under media/originals/hq-20261101 (ignored). Byte chunks are not separately playable clips.

New clean picture is media/derived/picture-v001/EP2_Clean_Visual_Master_v001.mp4: original162s plus4.5s THE END motion graphics,166.5s/3996frames. The original3888 video packets are preserved; a complete decode was checked. No old outro added, no second opening offset. Main-cut timing estimates in picture-timeline-v001.json are references; actual speech windows come from source audio and current picture. Original source frame/cut rounding may differ by one frame.

## Voices and speech

production.json contains source evidence, three-language text, timing and generated-WAV metadata. Dino=Puck; female Bunny/邦妮=Leda. Existing Moon/Cloud presets unchanged. Bunny delivery directions are new production instructions based on the approved plan, not claimed copies of unavailable audition prompts. Reusable definitions: config/voices.json. Terms: glossary.json. Natural Mandarin and Malaysian Malay are required.

Actual source was independently transcribed with cached small.en and medium CPU models, then quieter passages checked in cropped ranges. Evidence and review reports are under reports/. Draft Story Bible text is not used as a certified transcript; music-induced hallucinations are excluded. Machine checks do not establish owner accent/acting approval.

```bash
.venv/bin/python tools/production.py episodes/rainbow-bridge/production.json validate
# Explicit live call, only after checking the owner-authorized free-tier credential:
.venv/bin/python tools/production.py episodes/rainbow-bridge/production.json generate --lang en --live
.venv/bin/python tools/production.py episodes/rainbow-bridge/production.json verify-audio --lang en --model small.en
.venv/bin/python tools/production.py episodes/rainbow-bridge/production.json fit --lang en
.venv/bin/python tools/production.py episodes/rainbow-bridge/production.json render --lang en
```

Use zh/ms in place of en and the cached multilingual small model for their first audio verification. These render commands preserve editable dialogue-only working exports. Final release mixing uses audio-production.json below. Matching generated outputs are reused; changed text/styles need a separate take/version and explicit relinking. Never silently overwrite audio or substitute a voice/model. Free daily quota is finite; no billing is enabled. Named alternate keys require the existing explicit allowlist and billing-disabled authorization. No key values belong in reports or Git.

## Ending and differentiated music

```bash
.venv/bin/python tools/end_card.py episodes/rainbow-bridge/ending-v001.json
.venv/bin/python tools/scene_score.py episodes/rainbow-bridge/music-v001.json
```

THE END is central; smaller FLH logo, series and website are in the lower third. The same card is shared by all languages. Existing website palette/fonts are used. Reuse the checked picture master above rather than appending another ending on repeated runs.

music-v001.json has20 continuous sections: branded opening space, concern, reassurance, puzzle mystery, sparse circle teaching, discovery, small matching rewards, encouragement, triangle teaching/search, square lesson/comic searching, growing magic, full restoration peak, relief, hug, departure and closing cadence. Harmony, rhythm, orchestration and dynamics change, with held tones/tails connecting sections. Only restoration receives the strongest orchestral release. Local FluidSynth renders original MIDI arrangements using the registered FluidR3 bank; its MIT licence is retained under library/licenses/. No paid music API, GPU, sampled song or unlicensed download.

## Common backgrounds and final outputs

Action effects: sfx-cues.json, versioned library library/presets/v002/sfx_presets.json. Cue timing was reviewed in actual motion-sheet frames and remains editable after listening. The river/forest stem is independent from dialogue, effects and music. Generated stereo48kHz sources and score MIDI remain under media/derived/. Common music/SFX are ducked once using the three-language speech detector, then shared by hash across all final mixes.

```bash
.venv/bin/python tools/sfx.py validate episodes/rainbow-bridge/sfx-cues.json --production
.venv/bin/python tools/audio_production.py episodes/rainbow-bridge/audio-production.json validate
.venv/bin/python tools/audio_production.py episodes/rainbow-bridge/audio-production.json build
# Existing subtitle generator; complete-film offset is0 because opening is already included:
.venv/bin/python tools/subtitles.py episodes/rainbow-bridge/production.json episodes/rainbow-bridge/subtitles.en.json
```

Outputs are versioned under exports/ and never replace original sources. Per-language subtitle MP4/SRT/full_mix.wav and clean shared picture/English primary are packaged individually for Drive. No ZIP and no YouTube/social publishing. No fixed subtitle panel; use white full-frame captions with dark outline/shadow. Keep music dialogue-free and clear speech in the foreground. Final target is around-16LUFS and at most-1dBTP (configured ceiling-2.5dBTP). QA must include complete decode, exact duration/frame count, encoded loudness, generated dialogue comparison, subtitle readability, scene cues and ending. Human accent/acting/music approval remains distinct from technical checks.

Before the final common mix, link checksums from the actual verified full dialogue stems:

```bash
.venv/bin/python tools/link_shared_audio.py episodes/rainbow-bridge/production.json episodes/rainbow-bridge/audio-production.json
.venv/bin/python tools/audio_production.py episodes/rainbow-bridge/audio-production.json build
.venv/bin/python tools/brand_video.py episodes/rainbow-bridge/branding.en.json render
.venv/bin/python tools/brand_video.py episodes/rainbow-bridge/branding.zh.json render
.venv/bin/python tools/brand_video.py episodes/rainbow-bridge/branding.ms.json render
```

These branding manifests set `existing_branding=true`: captions are applied without adding any cards or re-encoding the mastered AAC. Their packaged subtitle offset is0. Matching finished outputs can be resumed by checksum; changed inputs require a new output version.

The Mandarin Dino takes explicitly reuse config/voice_direction.zh-v002.json (the actual EP1 per-line natural delivery profile); the basic registry alone does not apply that profile automatically. Controlled character-only retakes preserve all other actors and prior takes:

```bash
.venv/bin/python tools/revoice.py episodes/rainbow-bridge/production.json --lang zh --character dino --env-file /path/to/authorized/.env --keys GEMINI_API_KEY_X --live
```

Use only key variable names present in the episode's explicit authorization list. The optional `resume_free.py --generate-only --lang ms` stage generates a language without concurrently writing fitted manifest metadata; verification, fitting and rendering follow sequentially. Do not run two manifest-writing stages at once. A transient503 stops that job; inspect retained outputs and resume after backoff. Confirmed daily quota failure advances only within the authorized list.

Final encoded sound can be checked independently of automatic recognition spelling:

```bash
.venv/bin/python tools/review_shared_audio.py episodes/rainbow-bridge/production.json --lang en
.venv/bin/python tools/review_shared_audio.py episodes/rainbow-bridge/production.json --lang zh --model medium --by-cue
.venv/bin/python tools/review_shared_audio.py episodes/rainbow-bridge/production.json --lang ms --model medium --by-cue
.venv/bin/python tools/review_mix_integrity.py episodes/rainbow-bridge/production.json
```

The cue-aligned recognition reads the actual encoded mix at known speech windows with no reference text passed to ASR. Continuous VAD can omit short lines. Some Chinese/Malay short phrases still have recognition spelling/segmentation disagreements: these diagnostics are retained rather than relabelled as perfect transcripts. All selected source WAVs passed independent per-line checks. The waveform-integrity check verifies each of those known spoken signals is present and foregrounded in the actual mastered AAC, allowing only0.5ms alignment and requiring correlation>=0.95, without changing any voice or lowering ASR thresholds. It does not replace owner listening for acting, names, accent or musical taste. Final QA records both evidence types explicitly.

Release videos already contain subtitles. SRT files are included for editing and accessibility. Full-mix WAVs are decoded from the final mastered audio and trimmed/padded to exactly166.5s; original generated WAVs, fitted dialogue, pre-master float mixes, original/ducked background stems and MIDI remain separate. The source first162s picture remains byte-preserved in the clean master; subtitle exports are derived encodes and preserve the final AAC packets exactly.

Before packaging, record the passing regression run and build the individual release:

```bash
.venv/bin/python -m unittest discover -s tests > episodes/rainbow-bridge/reports/regression-tests-final.log 2>&1
.venv/bin/python episodes/rainbow-bridge/prepare_delivery.py
```

The packager refuses a failed/missing test result and changed existing packages. Generated file inventories stay under ignored reports/ and exports/.
