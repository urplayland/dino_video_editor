# Episode 2 audio edit plan

Active production state (2026-11-01): latest HQ sources supplied and checksum verified; owner approved full execution. All three166.5s/3996frame subtitle videos are rendered and technically checked, with new4.5s THE END. Owner listening/creative approval remains pending. Earlier missing-source/provisional notes below are historical and superseded by the dated updates.

Owner-described scene: Dino walking near a broken rainbow bridge, Bunny waving across a river. This description is not verified footage.

No original Episode 2 video, duration, dialogue stems or reviewed action timecodes are available in the repository. All first-scene timestamps stay null. Do not render this draft as if its timing had been reviewed.

Review actual foot contacts, Bunny movements and river continuity, fill scene/cue times, provide verified dialogue stems and licensed/original music, then promote reviewed cues and manifest status. Bunny=Leda selection is now owner-approved (2026-10-28), recorded in config/voice_candidates.json. Existing styles are unchanged; Bunny language-specific delivery styles remain unspecified.

Implementation tracking: shared audio system introduced 2026-10-27. Review/test results are recorded below.

## Integration and validation — 2026-10-27

Completed the reusable SFX library and shared multilingual mixing integration. Legacy presets/voices/styles remain unchanged; new versioned registry snapshot contains eleven new effect IDs (ten requested plus magical_ambience), three variations each. All33 local procedural assets passed WAV format, exact sample count, non-silence, no-clipping and metadata checksum checks. No third-party downloads, paid API or GPU. Bunny=Leda stays provisional in a separate candidate registry; its missing styles are not fabricated.

Extended existing production assets/build commands rather than replacing voice/subtitle workflows. Shared background buses are prepared/ducked once from a conservative combined three-language detector, then reused by hash for each language. The detector is never audible in final mixes. Final mastering/mux/decode/peak/picture checks use the extracted existing dub.py helper. New engines pin and validate full input/variant/provenance/registry hashes and protect caches/outputs from silent overwrite. Formal registry/cue/mix schemas, compatible episode templates and documentation are included.

All57 regression/integration tests passed, including measured music/SFX ducking and recovery, common-bus identity across three outputs, old preset compatibility, deterministic variants, imported licence/checksum requirements, unknown timing rejection, stale-cache refusal, resume and picture preservation. An independent12-second diagnostic acceptance fixture exercises every new effect ID and exports all three language slots. These use explicitly labelled synthetic tones, not invented dialogue or replacement character voices. Outputs and detailed reports live under episodes/audio-system-verification/; no Episode 1 rework is part of the deliverable. The owner instructed that Episode 1 is already released; all owner-selected videos and voices were rechecked unchanged. Agent-created earlier test artifacts remain ignored/unpublished and are not selected outputs.

Actual Episode 2 scene review/mix is blocked on original footage, exact duration, verified EN/ZH/MS dialogue stems and selected music with known provenance. Current cue timestamps remain null and draft renders are correctly rejected. No exact scripted action timecodes, dialogue, source contents, licences or approval have been invented. Generate and audition library assets now; populate/promote the cue plan only after actual video review.

## Bunny voice selection — 2026-10-28

Owner explicitly approved keeping Bunny (班尼) on Gemini Leda (丽娜). Updated the selection record from provisional to voice_selection_approved and documented the approval basis. No existing character styles, audio or released Episode 1 exports were changed. Language-specific Bunny delivery instructions and audition reference audio remain unknown; selection approval does not imply those missing assets exist. Reviewed the JSON and documentation diff for consistency.

## Bunny character clarification — 2026-10-28

Owner clarified that Bunny is female and requested a feminine Chinese name, preferably using 女. Adopted 邦妮 as the current proposed localized name (妮 contains 女), replacing 班尼 for future production. Recorded female gender; Leda voice selection remains approved. This naming proposal does not imply a separate owner approval of the exact spelling. Existing Episode 1 media and original sources remain unchanged. JSON parsing and diff whitespace checks passed.

## New HQ delivery inspected / plan pending — 2026-11-01

The earlier missing-picture status is superseded by the newly located Dino_Stories/EP2 HQ delivery. Read the current MD handoff and byte-assembled both masters; all source part/master hashes passed. Actual silent master is162s/3888frames/720x1280/24fps with an existing2s opening and no The End card, superseding the older178.958s branded plan. Reviewed sampled story and ending frames. See production-plan-2026-11-01.md for evidence, source precedence, proposed4–5s FLH end card with large centered THE END, three-language voice/subtitle work and differentiated original offline music. User explicitly requested plan review before execution: no generation, final render or Drive write performed. Actual dialogue remains untranscribed/unverified, and future cue timings must be checked against the latest master. EP1 unchanged.

