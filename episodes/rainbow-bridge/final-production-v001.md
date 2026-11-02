# EP2 final production v001

Full166.5s/3996frame,720x1280/24fps finals: EN, ZH and Malaysian MS. English retains exact owner-approved v004 AAC; the two localized versions use the same accepted picture/edit/opening/ending, original score and corrected magic/SFX marks, with independently fitted dialogue, subtitles and ducking. Dino=Puck, Bunny=Leda; approved registry/style strings unchanged.

```sh
.venv/bin/python tools/finalize_approved.py episodes/rainbow-bridge/final-en-v001.json
.venv/bin/python tools/review_audio.py episodes/rainbow-bridge/final-zh-v001.json
.venv/bin/python tools/review_audio.py episodes/rainbow-bridge/final-ms-v001.json
.venv/bin/python -m unittest discover -s tests -v
```

Restore ignored media/source metadata/fonts/soundfont first. Render commands do not call TTS or require a GPU. Exact English approved AAC is retained separately as M4A, allowing review MP4 cleanup. Existing production/SFX/score/subtitle/mastering helpers are reused; final labels and shared raw SFX are configured rather than creating a second mixer. production-final-v001.json provides frozen localized text and baseline source selection; per-language final configs determine actual exports/takes/timings. Do not invoke that source-selection manifest as an independent full release build.

English words/timing/sound are unchanged from approval. Canonical Chinese names are迪诺/邦妮. Malay shape terms remain bulatan/segi tiga/segi empat sama/bucu; closing question naturally shortens to Sedia nak mengembara lagi? for the same story meaning. Verified original triangle pronunciation is retained; rejected retake candidates remain as source history. No prior time stretch is compounded beyond10percent. New voice generations used only the existing authorized unbilled pool.

70 tests, full decode, actual encoded-speech/reaction integrity, all27 caption midpoint frames per language and final loudness checks passed. EN−16.15LUFS/−2.22dBTP; ZH−16.11/−2.12; MS−16.11/−2.33. English owner approval is recorded; localized final acting/accent can be assessed while viewing. No automatic metric claims human creative approval or phoneme-perfect lip sync.

[Final folder](https://drive.google.com/drive/folders/1XW0jJFadQ2FSofsezIKG8_grjA70Apqw) contains three MP4s individually (no ZIP), full SRT/ASS, editable stems, dialogue/music automation, QA and selected source voices. Original source backup and HQ footage remain untouched. Metadata/source hashes and cleanup audits are in ignored reports/final-v001. Confirmed reusable approved voice assets live in library/, with stable index JSON.

Four old published review MP4s were moved to recoverable Drive Trash after final/source checksum verification. All602 other prior files were preserved unchanged; old notes/audio were archived, not deleted. Source footage/audio, raw generations, selected WAVs, registries, scripts and Git history remain. No episode was posted to social media.

## Current localized endings — v002, 2026-11-02

BC now ends with **剧终 / 迪诺历险记**; BM with **TAMAT / Pengembaraan Dino**. Family Learning Hub, logo, website, colours and approved motion graphics remain. English stays v001. No voice generation or paid service was used.

```sh
.venv/bin/python tools/localize_ending.py episodes/rainbow-bridge/final-ending-zh-v002.json
.venv/bin/python tools/localize_ending.py episodes/rainbow-bridge/final-ending-ms-v002.json
```

Restore the referenced v001 final and existing branding/fonts first. The helper checks its source SHA, copies the picture through frame3866, and replaces only the last GOP from161.125s, with the translated card starting162s. Every video presentation timestamp, audio packet and audio timestamp remains identical. Both complete outputs decoded successfully; rendered cards were visually checked in the final movies.71 regression tests pass. Existing dialogue/subtitle files and stems still apply unchanged.

[BC final v002](https://drive.google.com/file/d/1hR3Caw1G2DBJ-OMUtjjc9K6fuhuZmRjE/view) and [BM final v002](https://drive.google.com/file/d/1qEJGQoPmRU4f3GRNhDsdn21esnFF91sz/view) are beside English in the final folder. Previous localized finals and metadata are retained in Previous_Final_Versions. Localized_Ending_Cards contains the editable card settings and separate animation exports. Remote readback verified all60 prior files by ID/size/MD5 and every new upload. Audit: reports/ending-localization-v002/delivery-verification.json.

## Publishing preparation

[EP2 publishing kit](https://drive.google.com/drive/folders/1qC3hJHK2mdYk50KmeMFTkJQ4meMaYeyy) contains six EP1-style covers, three-language upload copy, final-file selection/checklist and a deferred FLH website handoff. The release list tracks EP2 after EP1 in each existing language playlist; no platform or website changes were made. Reuse channel branding rather than recreating it.

```sh
.venv/bin/python episodes/rainbow-bridge/prepare_publishing.py
.venv/bin/python tools/channel_art.py episodes/rainbow-bridge/youtube-art-v001.json
```

The cover builder refuses existing image outputs; choose a new output directory for a new version, or restore the existing six exports. The artwork uses actual clean-master frame3552/148s with existing FLH assets and outlined fonts, not regenerated characters. prepare_publishing validates pinned final SHA256 values, exact picture timestamps against the original clean master and packages current EN audio without subtitles or re-encoding. Old pre-review clean-audio exports are not selected. The clean master retains the approved English ending; the BC/BM captioned releases use translated endings.
