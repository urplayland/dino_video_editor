# Episode edit plan

## Brief

- Goal:
- Source instructions / conversation notes:
- Editor and project filename:
- Source inventory report:
- Source timecode convention and frame rate:

## Cue sheet

Fill in timecodes only after inspecting the footage. Specify the source or timeline used for each range and use asset paths from the episode or shared library.

| Timeline in | Timeline out | Source / asset | Action | Audio treatment | Review notes |
| --- | --- | --- | --- | --- | --- |

## Export settings

Pending confirmation. Record destination, container, codecs, dimensions, aspect ratio, frame rate, audio sample rate, channels, loudness target, and caption delivery as applicable.

## Review

- [ ] Source media and kit instructions reviewed.
- [ ] Story, cuts, titles, and credits reviewed.
- [ ] Dialogue, sound effects, music, and synchronization reviewed.
- [ ] Captions reviewed, if applicable.
- [ ] Full exported file watched and technical properties verified.
- [ ] Feedback resolved and approval recorded.
- [ ] Project, sources, shared assets, report, and approved export backed up.

## Change log

| Date | Version | Changes / feedback | Approval |
| --- | --- | --- | --- |

## Shared SFX and music

- `sfx-cues.json`: identify scenes and set cue times only after actual-video review.
- `audio-production.json`: supply aligned EN/ZH/MS dialogue stem paths/checksums,
  music/ambience sources and provenance, actual duration and picture checksum.
- Keep unknown times/duration null and status draft; reviewed production rejects them.
- Pin registry/preset versions and retain editable stems and review reports.
- See `docs/sfx-and-mixing.md`; no episode media or provisional voices are approved
  merely because a schema or FFmpeg check passes.
