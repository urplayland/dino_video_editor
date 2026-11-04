# Episode workflow

## 1. Prepare

Create an episode with `python3 tools/dino.py init <slug> --title "Episode title"`. Use lowercase words separated by hyphens. The helper copies the template and creates local media and output directories. Save the Moon already has a starter folder.

## 2. Import and inspect

1. Copy supplied files into `incoming/`. Preserve originals and original names.
2. List archive contents and read any included instructions before extraction. Reject paths that escape the destination folder. Extract into a separate folder; never directly over an episode or library directory.
3. Copy episode sources into `episodes/<slug>/media/originals/`. Put derived audio, proxies, and converted files under `media/derived/`.
4. Move only confirmed reusable assets into `library/media/`, and catalogue their provenance and usage information in `library/catalog.csv`.
5. Update `episode.json` with repository-relative source paths. Do not enter guessed stream metadata.
6. Run `python3 tools/dino.py inventory <slug>`. Review probe failures and confirm duration, stream layout, frame rate, resolution, and audio properties before choosing edit settings.

An inventory hashes files in the episode media folder and the shared library. It is a point-in-time record, not a backup. Shared assets can appear in more than one episode inventory. Symlinks are rejected so reports stay within the workspace.

Reports have a schema version and repository-relative media paths. After moving or restoring the whole workspace, run `python3 tools/dino.py verify <slug> --report <inventory-path>` to detect missing or changed recorded files. A successful verification covers files listed in that report; rerun inventory to discover added files. Keep the report in the media backup.

Shared presets are versioned under `library/presets/`. Create a new version when changing an approved preset; preserve the old version and record which version an episode used. A provider model identifier in a supplied preset is historical configuration, not a guarantee that a service still supports it. Review provider integration separately before making generation calls.

## 3. Plan and edit

Read the episode plan and kit instructions. Record precise in/out timecodes after reviewing the footage. Document whether each audio cue replaces or layers over existing audio. Save editor projects under `project/`; keep caches under `work/`. Refer to media through relative paths where the editor supports it.

Do not apply automatic trimming, noise reduction, music replacement, loudness processing, captions, or other creative changes before the desired treatment is established.

## 4. Review and deliver

Write review renders to `exports/` using `<slug>_review_v001.<ext>` and increment the version for each review. Record the exact export settings in the episode plan. Use `<slug>_final_v001.<ext>` after approval.

Review the entire render for story continuity, black or frozen frames, audio synchronization, abrupt edits, clipping, dialogue clarity, spelling, caption timing, credits, and unintended missing media. Verify the exported duration and streams. Record review findings and approval before marking the episode complete.

## 5. Archive

Keep the original media, shared assets referenced by the episode, editor project, plan, inventory, and approved export together in a backup that preserves relative paths. Verify checksums after copying. Git stores the documentation and helper but does not provide the media backup. Remove temporary work only after a verified backup and when the user requests cleanup.
