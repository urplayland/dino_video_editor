# Dino Adventures — video post-production

A reusable workspace for editing the Dino Adventures series. Each episode has its own sources, editing plan, project files, and exports. Reusable audio and other series assets belong in the shared library.

The first episode is **Dino Save the Moon** (`save-the-moon`). Its video and audio kit have been imported and technically checked; see [the validation record](episodes/save-the-moon/source-validation.md). Editorial review and approved timing, audio mix, and export settings are still pending.

## Layout

| Location | Purpose | In Git? |
| --- | --- | --- |
| `incoming/` | Temporary landing area for supplied files | Instructions only |
| `library/catalog.csv` | Reusable asset descriptions, provenance, and usage notes | Yes |
| `library/presets/v001/` | Versioned voice and sound-effect presets, with approval status | Yes |
| `library/media/` | Shared audio, graphics, fonts, and other media | No |
| `templates/episode/` | Starting documents for every episode | Yes |
| `episodes/<slug>/episode.json` | Episode identity and source references | Yes |
| `episodes/<slug>/edit-plan.md` | Timing, editorial decisions, and review checklist | Yes |
| `episodes/<slug>/media/` | Episode originals and derived media | No |
| `episodes/<slug>/project/` | Editor project files and supporting notes | Yes |
| `episodes/<slug>/work/` | Temporary render files and caches | No |
| `episodes/<slug>/exports/` | Review and final deliverables | No |
| `episodes/<slug>/reports/` | Generated local inventories | No |

## Get started

Python 3.9 or newer is required. The helper uses the standard library; there are no Python dependencies.

```sh
python3 tools/dino.py doctor
python3 tools/dino.py init another-adventure --title "Dino's Next Adventure"
python3 tools/dino.py inventory save-the-moon
python3 tools/dino.py verify save-the-moon --report episodes/save-the-moon/reports/<inventory-file>.json
```

`init` refuses to overwrite an existing episode. `inventory` records SHA-256 hashes, sizes, and media metadata when `ffprobe` is available. It inventories the episode's `media/` and the shared `library/media/`; it does not import files or extract archives. Each run writes a new report.

For new deliveries, copy the supplied ZIP and MP4 into `incoming/` first, then follow [the workflow](docs/workflow.md). The Save the Moon sources are already under `episodes/save-the-moon/media/originals/`; the supplied root copies have also been retained locally.

`ffprobe` and `ffmpeg` are optional for workspace setup. The helper searches PATH and conventional Homebrew locations. Set `DINO_FFPROBE` or `DINO_FFMPEG` to override their executable locations. An inventory without `ffprobe` records file integrity but cannot verify stream properties. Neither tool is bundled with this repository.

Run helper regression tests with `python3 -m unittest discover -s tests -v`. The kit's voice-generation API integration has not been validated; dry-run previews do not establish provider compatibility.

## Project rules

- Preserve original media; make derived files separately.
- Keep episode-specific material out of the shared library until its reuse is confirmed.
- Record source provenance, credits, and any known usage restrictions.
- Use relative project paths so a copied workspace can be relinked.
- Record approved settings and editorial decisions per episode; do not infer them from another episode.
- Back up media separately. A Git clone contains plans and tooling, not the videos or shared assets.

See [the editing workflow](docs/workflow.md) and [the series notes](docs/series.md).
