# Dino Adventures production

Current selected editions are **English v007, Mandarin v009 and Malaysian Malay v007**. All three complete videos have technical verification records; the owner retained them for distribution planning. Canonical Chinese names are 迪诺、月亮、云爷爷; Malay names are Dino、Bulan、Atuk Awan. Later sections retain the revision history, including superseded English review holds. Current distribution planning is in [distribution.md](distribution.md). Media, API credentials and model caches are deliberately excluded from Git; restore them from the separate backup before running episode-specific media validation or production commands.

The active target is the complete 70.927018-second Dino Saves the Moon episode in English, Mandarin Chinese and Malaysian Bahasa Melayu. The owner cancelled the earlier prototype stopping point. Small synthetic test fixtures are engineering checks, not deliverables.

## Inputs and source verification

The owner-provided Google Drive handover was downloaded and safely extracted on 2026-10-25 after reading `DINO_CODEX_START_HERE.md`. Its obsolete prototype gate is superseded by the owner's production instructions. Originals are retained under `episodes/save-the-moon/media/originals/handover-20261025/`; the incoming delivery remains intact.

- `upload/Dino_save_the_moon_20261021165509(1).mp4`: original mixed-audio reference. SHA-256 `5d493def817a6c16617d275c20b659d7bc40157e7089c9f021342b83d9fb531b` matches the historical source record.
- `Dino_Saves_the_Moon_NO_AUDIO.mp4`: H.264 720×1280 silent picture master, duration 70.927018 s. SHA-256 `13a4c6e61bc3d986866d0c48cee202e2c88198fcf43a4a253affa901ff487a7f`.
- `Dino_Original_Audio.wav`: original extracted mixed track, 48 kHz stereo, 70.912 s. SHA-256 `b2fac8c6a6bb95f2060fd0ba2195d5e8f77442cea0bd12d8d2828a087b0d5430`.

Both MP4s passed full FFmpeg decoding. Their encoded picture-packet SHA-256 is identical: `335c15662779ad14fdbac3777154341fb0ef208929ffdaa357767d31e2b3e934`. Production copies this picture stream instead of regenerating or re-encoding the animation. The reported average frame rate differs from nominal 24 fps; original picture timestamps are preserved.

Two local CPU ASR passes (`small.en` and `medium.en`) agree on the film dialogue. The active manifest has 18 independent speaking cues, scene-localization translations, and source evidence references. Speaker assignments were checked against a picture contact sheet. These are machine-derived transcript/timing checks, not a claim of owner approval or perfect forced alignment. Precise onsets, acting, accents and final balance remain subject to full listening/visual review.

The three supplied generated audition recordings were transcribed separately. They contain extra material absent from the film, including references to a "cloudy kingdom" and additional Dino lines. They are preserved as unattributed audition references and are not silently inserted into the episode.

## Ready components and kit audit

The handover voice/style JSON matches the imported v001 presets. Approved voices remain Dino=Puck, Cloud Guardian=Charon, Moon=Sulafat. `config/voices.json` is the persistent active registry; exact successful audition style prompts and confirmed reference-WAV identities are still unavailable. Selection approval does not imply approval of every generated take.

`tools/kit/` retains the supplied scripts unchanged. Production reuses its procedural SFX generator through an adapter and the same approved voice/style definitions. Its Interactions API integration was not live-validated; production uses the `generateContent` REST adapter that successfully generated actual film dialogue. The handover generator's filename-only caching, `--force` overwriting, lack of timing validation and lack of a renderer are addressed by the production commands. The original kit remains intact.

`config/sfx_presets.json` holds reusable effect definitions and asset paths. Five supplied procedural effects are restored. `tools/score.py` creates an original deterministic celeste/pad underscore and night ambience without external recordings or paid assets. The score and SFX remain separate from dialogue; creative listening review is still necessary.

## Setup on Ubuntu or macOS

