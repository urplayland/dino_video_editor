# Unified story storage — implementation status

Owner approved the per-episode structure and clarified that the earlier word was Dino, not demo. No demo-story category was introduced.

Implemented:

- EP1 and EP2 each have Story_Bible,Guidelines,Footage,References,Production under01_Editing; Videos,Subtitles,Audio,Clean_Master under02_Final_Product; and episode-specific03_Publishing.
- Original native EP2 Story Bible retained unchanged. EP1's new Bible reference explicitly records that no separate authoritative Bible was found instead of inventing a narrative/transcript.
- Per-language statuses and episode indexes are in Git and Drive. EP3 has a source-not-yet-established index and the three standard top-level containers; no final media or title is fabricated.
- EP1 cover files/episode copy separated from channel-wide branding. Existing Channel branding is under the private Library/Branding. Public/shared source groups have not been merged into that private root.
-64 within-access moves verified old/new parents and identical access-role sets. Original files retain IDs and media bytes. Four empty legacy containers removed only after empty-list checks.
- EP2 independent stems/SRT/ASS preserved and grouped as final products. Three complete47,952,102byte48kHz stereo24bit WAVs decoded from existing final AAC, each166.5s; PCM hashes match final audio exactly. No TTS, animation regeneration, new paid service, YouTube upload or website deployment.
-96 small immutable Git assets,30,559,904bytes: versioned procedural SFX, existing episode effect/ending assets, FLH bumpers/logo/background/sonic mark, approved voice references and original MIDI. Existing creative/provider/licence metadata preserved, including pending-listening status where applicable. Large fonts/footage/full stems/soundfont remain ignored. Full font notices must be collected before adding font binaries.
- Narrow ignore allowlist/checksum validator added; unrelated media/work credentials still ignored. Engineering fixture source lives in tests/fixtures, with helper/docs updated. Reusable episode template now includes Bible/guidelines/status/index and init fills identity correctly.
- `tools/dino.py pull` restores from a repository-path/Drive-ID/size/SHA256 manifest using an existing authenticated rclone remote. It validates paths, refuses changed existing destinations, stages downloads and atomically installs verified bytes. A real1505byte final SRT was restored into a separate empty tree by stable Drive ID; no existing source overwritten. Restore manifests are ignored metadata, not proof that every current input has already been mapped.
-78 regression tests passed, including checksum/path/credential/ignore protections and corrupt-download/no-overwrite tests. Pinned assets are separately checksum verified.
- A clean local Git clone verified all96 pinned assets and excludes large original/export media and.env. The relocated engineering fixture was actually rendered through all three synthetic language outputs; the mixer accepts only the explicit test-fixture namespace in addition to its existing episode namespaces. Generated fixture/download/mix staging caches were removed after validation, not archived as stories.
- Final cloud readback preserved all716 pre-existing files by ID:710 byte/hash-identical and six intended current-guide/index updates. All six selected EP1/EP2 movies retain pinned SHA256s. Three new complete mixes and all new status/Bible-reference/guideline/index documents verified by remote SHA256/size. Mutable current indexes match actual paths and hashes; historical manifests untouched.

Current follow-up — 2026-11-02:

- Owner confirmed shared Dino_Stories access with the two existing editors. Episodes and Library now reside there; EP1/EP2/EP3 use the same structure. The old private empty root was removed. All sources preserved.
- One Family Learning Hub channel, three language playlists. Channel profile, episode statuses and indexes agree. No automatic social publishing.
- EP2 English stays v001; ZH/MS v003 endings use Dino Adventures with 完/TAMAT. Full decode, unchanged audio and exact story-frame preservation verified; new final files and current download guides are on Drive. v002 inputs remain in Production/Source_Video_Inputs.
- The small Git registry is now v002:100 files/30,704,692bytes including both current localized ending cards.78 regression tests passed.
- Complete original/current-runtime source backup and restoration mapping are in progress. Original sources remain on the server under AGENTS.md; only reproducible or precisely backed-up derived media may be removed. Historical Drive manifests remain unchanged.

Audit records are ignored under work/unified-storage and work/unified-finish.
