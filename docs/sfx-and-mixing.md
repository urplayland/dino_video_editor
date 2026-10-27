# Reusable SFX and multilingual mixing

This implementation extends the existing production pipeline. It consumes the
already verified full `.dialogue.wav` stems from `tools/dub.py` and reuses that
module's final mastering, encoded loudness/decode checks and video-packet hash
verification. It never regenerates dialogue or uses the original mixed soundtrack.
Approved character voices/styles remain unchanged. Bunny=Leda is provisional in
`config/voice_candidates.json`, which is not loaded by the approved TTS generator.

## Library and versioning

`config/sfx_presets.json` remains schema_version 1 for compatibility. The release
snapshot is `library/presets/v002/sfx_presets.json`; new presets have independent
`preset_version` and named `variations`. Existing whoosh/chime/pop/footsteps/rumble
entries remain unchanged. New IDs are:

- dino_footstep, bunny_hop, bunny_surprise
- magic_pop, magic_whoosh, puzzle_click
- rainbow_restore, soft_hug
- forest_ambience, river_ambience, magical_ambience

All eleven new effects have three 48 kHz stereo PCM16 variations. Recipes are
original deterministic Python synthesis. Footsteps/clicks have rounded transients;
magic sounds use pitch envelopes/chords/filtered noise; beds use evolving filtered
noise and sparse chirps/tones. Each asset has a recipe fingerprint and SHA-256
sidecar. These are reusable sounds requiring normal creative listening review,
not claims of owner approval or professionally recorded Foley.

```sh
python3 tools/sfx.py generate
python3 tools/sfx.py generate --effect river_ambience --effect dino_footstep
python3 tools/sfx.py --registry library/presets/v002/sfx_presets.json generate
```

Generation needs only the Python standard library. No audio is downloaded, no
key is read, and no API/GPU is used. Existing matching caches are reused; changed
recipes/files are rejected. Preserve the old cache and choose new versioned asset
paths when editing recipes. Old presets and immutable snapshots must remain.

To substitute licensed audio, append a variation with `id`, `asset_path`,
`duration_s`, `gain_db`, `sha256`, `provenance` and `license`, without `generator`.
Record the actual source, licence identifier/terms and permission evidence in
`provenance`. The mixer verifies the bytes and actual duration. Only register
permitted assets; there is deliberately no automatic stock-site downloader.
The procedural licence label means project-generated audio without third-party
samples; it does not assert public-domain status or unknown ownership rights.

## Editable scene cues

```json
{
  "id": "dino-contact-01",
  "scene_id": "scene-01",
  "preset_id": "dino_footstep",
  "preset_version": "v001",
  "timestamp_s": null,
  "duration_s": null,
  "gain_db": -2,
  "variation": "v02",
  "status": "draft",
  "timing_basis": null
}
```

`timestamp_s` is seconds from the actual picture master start. After video review,
set the real time, a review/evidence note in `timing_basis`, and status verified or
approved. Use one cue per observed foot contact when that level of detail is
needed. SFX overlaps are intentional and allowed; duplicate IDs, unknown scenes,
unknown variations, version mismatches and cues beyond the episode are rejected.
Unknown draft values are not replaced with guesses. Promote the plan itself to
verified/approved only after reviewing the picture and duration.

Effective gain is preset default + variation gain + cue gain. An omitted variation
uses a stable cue-ID/preset-version hash, so reordering cues or changing process RNG
does not change takes. An explicit variation locks the take. `loop: true` permits
long ambience/music cues; per-cue fades and exact sample trimming prevent hard
starts/ends. Beds remain stereo and cues are not positioned by invented video actions.

```sh
python3 tools/sfx.py validate episodes/rainbow-bridge/sfx-cues.json
python3 tools/sfx.py validate episodes/rainbow-bridge/sfx-cues.json --production
```

The first command can inspect a draft; the second intentionally rejects the
Episode 2 sample while footage, timestamps and duration are missing. The sample
contains Dino contact, conditional Bunny movement, river and gentle magical beds.
Bunny waving is not assumed to be hopping. Formal schemas are in
`schemas/sfx.schema.json`, `schemas/sfx-cues.schema.json` and
`schemas/audio-production.schema.json`.

`python3 tools/dino.py init <slug> --title ...` copies compatible draft SFX/audio
configs and replaces their project-relative episode paths. Existing episode.json
behavior is unchanged. The Episode 2 working slug is `rainbow-bridge`; it is not
an approved episode title and contains no invented dialogue.

