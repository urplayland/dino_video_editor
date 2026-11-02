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
