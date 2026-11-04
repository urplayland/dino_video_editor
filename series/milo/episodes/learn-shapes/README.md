# Milo Series post-production

EP01: Let's Learn Shapes! Formal EN/ZH/MS releases use the owner-selected Achernar voice, the approved 1,207-frame 1280×720/24fps picture with its requested circle removal, existing FLH logo/jingle, original instrumental score and matching overlay subtitles. With branding, each movie is 1,315 frames / 54.791667 seconds.

Code/configuration live in the unified workspace Git repository; original media, runtime assets, cached models, takes, review exports and reports are ignored and retained separately. No credentials are tracked. The `series/dino` directory supplies shared production helpers, the approved FLH logo/jingle and its provenance. The workspace root `.env` is read privately for the explicitly selected `GEMINI_API_KEY`; it is never copied.

## Reproduction

Shared owner guideline for Milo and Dino: [Videos/Production_Guidelines.md](https://drive.google.com/file/d/1mfEJlUVYEakgr9LQ2Zs200RG9WFLil8M/view). Read this common Drive reference before future production. Local source: `../../../../shared/Production_Guidelines.md`.

Future final-export requirement (owner instruction, 2026-11-04): deliver uncompressed video masters with PCM audio, rendered directly from the editing timeline. Let YouTube/Facebook handle platform encoding; do not default final delivery to H.264/H.265 or AAC, or convert an already compressed review into an uncompressed master. Preserve source resolution/frame rate and verify actual codecs and full-output QA. See the shared `../../../dino/docs/production.md` guide. Current Milo EP01 files and uploads are explicitly exempt and stay unchanged. The current scripts encode compressed MP4s and must be adapted before use for future final deliveries.

Use the workspace Python virtual environment with faster-whisper, PyAV, Pillow, NumPy and SciPy. FFmpeg/FFprobe and FluidSynth are required. Restore the source files and checksum-pinned branding fonts before use. See `edit-plan.md` and the original Drive handoff for sources, approvals and limitations.

Run `generate_voice.py` to resume exact cached speech requests; generation makes live Gemini calls only for missing groups, with no automatic retry or credential rotation. `build_assets.py` derives landscape identity clips and the offline score. `assemble_en_v1.py` fits checked dialogue and writes the versioned complete review; it refuses to overwrite the output movie. `verify_en_v1.py` checks full decoding, source-picture continuity, subtitle previews, loudness/peaks, original hashes and final encoded dialogue.

The owner approved English v002 and requested formal EN/ZH/MS versions. Formal EN is byte-identical to the approved English movie. Six shapes remain: triangle, square, oval, rectangle, star and diamond. The original Square-to-Oval framing jump is retained. Original media and earlier reviews are preserved. The owner approved the English, Mandarin and Malay versions and reported publication on 2026-11-04.

`formal_release.py` creates localized plans and generates independent complete lines, caching exact request fingerprints and hashes. Select a key explicitly from the recorded owner-authorized free-tier pool; it stops on quota and never enables billing. `assemble_localized.py` runs separate align/master/render stages to bound memory on this small server. No internal speech cuts are used; full-line fit is limited to 10% speedup. `verify_formal.py` checks geometry, complete decoding, every story-frame position, captions, source hashes, loudness and local encoded-mix transcription.

Drive delivery: `Videos/Milo/Episodes/EP01_Learn_Shapes/02_Final_Product/{Videos,Subtitles,Audio}/{EN,ZH,MS}`. Videos are named `Milo_EP01_<LANG>_Final_v001.mp4`; subtitles/audio are under `Final_v001` within their respective language folders. `Videos/Milo/Library` remains the shared library. Empty legacy folders were removed; CN/BM language folders were renamed in place to ZH/MS.

The owner requested private YouTube uploads, then approved all versions and reported publishing them. The last read-only check observed ZH/MS public and EN private; no visibility changes are made during cleanup. `youtube_private_upload.py` permits only these three checked finals, verifies the connected channel, persists resumable sessions privately, and sets private visibility with child-directed audience and language metadata. It cannot publish, delete, or write playlists. Existing narrow OAuth scopes remain `youtube.upload` plus `youtube.readonly`. Playlist assignment remains manual in YouTube Studio.

## Archived reviews and cleanup

Earlier local EN review exports are retained under `archive/reviews/EN_v001` and `archive/reviews/EN_v002`. Drive reviews are under `01_Editing/Production/Archive/Reviews/{Videos,Subtitles,Audio}/EN`; active final delivery holds only the approved files. Raw voice takes, originals, final exports, branding and QA records remain retained. Disposable model caches and scratch renders were removed after checksum verification. The reusable score PCM and retouch sky plate now live under `media/derived`.
