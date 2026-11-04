# Milo Series EP01 — Let's Learn Shapes!

## Latest owner decision — future export policy, 2026-11-04
Owner approved all three versions and reports publishing them. The owner then requested no compression for future final delivery and explicitly said no re-export is needed for this episode. Record uncompressed video plus PCM audio, directly from the editing timeline, as the future default; platform encoding is left to YouTube/Facebook. Shared production guide and Milo README updated. Existing EP01 files/uploads stay unchanged. Publication was owner-reported for all three; the last read-only API check observed ZH/MS public and EN private, so do not claim all three were independently verified public.

## Current owner direction
On 2026-11-04 the owner requested post-production to begin from the Drive handoff and authorized rclone for media transfers. The previous deferred-production instruction is superseded for versioned review work. Approved master and original sources must remain untouched. No publishing is authorized by the post-production request.

Deliver EN, Mandarin Chinese, and Malaysian Bahasa Melayu versions using the same approved 1280×720 picture edit. Reuse the verified Dino EP2 FLH identity/jingle in proportionally adapted 16:9 bumpers. Preserve the accepted Square-to-Oval visual imperfection; do not regenerate animation.

## Intake
Drive episode folder: `1P6NboGvygDlKnfzmH7bi2CTlNgSc8tEP`.
Existing authenticated remote: `GDrive:`. Production handoff, clean master, silent master, editing ZIP and Base.mp4 copied to `media/originals/` with immutable/checksum transfer options. The editing ZIP was inspected without executing its shell script. Its timeline notes describe 1,207 decoded frames and approximately 50.292 seconds.

## Voice selection in progress
The owner asked to analyze the original first ten seconds and shortlist stock voices to audition in AI Studio. No final Milo voice is selected. The source brief specifies a warm, energetic, curious young boy fox.

A separate 10.0-second mono WAV was extracted to `work/milo-original-first10s.wav`. Local tiny.en ASR is recorded in `reports/opening-transcript-v001.json`; transcript is machine-derived and not yet manually verified. Mixed-track pitch measurements are in `reports/opening-acoustic-analysis-v001.json`; music may confound them and they must not be represented as clean speech pitch or an exact voice match.

The owner explicitly authorized sending only this ten-second excerpt to Google Gemini for voice analysis. An initial attempt before that clarification was rejected by automatic review and did not execute. Subsequent model calls encountered model-not-found/service overload responses; no voice identity claim follows from failed calls. Successful analysis, if returned, is stored separately in `reports/opening-voice-analysis-v001.json`.

## Remaining checks
- Confirm complete actual dialogue, source word/line timings, and the seventh shape claimed in the recap. Do not invent the missing shape or silently rewrite the recap.
- Owner chooses Milo voice after auditions; no full-episode dubbing before that choice.
- Verify selected FLH bumper source/provenance and retain original sonic logo audio.
- Build natural localized scripts, voice takes, music/SFX buses, subtitles and versioned reviews.
- Fully decode and inspect exported movies, including scene joins, dialogue/subtitles, picture continuity and audio peaks/loudness. Technical checks do not constitute owner listening approval.
- Keep all source, media, caches, exports, and credential values out of Git unless a specific established small-asset policy applies. This Milo working folder is outside the Dino Git repository.

## English v001 execution
Owner selected Achernar after AI Studio auditions and requested EN v1 first. Character name remains Milo. Eight scene-group speech takes were generated with `gemini-3.8-flash-tts`, preserving exact request fingerprints and raw WAVs. Nineteen dialogue/subtitle cues were derived and matched by local ASR. No full Mandarin/Malay voice generation performed.

Original FLH logo and jingle hashes verified against approved v004 provenance. Landscape bumpers recreate the same composition/theme proportionally at 1280×720: 2s intro, 2.5s outro. An original seven-section 112-BPM instrumental score was rendered from editable MIDI using the checksum-verified FluidR3 bank; original licence notice retained. Dialogue, music, effects, intentionally silent ambience and mastered audio are separate.

Initial engineering render passed full decode, 1,207 story-frame comparisons and loudness/peak checks. Independent encoded-mix ASR caught a faulty automatic split inside `sign` and before the article in `A diamond shape`. Raw recordings contain the full words; cut boundaries corrected to measured quiet gaps at 1.88s in the oval take and 1.00s in the diamond take. The first render/reports were retained under ignored `work/en-v001/preQA-render`, never uploaded or represented as final. Star/diamond effect placements were refined from actual picture outlines. No picture regeneration.

A render timeout retained the partial file separately. Final encoder uses CRF18/veryfast with bounded threads and sufficient timeout for this small server. Final verification must run on the corrected completed file.

Owner explicitly authorized delivery of English v1, subtitles and independent audio tracks into existing `02_Final_Product/Videos/EN`, `Subtitles/EN/Review_v001`, and `Audio/EN/Review_v001` after automatic approval initially required that exact upload authorization. No sharing changes, original replacement or social publication.

