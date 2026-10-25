# Dino Adventures — multilingual dubbing production

A reusable post-production workspace for Family Learning Hub's Dino Adventures series. The current goal is the **entire 70.927-second Dino Saves the Moon episode** in English, Mandarin Chinese and Malaysian Bahasa Melayu. The earlier prototype stopping point has been cancelled.

The complete handover is now imported locally, including the original mixed-audio MP4, a silent picture master, original audio, kit scripts/presets, effects and audition recordings. The animation is preserved. Approved voices remain **Dino=Puck, Cloud Guardian=Charon, Moon=Sulafat**, using `gemini-3.8-flash-tts`.

**Current delivery:** the owner selected English **v007**, Mandarin **v009**, and Malaysian Malay **v007** for distribution planning. All three complete videos passed technical checks; Mandarin v009 includes the natural-dialogue/name revision. Approved names are 迪诺 / 月亮 / 云爷爷 in Chinese and Dino / Bulan / Atuk Awan in Malay. Outputs, subtitles, audio stems and media verification reports remain outside Git. See [the selected delivery manifest](episodes/save-the-moon/distribution-selection.json) and [the episode plan](episodes/save-the-moon/edit-plan.md) for exact hashes and review history. No social-platform publication has occurred.

Read [the production setup and commands](docs/production.md), then [the episode plan](episodes/save-the-moon/edit-plan.md) for actual progress and review results. Expected final files are not evidence of completion; all three real videos must be rendered and verified.

## Layout

| Location | Purpose | In Git? |
| --- | --- | --- |
| `incoming/` | Original delivery and isolated intake | Instructions only |
| `config/voices.json` | Persistent character registry | Yes |
| `config/sfx_presets.json` | Persistent reusable effect registry | Yes |
| `schemas/` | JSON Schema contracts | Yes |
| `library/catalog.csv` | Shared media provenance and usage notes | Yes |
| `library/presets/v001/` | Preserved imported preset version | Yes |
| `library/media/` | Reusable SFX, score and ambience | No |
| `templates/episode/` | Compatible starter episode documents | Yes |
| `episodes/<slug>/episode.json` | Episode identity and source hashes | Yes |
| `episodes/<slug>/production.json` | Multilingual dialogue, source timing, cues, outputs and verification references | Yes |
| `episodes/<slug>/edit-plan.md` | Decisions, changes and review findings | Yes |
| `episodes/<slug>/media/` | Preserved sources and derived voice stems | No |
| `episodes/<slug>/project/` | Editor notes/projects | Yes |
| `episodes/<slug>/work/` | Model cache and temporary work | No |
| `episodes/<slug>/exports/` | Full MP4s, editable bus stems and render reports | No |
| `episodes/<slug>/reports/` | Inventories, transcripts and validation reports | No |

## Quick start

Python 3.10+, FFmpeg/FFprobe and the small production validation dependency are required. Optional CPU transcription dependencies are needed for end-to-end audio verification. See [Ubuntu/macOS setup](docs/production.md#setup-on-ubuntu-or-macos).

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-production.txt -r requirements-transcription.txt
python3 tools/dino.py doctor
.venv/bin/python tools/production.py episodes/save-the-moon/production.json status
```

Once the selected owner-confirmed free-tier key has quota:

```sh
HF_HOME="$PWD/episodes/save-the-moon/work/huggingface" \
  .venv/bin/python -u tools/production.py episodes/save-the-moon/production.json build --live
```

`build` resumes retained stems, verifies dialogue, fits timing, mixes separate audio buses, stream-copies the silent picture and checks full exports. It stops on quota or failed checks. Generation without `--live` is dry-run. Keys are read privately from `.env` or an explicitly authorized `--env-file`; no billing is enabled or credential rotation performed.

Workspace commands remain dependency-free:

```sh
python3 tools/dino.py init another-adventure --title "Dino's Next Adventure"
python3 tools/dino.py inventory save-the-moon
python3 tools/dino.py verify save-the-moon --report episodes/save-the-moon/reports/<inventory-file>.json
```

`init` never overwrites an episode. Inventory/verification record SHA-256 and optional ffprobe metadata using project-relative paths. Preserve originals and derive new files separately. Media and model caches are excluded from Git and require a separate backup; a Git clone alone does not contain the footage, voices or exports. Never commit `.env`.

Run tests with `.venv/bin/python -m unittest discover -s tests -v`. Tests create synthetic fixtures and do not require episode media, Gemini keys, transcription models or paid requests; FFmpeg integration checks are skipped if FFmpeg/FFprobe are unavailable. See [the general workflow](docs/workflow.md) and [confirmed series decisions](docs/series.md).

The current English review uses an editable nine-cue orchestral score rather than a single repeating background loop. See [scene-based score and offline rendering](docs/production.md#current-english-review-scene-based-underscore-v002). English v007 is accepted. The owner has authorized matching Mandarin and Malaysian Malay editions using the same picture, FLH bumpers, scene score and overlay subtitle design.

Distribution planning: [YouTube audio tracks and social-video preparation](docs/distribution.md). GitHub contains the production scripts, registries and manifests; media storage is separate, as described in [the storage assessment](docs/github-media-storage.md).
