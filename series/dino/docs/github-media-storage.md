# GitHub media storage check — 2026-10-25

This is a read-only capacity check. No media was committed or uploaded to GitHub; repository ignore rules remain in effect. The owner's remaining account quota and billing settings have not been queried.

| Method | Relevant published limits |
| --- | --- |
| Regular Git | Files above 50 MiB warn; files above 100 MiB are blocked. Browser uploads are limited to 25 MiB. Repository guidance favors small code repositories. |
| Git LFS on GitHub Free | Included storage 10 GiB and download bandwidth 10 GiB per month, attributed to the repository owner's account. Maximum file size 2 GB. Each changed full-file version adds storage; this is not 10 GiB for every repository. |
| Project Release assets | GitHub's large-file documentation says release binary total size and download bandwidth are not limited; individual assets must remain below the applicable plan's LFS file limit (2 GB for Free). This is distinct from the LFS allowance. |

Official references: [LFS billing and free allowances](https://docs.github.com/en/billing/concepts/product-billing/git-lfs), [LFS per-file limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage), [large-file and Release guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

Measured original mixed MP4 is 69,862,751 bytes (69.86 MB); English v007 is 53,592,133 bytes (53.59 MB). Together these are about 123.45 MB. Each is below the regular Git hard limit but above its warning threshold; LFS or project Release assets keep large media out of code history. The current episode's source and three completed editions fit comfortably within the *included* LFS capacity, assuming enough of the owner's shared allowance remains. Exact initial measurements are retained in `episodes/save-the-moon/reports/github-storage-check.json`.

The owner asked to check first, so no GitHub upload, publication, LFS setup, billing change or Git ignore exception has been made.