## Shared buses and complete language exports

Install the existing schema dependency and FFmpeg/FFprobe (macOS or Ubuntu):

```sh
python3 -m pip install -r requirements-production.txt
python3 tools/audio_production.py episodes/rainbow-bridge/audio-production.json validate
```

For real production, supply verified input paths, SHA-256, source/licence metadata,
actual duration, aligned EN/ZH/MS dialogue stems and their existing render report
paths. `music` accepts one or more reviewed scene-based music cues; `ambience` is
mixed into the common SFX bus. Looping is explicit. No music file/licence is invented
for Episode 2. Source video/audio and all existing outputs remain untouched.

```sh
python3 tools/audio_production.py <episode-audio-manifest.json> prepare
python3 tools/audio_production.py <episode-audio-manifest.json> build
```

Preparation writes `music.raw.wav`, `sfx.raw.wav`, an inaudible detector stem,
`common.music.wav`, `common.sfx.wav` and `shared.json`. It sums the three dialogue
stems only as a conservative shared detector: speech in any language can duck both
beds. The detector is never mixed into the release audio. Thus all three releases
use exactly the same already-ducked music/SFX files, not three independently
ducked backgrounds. Per-language final loudness normalization can apply different
global gain to the complete mix; common source-bus hashes remain identical.

Music and SFX ducking threshold, ratio, attack and release are separately editable.
Defaults use 15/350 ms for music and 5/220 ms for SFX, with conservative peak
headroom. All buses are 48 kHz stereo and exactly round(duration×48000) samples.
The final premix is float WAV; the existing two-pass loudnorm/AAC pipeline checks
full decode, target loudness within 1 LU, encoded peak below -0.8 dBTP and identical
video packets. It rejects silence/invalid audio. Default final target is -16 LUFS
and -2.5 dBTP to leave AAC headroom.

All inputs, selected variations, effective gains, licences/provenance, common
hashes and FFmpeg version are recorded. Input/recipe/output changes invalidate
caches; partial outputs require a new version. Existing files are never silently
overwritten. Valid complete builds resume without rewriting their outputs.

To run as an optional final step of existing `tools/production.py`, set
`shared_audio_manifest` in the episode's production JSON, pointing to the reviewed
audio-production config. `build` then runs the shared mix after existing dialogue
stems are ready. Or invoke `production.py <production.json> mix-shared`. Leaving
this optional field absent preserves existing production behavior.

## Independent verified acceptance output

Episode 1 has already been released and is not part of this work. Existing
approved videos/sources are preserved and are not reworked or republished.
The reproducible acceptance output is deliberately independent of episode media:

```sh
.venv/bin/python tools/verify_audio_system.py --version v001
```

This runs the complete production engine, not a separate mock mixer. It creates a
12-second synthetic video card, separate detector-tone fixtures for the three
language slots, a local diagnostic underscore, and cues exercising all eleven
new effect IDs. It exports three MP4s, editable full premixes, exact common buses
and acceptance/provenance reports under `episodes/audio-system-verification/`.
The tones are explicitly test signals, not character voices or fabricated film
dialogue. No Episode 1 footage or audio is needed, modified or uploaded. The fixture
is a repeatable engineering acceptance artifact, not a substitute Episode 2 film.

To resume without regenerating its source fixtures:

```sh
.venv/bin/python tools/audio_production.py \
  episodes/audio-system-verification/media/derived/fixture-v001/audio-production.json build
```

The existing branding/subtitle workflow accepts explicit verified dialogue
provenance from the new engine and keeps the old full-manifest check for legacy
renders. Exact subtitle styles, character presets and approved released material
are unchanged. All generated media/caches/reports stay outside Git.

Real Episode 2 final sound design still requires the original footage, actual
scene duration, reviewed cue times, verified dialogue stems and a music asset
with known rights. Null draft cue times deliberately block production; nothing
is fabricated merely to make a command run. New SFX also need normal creative
listening approval; technical validation does not claim owner approval.

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Tests include real CPU FFmpeg mixing, measured ducking during dialogue and recovery
between lines, three-language shared-hash identity, clip/loudness/decode checks,
original-picture preservation, tamper/overwrite protection, deterministic variations,
licence requirements, malformed/draft cues and legacy registry compatibility.
