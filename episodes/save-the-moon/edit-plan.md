# Episode edit plan

## Brief

- Goal: Complete the entire 70.927-second episode in English, Mandarin Chinese, and Malaysian Bahasa Melayu, with reusable production tooling and verified rendered videos.
- Source instructions / conversation notes: Owner full-production instructions in this session; imported `media/originals/handover-20261025/DINO_CODEX_START_HERE.md` (prototype gate superseded).
- Editor and project filename: Python/FFmpeg; active manifest `episodes/save-the-moon/production.json`.
- Source inventory report:
- Source timecode convention and frame rate: Seconds from original/silent-master start; preserve picture timestamps (nominal 24 fps, variable average reported).

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

## Historical prototype brief and implementation — 2026-10-25

Superseded by the full production direction below. Earlier prototype limits and approval gates are historical, not current instructions.

Owner supplied the earlier pipeline brief in this session. Confirmed direction: Family Learning Hub; English/Mandarin/Malaysian Malay; Dino=Puck, Cloud Guardian=Charon, Moon=Sulafat; Gemini 3.8 Flash TTS; CPU-only Python/FFmpeg workflow on macOS and Ubuntu. Start with a real 8–10-second English scene and obtain review before expanding. Exact audition style prompts remain unknown. No film dialogue or timecodes have been added.

Current checkout inspection found no MP4, kit ZIP, extracted kit scripts or WAV payloads. Historical source-validation metadata has not been revalidated against source files. Owner is preparing the Gemini key in local `.env`; its value is never recorded here. No API generation has been authorized or performed during this implementation.

Added active persistent registries under `config/`, preserving original v001 imports; a dependency-free `tools/dub.py` with dotenv loading, explicit dry-run/live generation, per-line provenance, separate regeneration takes, validation, conservative time fitting and FFmpeg replacement mixing/rendering. Installed FFmpeg/FFprobe on this Ubuntu server. See `docs/dubbing.md` for setup and the API contract audit.

Remaining production gates: recover and inspect kit/media; one authorized English Dino API test; verify transcript/speakers/timing; select real scene; review original-voice separation or rebuild dialogue-free background; listen to generated lines; choose provisional review mix targets; render and review the complete real prototype. Formal JSON Schema support and automatic transcription/separation are not implemented.

| Date | Version | Changes / feedback | Approval |
| --- | --- | --- | --- |
| 2026-10-25 | pipeline-poc-foundation | Recovered brief; added registries and local dubbing helper; 16 local regression/integration tests passed, including an actual FFmpeg test-fixture render, decode, source-integrity and original-audio-exclusion check. No episode render or source modification. | Voice selections confirmed by owner; prototype pending |

Verification result: `python3 -m unittest discover -s tests -v` passed all 16 tests on this Ubuntu server with FFmpeg 6.1.1. Integration exposed an audio-timestamp/padding issue; sample-count timestamps and finite padding fixed it. Tests use synthetic fixtures and mocked Gemini responses, not production media or live API calls. `.env` contains a nonempty key and is mode 0600; no key value was displayed or added to tracked files.

## Owner direction — direct source-based generation, 2026-10-25

Owner authorized using the configured Gemini key to generate real dialogue based on the existing source audio, rather than a separate invented short audition. Owner reports Gemini 3.8 Flash TTS generation succeeded in another project. Proceed with source-based English POC generation when media is available; no further approval is needed for that authorized generation scope. This authorization does not permit a full three-language episode production before POC review.

Rechecked project, incoming, episode, shared-media and likely upload locations: no Dino source video, kit ZIP or character WAVs are available. Temporary synthetic debug WAVs and unrelated other-project audio are not episode sources. No original transcript or timing can be established until the source media is supplied. No live API call was made.

## Current production direction — 2026-10-25

Owner explicitly cancelled the 8–10-second prototype stopping point and authorized end-to-end production for the entire 70.927-second Dino Saves the Moon episode. Small internal checks are permitted, and successful checks must be followed by continued production. No separate prototype approval is required before full production.

Deliver all three complete playable dubbed MP4s (English, Mandarin Chinese, Malaysian Bahasa Melayu), reusable cross-platform CPU-only Python/FFmpeg commands, persistent character/SFX JSON registries, verified episode dialogue and timing manifests, generated audio stems, and README production instructions. Use approved voices unchanged: Dino/Puck, Cloud Guardian/Charon, Moon/Sulafat. Use the supplied silent MP4 as the video master, verify dialogue and timing against the original, and add appropriate dialogue-free music, ambience and synchronized effects. Do not regenerate animation or treat sample dialogue as the transcript. Check quota and billing before paid generation, avoid redundant calls, and retain provenance and editable stems. Completion requires inspecting and verifying the actual full renders, not just passing script tests.

Current external blocker: the handover ZIP, original MP4, silent master MP4, kit scripts and media assets are still absent from this checkout. The supplied ChatGPT Library URL previously failed to fetch; owner instructed stopping rather than bypassing authentication. On this production turn, `incoming/` and shared media contain only README files, and the episode has no media payload. Ask owner to place the handover ZIP in `incoming/` or provide an accessible server path. Read `DINO_CODEX_START_HERE.md` first after safe archive inspection/extraction. Reuse the supplied scripts before further implementation; current `tools/dub.py` remains a tested prototype foundation with an explicit 8–10-second constraint, not a production-complete renderer.

No production dialogue, timings, export approval or media review has been fabricated. No paid API call or final episode render has been performed.

## Production delivery imported and processed — 2026-10-25

The owner supplied an accessible Google Drive link. Downloaded handover SHA-256: `750546b54d70cc0f2bfb15d663634292e31d1224dd09f25e61b615ccc0702878`. Read `DINO_CODEX_START_HERE.md` before extracting into a fresh intake directory; validated archive paths and preserved originals. The supplied handover's prototype gate is superseded by the owner's full-production direction. Original and silent MP4s both passed full decoding. Silent master is 70.927018 s, 720×1280 H.264, with no audio. Its encoded picture stream matches the original exactly: `335c15662779ad14fdbac3777154341fb0ef208929ffdaa357767d31e2b3e934`. Source MP4 SHA-256 matches the historical intake record. No source was re-encoded or overwritten.

