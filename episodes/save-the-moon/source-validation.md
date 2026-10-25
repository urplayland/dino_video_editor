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