Python 3.10+, FFmpeg/FFprobe with H.264/AAC and audio filters, and a local Gemini key are required. No GPU is required. On Ubuntu install `ffmpeg` with apt; on macOS install it with Homebrew. The workspace helper supports `DINO_FFMPEG` and `DINO_FFPROBE` executable overrides.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-production.txt
# Optional for local transcription and generated-dialogue verification; needed by build:
.venv/bin/pip install -r requirements-transcription.txt
python3 tools/dino.py doctor
```

The rendering/TTS helper uses the standard library. The production controller adds `jsonschema` for formal Draft 2020-12 validation; CPU transcription uses `faster-whisper` and PyAV. PyAV 16.1.0 is pinned because version 19 removed an argument used by the tested faster-whisper release. Models are cached locally under episode work when `HF_HOME` is set; they are not included in Git.

Create `.env` from `.env.example` only if `.env` does not exist. Enter the key locally as `GEMINI_API_KEY`. Only this assignment is read; the file is never executed as shell code. Runtime variables take precedence. Do not print or commit the key. An explicitly authorized alternate dotenv may be selected using `--env-file`; its contents are not copied into the project, logs or media records. `--env-key GEMINI_API_KEY_B` explicitly selects one named Gemini variable only when that key is owner-authorized; unrelated settings are not loaded. Credential selections and billing confirmations belong in the non-secret `api_preflight` manifest section.

## Production commands

All media/configuration paths inside manifests are repository-relative. Run from the repository root. Default generation is dry-run; `--live` makes actual API requests using the selected key. Current safeguards permit only the owner-confirmed free-tier production mode. Billing must be reviewed and explicitly authorized before changing that mode.

```sh
.venv/bin/python tools/production.py episodes/save-the-moon/production.json validate
.venv/bin/python tools/production.py episodes/save-the-moon/production.json status
.venv/bin/python tools/production.py episodes/save-the-moon/production.json assets
.venv/bin/python tools/production.py episodes/save-the-moon/production.json generate --lang en
```

One-command resumable production, once the selected free-tier project has quota:

```sh
HF_HOME="$PWD/episodes/save-the-moon/work/huggingface" \
  .venv/bin/python -u tools/production.py episodes/save-the-moon/production.json build --live
```

To use another owner-authorized local key file, without modifying either project's secrets:

```sh
HF_HOME="$PWD/episodes/save-the-moon/work/huggingface" \
  .venv/bin/python -u tools/production.py --env-file /path/to/authorized/.env \
  episodes/save-the-moon/production.json build --live
```

`build` completes each language before advancing: generate missing cues, verify generated speech locally, fit the timeline, render, technically verify the full MP4 and independently check dialogue in the encoded mix. It stops on API quota, speech mismatch, excessive timing drift, stale provenance or render failure. Matching generated WAVs are skipped. Already completed exports are skipped only when manifest, source, audio provenance and export checksum match. It never silently switches credentials, models, presets or billing.

Individual stages:

```sh
.venv/bin/python tools/production.py episodes/save-the-moon/production.json generate --lang en --live
HF_HOME="$PWD/episodes/save-the-moon/work/huggingface" \
  .venv/bin/python tools/production.py episodes/save-the-moon/production.json verify-audio --lang en --model small.en
.venv/bin/python tools/production.py episodes/save-the-moon/production.json fit --lang en
.venv/bin/python tools/production.py episodes/save-the-moon/production.json render --lang en
HF_HOME="$PWD/episodes/save-the-moon/work/huggingface" \
  .venv/bin/python tools/production.py episodes/save-the-moon/production.json verify-export --lang en --model small.en