Compared `small.en` and `medium.en` CPU transcripts against each other; reviewed picture contact sheet for speaker/action context. Established 18 source-based dialogue cues and editorial Mandarin/Malaysian Malay translations in `production.json`. Machine transcript/timing agreement is recorded separately from human review. The three supplied generated WAVs were transcribed separately; their extra audition lines are not the film transcript and are not inserted into production. Exact approved audition prompts and reference voice identities remain unknown.

Restored the kit's reusable SFX, preserved original kit scripts under `tools/kit/`, and added full-production orchestration, formal JSON Schemas, per-language timeline fitting, local generated-speech checking, independent audio buses, music ducking, original local score/ambience, encoded-audio loudness checks and exact picture-stream preservation checks. `docs/production.md` contains reproducible macOS/Ubuntu commands. The older prototype contract remains supported but does not limit production duration.

Gemini 3.8 Flash TTS generated actual English dialogue successfully with the approved voices. The owner confirmed billing disabled on the Dino key. After 11 English stems were retained, Google returned a daily free-tier quota error (`GenerateRequestsPerDayPerProjectPerModel-FreeTier`, limit 10, reported retry delay 79744 s). API calls stopped; no billing was enabled. The owner then explicitly authorized the Bursa SIM primary `GEMINI_API_KEY` and separately confirmed billing disabled there. Read only that key into process memory using an explicit dotenv path; did not display it, copy it into Dino's `.env`, alter Bursa configuration, or automatically rotate other keys. The primary differs from Dino's original key and its model metadata request succeeded. It generated the seven remaining English lines. Full English audio verification/rendering is in progress; three-language production is not complete.

First 11 English generated stems passed local ASR text matching with similarity 1.0 (punctuation/case ignored). This verifies requested words at machine level, not voice identity, accent or creative approval. Later generated stems must pass the same checks before rendering.

Working full-output settings: preserve complete H.264 picture stream, AAC stereo 48 kHz at 192 kbps, MP4 faststart, -16 LUFS target and -1.5 dBTP normalization target. Preserve per-line WAVs, per-bus stems and a floating-point premix. These are implementation working settings, not an assertion of owner/platform export approval. All final real renders still require full listening/visual review and technical verification.

| Date | Version | Changes / feedback | Approval |
| --- | --- | --- | --- |
| 2026-10-25 | production-v001 | Imported complete handover; source-based 18-cue multilingual manifest; full pipeline and source/picture checks; 18 English stems saved; full English checks/render in progress. | Full production authorized; approved voices retained; billing remains disabled; final renders not approved or complete |

## Full English render verified — 2026-10-25

All 18 English dialogue stems passed local per-line ASR comparison at normalized-text similarity 1.0. Full English output: `episodes/save-the-moon/exports/dino_saves_the_moon_en.mp4`, duration 70.927018 s. Full decode and stream checks passed. Encoded integrated loudness is -16.00 LUFS; measured true peak is -1.43 dBTP. Encoded picture-packet hash matches the supplied silent master exactly. Export SHA-256: `f3cb72a218c403cf8f138ae73ca3073d76edb514025ff77fa759dbf51e98d285`. Independent ASR of the actual mixed MP4 passed with 0.989 normalized-text similarity; isolated per-line checks passed exactly. This is technical/machine verification, not a claim of owner listening/acting/accent approval. Full human visual/listening review remains pending.

Maximum fitted English cue start shift is approximately 0.553 s; maximum speedup is 10%. Saved separate full-length dialogue, music, ambience and SFX stems plus a floating-point premix and detailed export report. Original animation and originals remain unchanged.

The Bursa primary free-tier key then generated four Mandarin stems before Google returned the same daily quota type (`GenerateRequestsPerDayPerProjectPerModel-FreeTier`, limit 10, retry delay 78621 s). API calls stopped; billing remains disabled. Owner has been asked whether other configured Bursa Gemini keys are also unbilled and authorized for use. No such additional key has been used pending that confirmation. Current deliverables: full English MP4 technically verified; Mandarin 4/18 stems; Malay 0/18 stems; three-language production incomplete.

Local verification update: 26 regression/integration tests passed after explicit dotenv-key selection was added. The additional completion-state regression and all nine production-controller tests then passed. Tests include an actual synthetic 72-second stream-copy render, separate buses/ducking, exact video packet hashes, encoded loudness checks, schema validation and timing limits. No further API calls were made after the Bursa primary daily quota response; remaining named keys await owner billing/usage confirmation.

## Owner-requested English delivery upload — 2026-10-25

Owner explicitly requested placing the completed video in the Dino folder at the same Google Drive level as BursaManual. Confirmed existing destination `GDrive:Dino` (folder ID `1rnP1qvd2bm3JYTuqtoskPGeOWM40mPM9`, already containing the source handover). Uploaded only the completed English full episode as `dino_saves_the_moon_en.mp4` using immutable copy semantics. Remote size 70,307,680 bytes and SHA-256 `f3cb72a218c403cf8f138ae73ca3073d76edb514025ff77fa759dbf51e98d285` match the local verified export. Drive file ID `1TpXWZoXOYfdcA70G7JLHKQAFjQVGJkt_`. No sharing permissions were changed; local originals and export retained. This upload does not imply owner creative approval or completion of Mandarin/Malay production.

## English FLH packaging priority — 2026-10-25

Owner authorized using other available configured Gemini keys in free tier for later language production, and explicitly prioritized English brand packaging before further voices. No further Chinese/Malay generation during this branding task. Owner requested Family Learning Hub logo and presentation using the neighboring FLH project materials. Found the approved H-path/star identity in `webapp/lib/brandArtwork.ts`, existing owl mascot in `logo_banner.png`, Outfit/Nunito fonts and their OFL notice. Copied reusable assets with source hashes into `library/media/branding/flh-v001/`; neighboring project remains unchanged.

First packaging interpretation: Family Learning Hub presents title card, a small corner logo on the full story, and a closing brand card using the existing mascot/website. No new presenter character or narration is invented. Planned additions: 3 s intro and 3 s outro around the complete 70.927018 s English story, resulting in about 76.927018 s. Existing English video/voices, source animation and original Drive upload remain preserved. Branding is a new derived version and requires video compositing/re-encoding; the unbranded master retains its exact picture-stream preservation proof.