## Production authorized — 2026-11-01

Owner approved the plan and explicitly requested distinct music character, urgency and emotional progression comparable to EP1. Proceed with all production stages; original sources copied intact to media/originals/hq-20261101. No paid API authorization; existing free-tier authorization persists. New materials remain review outputs until actual checks/listening.

## Production implementation / checks — 2026-11-01

New end_card.py produces a4.5s FLH Playful Clarity ending with large centered THE END, smaller brand/series/website below. All3888 source picture packets preserved when appending; complete166.5s/3996frame clean picture fully decoded. Uploaded intact to Drive Production_v001/00_Shared_Master, verified size and MD5. Source/Episode1 unchanged.

Original small.en+medium ASR was compared, with focused scene checks recovering quiet Bunny encouragement and reaction lines.27 verified source-based lines localized into EN/ZH/MS;81 selected recordings generated. All81 per-line technical transcript checks passed. Dino Mandarin explicitly reused the tuned EP1 zh-natural-v002 per-line direction;15 newly directed takes replace earlier basic-style attempts, which remain retained locally. One transient503 was resumed after backoff; no billing enabled. A retake recovery bug for a previously ungenerated canonical first take was fixed, tested, and the completed audio recovered without another request.

Mandarin ASR normalizes genuine traditional/simplified forms. Only two teaching cues have documented whole-phrase same-pronunciation spelling aliases (角/脚 jiǎo, 它/他 tā); raw recognition is retained, no global substitution or lowered threshold. Independent medium checks resolved the other spelling uncertainties, and required 迪诺 name checks passed. The rules do not establish human acting/accent approval.

The original MIDI score has20 continuous sections (19 playable individual section WAVs), varying instrumentation, tempo64–112 and dynamics: measured mean level approximately-33dBFS for river concern, -24.5dBFS for restoration peak and -29.9dBFS for the hug. River/forest ambience fades with the actual departure.16 reviewed action-effect cues and common dialogue-aware ducking are integrated. Three full clean sound mixes technically rendered; full soundtrack ASR and fixed subtitle exports are in progress. Brand renderer now supports already branded masters without adding bumpers or offsets, preserves AAC packets and checks complete decode/frame count. New checksum-linking and individual-file packaging helpers reuse the existing mixer.62 automated tests passed after these fixes; further source changes require the final suite refresh before delivery.

## Final review deliverables — 2026-11-01

All three full fixed-subtitle MP4s rendered and decoded successfully:166.5s,3996frames,720x1280/24fps. Actual final EN/ZH/MS caption frames and THE END frame were visually inspected: white text/dark outline-shadow at the bottom of the full picture, no dedicated subtitle panel, no sampled character obstruction; closing logo/website stay below the large central title. Final subtitle versions preserve the exact mastered AAC packets. Measured EN-16.15LUFS/-2.28dBTP, ZH-16.10/-2.34, MS-16.08/-2.33.

All81 selected source recordings passed per-line automated checks. Final encoded dialogue waveforms were compared cue by cue to those verified stems: minimum correlation EN0.963598, ZH0.973200, MS0.965071, with at most0.5ms codec alignment allowance. This confirms every known speech cue is present/foregrounded in the actual mixed AAC, including short lines omitted by continuous ASR. Continuous/cropped recognizer spelling/segmentation disagreements remain retained as diagnostics, not falsely labelled perfect recognition; they do not alter the canonical subtitles or voice requests. Owner should listen for natural accent, name pronunciation, acting and musical preference.

Shared music/SFX hashes match across the three complete soundtracks. The existing production build/status now links verified dialogue stems, reuses shared mixes, checks actual final waveforms and distinguishes working-export ASR from final-content acceptance. Resume was checked without live API calls or media replacement. The original first162s picture payload, HQ originals and owner-selected released EP1 files are unchanged. Individual-file packaging (no ZIP) includes editable stems, selected line WAV/metadata/checks,19 music section WAVs, MIDI, soundfont/fonts/licences and production code. Drive destination is EP2/02_After_Editing/Production_v001; transport readback is recorded separately in reports/drive-delivery-verification.json after upload. No social posting or new public publishing.
