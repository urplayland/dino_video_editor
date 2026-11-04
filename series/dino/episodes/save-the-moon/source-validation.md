Current-delivery update: the complete handover was restored from the owner-provided Google Drive link on 2026-10-25. See the appended validation and current episode plan. Earlier references to root copies or the originally named kit ZIP are historical.

# Save the Moon — source validation

Checked on 2026-10-25. This is a technical intake record, not an editorial approval.

## Original video

- Filename: `Dino_save_the_moon_20261021165509.mp4`
- Size: 69,862,751 bytes.
- Container duration: 70.927018 seconds.
- Video: H.264 High, 720 × 1280, progressive, 1,694 frames.
- Reported nominal frame rate: 24/1; average: 26019840/1089439. Review frame timestamps before choosing a constant-frame-rate timeline or conversion.
- Audio: AAC-LC, 48,000 Hz, stereo; stream duration 70.912 seconds.
- Full audio/video decode with FFmpeg completed without reported errors.
- SHA-256 of the imported copy matches the supplied root original; recorded in `episode.json`.

## Audio kit

- Filename: `Dino_Adventures_Audio_Kit.zip`; 502,354 bytes.
- ZIP CRC check passed; extraction paths were checked before extraction.
- Five included WAVs: footsteps, rumble, whoosh, chime, pop. All ten WAV copies (original extraction and shared library) were successfully probed in the inventory.
- Shared voice and SFX preset JSON files were preserved unchanged under `library/presets/v001/`.
- Voice script dry runs completed for English, Mandarin, and Malay with zero API calls.
- Provider API behavior, model availability, generated speech quality, and lip synchronization have not been tested.
- Dialogue is explicitly labelled `AUDITION_EXAMPLES_NOT_VERIFIED_FILM_DIALOGUE`; all dialogue and SFX timings are unset.
- Voice styles are provisional reconstructions. SFX are synthetic placeholders. No separate license file was included.

## Reuse and remaining review

The source ZIP, extracted files, and imported MP4 are preserved under `media/originals/`. Root originals also remain unchanged. Media and detailed generated reports are local and ignored by Git; back them up separately.

Before editing: review the footage and original kit instructions, recover the earlier conversation's creative decisions, verify the transcript and cue timing, confirm presets, and choose editor and export settings. No production audio generation or final video edit has been performed.

## Restored production handover — 2026-10-25

Complete delivery safely extracted and preserved under `media/originals/handover-20261025/`; a checksum-verified copy of the archive is retained as `media/originals/dino-production-handover-20261025.zip`. Delivery hash: `750546b54d70cc0f2bfb15d663634292e31d1224dd09f25e61b615ccc0702878`.

Original MP4 hash is unchanged from the historical source record. Silent MP4 hash: `13a4c6e61bc3d986866d0c48cee202e2c88198fcf43a4a253affa901ff487a7f`. It has only H.264 video, 720×1280, duration 70.927018 s. Both MP4s fully decode without reported errors and share identical encoded picture hash `335c15662779ad14fdbac3777154341fb0ef208929ffdaa357767d31e2b3e934`. The separate original WAV is PCM 16-bit 48 kHz stereo, 70.912 s, SHA-256 `b2fac8c6a6bb95f2060fd0ba2195d5e8f77442cea0bd12d8d2828a087b0d5430`.

The restored kit contains all three Python scripts, JSON presets, five WAV effects and a sample cue manifest. Three additional generated audition WAVs last 11.04, 47.92 and 20.08 seconds. Their content was independently inventoried/transcribed; no character identity or production approval is inferred from their filenames. They contain audition material not present in the actual film. Active voice selections/styles match the kit JSON. A real Gemini TTS call has now succeeded; the earlier "untested" API statement remains historical. Current generation and review state is recorded in the episode plan and per-line reports.
