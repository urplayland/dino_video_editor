# SFX registry v002

Immutable snapshot of config/sfx_presets.json at this release. Five legacy IDs
and their existing paths/gains remain intact. Eleven new stable IDs (the ten
requested effects plus magical_ambience) each have three procedural variations.

The audio assets and per-file generation/checksum sidecars live outside Git in
library/media/audio/sfx/procedural-v002/. Reproduce using tools/sfx.py. No external
samples, paid APIs, downloads or GPU are used. New sounds are technically
validated; creative listening approval is distinct and is not fabricated.

Each cue pins preset_version. Append new IDs freely; changing an existing recipe,
asset, variation ordering/identity or gain requires a new preset/asset version
and a new registry snapshot. Do not overwrite the old asset/cache or this snapshot.
Imported professional assets need an explicit SHA-256, source/provenance and
licence on their variation. Verify actual reuse permissions before registering
third-party files. No public-domain/CC0 status is implied for project synthesis.
