# EP2 production plan — approved and executing

Date: 2026-11-01. Owner subsequently approved this plan and requested distinct musical character/tension across story sections, comparable to Dino Saves the Moon. Production and the planned Drive handoff are now authorized; no social publishing or paid APIs. Earlier EP1 release remains untouched.

## Grounded inputs and precedence

Drive home: https://drive.google.com/drive/folders/12q8LbbYkgs5hFuO00_PFWlSjum3gyyV4
Latest HQ handoff: https://drive.google.com/drive/folders/1yOBAba84wt021XVxozHEaQxW-XPKkKVH
Read EP2_CODEX_POSTPRODUCTION_PROMPT.md, README_HQ_ASSEMBLY.md, ASSEMBLY_MANIFEST.json, timeline_v5.json, and the Story Bible/Prompt Guidelines (including historical versus latest updates). Latest HQ README supersedes the older 178.958333s branded handoff: Review v5 picture + existing 2s opening, no old handmade The End and no old outro appended. The new end card is explicitly owner requested; it supersedes older instructions to add no cards. Keep the accepted story departure intact.

Both HQ files are supplied as four BYTE chunks, not four playable scene clips. Downloaded all eight chunks for inspection; every part and reconstructed master matches the assembly manifest SHA256 and size. Inspection files are ignored under reports/drive-review-2026-11-01/. Originals in Drive remain untouched.

Measured silent picture: EP2_No_Audio_HQ_No_End_Card.mp4, 190747100 bytes, SHA256 03241b4cda44ca8eca45c2329434edaa9b1d0b98dd93a8ffad43c38eb08216c0, 720x1280, 24fps, 3888 frames, 162.000000s, no audio stream.
Measured guide version: 194660543 bytes, SHA256 e1132f789452e1a24909fd0ce5e4648ca70037a16d9ba58b3a748939adc4a2db, matching video dimensions/frame count, AAC guide, container162.021333s. The small AAC/container tail must not define the picture timeline.
The opening reference is2.000000s. timeline_v5.json describes the main cut BEFORE that opening (25 segments; Scene03 and Scene14 omitted; accepted22A/22B composite appears once). Its estimated main duration159.95833s differs from assembled162s minus2s by about one frame. Confirm actual frame boundaries when building production cues; do not use rounded JSON estimates as exact final timestamps.

Visually reviewed a6-second-interval contact sheet across the silent master and0.5-second samples across the last4seconds. Visible beats include pink circle, cyan triangle, lavender square; three placements, restoration, reunion and retained departure/fade. This is sampled picture inspection, NOT a full-motion QA pass or a verified audio transcript. Footages lists28 assets; frame/reference folders mix candidates and approved material, so do not treat every item as production approved. Older Postproduction_Handoff and01_Before_Editing currently list empty through the connector; latest usable HQ delivery is under02_After_Editing. Optional EP2_Original_BGM_Stem.mp3 exists, but its title alone does not establish isolation or licence.

## Proposed ending (4–5 seconds)

Keep the existing departure/fade, then a new FLH motion-graphics end card matching EP1's actual Playful Clarity assets. Cream background, exact blue/green/gold/purple palette, Outfit/Nunito, rounded shapes, subtle sparkle and gentle pop/rebound. Large THE END centered with clear breathing room. Small Dino Adventures, FLH logo/brand and familylearninghub.com in the lower area, inside mobile safe margins. No logo overlay throughout the story. Use the same shared card for all three languages. No added narrator or spoken end tag.

Create the card with existing local logo_bumper/FFmpeg/vector tools and actual FLH assets, without paid video generation or new character animation. It is a new branded graphic ending, not a fabricated new3D story scene. Do not reinsert the rejected handmade end card. Expected final duration166–167s (proposal until exact new card length is fixed), below the inherited180s picture-duration limit. Existing opening counted once; subtitles start from complete-film zero.

## Dialogue and subtitles

Transcribe actual guide audio per character and scene, check against current picture. Distinguish verified speech from unclear words and any new localized adaptation; never call draft Bible text an actual transcript. English first for complete synchronization and voice review, then Mandarin and Malaysian Malay on the same final picture. The requested three tracks mean three language versions, not an invented third speaking character.