```

Use `zh`, `ms` or `all` where supported. The verification model for Chinese/Malay is multilingual `small`. `verify-audio --existing-only` checks partial generated material but does not claim that a language is complete. `--line <id>` generates one selected missing line. `--regenerate` preserves the previous take and writes a separate new take; select it with the cue's language-specific `audio_path`. Never use regeneration to retry blindly after a timeout.

API requests default to 21 seconds apart. Quota errors retain safe metric/limit/retry diagnostics and stop further requests. Quotas are per Google project, not per key; a different key is not proof of a separate quota. A metadata request checks model access but cannot establish billing status or remaining allowance. The owner confirmed billing disabled for the Dino key and later for the selected Bursa SIM primary key. Each reached its daily TTS quota. English is fully rendered and technically checked; further generation depends on reset or another explicitly authorized unbilled key/project. There is no automatic key rotation.

## Audio and export behavior

Each generated line retains the exact model, preset/version, style, transcript, audio format, request fingerprint, WAV checksum and duration. Cache reuse requires request and checksum agreement. API generations are nondeterministic; reproducibility uses retained, verified stems rather than assuming a repeat request gives identical samples.

Per-line local ASR compares generated words to requested text and records measured levels. Gain is adjusted toward a consistent speech level with a peak margin. This check does not certify character identity, accent or expressive quality. The original word/timing evidence remains separate from translations and per-language fitted timing.

Timing fitting trims only near-silent edges, retains breathing room, allows no more than 10% speedup, and rejects start shifts over 1.5 seconds. It records every trim, shift and tempo change. This serves natural action alignment without requiring strict lip synchronization. It does not rewrite source dialogue or overwrite source cue times.

Music is ducked under dialogue. Separate timeline-length dialogue, music, ambience and SFX WAV buses plus a floating-point premix are retained alongside each render. All original mixed audio is excluded; only the silent picture master and explicitly selected dialogue-free assets are used.

Working output settings are H.264 picture stream copy, AAC stereo 48 kHz/192 kbps, MP4 faststart, -16 LUFS integrated target and -1.5 dBTP normalization target. These are documented production working choices, not claims of a platform-specific delivery certification. Export checks include full decode, duration/streams, encoded audio loudness/peak margin and exact picture-packet hash equality against the silent master. Per-export JSON records the manifest, hashes, trims, FFmpeg version and measured results. Failed checks do not result in a claimed completed episode.

Expected final MP4s:

- `episodes/save-the-moon/exports/dino_saves_the_moon_en.mp4`
- `episodes/save-the-moon/exports/dino_saves_the_moon_zh.mp4`
- `episodes/save-the-moon/exports/dino_saves_the_moon_ms.mp4`

Do not infer that an expected filename exists. Check `status` and the episode plan for actual progress. No episode is published or uploaded by these commands.

## Extending the series

Append a character to `config/voices.json` with a stable ID, display name, model, voice, language styles, preset version, approval status and reference metadata. Preserve approved definitions and use a new registry/version for deliberate changes. Add effects with an existing WAV or supported generator and provenance/licensing metadata. A new JSON effect name does not itself synthesize a sound.

Create future episodes with `tools/dino.py init`. Add their verified original and silent-master references, source evidence and a production manifest using `schemas/production.schema.json`. Episode-specific cues/outputs stay under that episode; confirmed reusable media stays in `library/`. No core-renderer rewrite is required for more characters or asset-backed effects.

## Validation and review

```sh
.venv/bin/python -m unittest discover -s tests -v
python3 tools/dino.py inventory save-the-moon
```

Tests include a synthetic 72-second production render, separate buses/ducking, packet-identical copied video, decode/duration checks, source preservation, schema rejection, request caching, path protection and timing limits. Synthetic test movies are not episode deliverables. Inspect and listen to each full real render for acting, pronunciation, cue placement, music/SFX quality, transitions, clipping and continuity; document findings in the episode plan.

## FLH brand packaging and explicit ending

Owner prioritized the English branded version before further language generation and asked for an ending. `config/branding.json` uses the current approved H-path/star identity, existing owl mascot and Outfit/Nunito fonts copied from the neighboring Family Learning Hub project with hashes/provenance and the provided OFL notice. No neighboring application files are modified.

`episodes/save-the-moon/branding.en.json` wraps the full English production with a 3-second Family Learning Hub presents card, a small corner logo over the complete story and a 4-second The End/brand/website/thanks card. Existing score supplies gentle opening/closing music; no new voices or API calls are required. Intended duration is 77.927018 s. This is a separately encoded derived picture, while the silent source and the prior unbranded export remain untouched.

```sh
python3 tools/brand_video.py episodes/save-the-moon/branding.en.json preview
python3 tools/brand_video.py episodes/save-the-moon/branding.en.json render
```

Inspect the preview before rendering. Preview provenance prevents silently reusing stale cards after configuration changes; select new work/preview directories when revising. Rendering checks complete duration/decode, loudness/peak margin and correlation of the extracted story audio against its verified source at the 3-second offset. The original English export is checked unchanged. Existing versions are never overwritten.

The owner subsequently authorized the remaining available configured Bursa Gemini variables for free-tier use. After English branding is finished, the explicit `tools/resume_free.py` runner can resume a named, recorded allowlist. It reads one selected key at a time, prints only variable labels, preserves matching outputs and advances to the next explicitly authorized credential only on a confirmed daily free-tier quota error. It stops for other failures. It never creates projects, enables billing or changes either dotenv file. Keys/values are not copied into the repository. Example with a subset of the owner-authorized variables:

```sh
HF_HOME="$PWD/episodes/save-the-moon/work/huggingface" \
  .venv/bin/python -u tools/resume_free.py episodes/save-the-moon/production.json \
  --env-file /path/to/authorized/.env --keys GEMINI_API_KEY_B GEMINI_API_KEY_C
