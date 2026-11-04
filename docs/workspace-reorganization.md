# Workspace reorganization — 2026-11-04

The owner requested cleanup, a layout for both Dino and Milo, and committing/pushing the resulting work. The previous Dino Git history and existing remote are retained as one workspace repository.

| Previous location | Current location |
|---|---|
| `dino_video_editor/` | `series/dino/` |
| `milo_ep1/` | `series/milo/episodes/learn-shapes/` |
| Root YouTube Python helpers | `tools/publishing/` |
| Root channel policy and playlist metadata | `config/publishing/` |
| Root YouTube OAuth clients/token | `secrets/` (ignored, private permissions) |
| Root Codex diagnostics | `local/diagnostics/` (ignored) |
| Milo earlier EN review exports | Episode `archive/reviews/` (ignored) |

The root `.env` remains private and ignored; the Python environment remains `.venv`. A pre-change Git bundle, the prior uncommitted Dino patch and Milo's unborn Git metadata are retained under ignored `backups/restructure-20261104`. There was no Milo commit history or remote to merge.

Milo scratch cleanup removed 113 temporary/cache files totaling 965,484,911 bytes. Original source hashes and all24 formal final files were verified first. Raw voice takes, approved final videos, subtitles, audio tracks, fonts, score, source picture and prior review exports remain retained. The reusable 48kHz score PCM and retouch sky plate moved into `media/derived`; final assembly no longer depends on deleted scratch files or active review exports. Historical QA records may contain old absolute paths; those remain historical evidence, with the migration table above supplying the current locations.

On Drive, the 18 superseded review files were archived under `Videos/Milo/Episodes/EP01_Learn_Shapes/01_Editing/Production/Archive/Reviews/{Videos,Subtitles,Audio}/EN`, retaining their file IDs. Active `02_Final_Product` keeps the 24 approved final deliverables. Original sources, finals, sharing permissions and the shared `Videos/Production_Guidelines.md` are preserved.

The owner approved EN/ZH/MS and reported publication. The last read-only YouTube check observed ZH/MS public and EN private; no publication settings were changed during cleanup. Completed-upload records remain local to prevent duplicate uploads.

No current video was re-exported. Future final delivery follows the shared uncompressed-video/PCM-audio instruction. Existing rendering implementations retain their historical behavior for EP01 and must be adapted before use on future final deliveries.

## Validation

The relocated Dino suite passed all 78 tests. Its selected-media policy verified 100 pinned files (30,704,692 bytes). Milo helper imports, resource paths, Python syntax and JSON parsing passed; original-source and all24 final-file checksums remained unchanged. The moved YouTube helper verified the existing channel with upload/read-only scopes and deletion blocked. Staged content was checked against configured credential values; private credentials, full deliveries, reports, caches and backups are excluded from Git.

## Local files reconciled after pull — 2026-11-04

In this checkout, pulling41c0765 moved tracked Dino files into series/dino but left ignored local originals/runtime media/reports at the old root paths. The owner authorized removing unused leftovers. Merged1463non-colliding local files/2,969,919,199bytes from root episodes,incoming,library,work into the corresponding series/dino locations. Each move retained device/inode,size and mtime; originals were relocated without overwrite, deletion or re-encoding. Removed the four empty legacy roots and43ignored Python bytecode cache files/545,791bytes. Shared root tools/publishing,config,docs,.env and.venv retained. No Drive or credential changes.

Ran the78Dino regression tests from series/dino; all passed. The100pinned small assets/30,704,692bytes also verified at the new root. Detailed move/cache/result inventories and test log are ignored under local/diagnostics/dino-layout-migration-20261104. This was a directory reconciliation, not a3GB storage deletion; retained source material remains available locally.