Owner added an explicit ending requirement during the first branding render. Stopped that unfinished render and revised the derived ending before publication: a 4 s closing card with The End, FLH logo/name, Dino Adventures, existing owl mascot, website and thanks, with music fade-out. Intro remains 3 s and complete source story remains 70.927018 s, giving an intended branded duration of 77.927018 s. Old preview assets remain preserved; revised working cards are under branding-en-v002. No original or completed unbranded render was overwritten.

## English FLH branded version with ending verified — 2026-10-25

Completed `exports/dino_saves_the_moon_en_flh_v001.mp4`: actual duration 77.927214 s, intended timeline 77.927018 s (3 s intro + 70.927018 s complete story + 4 s explicit ending). H.264 720×1280 video and AAC stereo audio, all 1,694 story frames plus 72 intro and 96 ending frames retained (1,862 total). Full decode, stream/duration and sampled actual encoded-frame review passed. Encoded integrated loudness -16.07 LUFS, true peak -1.26 dBTP. Story audio correlation against the verified unbranded English source at +3 s is 0.999867. Comparison explicitly pads tail silence to the intended timeline; an initial verification caught a 73 ms source AAC decoded-tail difference, which was resolved without altering dialogue or loosening correlation checks. Source English export hash remained unchanged.

Branded output SHA-256 `abde5324324dfcb188d0e6a1c07d875eade0f118e6e02135c8138578407ca57e`. Existing master and unbranded upload remain intact. Actual encoded preview is `reports/branding-en-v002/encoded-review.png`. FLH presents/title card, corner H/star logo and The End/brand/mascot/website/thanks closing card use existing FLH assets. No new host, voices or animation were generated. Preparing the owner-requested Drive delivery before resuming other languages using the newly authorized existing free-tier keys. Owner creative review remains pending.

## Owner revision: clean story, playful cards and cute ending animation — 2026-10-25

Owner requested no logo along the movie, simple attractive decoration matching FLH Playful styling on the opening, and cute animation on the ending. Prioritize this English revision before more language requests. All in-progress language generation/check commands have ended and outputs are retained (Chinese 18 source takes plus one selected Moon-name pronunciation take; Malay 7/18). Chinese automatic checks flagged script variants, names and short-word recognition for further local review; no unresolved language render is declared complete.

New branding v002 will disable the story watermark entirely, retain the complete English source, decorate the warm FLH cards with existing star/crescent assets and simple pale rounded shapes, and animate the existing owl with a gentle bob/tilt and drifting stars at the ending. No story animation, character voices or dialogue is regenerated for branding. Earlier English v001 and its Drive upload remain preserved for comparison. New work/preview directories are versioned separately.

## Playful English revision v002 delivered — 2026-10-25

Completed `exports/dino_saves_the_moon_en_flh_v002.mp4` with no logo anywhere in the story filter path, playful rounded light decorations, existing FLH star/crescent graphics and animated owl/stars on the ending. Opening has 72 distinct frame hashes; ending mascot-region check has 96 distinct hashes, confirming actual motion. Complete 1,694-frame story plus 168 card frames retained (1,862 total). Story audio correlation remains 0.999867. Full-duration decode/loudness/peak checks passed. Full-story top-left 128×128 crop SSIM against the unbranded source across 1,694 frames is 0.991220; report records watermark disabled.

Uploaded to owner-requested `GDrive:Dino/dino_saves_the_moon_en_flh_v002.mp4` without overwriting earlier videos. Remote size 53,511,016 bytes and SHA-256 `b37f92ea29e791d7258a2ce752e4c166924ddf5c0724ecd78f7010fe723249d5` match local. Drive ID `1IIfRxmmAdfVbNYqOKnm6ndy9NZ4eoyf9`. Earlier v001 and unbranded uploads remain intact. This is the current English review version, pending owner creative review.

Other language progress resumed only after this delivery. All 18 Mandarin source takes are present; automatic verification flagged traditional/simplified orthography, same-sound pronoun spellings, proper-name and short-word recognition. Normalization now treats orthographic/homophone differences as spoken equivalents without accepting genuinely different words. The selected alternate Moon-help take retains Sulafat and adds explicit Dino pronunciation guidance; all previous takes are preserved. Existing Mandarin title rendering had missing glyphs under native drawtext despite glyph coverage; independent Unicode text layers with copied Noto CJK fonts and license notices render correctly. Malay generation resumes with authorized free-tier key F from 7 retained stems. No paid billing is enabled.

## Owner revision: short logo bumper — 2026-10-25

Owner finds the current packaging odd and asks for simple cartoon-style animation similar in pacing to a Pokémon brand bumper, featuring the website identity. Rework English first into a short logo-focused opening/ending using only the existing FLH H/star logo, brand name and website. Remove the scattered decorative layout, owl presentation and dense title-card copy from this revision; keep the entire movie free of logos. No new story animation or voices are generated. Existing branded revisions remain preserved. Other-language voice files and alternate takes are retained, with corrected Mandarin selections also recorded in reports/production-v001/selected-mandarin-corrections.json.

## Owner refinement: preschool logo bumper and one dialogue removal — 2026-10-25

Owner clarified a Cocomelon-like simple, bright preschool identity bumper using the FLH website logo rather than a decorative title page. Implement a short gentle logo arrival/bounce and clear FLH name/website on opening/ending, no owl, scattered decorations or movie watermark. This supersedes the prior Pokémon pacing reference. Preserve the approved FLH art and all story animation; no borrowed programme assets or new narrator are needed.

Owner specifically asked to remove only the standalone Moon call immediately after Where did the moon go. Identified cue `dino-call` (story window 8.05–9.8 s; audible word around 8.3 s). Marked this cue excluded from the dub while retaining the verified source transcript and original WAV. Keep `dino-opening` and `dino-call-hear` (Moon! Can you hear me?) unchanged. Mix from separate stems so music/ambience continue through the removed word. Render a new edited English source instead of overwriting prior sources/exports. Matching translated standalone calls are likewise excluded in future language builds.

## English single-call removal verified — 2026-10-25