Dino=Puck; Bunny/邦妮=Leda, owner-approved female voice. Existing Cloud=Charon and Moon=Sulafat remain unchanged and are used only if actually present. Reuse existing EN/MS styles and natural Mandarin direction for existing characters. Bunny's language-specific delivery instructions are missing: draft a warm, youthful, natural feminine direction consistent with the Bible and distinguish it from an approved audition prompt. Keep Malaysian pronunciation; natural conversational Mandarin. Canon shapes are pink circle, cyan triangle, lavender square; corners0/3/4. Complete shared terminology before batch TTS.

Generate one editable WAV per verified/localized line, fit concise text/natural pacing to the existing picture, no duplicate guide dialogue. Retain original source reference separately. Gemini calls only after plan approval, current model/free-tier availability check, and quota handling. No unapproved paid calls; quota exhaustion is reported, not worked around by assuming billing authorization.

Reuse EP1 full-frame subtitle workflow: readable white text, dark outline/shadow, bottom safe placement, no separate black subtitle panel, adjust only when needed to protect key action. Export matching SRT from the same complete-film timeline. No second opening offset.

## Proposed music arc

The approximate windows below are planning ranges from v5 plus the existing opening, not verified frame-accurate sound cues. Recheck against the actual master/voice delivery before locking.

| Full-film approximate window | Story section | New arrangement |
| --- | --- | --- |
|0–2s|Existing FLH opening|Keep established short brand tag|
|2–24s|Bunny needs help; Dino identifies problem|Warm magical woodwinds/celeste, mild concern and space for dialogue|
|24–49s|Circle learning/discovery/placement|Light plucked strings, simple round motif, restrained placement reward|
|49–84s|Triangle observation/search/placement|More curious rhythmic variation, three-note motif and gentle forward motion|
|84–124s|Square clue/search/discovery/placement|Light comic pizzicato, brief curious pause, four-note response; no loud scare|
|124–142s|Magic framework and solid bridge restoration|Gradual string/harp build, strongest musical release synchronized to actual restoration|
|142–162s|Relief, reunion/hug and departure|Warm melody returns, softer resolution and natural musical tail|
|New final4–5s|THE END/FLH|Short resolving melody, subtle familiar brand tag; no abrupt cut|

Compose new episode-specific material with existing tools/scene_score.py, registered instruments and installed FluidSynth; no paid music API, GPU or downloaded soundtrack. Preserve MIDI, cue JSON, per-section WAV and full music stem plus the existing SoundFont licence/provenance. Shared motifs connect the sections; change harmony, rhythm, instrumentation and dynamics rather than looping one track or abruptly switching unrelated songs. Crossfades/held notes bridge cuts; silence/space is intentional during teaching. This is offline original composition/arrangement, not a claim of generated live orchestral performance or owner-approved music quality.

## SFX, mix and delivery

Reuse tools/sfx.py, versioned registry, tools/audio_production.py and existing subtitle/mastering helpers. Continuous river/forest ambience where appropriate; action-aligned footsteps, pickup/placement, subtle reward chimes, restoration swell and soft reunion. Do not add major restoration effects before all three stones are fitted. No weather/rain interpretation of three languages.

Keep editable dialogue/music/ambience/SFX stems. Use common music/SFX across all languages, shared dialogue-aware background ducking, final loudness target around-16LUFS, true peak ceiling-1dBTP or safer. Measure actual encoded results, speech timing, fades and absence of duplicate guide speech.

After plan approval: (1) establish final picture/end card and exact frame manifest; (2) verify transcript/localized terms, draft missing Bunny directions, prepare full EN dub and score; (3) review EN as a full episode; (4) use approved common picture/score for ZH/MS; (5) decode and inspect all full exports, subtitles/cuts/repair/hug/ending plus audio listening QA; record what is machine checked versus human reviewed. Do not claim completion based only on script exit status.

Deliver individual files under EP2/02_After_Editing:00_Shared_Master silent/subtitle-free master and clean EN-audio primary; en/zh/ms latest subtitle MP4, SRT and full_mix.wav; editable stems, score/MIDI, manifests, provenance and production README. Preserve before/after separation, original clips and HQ split sources. No ZIP, no social publishing, no overwrite of EP1. Any upload during the future execution follows owner-approved scope and verified Drive readback; saving approved scene footage also requires Story Bible synchronization.

## Initial inspection state (superseded by execution approval)

Inspection and proposed plan only. No new speech/music/end card generated, no paid calls and no Drive changes. Remaining execution dependencies: owner plan approval, actual transcript verification, Bunny delivery directions, live free-quota/model access. Existing assets and local rendering/composition tools are available; no need to request resubmission of the provided HQ masters.
