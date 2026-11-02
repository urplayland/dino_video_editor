# English v003 compact sync review

Requested scope: a compressed review first, not a new final-quality export. Preserve v002 picture/edit/ending, voices and music arrangement; fix the two early lines and the activation/construction SFX. No API calls or new generation credits.

```sh
.venv/bin/python tools/review_audio.py episodes/rainbow-bridge/review-en-v003.json
```

The versioned helper validates compact encoding options, uses the existing production timeline/score/SFX/subtitle/mastering functions, and exports540×960/24fps with CRF28/veryfast. Source picture remains unchanged before subtitle burn/review scaling. Dialogue and subtitle final windows: triangle50.1374–52.0562s; Bunny under-foot107.1250–109.1321s. Chimes follow individually reviewed stone halos at125.000/126.625/128.125s; frame and solid-bridge accents follow131.417/134.417s with continuous gentle construction air through138.625s.

New procedural variants are episode-specific pending review, using existing original generators; approved library/voice definitions are unchanged. Full editable stems/automation remain local and ignored under exports/Review_EN_v003 and media/derived/review-en-v003. Only the compact MP4, change log, dialogue timeline, SRT/ASS and QA record are uploaded individually for this review. Earlier versions are preserved. Freeze this configuration once delivered; future changes need new work/output paths. Cache provenance intentionally refuses an existing build made with a different tool revision.

67 tests pass. Entire166.5s/3996frame review decodes; final AAC is identical to the checked clean mix. Actual−16.16LUFS/−2.31dBTP; every dialogue waveform present (minimum correlation0.982074). Close-up picture sampling anchors the two dialogue entries; this is not a claim of phoneme-perfect lip sync or owner listening approval. Review source markers and raw effect/music balance measurements are retained in ignored reports/review-en-v003.

Drive: https://drive.google.com/drive/folders/1bBaeqWxjxz_PiUZLE87scEf1PrQMSo2y
Movie: https://drive.google.com/file/d/1MpeIX4-WXpaYpa_RZfqrBmXsCB1D5pGz/view
Final high-quality EN output and ZH/MS revisions await review.