Rendered new `exports/dino_saves_the_moon_en_edit_v002.mp4` from retained stems. Comparing actual render provenance with the preceding English export shows exactly one removed cue (`dino-call`) and identical checksums for every other used dialogue stem. In the 8.05–9.8 s window the new separate dialogue bus is digitally silent (PCM16 peak 0), while the music bus remains nonzero (peak 1965). Later Moon! Can you hear me? dialogue remains nonzero (peak 7864) and its source stem unchanged. Picture-packet SHA-256 is still identical to the silent source. Report: reports/production-v001/english-single-moon-removal.json.

Prepared logo-only preschool bumper v003 with the original FLH logo, brand name/website, gentle pop/rebound, a brief palette-colored sparkle and an original four-note mallet tag. Opening 2 s and ending 2.5 s; intended full branded duration 75.427018 s. No narration or external assets/recordings were generated. Active brand configuration is config/branding-logo-v003.json; final render is in progress as dino_saves_the_moon_en_flh_v003.mp4. Earlier versions remain preserved.

## English logo-bumper revision v003 verified — 2026-10-25

Completed `exports/dino_saves_the_moon_en_flh_v003.mp4` using edited 17-cue English source and simple FLH-only logo bumpers. Duration 75.427214 s; 1,802 video frames = 1,694 complete story frames + 48 opening + 60 ending. Full decode/stream/duration checks passed; encoded integrated loudness -16.17 LUFS, true peak -1.43 dBTP. Packaged story audio correlation against the corrected English source at +2 s is 0.999894. No watermark is applied during the story. The only requested story speech removal is the standalone dino-call cue; the subsequent combined call is retained. All earlier unbranded/branded versions and original voice takes remain unchanged.

Final file SHA-256: `c0edfbbde0f66956488b8840edd02aa39684cd3cc0033233e3b4a1739976f68f`. Uploaded to the same owner-requested Dino folder as a new v003 filename; remote verification is recorded below. Thirty regression/integration tests passed, including the explicit omission regression (standalone call excluded, opening question and later Moon! Can you hear me? retained). No API calls were made for this revision.

Drive delivery verification: `GDrive:Dino/dino_saves_the_moon_en_flh_v003.mp4`, ID `1xUskZnhRYWK1XUq7Ih2VJqRhGQDkAfZC`, 53,422,899 bytes. Remote SHA-256 matches local `c0edfbbde0f66956488b8840edd02aa39684cd3cc0033233e3b4a1739976f68f`. Sharing permissions unchanged. This is the current English review cut; Mandarin/Malay audio work is preserved and those full versions remain incomplete.

## Owner-approved English packaging; scene music revision — 2026-10-25

Owner likes English v003 and requests varied dramatic music before reviewing English again. Mandarin/Malay production is on hold pending that review. Preserve approved logo bumpers, story visuals, 17 selected English dialogue stems and the standalone Moon-call removal. Replace only the story underscore with nine continuous editorial cues: moonlit wonder, eerie missing Moon, search suspense, imposing Guardian, warm friendship, trapped-Moon urgency, rescue build, liberation climax around 54.7 s, and gentle gratitude/resolution. These are music cue boundaries based on picture/dialogue review, not claims of exact scene cuts. Compose offline with editable JSON/MIDI and FluidR3 instruments; retain MIT permission notice. No voice/API calls or original-media modifications. New versioned outputs will preserve v003 for comparison.

Scene score rendered successfully: 9 continuous cues, 330 editable MIDI notes, separate instrument registry and MIT notice retained. Technical section measurements show the liberation cue at mean -24.2 dBFS versus -33.8 dBFS during the missing-Moon section; the build grows through -26.4 dBFS before resolving softly. These are actual rendered-score measurements, not an assertion of owner listening approval. Full English remix exported as `exports/dino_saves_the_moon_en_score_v003.mp4`, integrated -16.00 LUFS, true peak -1.38 dBTP. Dialogue, ambience and SFX bus SHA-256s exactly match the preceding approved-dialogue edit; all 17 selected stems and the source picture-packet hash remain unchanged. No Gemini API calls. Thirty-four regression/integration tests passed, including deterministic MIDI/timing and language-hold checks. Packaged v004 export/encoded-speech verification in progress.

The new full mixed English MP4 passed independent local `small.en` ASR comparison at normalized-text similarity 0.974. All 17 source-stem verification records remain selected and unchanged; machine recognition is a technical intelligibility check, not human music approval. Assets now have content-versioned inventory reports so a later score cannot silently reuse the preceding music inventory.

## English scene-music revision v004 delivered — 2026-10-25

Completed `exports/dino_saves_the_moon_en_flh_v004.mp4`: 75.427214 s, H.264 720×1280 plus AAC stereo, all 1,802 frames retained. Full decoding/duration/frame-count/loudness checks passed. Encoded integrated loudness -16.15 LUFS, true peak -1.30 dBTP. Packaged story audio correlation to the newly verified raw remix is 0.999815. The complete encoded picture-packet hash is EXACTLY identical to approved v003 (`SHA256=80d8f384a12cb048cf27b26190fc266cb483de364e9c60d19647738b41952e6e`), so opening, story and ending visuals are unchanged. Same bumper assets/music/tag reused; story underscore is the requested nine-cue revision. Dialogue, ambience and SFX buses remain bit-identical to the previous approved-dialogue edit. Technical mixed-speech check passed at 0.974 similarity; all 34 regression/integration tests passed. No billable or voice-generation calls. Owner musical review remains pending; Chinese and Malay actions stay blocked by the enabled-language gate.

Delivered a new file to the already owner-requested `GDrive:Dino/dino_saves_the_moon_en_flh_v004.mp4`; all previous versions retained. Remote size 53,442,764 bytes and SHA-256 `cf9a067124870cb9c323a2ff65798e4997c7bb16f8c22eff68d91411db671ede` match the local export report. Drive file ID `1P4q-CL9h_xcgzJlUePY3fTOVEwh0KJzK`; existing sharing permissions unchanged.

## Owner revision: website Playful Clarity branding — 2026-10-25

Owner requests the opening and ending follow the website playful theme and colors. Read the actual FLH globals.css, canonical docs/ui_components.md and ogBrand.tsx from the neighboring project. Canonical cream #FFFDF9, ink #4B4B4B, blue #1CB0F6, green #58CC02, gold #FFC800, story-purple #8549BA, blue rim #1899D6 and warm shadow #E5D8BB are reused with existing Outfit/Nunito fonts and official logo. Adapt to simple animated identity bumpers using restrained rounded edge tints, a blue hard-rim website capsule and gentle logo motion. No mascot/title-page clutter added. New configuration v004 and bumper assets v004; full English export v005 preserves the prior score/dialogue/story, logo-free story and 2 s/2.5 s packaging lengths. Chinese/Malay remain on hold. No Gemini calls.

