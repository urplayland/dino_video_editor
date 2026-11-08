# Dino environment retirement and recovery

The owner moved future Dino editing to another environment on2026-11-08. This server now keeps the Git workspace, editing/provenance records and shared runtime needed by Milo; it no longer keeps the verified large Dino media working set. The root environment and credentials remain local and private. No production video was regenerated and no remote service/cron changed in this cleanup.

The owner explicitly allowed removing local original-media copies **only after** verifying their intact Google Drive counterparts, overriding the usual no-original-cleanup rule for this retirement. Drive originals and approved products were not deleted or modified.737local files/2,593,682,694bytes were removed:1,799,092,237bytes of exact Drive-backed copies and794,590,457bytes of regenerable old mixes/compression/Python caches. Original directories were not removed wholesale. Unbacked source/provenance/QA records remain local. Shared Dino library files, Milo, publishing tools, private.env and the root Python environment were retained.

Restore on the new environment:

1. Clone the existing GitHub repository and use `series/dino` as the working directory.
2. Download [DINO_MEDIA_RESTORE_v002.json](https://drive.google.com/file/d/16HgAtIW5AMcQcG5yA2VHeyZB_24kRJBW/view) through an authorized Drive account. Its750repository-relative paths are relative to `series/dino`, not the unified Git root. Configure the existing `GDrive:` rclone remote securely on that machine.
3. Restore exact media without generation:

```sh
cd /path/to/workspace/series/dino
python3 tools/check_git_assets.py
python3 tools/dino.py pull --manifest /path/to/DINO_MEDIA_RESTORE_v002.json
```

Existing differing files cause an error instead of being overwritten. Each downloaded object is checked by size and SHA256. Private runtime credentials/authentication must be set up separately; they are not in Git or the shared Drive manifest. Do not copy an entire.env or credential directory into a public kit.

The manifest was freshly verified against all750Drive file IDs/size/SHA256 before retirement, uploaded and downloaded back for a byte-identical check. Three actual recovery downloads (EP1 voice source,EP2 voice source,original metadata) passed size/SHA256 validation. Six selected complete episode files remain pinned by the episode release manifests. Existing v001restore manifests/historical delivery records are unchanged.

Keep current downloadable finals under the existing Drive `Episodes/<episode>/02_Final_Product` folders. The manifest's storage folder is [Library/Restore_Manifests](https://drive.google.com/drive/folders/1RPkPvISfO5oUKeUkwcWeJUI27WSlBvZI). Episode-specific plans/configuration, voices, naming and shared production guidelines remain in Git. Future final video exports must follow `shared/Production_Guidelines.md` (uncompressed video/PCM); this retirement does not authorize re-encoding released episodes.

Detailed inventories, removal records, recovery checks and results stay outside Git under `local/diagnostics/dino-retirement-20261108`. The filesystem reached full capacity due to unrelated concurrent writes while preparing retirement; eight verified rebuildable old-cache files/163,416,672bytes were removed first, then counted once in the total above. No unrelated job, service, data or log was removed to make space.