## English v001 delivered for review
Corrected complete review: https://drive.google.com/file/d/12XCQB5kclY3mnTFXf2E6eih0YO6pkzEl/view
54.791667s, 1,315 frames, 1280×720, 24fps. All 1,207 story-frame positions compared with source; upper-frame SSIM average 0.99318, minimum 0.98745. Full decode passed, no unexpected black runs. Encoded audio -16.94 LUFS, -1.79 dBTP. Independent base.en encoded-story transcript similarity 0.98333 against 0.96 requirement; remaining difference is Wow/Whoa recognition. All original intake hashes unchanged. No dialogue speedup or start displacement used.

Video, subtitles and audio delivery verified by exact remote size/MD5 for 10 files, 80,554,967 bytes. See ignored reports/drive-delivery-verification-v001.json. Technical QA reports remain local because automatic review rejected their separate upload as outside the explicit media delivery scope. No social publication or sharing changes. Owner listening/creative review pending; EN-first milestone delivered, Mandarin/Malay production not started.

## English v002 correction and six-shape revision
Owner reported that the tail of everywhere was clipped in v001, then requested removal of the circle because the story teaches six shapes. Investigation confirmed v001 first-line cut at raw1.42s despite actual speech extending to about1.78s; ASR text alone missed it. v002 moves the split to the measured2.00s quiet gap, retains the raw1.42–1.78s tail with placed RMS0.09466, and audits all other split points. Shared quiet-gap overrides preserve complete words. The revised six-shape recap was generated once with the selected Achernar voice and retained as a continuous scene take. Other raw takes reused.

Circle removed only from derived ending frames using clean sky from the same shot with foreground ear/star protection; no animation regeneration. Lossless retouched155-frame ending asset and mask/provenance retained. Original source and v001 review remain unchanged. Full v002 decode and1,315frame geometry/timing checks passed. Encoded audio -16.74LUFS/-1.14dBTP; final local base.en transcript similarity0.98333, all shape names and complete everywhere/six-shape recap confirmed. Owner explicitly authorized v002 video/subtitle/audio upload. 8 Drive files verified by size/MD5. Link: https://drive.google.com/file/d/1WAsPkKqoGYF53f1eG4VNSd06Cnelydza/view
QA reports retained locally; no social publication or sharing changes. Owner review pending.

## Formal EN/ZH/MS release — owner authorization 2026-11-04
Owner approved English v002 and requested formal EN, ZH and MS deliverables in the episode folder structure. Formal EN preserves the exact approved video bytes. ZH/MS use independently recorded complete lines with Achernar, natural Mandarin and Malaysian Malay, locked six-shape picture and original brand jingle. Localized acting still awaits owner listening. Original long Mandarin recap retained separately; shorter natural recap fits the scene without speedup.

Drive live inventory confirmed series already at Videos/Milo. Only four verified-empty obsolete root folders (Footage, Final_Videos, Project_Files, References) were removed using recoverable Drive trash. Episodes/Library, all source assets, original sharing and review versions preserved. Existing CN/BM language folders renamed in place to ZH/MS, retaining their IDs.

Gemini uses the recorded owner-authorized unbilled key pool. Primary returned quota; B and C each returned explicit daily free-tier limit10. Generation stops on each response, resumes only missing takes with an explicitly selected authorized key, and reuses identical interjection requests. No billing or model changes.

Owner additionally requested YouTube uploads after completion and will prepare publication. Upload only technically checked formal versions as PRIVATE, education category, child-directed audience, correct language metadata; preserve narrow youtube.upload + youtube.readonly authorization and manual playlist assignment. No publication, schedule, deletion or playlist writes authorized by this stage.

## Formal releases delivered and uploaded privately
All three formal MP4s passed full decode, 1,315-frame/24fps/1280x720 geometry, all 1,207 story-frame comparisons, 19 subtitle cues, source preservation, loudness and peak checks. EN remains byte-identical to owner-approved v002. ZH/MS line fits use no speedup, maximum source-start shifts0.080s/0.279s. Final LUFS/true peaks: EN -16.74/-1.14dBTP; ZH -16.71/-1.80dBTP; MS -16.02/-2.85dBTP. Mandarin sign take corrected after initial local transcription; first render/take retained. Final encoded local base transcripts retained. Stronger multilingual small resolved target Mandarin shape/object names and Malay bujur, rectangle, kite and berlian. ASR homophone/spelling limitations and unreviewed localized acting remain; no human listening approval implied.

Drive: all24 final files verified by size/MD5,210075763bytes. Private YouTube uploads read back on the intended channel: all3 processed successfully, private visibility, made-for-kids true, language metadata and localized descriptions. No publication, playlist writes, deletion or sharing changes. Owner can assign each EP01 to its matching Milo language playlist and publish after listening.

## Owner-approved cleanup and unified workspace
Owner requested cleanup, commit/push and a shared layout for Dino/Milo. Episode moved from `/srv/video_editor/milo_ep1` to `/srv/video_editor/series/milo/episodes/learn-shapes`. Dino moved to `series/dino`; publishing tools/configuration and private credentials separated at workspace root. Preserved original/final media, all voice takes, brand assets, QA evidence and historical review exports. Removed113 scratch/cache files (965484911bytes) after verification; reusable score PCM and sky plate promoted to derived media. Drive18 earlier review files archived by metadata moves retaining IDs;24 active final files remain checksum-verified. Existing MP4 releases are exempt from future uncompressed exports and were not replaced.