## Website-theme English v005 verified and delivered — 2026-10-25

Completed `exports/dino_saves_the_moon_en_flh_v005.mp4`, 75.427214 s, 1,802 frames, H.264 720×1280/AAC stereo. Visual preview inspected: official logo remains central, brand and website readable without clipping, quiet rounded palette accents and blue hard-rim website pill follow the actual website theme. Intro/outro have 48/48 and 60/60 unique decoded frame hashes, confirming animation. Full decode, stream, frame-count, duration and loudness checks passed; -16.15 LUFS, -1.30 dBTP. The ENTIRE encoded audio-packet hash is identical to v004 (`SHA256=1ad0637ebf5215e9a88c3c6d23d1fa411b1a974c6e375e9ebd89d83255f9fc91`), preserving all music, dialogue, ambience, effects and bumper audio. Story audio correlation to the verified source remains 0.999815. No Gemini requests. Chinese/Malay hold remains active.

Uploaded new v005 to the owner-requested `GDrive:Dino` folder, preserving previous versions and sharing permissions. Remote 53,461,313 bytes, SHA-256 `e8d217f1d1402c0118b264247546c377c4b38474ebc94cad52e2f38ec6385968` equals local verified output. Drive ID `1YxNrC_pqc2m56KRGGPWAjsWv2kLERiwu`. Pending owner creative review.

## Owner revision: Cloud entrance timing and learning subtitles — 2026-10-25

Opening/ending approved by owner; preserve both exactly. Reviewed Cloud contact sheet at story 27–39 s and 31–35 s quarter-second mouth/face frames. Arrival SFX was at 28.6 s, before small Cloud materializes around 30.5 s; low rumble was at 29.2 s. Face emerges around 32.1–32.3 s, after the existing 31.5 s dub starts. Revised arrival 30.35 s, formation rumble 31.65 s, first Cloud line 32.15 s (+0.65 s). Reflow the next question, Dino reply and Your friend? using identical selected audio/tempo with 60 ms gaps; later Look! and all subsequent lines retain existing positions. Exact before/after changes in reports/sync-subtitles-v001/timing-changes.json. No new TTS or fabricated dialogue.

Owner requests uniform lower subtitles that do not block the main characters and support learning. Use exact verified English dialogue/fitted windows, up to two lines, Nunito bold 36px in warm ink on a reserved cream 160px bottom area. Fit the complete picture proportionally to 630×1120 above it, centered in the original 720×1280 canvas without cropping; do not overlay any subtitle on original picture. Keep approved bumpers full frame and subtitle-free, 2 s/2.5 s. Retain editable ASS and final-timeline SRT. New raw sync v004 and branded v006 preserve all earlier exports. Chinese/Malay hold remains.

Subtitle preview reviewed with the approved full-size bumpers and complete proportional story picture: single-line call is centered in the lower cream area, no character overlap or text clipping. Explicitly selected the font file’s actual internal family Nunito ExtraLight, Bold style, for libass rather than relying on fallback. All 38 regression/integration tests passed, including timestamp precision, two-line bounds, ASS control rejection, removed-call exclusion, safe-area layout and persistence of the Cloud timing override. Preservation check confirms all 17 voice source SHA-256s, trim bounds and tempo (within 1e-12 floating-point tolerance), source picture packets, music and ambience buses are unchanged. Full packaged render and independent encoded-speech check in progress.

## Cloud sync + learning subtitles English v006 verified and delivered — 2026-10-25

Completed `exports/dino_saves_the_moon_en_flh_v006.mp4`: 75.427214 s, 720×1280 H.264/AAC stereo, 1,802/1,802 expected frames. Full decode/duration/loudness checks passed; -16.17 LUFS, -1.40 dBTP. Story audio correlation to the corrected raw source is 0.999825. Independent CPU ASR of the complete corrected mix passed at 0.974 similarity; detected Cloud first speech 32.24 s and follow-up question 35.26 s, agreeing with the revised placements. Long two-line subtitle inspected in ACTUAL final encoded frame (38 s including intro): both lines readable wholly inside lower cream band, no face/body/picture overlap or clipping. Approved bumper configuration/cache unchanged. All 38 tests passed. No TTS/API calls; original sources and earlier exports preserved.

Uploaded new v006 MP4 and matching final-timeline SRT to the owner-requested Dino Drive folder, without modifying sharing permissions. Remote video size 45,763,197 bytes and SHA-256 `b189112178c76b431e372a1a15e7ff307b320f4d6f3d752b9dadfc9a51ae630d` match local report. Video Drive ID `1MmRQDjHqORvcVwYGDiANKoUnf9hzHu5P`. Owner should review Cloud alignment and subtitle presentation; Chinese/Malay remain held.

## Owner correction: subtitles over full-frame picture — 2026-10-25

Owner rejected the separate lower subtitle area. Restore the full original 720×1280 story picture with no scale, padding, crop or reserved band. Burn English subtitles directly over the movie near the bottom, using bold white Nunito with 2.5px dark outline and 2px translucent shadow, maximum two lines and 34px lower margin. Review every speaking cue against character/action positions, favoring the ground below characters and keeping faces/hand gestures visible; do not claim zero overlap of every body part. Optional per-cue positions support necessary editorial exceptions while keeping a consistent lower placement. Preserve approved bumpers and the complete v006 corrected audio/Cloud timing. New branded export v007 and subtitle assets v003 retain all rejected/previous exports. No Gemini calls.

Reviewed all 17 actual subtitle cue midpoint previews at reports/subtitles-overlay-v001/all-cues.png. White type with outline/shadow remains readable over the textured night/ground and ending sparkles. Lower center placement avoids faces and key raised-hand/magic actions; close Dino framing can overlap lower torso, accepted as minimizing obstruction rather than claiming no character overlap. Full 720×1280 image now fills the canvas with no cream margins or reserved subtitle band. Four focused subtitle/timing/Cloud-override tests passed; full export decode/loudness/frame-count validation remains in progress.

