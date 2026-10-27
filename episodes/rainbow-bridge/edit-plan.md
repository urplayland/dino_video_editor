# Episode 2 audio edit plan

Owner-described scene: Dino walking near a broken rainbow bridge, Bunny waving across a river. This description is not verified footage.

No original Episode 2 video, duration, dialogue stems or reviewed action timecodes are available in the repository. All first-scene timestamps stay null. Do not render this draft as if its timing had been reviewed.

Review actual foot contacts, Bunny movements and river continuity, fill scene/cue times, provide verified dialogue stems and licensed/original music, then promote reviewed cues and manifest status. Bunny=Leda remains provisional in config/voice_candidates.json; no approved voice styles were changed and no Bunny speech may be generated until approved.

Implementation tracking: shared audio system introduced 2026-10-27. Review/test results are recorded below.

## Integration and validation — 2026-10-27

Completed the reusable SFX library and shared multilingual mixing integration. Legacy presets/voices/styles remain unchanged; new versioned registry snapshot contains eleven new effect IDs (ten requested plus magical_ambience), three variations each. All33 local procedural assets passed WAV format, exact sample count, non-silence, no-clipping and metadata checksum checks. No third-party downloads, paid API or GPU. Bunny=Leda stays provisional in a separate candidate registry; its missing styles are not fabricated.

Extended existing production assets/build commands rather than replacing voice/subtitle workflows. Shared background buses are prepared/ducked once from a conservative combined three-language detector, then reused by hash for each language. The detector is never audible in final mixes. Final mastering/mux/decode/peak/picture checks use the extracted existing dub.py helper. New engines pin and validate full input/variant/provenance/registry hashes and protect caches/outputs from silent overwrite. Formal registry/cue/mix schemas, compatible episode templates and documentation are included.

All57 regression/integration tests passed, including measured music/SFX ducking and recovery, common-bus identity across three outputs, old preset compatibility, deterministic variants, imported licence/checksum requirements, unknown timing rejection, stale-cache refusal, resume and picture preservation. An independent12-second diagnostic acceptance fixture exercises every new effect ID and exports all three language slots. These use explicitly labelled synthetic tones, not invented dialogue or replacement character voices. Outputs and detailed reports live under episodes/audio-system-verification/; no Episode 1 rework is part of the deliverable. The owner instructed that Episode 1 is already released; all owner-selected videos and voices were rechecked unchanged. Agent-created earlier test artifacts remain ignored/unpublished and are not selected outputs.

Actual Episode 2 scene review/mix is blocked on original footage, exact duration, verified EN/ZH/MS dialogue stems and selected music with known provenance. Current cue timestamps remain null and draft renders are correctly rejected. No exact scripted action timecodes, dialogue, source contents, licences or approval have been invented. Generate and audition library assets now; populate/promote the cue plan only after actual video review.
