# Shared media

Store confirmed reusable assets here, grouped by purpose, such as `audio/music/`, `audio/sfx/`, `graphics/`, or `fonts/`. Add a row to `../catalog.csv` for each asset that will be reused.

Preserve original filenames where possible. Reference files by repository-relative path. Do not assume that the supplied audio kit is series-wide until its contents and instructions are reviewed.

Large media payload is ignored by Git and needs a separate verified backup.
Owner-selected small immutable assets are now explicitly pinned by
`library/presets/git-assets-v002.json`; only those paths are allowed through
the ignore rules. Run `python3 tools/check_git_assets.py` before committing.
This storage selection does not change creative approval or provider/licence
metadata. Fonts and the large soundfont remain separately restored assets.