## Full-frame overlay subtitles English v007 verified and delivered — 2026-10-25

Completed `exports/dino_saves_the_moon_en_flh_v007.mp4`, 75.427214 s, 720×1280, 1,802/1,802 frames. Full decode/duration/loudness checks passed: -16.17 LUFS, -1.40 dBTP; correlation with corrected story source 0.999825. Entire encoded audio packet hash is identical to v006 (`SHA256=f4eb8ff7f12129ba4383801cf31c068f68c97e090efafa3adbde72cc1ae9a811`), preserving Cloud timing, dialogue, music/SFX and bumper sound. Approved bumper config is also identical. Actual encoded Cloud two-line frame at packaged 38 s inspected: full-frame image restored, no separate band/padding, white outlined/shadowed text sits over ground below Dino, with faces and hands unobscured. All 17 cue midpoint previews reviewed; four focused subtitle/timing tests passed. First render process was interrupted before completion; retried successfully with retained process log, without modifying originals or previous exports. No Gemini requests.

Uploaded MP4 and final-offset SRT to owner-requested Dino folder. Remote MP4 53,592,133 bytes and SHA-256 `bbdd8ed57c0620e191387974a9b67e1ebae07ce8f8a37f01995a315d054439ab` match the local verified export. Drive ID `1FJUBGEJMDqAyCtFAe4wnjdY-RiO3KPrS`. Sharing permissions unchanged; earlier videos retained. Owner creative review pending; Chinese/Malay hold remains.

## Owner accepted v007; Drive delivery cleanup — 2026-10-25

Owner said overall v007 is acceptable and requested keeping only v007 among delivery versions, removing older versions and any standalone silent source. Interpreted contradictory repeated version wording by the explicit final keep-v007 instruction. Verified v007 Drive ID/hash before cleanup. Moved seven superseded video deliveries (unbranded English and branded v001–v006) plus v006 SRT to Drive trash, not permanent deletion. Verified Dino folder now contains only v007 MP4, v007 SRT and the original Dino_Codex_Handover_All.zip archive. No standalone silent MP4 existed in the Drive folder; did not delete the source ZIP to remove a file contained within it. Local original sources/production assets/exports preserved. Audit: reports/drive-cleanup-v001.json. No sharing changes, generation calls or language production performed during cleanup.

## Owner resumes Mandarin and Malaysian Malay from approved English v007 — 2026-10-25

Owner explicitly requests both languages follow v007, releasing the English review hold. Enable en/zh/ms production. Reuse exact approved FLH bumper configuration/cache, full-frame picture, scene score, shared SFX/ambience and white outlined/shadowed lower subtitles. Preserve approved voices Puck/Charon/Sulafat and Malaysian pronunciation instructions. Retained 17 active stems exist in each language; check them before generating any new takes. Apply shared visible Cloud first-speech anchor 32.15 s, then independently fit language-specific durations; do not blindly copy English cue lengths. Use Noto Sans CJK SC bold for Chinese and existing Nunito bold for Malay. GitHub storage requested as read-only research; no media pushed or ignore rules changed.

Mandarin: all 17 selected active stems passed independent per-line local ASR. The requested text 月亮得救了！ is actually spoken as 月亮得救啦！ according to both small and medium models. Preserve the exact original TTS request/fingerprint and selected Puck take; separately record verified `spoken_text` for matching subtitles and audio review. This is a documented natural final-particle variation, not an invented source-film line or owner acting approval. Mandarin selected voice gains and timings verified.

Malay: the initial fit exceeded the drift limit around the Guardian exchange. Generated four free-tier Charon retakes using owner-authorized unbilled key I; kept the first challenge, together invitation and latest compact reveal. Earlier longer reveal retake retained but not selected. Natural localized text shortened to Bulan tersekat di sebalik awan. and Mari kita bantu dia bersama-sama. without changing their meaning. All 17 selected Malay stems passed local ASR (0.98–1.0 for the new takes). Both languages fit within the existing 10% maximum tempo and 1.5 s maximum source-start drift; original source timeline stays separately preserved. All 39 regression tests passed before the additional request-versus-spoken-particle regression. Final branded renders and whole-mix speech checks in progress.

## Three v007 editions technically complete — 2026-10-25

Chinese and Malay branded v007 renders both completed, each 75.427214 s and all 1,802 expected frames. Mandarin: -16.18 LUFS/-1.47 dBTP, story correlation 0.999815. Malay: -16.17 LUFS/-1.34 dBTP, story correlation 0.999744. Full decode/stream/duration/frame checks passed. Inspected actual final encoded Cloud-question frames and all 17 subtitle midpoint previews per language: correct glyphs, readable white outline/shadow, full-frame original picture, no subtitle band, faces and major gestures remain visible. Identical approved brand configuration and exact music/ambience/SFX bus hashes across all three languages. All 51 active dialogue stems match locked voice preset metadata; silent-master picture packet hashes remain identical in raw editions.

Whole encoded-mix speech checks passed: Mandarin 0.983871 after normalizing four traditional/simplified orthographic forms, Malay 0.996933 after fixing difflib autojunk false-negative behavior on long character sequences. Original recognition text and preceding scores retained; threshold unchanged at 0.96. Meaningful substitutions are still distinct. Thirty-nine regression tests plus all eight focused subtitle/transcript/timing tests passed. Added regressions for actual-versus-requested particle provenance, orthographic forms and long Malay repeated-letter comparison. Four authorized free-tier Charon retake calls made this language run, using key I; three selected takes, one longer reveal retained but unused. No new Chinese/English voice calls and no billing changes. Upload to owner-requested Dino folder in progress. GitHub remains a read-only storage study.

## Mandarin/Malay v007 delivery verified — 2026-10-25

Uploaded both complete localized MP4s and matching final-timeline SRTs to `GDrive:Dino`, alongside accepted English v007. All six remote files match local SHA-256 and byte size; no sharing changes. Chinese file: Drive ID `1HyhTJdSdAi3DTywE35ayIQVB1X4kwEuc`, 53,553,599 bytes, SHA-256 `1c17757d2c387b63db1c66becd41254550add37f707abf4773052d0e0e8d09e9`. Malay file: Drive ID `1RuQHswSz6yFQgQZcoQ1C29w6v277tU1a`, 53,618,602 bytes, SHA-256 `a96a12ae6ecb09af13ccf45b9b469cb18a3107a3eebcd4e9c987c1f57922903a`. English file hash/ID unchanged. Complete delivery audit: reports/delivery-v007-three-languages.json. Production status now reports all three full raw exports and whole-mix checks complete; final packaged outputs are additionally verified by reports/multilingual-v007-verification.json. English accepted; new language accent/acting remains subject to owner review.