```

### Current English packaging revision v002

Owner requested no logo during the story, playful opening decoration and cute ending animation. `config/branding-playful-v002.json` disables the story watermark. The opening/ending use pale rounded shapes, existing FLH star/crescent assets and gentle mascot bob/tilt, while text stays readable. All 1,694 source story frames remain. v001 is preserved; active English configuration points to the new v002 MP4, using work/preview version003.

Branding now uses Pillow for deterministic vector-like decoration and independent Unicode text layers, not generated/replaced logo or mascot art. Install `.venv/bin/pip install -r requirements-branding.txt` and run branding commands through `.venv/bin/python`. Native drawtext lacked some Chinese glyphs in previews despite font coverage; independent Unicode layers with Noto CJK passed visual inspection. Font provenance/notices are retained in library/configs. Only title/end cards contain branding; the movie itself is unmarked.

Mandarin and Malay manifests use the shared playful layout with localized title/end text. They remain in progress until actual full renders and encoded-dialogue checks pass.

### Current logo-focused review revision v003

The owner refined the direction to a simple preschool-style website-logo bumper. `config/branding-logo-v003.json` and `tools/logo_bumper.py` reuse the unchanged FLH logo and fonts for a gentle logo arrival/rebound, brief brand-color glint, brand name and website. An original four-note mallet tag is generated locally; there is no new voice or programme asset. The 2-second opening and 2.5-second ending replace the decorated/mascot card layout. The complete movie remains unmarked.

Owner also removed only the standalone Moon call after Where did the moon go. The verified source transcript row remains in `production.json` with `include_in_dub: false`; its old WAV is retained. All language builds skip excluded cues, keeping the same picture timeline and backgrounds. The later Moon! Can you hear me? is included. The active English source is a separately versioned corrected mix; none of the earlier exports are overwritten. The current full branded English file is `dino_saves_the_moon_en_flh_v003.mp4`, about75.43seconds.

## Current English review: scene-based underscore v002

The owner approved the v003 logo packaging and requested a less repetitive story score. English is the only enabled production language in `production_languages`; the controller blocks Chinese/Malay generation, fitting and rendering until the owner approves the revised English mix. The three target languages and existing takes remain in the manifest. Remove the hold only after that approval.

`episodes/save-the-moon/music-v002.json` is the editable, full-duration nine-cue music sheet. Its boundaries are editorial music placements based on picture/dialogue review. It changes orchestration, harmony, rhythm and dynamics from wonder through eerie concern, search suspense, the imposing Guardian, friendship, urgency, rescue build, liberation and gratitude. The liberation peak begins at story 54.7 s (56.7 s including the opening bumper). `tools/scene_score.py` writes deterministic standard MIDI and renders it offline using FluidSynth. No Gemini/music-generation requests are needed. The final mix retains dialogue ducking and keeps speech, music, night ambience and SFX as separate full-length stems.

Additional optional composition dependency: FluidSynth CLI, CPU only. Ubuntu: `sudo apt install fluidsynth fluid-soundfont-gm`; macOS: `brew install fluid-synth`. To reproduce this exact score, supply the same FluidR3 GM soundfont at the registry's project-relative path with the recorded SHA-256. Ubuntu's source is `/usr/share/sounds/sf2/FluidR3_GM.sf2`; the MIDI standard/programme map is independent of OS. The 145 MB bank is excluded from Git. Its actual MIT license/copyright notice is retained at `library/licenses/fluidr3-gm.txt`; the preset registry records its source and hash. The composition is original, but its rendered instrument sounds use this third-party sample bank. Already rendered WAVs can be mixed without FluidSynth installed.

```sh
.venv/bin/python tools/scene_score.py episodes/save-the-moon/music-v002.json
.venv/bin/python tools/production.py episodes/save-the-moon/production.json render --lang en
.venv/bin/python tools/production.py episodes/save-the-moon/production.json verify-export --lang en --model small.en
.venv/bin/python tools/brand_video.py episodes/save-the-moon/branding.en.json render
```

Outputs are versioned and protected against overwrite. To revise a composition, use a new score output/work directory and new video filenames. The active branded v004 uses the same v003 FLH logo clips and original bumper music/tag. Only its complete story underscore changes. Existing approved v003, original source files and earlier exports remain intact. Composer provenance includes exact MIDI notes, cue recipe, soundfont hash/license, rendered WAV hash and measured loudness; music/mix review is still an owner creative decision.

## Website-aligned opening and ending

The active English packaging configuration is `config/branding-logo-v004.json`, used for branded English v005. It reuses FLH's actual **Playful Clarity** theme from the neighboring website: warm cream/ink, blue/green/gold/purple, Outfit/Nunito, rounded shapes and a hard-rim blue website capsule. Small edge tints are derived presentation shades; exact solid tokens and source file hashes are recorded in `reports/branding-en-v006/website-theme-reference.json`. Existing official logo and gentle pop/rebound animation remain. Bumpers keep the 2 s opening and 2.5 s ending. The complete story still has no logo, and its dialogue, scene score, ambience and SFX come from the already verified English score remix. This branding revision requires no TTS calls. Earlier branded videos and bumper assets are retained under their own versions.

## English Cloud sync correction and first subtitle layout (superseded)

The owner approved the Playful Clarity opening/ending. Branded v006 preserves those exact cached clips, all English voice takes and the scene score. Picture review found the old 28.6 s arrival whoosh preceded visible Cloud formation around 30.5 s, while the 31.5 s first spoken line preceded his emerging face around 32.1–32.3 s. Revised story placements: arrival 30.35 s, rumble 31.65 s, first line 32.15 s. The following question/reply/Your friend? are reflowed without overlaps. All later dialogue stays in place. These are editorial sync corrections; phoneme lip sync is not claimed. Exact changes/evidence are under `reports/sync-subtitles-v001/`.

Per-language `timing_overrides` preserve owner-directed placement when running `fit` again. They are separate from verified original dialogue/source timing and never change another language's timing silently.

Subtitles use the exact selected dialogue and fitted cue windows, including omission of the removed standalone Moon call. Run:

```sh
.venv/bin/python tools/subtitles.py episodes/save-the-moon/production.json episodes/save-the-moon/subtitles.en.json
.venv/bin/python tools/brand_video.py episodes/save-the-moon/branding.en.json render
```

The story picture fits proportionally to 630×1120, centered horizontally in the unchanged 720×1280 output. A reserved 160px cream lower area holds up to two lines of 36px bold warm-ink subtitles, so text never overlays the source picture. The complete original picture is retained without cropping. Intro/outro remain full-frame and have no subtitles. FFmpeg requires its standard libass `ass` filter. The supplied Nunito bold file internally declares family `Nunito ExtraLight`, style Bold; the ASS uses that actual family and loads the repository font directory explicitly.

Editable ASS/story SRT and subtitle provenance remain in episode work/reports. The exported `.srt` beside branded v006 includes the 2 s opening offset and therefore matches the final MP4. The ASS is applied before brand concatenation and uses story-relative times. Both are protected against silently overwriting changed content; choose new asset/export versions for subsequent editorial changes. Chinese/Malay production is still held pending English owner review.

## Current subtitle layout: full-frame overlay (v007)

Owner rejected the independent subtitle area in v006. Active `subtitles.en.json` now uses `layout: overlay`; `caption_filter` applies only ASS, without scaling, padding, cropping or changing the picture canvas. Bold 36px white Nunito has a 2.5px dark outline and 2px translucent black shadow. Captions are bottom centered with a 34px lower margin and at most two lines. All 17 speaking-cue midpoint previews were reviewed against faces, hands and major actions; default bottom placement generally uses the ground area. Close framing can still overlap a lower torso; this is an editorial attempt to minimize obstruction, not a guarantee that every character pixel stays uncovered. Optional `cue_positions` allows per-cue bottom-anchored ASS positions if future action requires an exception.

The approved full-size FLH bumpers, Cloud synchronization and whole soundtrack are retained. Story ASS/SRT are in subtitles-v003; the v007 exported SRT includes the 2s opening offset. Old v006 assets and the former band renderer remain supported for historical reproducibility but are not used by the active English video. Run the same subtitle/branding commands above to produce a new versioned export.

## Completed v007 language editions

The owner accepted English v007 and explicitly resumed Mandarin and Malaysian Malay. The previous English-only hold is released; all three languages are enabled. The current branded manifests use the same approved `branding-logo-v004.json` and cached FLH bumpers. Final videos are `dino_saves_the_moon_{en,zh,ms}_flh_v007.mp4`, each 75.427214 seconds including the 70.927018-second complete story. Each has its corresponding overlaid subtitles and matching final-offset SRT. English remains the accepted design reference; language voice acting/accent review remains with the owner.

All 51 active source stems match the approved Puck/Charon/Sulafat preset metadata. Identical full-length music, ambience and SFX buses are reused. Each language has independently fitted speech (maximum 10% speedup and 1.5 s source-start drift); Cloud's first line is anchored to 32.15 s, following the approved entrance correction. Original dialogue/audio and the excluded standalone Moon call remain preserved.

A TTS request and its actual verified speech may differ by a natural particle. `audio.<lang>.spoken_text` records an evidenced actual transcript for subtitles/ASR without rewriting `text.<lang>` or falsifying the original request fingerprint. The selected Chinese Puck take requests 月亮得救了！ and is independently recognized as 月亮得救啦！ by two local models. That documented variation is preserved; it is not substituted into source-film transcription.

Mandarin QA normalizes traditional/simplified orthography while retaining meaningful word differences. Long transcript comparison explicitly disables `SequenceMatcher`'s autojunk heuristic; otherwise common repeated letters in Malay can be discarded and produce false failures. Acceptance stays at 0.96; actual whole-mix Mandarin similarity is 0.983871 and Malay 0.996933. Original recognition strings and earlier comparison values remain in reports, rather than rewriting evidence or lowering thresholds.

Reproduction uses the existing production and brand commands, with immutable versioned media:

```sh
.venv/bin/python tools/production.py episodes/save-the-moon/production.json validate
.venv/bin/python tools/production.py episodes/save-the-moon/production.json status
# Reuses matching existing verified exports without calling Gemini:
.venv/bin/python tools/production.py episodes/save-the-moon/production.json build
# First-time packaging for a new version, after selecting fresh export paths:
.venv/bin/python tools/subtitles.py episodes/save-the-moon/production.json episodes/save-the-moon/subtitles.zh.json
.venv/bin/python tools/brand_video.py episodes/save-the-moon/branding.zh.json render
.venv/bin/python tools/subtitles.py episodes/save-the-moon/production.json episodes/save-the-moon/subtitles.ms.json
.venv/bin/python tools/brand_video.py episodes/save-the-moon/branding.ms.json render
```

Completed packaging intentionally refuses overwrite. Exact final duration, frame counts, levels, hashes, shared-bus identity, voice metadata and bumper checks are recorded in `reports/multilingual-v007-verification.json`; per-export reports and editable stems sit beside the raw and branded MP4s. The latest GitHub capacity check is documented in [GitHub media storage](github-media-storage.md); no media has been pushed to GitHub.

## Chinese natural-dialogue revision v008 and canonical names

The owner confirmed **迪诺 (dí nuò), 月亮, 云爷爷** and rejected the briefly suggested 露娜. `config/character_names.json` is the reusable naming registry. `config/voices.json` adds localized-name/profile metadata without modifying the previously approved v001 voice styles or the locked Puck/Charon/Sulafat selections. `config/voice_direction.zh-v002.json` holds the shared conversational Mandarin direction; episode-only emotions, text overrides and duration suggestions live in `episodes/save-the-moon/voice_direction.zh-v002.json`. Exact compiled per-cue instructions are retained in the manifest and generated-take provenance.

All 17 active Chinese lines were revoiced in response to the owner's delivery feedback, with connected conversational phrasing, reduced dragged vowels/pauses, and restrained character acting. The first Moon help call uses a clearer supported call and positive pronunciation anchors (迪 as in 迪士尼, 诺 as in 承诺). Audio/subtitles use Chinese 迪诺 rather than the earlier mixed English Dino input. English and Malay v007 remain unchanged. The Chinese output is versioned v008 with new subtitle assets and `reports/production-v002/`; the prior manifest and v007 recordings/reports remain intact.

`tools/revoice.py` resumes explicitly directed retakes by matching exact request fingerprints and WAV hashes, including completed takes not yet relinked when a run was interrupted. It preserves old takes and never enables billing. It advances an explicitly authorized credential list only after a confirmed daily **free-tier** quota error; other errors stop rather than silently retrying. Default is dry-run. A typical reviewed revision command is:

```sh
.venv/bin/python tools/revoice.py episodes/save-the-moon/production.json --lang zh --env-file /path/to/authorized.env --keys GEMINI_API_KEY_S GEMINI_API_KEY_T
# Add --live only for owner-authorized free-tier generation.
# Add --line moon-help to regenerate only one explicitly directed line.
```

Names are checked independently of the overall ASR similarity. Wrong initials (李诺/伊诺/依诺/比诺 or Latin Dino) do not pass the strict Chinese check. ASR sometimes writes exact same-tone homophones such as 敵諾 or 狄懦 for dí nuò. A small explicit per-name spelling list is allowed for comparison only; raw recognition text is retained, with a separate canonical comparison transcript. Subtitles always display 迪诺. These homophone mappings never waive changed initials or tones, and regression tests cover that distinction. Name check policy/aliases are recorded in each verification report and checked again by the renderer.

The newly recorded Dino-free line requests 月亮得救啦！ and is independently recognized as 月亮得救了！ by small and medium models. Its actual `spoken_text` is recorded separately so subtitles match the recorded particle, while the original request and fingerprint remain accurate. This metadata does not assert owner listening approval or perfect phonetic recognition; final naturalness and accent are reviewed by listening to v008.

The final delivered natural Mandarin revision is **v009**, replacing the undelivered v008 engineering candidate. Its first Moon call is 小迪诺，救救我！; the connected form resolved the final isolated-name ambiguity while keeping the canonical 迪诺 name. Actual final encoded clips of all four name calls pass the strict phonetic-name check. The full picture, music/effects and approved FLH bumpers remain unchanged. Final mastering also catches AAC intersample peak overshoot using a provenance-tracked 192 kHz oversampled transient limiter, then copies video packets untouched; the original -16 LUFS ±1 / peak≤-0.8 dBTP checks remain enforced. Current Mandarin delivery is -16.23 LUFS, -1.89 dBTP, 75.427409 s, 1,802 frames. English/Malay remain v007.
