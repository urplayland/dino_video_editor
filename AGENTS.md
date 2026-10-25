# Dino Adventures workspace

This repository supports post-production for the whole Dino Adventures series.

- Preserve original sources. Never overwrite, delete, or re-encode originals as a cleanup step.
- Put episode-specific content in `episodes/<slug>/` and confirmed reusable assets in `library/`.
- Keep media, caches, inventories, and exports out of Git using the repository ignore rules.
- Keep the episode template and helper compatible. Use project-relative paths.
- Treat missing creative decisions and source metadata as unknown. Do not fabricate timecodes, dialogue, asset contents, licensing, approval, or export settings.
- Read kit instructions and the episode plan before editing. Record changes and review results in the episode plan.
- Do not publish or upload episode media unless the user requests it.
- Prefer a small dependency-free helper over introducing an application or framework without a concrete need.