GitHub research completed from official documentation: Free LFS includes 10 GiB storage and 10 GiB/month downloads, 2 GB single LFS file; regular Git blocks files above 100 MiB. Release assets use a different allowance model, documented in docs/github-media-storage.md. Original mixed source 69.86 MB plus three final videos about 230.63 MB fit included LFS capacity assuming account remaining quota is sufficient. Owner remaining allowance not queried. No GitHub media upload, publication, LFS setup, billing change or ignore-rule exception performed.

## Owner: canonical Chinese names and natural conversational Mandarin — 2026-10-25

Owner rejected inconsistent Dino pronunciations (Yino/Bino) and confirmed final names 迪诺、月亮、云爷爷, superseding the briefly proposed 露娜. Pronunciation is dí nuò (second/fourth tones), correcting the earlier Dī nuò instruction. Store canonical names separately and attach metadata to existing voice definitions without overwriting v001 styles or changing Puck/Charon/Sulafat. Owner also finds Chinese voice delivery unnatural and requests conversational intonation. Revoice all 17 active Mandarin lines with shared natural-dialogue profile zh-natural-v002, character-specific restrained acting and short connected phrases; do not change visuals/music/SFX/approved bumpers, English or Malay. New Mandarin v008 and versioned reports/subtitles preserve v007 and old takes. Verify name-bearing lines separately; an overall text match alone must not accept a wrong name. Free-tier-only generation with explicitly authorized existing credentials; no billing changes.

Natural Mandarin generation finished: 17 full-line retakes plus one focused first-name call, using explicitly authorized unbilled S/T credentials. A confirmed daily free-tier quota response caused the allowed transition S→T; no billing activation or model/voice change. All old recordings preserved. The first new Moon call was recognized as 李诺 by small ASR and 迪诺 by medium; it was NOT accepted merely on the medium result. Recorded a clearer, supported call with positive 迪士尼/承诺 pronunciation anchors. Its small-model transcription 敵諾 is phonemically dí nuò, matching the correct name. Other name calls include correct 迪诺 and same-tone 狄懦 spellings; canonical subtitle spelling always 迪诺. Explicit homophone mapping is limited to same initials/vowels/tones, with 李/伊/依/比 and Latin Dino still rejected. Required-name checks are independent of sentence similarity and enforced again at render.

All 17 selected new takes pass local speech checks and all four name calls pass the independent required-name rule. The natural Dino-free take is actually spoken 月亮得救了！ according to two independent ASR models, recorded as spoken_text without rewriting its requested 啦 script or generation provenance. New subtitles use the actual particle. Full timing fit passed, preserving the 32.15 s Cloud entrance anchor, maximum 10% speedup and maximum 1.5 s start drift. Full raw mix/render/packaging and whole-mix verification in progress.

## Natural Mandarin/name revision v009 verified and delivered — 2026-10-25

Final canonical names: 迪诺 (dí nuò), 月亮, 云爷爷. Revoiced all 17 active Mandarin lines with conversational character-specific direction while retaining approved Puck/Charon/Sulafat. Nineteen successful free-tier generations in this revision: 17 main takes plus two extra first-call refinements, using explicitly authorized S/T credentials; prior takes preserved. The first refinement passed full-mix recognition but its isolated final MP4 clip was still ambiguous (李诺), so intermediate v008 was NOT delivered. Final natural address 小迪诺，救救我！ keeps the same canonical name and gives it connected phonetic context. All four required-name checks now pass on decoded FINAL v009 MP4 clips: first call and question recognized 迪诺, thanks/praise recognized explicit same-tone 狄諾/狄懦 spellings. Subtitles consistently show 迪诺. Wrong initials remain rejected; raw ASR evidence retained.

Final output `exports/dino_saves_the_moon_zh_flh_v009.mp4`, duration 75.427409 s, 1,802 complete frames. Full final decode, stream, duration, subtitle visual review and all four encoded-name checks passed. Complete raw-mix ASR comparison 0.991935; no threshold reduction. Mastered output -16.23 LUFS, true peak -1.89 dBTP, story audio correlation 0.999410. The initial joined AAC encode exceeded the existing peak margin (-0.66 dBTP); conservative oversampled transient limiting fixed it without changing picture packets or relaxing acceptance checks. Guard source/output hashes and filter provenance retained in branding-zh-v009. All original picture frames, approved FLH bumper config and exact music/ambience/SFX bus hashes preserved; English and Malay v007 unchanged. Forty-six automated regression/integration tests passed, plus actual final MP4 decode, name and mastering checks.

Uploaded final MP4 and corresponding final-offset SRT into owner-requested GDrive:Dino; previous deliverables retained and sharing unchanged. Remote video 53,532,484 bytes and SHA-256 `4ec4ded8d0825a40a95d20c6d23a5ae95ef6f3fb6afe7910e58a2f7c90c70107` match local. Drive ID `1_vz-xrUe2E3nHQE8kfdG7jpFarAeoR1A`. Owner listening approval for naturalness/acting remains pending. No GitHub media upload or billing change.

## Owner-requested Malay terminology audit — 2026-10-25

Audited all 17 active Malay lines against delivered v007 subtitle cues, selected raw-render provenance and final MP4 checksum. Dino appears consistently in four name-bearing lines; Bulan in eight, Gunung Awan in one. Dino kecil appears twice as the source little-Dino affectionate adjective, not a different proper name. Only the selected tersekat phrasing is active; older terperangkap recordings are archived, not silently mixed into the deliverable. Pronouns saya/kamu/kita/dia are consistent. Tolong requests versus bantu action are context-dependent uses rather than a name/term drift. Ordinary awan and place Gunung Awan must not be globally replaced with the Cloud Guardian character name.

