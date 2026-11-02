# Restoring Dino Adventures media

Git stores scripts, episode settings and the checksum-pinned small asset set. Large media lives in the shared Dino_Stories Google Drive. Existing two creator editors retain access. One Family Learning Hub channel uses three Dino Adventures language playlists.

Use Episodes/EP01_Save_the_Moon or EP02_Broken_Bridge/02_Final_Product/Videos for upload-ready captioned films. Subtitles, Audio and Clean_Master are separate deliverables. Source material stays in01_Editing; precise additional recovery inputs are in Footage/Source_Files, preserving repository-relative paths. Shared fonts/soundfont/branding runtime inputs are under Library/Runtime_Assets. These are backups, not new creative versions.

The full machine-readable restore manifest is kept outside Git, in [Library/Restore_Manifests](https://drive.google.com/drive/folders/1RPkPvISfO5oUKeUkwcWeJUI27WSlBvZI). The verified [DINO_MEDIA_RESTORE_v001.json](https://drive.google.com/file/d/1xBSeichbt3wHHdU5H8humc6X_pnajC_5/view) maps750 exact repository paths to Drive IDs, sizes and SHA256 checksums. Obtain it with an authorized Drive connection. Do not restore from a historical delivery manifest that predates the current final selection.

With Python3, rclone and an already authenticated `GDrive:` remote:

```sh
python3 tools/check_git_assets.py
python3 tools/dino.py pull --manifest /path/to/DINO_MEDIA_RESTORE_v001.json
```

For an isolated recovery test, add `--destination-root /path/to/empty-folder`. To restore one entry, add `--only episodes/.../exact-file.wav` using its recorded path. Existing identical files are skipped; differing files cause an error and are never overwritten. Every downloaded file must match its recorded size and SHA256 before installation. This command does not generate voices or incur model-generation charges.

Original sources are preserved. Local caches and backed-up derived exports may be removed only after coverage and recovery checks. Secrets stay outside Git and shared source backups; environment setup and authentication must be configured separately.
