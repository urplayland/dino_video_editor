# GitHub and Google Drive responsibilities

GitHub repository: https://github.com/urplayland/dino_video_editor

Drive root: https://drive.google.com/drive/folders/1wOs05ILi2Pzba6vMt1eB1ja1cSplfsHa

| Material | Authoritative home | Purpose of any other copy |
| --- | --- | --- |
| Python tools, tests, schemas, requirements, templates | GitHub | Old Drive project snapshots are redundant only when exact content is verified in Git history. |
| Voice/SFX registries, cue/timing/production JSON, selection/status manifests | GitHub | Drive handoff copies can stay where editors need them; do not confuse delivery metadata with redundant code. |
| Curated small reusable SFX, bumpers, ending cards, MIDI and approved reference assets | GitHub's explicit checksum allowlist | Selected Drive copies support editing/downloads and may be dependencies of the restore manifest. |
| Original animation/audio, alternate takes, scene references, native Story Bible/guidelines | Google Drive | Git stores instructions/references; original sources are preserved. |
| Full-length dialogue, raw voice takes, music/ambience/SFX stems and complete mixes | Google Drive | Working local copies can be restored; generated mix caches are not new source assets. |
| Current complete EN/ZH/MS movies, clean masters, SRT/ASS and publishing artwork/copy | Each episode's Google Drive Final_Product/Publishing folders | Git pins selection/settings/links; complete films and stems stay out of Git. |
| Large fonts/soundfont and notices | Google Drive | Runtime/source dependency bytes are restored by exact file ID; do not delete them with a code snapshot folder. |
| Recovery inventories, Drive IDs/hashes and cleanup execution reports | Library/Restore_Manifests on Drive; ignored local work/ | Detailed inventories stay outside Git. |
| API keys/OAuth credentials | Runtime secret configuration | Never Git or shared Drive kits. |

Small editor-facing indexes, guidelines, status files, licensing notices and publishing settings can intentionally exist in both locations. Their Git copy controls reproducible builds; the Drive copy makes the episode usable by editors. Do not automatically delete all matching files.

## Audited cleanup handoff — 2026-11-03

Verified remote GitHub main matched local commit `9c14728c01a53896fdbc92d8a21692afe0108338`. At that baseline Git contained290files/31,942,681bytes, including100checksum-pinned small assets. No tracked runtime secret files were found. The audit confirmed all750 existing recovery paths against current Drive IDs/size/SHA256 and all six selected EP1/EP2 final videos against their pinned release hashes. Drive listed1092files/4,927,936,148known bytes; native Google document storage is not inferred from missing sizes.

The explicit [Drive cleanup candidate manifest](https://drive.google.com/file/d/1jRBN3npWY59WxhXS7vbxO4GYYnggRp9p/view) lists166file IDs/26,535,085bytes:143exact current Git copies in the EP2 Project_Source snapshot,17exact historical source versions retained in reachable Git commits,and6superseded v002 ending-card assets already in Git. Each entry pins Drive path/ID/size/SHA256 and immutable Git commit/path. None is referenced by the existing recovery manifest. Historical commits are ancestors of the audited pushed main; matching a filename was not accepted as evidence.

Everything outside that explicit list remains untouched. In particular, keep the large soundfont/fonts and four recovery-linked Git duplicates inside Project_Source; that folder cannot be deleted as a whole. Preserve current ending cards, source takes, licence/provenance records, native documents, all final/publishing products, restoration manifest, indexes and collaborators. Apparent duplicate scene/reference bytes serve different creative roles and were excluded.

This handoff has not deleted or moved any Drive file. The other ChatGPT session must recheck current state and accessible Git content before any deletion, use recoverable Trash only, record results and update mutable current indexes. If it cannot perform recoverable trash or content/dependency verification, it must report that limitation without claiming success. Historical manifests remain unchanged. See [the ready-to-paste prompt](drive-cleanup-prompt.md).
