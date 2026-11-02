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

Pending external choices:

1. Top-level merge/access. EP1/channel assets are private. Dino_Stories/EP2/EP3 has two additional writers. Moving EP2 into the private Episodes container removed those writers; it was immediately rolled back. No permissions changed via an API. Owner must choose common collaborative access (would grant those members access to currently private EP1/branding) or private-only access (would remove their existing inherited story access). Do not silently choose either.
2. Channel routing. Earlier confirmed record: @familylearninghub-flh, one channel/three language playlists. Latest owner wording mentions three channels. No three channel URLs were provided or verified. Downloadable videos are ready; account routing must be clarified before altering channel profiles or publishing automatically.
3. Complete media restore mappings/recovery coverage. Only after all retained original/current inputs have verified Git or Drive counterparts and recovery tests can the remaining server media be offloaded. This implementation performs no further original/server source deletion. Runtime credentials must remain separate from Git.

Audits: ignored work/unified-storage/{dino-before,stories-before,within-access-move-plan,within-access-move-log,episode-doc-upload-log,full-mix-qa,tests-final}. No existing archival manifests were overwritten; mutable current indexes/guides are updated to the new paths. Released EP1 and all six selected final movies retain their exact identities.
