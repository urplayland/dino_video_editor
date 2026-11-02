# Proposed unified series storage

Status: inspection and proposal requested by the owner,2026-11-02. This document does not approve a migration or assert that all media is backed up. No media moved, added to Git or deleted in this inspection.

## Observed split

- Drive Dino(id1rnP1qvd2bm3JYTuqtoskPGeOWM40mPM9) holds Dino_Saves_the_Moon and FLH_YouTube_Launch_Kit_v001.
- Drive Dino_Stories(id1wOs05ILi2Pzba6vMt1eB1ja1cSplfsHa) holds Characters,EP2,EP3,Story_Ideas. The two roots have different observed sharing states; audit actual permissions before merging parents. Do not silently enlarge access.
- Repository episodes/save-the-moon and episodes/rainbow-bridge are actual episode configurations with established relative paths. episodes/audio-system-verification is an engineering fixture, not evidence of a separate story. The owner's separately mentioned demo/demo story has not yet been identified; do not rename it or assign an episode number by assumption.
- Existing helpers/templates already support reusable registries, episode manifests, audio cues, final selection, publishing copy and channel artwork. Extend these rather than introduce another app/project.
- Current checkout totals roughly11GB including6.7GB EP1,2.9GB EP2,320MB library,296MB incoming and424MB virtualenv. These are observed local folder sizes, not a verified cleanup allowance. Original sources must not be removed merely because another file has the same name.

## One series entry point

Proposed logical Drive layout; actual folder moves need verified source/destination mappings:

```text
Dino_Adventures/
  00_START_HERE.md
  Library/
    Characters/             # character identities/reference art
    Branding/
      Channel/              # ONE avatar/banner/channel setup, not per episode
      Intro_Outro/          # approved common bumpers + language/title variants
    Audio/                  # reusable SFX, approved voice references, music sources
  Episodes/
    EP01_Save_the_Moon/
      00_START_HERE.md
      01_Editing/           # source picture, editable audio/subtitles, production inputs
      02_Final_Product/     # selected EN/ZH/MS only
      03_Publishing/        # episode covers, copy, checklist, website handoff
    EP02_Broken_Bridge/
      # exactly the same three subfolders and entry guide
    EP03_<confirmed-title>/ # keep its actual current title until verified
      # same layout when material exists; do not fabricate empty deliverables
  Story_Ideas/              # unassigned ideas, before an actual episode exists
```

Each real story has one home. A story prototype/demo is a status of that story, not another project root or another publishing kit. Use draft/demo/review/approved/released only with evidence. Engineering demos belong under tests/fixtures, and reusable starter instructions under templates/episode. Retain helper/test compatibility when moving the existing engineering fixture.

Episode-specific cover/title/description files from the old channel launch kit belong under EP1/03_Publishing. Only channel-wide identity/setup stays in Library/Branding/Channel. EP2 keeps its own covers/copy under its own03_Publishing. Do not duplicate global channel setup in every episode.

In Git keep the existing lowercase library/,episodes/,config/,tools/,tests/,templates/ structure and stable episode slugs. Store episode number/display name in a central index referencing episode.json/distribution-selection.json/youtube-release.json. Human Drive labels may include EP01/EP02; restore mappings must preserve the exact existing repository paths rather than rename hundreds of frozen references.

## Git versus Drive

Already in Git: Python helpers, schemas, episode text/timing/creative configs, voice/SFX registries, mixing/music recipes, subtitle/branding style settings, source hashes/selected-release pointers, tests and docs.

Candidate small immutable media to pin in Git, retaining recorded status/provenance:

| Asset group | Observed payload | Proposed treatment |
|---|---:|---|
| Procedural SFXv002:33 WAVs +33 sidecars |25,058,850bytes | Git with recipes/checksums; pending-listening statuses stay pending |
| EP2 stone activation/bridge-air variants:4 WAVs +4 sidecars |2,164,154bytes | Pin current episode assets; do not silently promote all to approved series presets |
| Approved Puck chuckle and Leda clue/reference metadata |183,975bytes | Git; preserve provider/source metadata and approved IDs |
| Current FLHv004 intro/outro +provenance |245,339bytes | Git; supersededv003 is not the default |
| FLH logo/mascot and composed logo sting |967,329bytes | Git with existing FLH source attribution |
| Existing shared decorative background +generation record |1,692,513bytes | Git one canonical copy; manifests can point to it |
| EP2 accepted English/Chinese/Malay endings +sidecars |232,889bytes | Git pinned at current paths or explicit compatible mapping |

These candidate groups total30,545,049bytes before optional fonts/icons. Do not blanket-unignore library/media or every MP4/WAV. Add a narrow allowlist for the accepted assets and retain default ignore rules for episodes' source/exports/work/reports. The starter-kit samples have no separate licence/creative approval in their catalog and should not automatically be committed as approved reusable assets.

Font follow-up: existing Outfit/Nunito notice is a298byte summary with links, not complete bundled licence text. Collect complete matching notices before packaging fonts. Existing Noto notices are present. Large CJK fonts can remain Drive-restored runtime assets; small Latin fonts may be pinned with complete notices. Do not invent permission or public-domain labels.

Drive retains originals, full story/final MP4s, full-length dialogue/music/ambience/SFX stems, long voice takes, large fonts/instruments and one canonical publishing delivery. The FluidR3 soundfont alone is148,398,306bytes; selected episode videos are roughly164MB each. Do not commit these to ordinary Git or add an LFS billing dependency without owner authorization.

GitHub's official documentation blocks ordinary Git files over100MiB and recommends small repositories, ideally under1GB:
https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github

## Server can become a cache only after verified recovery

1. Establish the unified series/episode index and canonical Drive homes. Inventory existing folders, permissions and IDs first; preserve original source files, IDs, native Google Docs and shared links during migration.
2. Pin the chosen small Git assets, full required notices and provenance. Verify clone/checksums, then commit/push. Keep Git media narrowly versioned; do not create copies per episode of common branding/audio.
3. Build authoritative Drive restore manifests containing repository-relative path,Drive file ID,bytes,SHA256 and asset role. Keep generated inventories on Drive/ignored reports; track only schemas, the compact root/manifest references and restoration tooling in Git. Reuse existing production/episode manifests for selections.
4. Verify every retained original/current input has an exact Drive or Git counterpart. Large original handover packages, approved source takes and never-regenerate items must be accounted for. Rebuildable caches need recipes/source dependencies, not compulsory duplicate backups.
5. Extend the existing helper with on-demand pull and cleanup commands. Proposed capabilities, not currently implemented commands: fetch one episode/language or shared asset group; download to a temporary file; verify SHA256; install at the exact relative path; refuse path escapes/symlinks/overwriting changed files. Use existing authenticated Drive/rclone access, never include credentials in Git.
6. Test recovery into a separate empty directory and run existing configuration/media checks without paid generation. A successful upload is not proof of recovery. Only then offload the verified server media copies and caches. Canonical original bytes remain protected in the verified archive; do not delete source material based on filename/status guesses.
7. Keep Git checkout and the selected small Git assets locally. Runtime secrets stay out of Git and must be handled separately; never delete.env or account credentials as generic cleanup. Virtualenvs and model caches are rebuildable from pinned setup instructions; scope cleanup to this workspace, not other server projects.

No Drive merge or source offload has been performed as part of this proposal. Episode1/2 released media and voice identities are unchanged. The FLH website addition remains a separate later task.