Recorded reusable current-usage glossary config/terminology.ms.json and existing Dino/Bulan Malay forms in the name registry. Malay Guardian name not previously confirmed or spoken in this episode; asked owner to choose, recommending Atuk Awan based on DBP atuk = colloquial datuk. Kept proposal explicitly unapproved pending reply. DBP references retained for atuk, nak/hendak, dah/sudah and tersekat/blocked. Current register is natural Malaysian conversational dialogue, not fully formal written BM; Kamukah itu? is grammatical but more literary than nearby tak/nak/dah, with Bulan? Itu kamu? suggested for future voice revision. No media, dialogue or audio altered and no API calls. Audit: reports/malay-terminology-audit-v001.json.

## Owner confirms Malay Guardian name — 2026-10-25

Owner confirmed Atuk Awan. Promoted the pending proposal to owner-confirmed canonical name in config/character_names.json and config/terminology.ms.json, and added matching localized-name metadata to the existing Charon voice definition. Ordinary awan and place Gunung Awan remain distinct. Current episode contains no spoken address to the Guardian by name; no dialogue was invented and no media/TTS regeneration was needed. Approved voice presets/styles, existing delivered videos and subtitles remain unchanged.

## Owner retains latest three; social distribution research — 2026-10-25

Owner asks to retain the latest three editions and investigate YouTube multi-language audio, Reels compatibility for this 75-second episode and other social channels. Pinned English v007, Mandarin v009 and Malay v007 in distribution-selection.json with verified file hashes; no media changed, deleted or uploaded to social platforms. All are 720×1280 vertical, nominal 24 fps/VFR, approximately 75.427 s, with burned-in language-specific subtitles.

Current YouTube official documentation says custom multi-language audio supports both videos and Shorts for creators with Advanced features; actual account availability has not been inspected. Recommend one clean picture master plus existing three complete full-length mixes and three independent SRT tracks. Existing burned-in subtitle copies cannot visually switch captions merely by selecting a different audio language. A new no-burned-subtitle derivative can be created from preserved raw picture/dub and approved bumpers without new animation or TTS. The 75-second vertical release fits YouTube Shorts (up to 3 minutes).

75 s also fits Reels/TikTok distribution; do not cut story to 60 s solely on duration assumptions. Recommend separate language posts for social platforms to retain approved custom voices/subtitles. Before publishing, create separate platform exports if needed: fixed 30 fps recommended and overlay captions positioned against actual app UI, since existing captions are close to the bottom. Keep full-frame picture and avoid faces/actions. No claim that upscaling creates new visual detail. Public Instagram help/developer pages were login/rate-limited during this research, so no precise current maximum length or universal app upload validation is claimed; Meta publicly documents Instagram Reels/video support well above 75 s, Facebook unified Reels supports this duration, and TikTok Studio official documentation accepts uploads far longer than 75 s. Audience setting Made for Kids should reflect this explicitly child-directed episode. All platform recommendations are planning only; no posting authorized by this query.

## Owner-requested source commit/push preparation — 2026-10-25

Owner explicitly requests committing and pushing preparation/script changes to the existing GitHub repository. Reviewed source changes, updated stale README/episode status to selected English v007/Mandarin v009/Malay v007, and added docs/distribution.md. Confirmed .env, all originals/exports/audio/assets, model caches and generated reports remain ignored. Scanned prospective source files for Google/GitHub credential signatures, private-key headers, binary/media content and unexpected large files; no matches. Existing origin/main fetched successfully and matched local base before committing.

A source-only checkout test exposed two tests depending on ignored episode fonts/reports/WAVs. Replaced those dependencies with temporary synthetic audio/font-metric fixtures while retaining real subtitle generation, timing-offset and Cloud-override assertions. All 46 tests then passed from a fresh source-only copy, including FFmpeg integration tests, without API keys, real media or transcription models. Full local production schema validation and git whitespace checks also passed. Proceeding with a normal commit and push to main; no force-push, media upload, billing change or social publication.


## Owner-requested before/after media archive verified — 2026-10-25

Organized the explicitly requested Dino Drive folder into `Dino_Saves_the_Moon/01_Before_Editing` and `02_After_Editing/{en,zh,ms}`. Before editing contains the unmodified original mixed MP4, supplied original WAV and unchanged original handover ZIP. The silent master stays inside that provenance package and locally; no redundant standalone silent MP4 uploaded. After editing contains exactly the selected English v007, Mandarin v009 and Malaysian Malay v007 MP4/SRT pairs plus one complete mixed WAV per language. The existing animation is unchanged; post-production means dubbing, music/ambience/SFX, subtitles and approved FLH bumpers.

Extracted each full final mix from its selected MP4 into 48 kHz stereo PCM16 and aligned it to 3,620,497 samples (75.427020833 s). Sample-based padding/trimming fixes the initial derived Chinese WAV duration discrepancy; independently decoded PCM SHA-256 now matches each WAV exactly. Includes opening and ending audio; makes no claim of restoring AAC quality. All 14 remote files passed byte-size and SHA-256 verification. Seven pre-existing selected video/subtitle/archive file IDs are unchanged after same-Drive moves, preserving existing sharing links. Only after the complete set passed verification, moved superseded Chinese v007 MP4/SRT to Drive trash. Final listing contains exactly the 14 expected files; all local originals, editable stems and earlier working renders remain untouched. No TTS calls or social publication.

Episode folder: https://drive.google.com/drive/folders/1wJTManR5zTMW1bzZSSWCJNKvTWWcQRAm . Uploaded README and media manifest explain provenance and selected versions. Local ignored audit: `reports/media-archive-v001/archive-verification.json`, with before/after listings and per-file checksums/IDs. Storage conventions documented in `docs/media-archive.md`; code/docs only are committed to GitHub.


## Media ignore rules reinforced — 2026-10-25

Owner requested keeping non-source deliverables out of Git. Extended media/archive exclusions from root-only MP4/ZIP to common video/audio/archive formats at any depth, plus Python/tool cache directories. Existing episode media/work/exports/reports and library media exclusions remain; blank `.env.example` stays tracked while real `.env` files stay ignored. Checked the complete tracked-file list: no video/audio/archive files or real dotenv files are tracked. Verified representative media, cache, export, report and secret paths with `git check-ignore`; `.env.example` remains eligible. No files removed from disk and no history rewrite.
