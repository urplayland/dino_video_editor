# Selected deliverables and platform preparation

The owner retained English v007, Mandarin v009 and Malaysian Malay v007. `episodes/save-the-moon/distribution-selection.json` pins their paths/hashes. All are approximately 75.427 seconds, vertical 720×1280, nominal 24 fps with preserved variable picture timing. Each currently has its own language's subtitles burned into the picture. Original sources, full audio mixes, dialogue/SFX/music stems and editable subtitle files are kept outside Git. These three outputs remain the content baselines; no extra platform derivative or social upload has been made.

## YouTube: one video with language tracks

[YouTube's current documentation](https://support.google.com/youtube/answer/13338784?hl=en) supports uploading custom language audio tracks to both videos and Shorts for creators with Advanced features. Actual channel availability has not been checked. If available, use one video with three uploaded full mixes, corresponding subtitle tracks, and translated titles/descriptions. If unavailable, separate language videos remain the fallback.

Use a clean-picture master from the preserved uncaptioned story and approved FLH bumper clips. The silent master is an editing/interchange asset; the primary upload copy includes the selected English audio with no burned subtitles. Add the other complete language mixes (dialogue, music, ambience, sound effects and bumper audio), each aligned to the full approximately 75.427-second timeline, and the three verified SRT files separately. Switching audio cannot remove or change subtitles already burned into an MP4, so the existing captioned language-specific MP4s remain separate viewing copies. No new animation or TTS generation is needed for this packaging.

Reproduce the clean master and English primary copy with:

```sh
python3 tools/export_clean_master.py episodes/save-the-moon/clean-master.json
```

The exporter uses the unchanged original silent story and hash-verified approved bumpers. It preserves all 1,802 frames and checks every picture timestamp against all three selected releases. It refuses to overwrite existing outputs. The English primary copy uses stream copy for both video and selected final English audio; packet hashes and a full decode are checked. To package primary audio after a separately completed clean-master render:

```sh
python3 tools/export_clean_master.py episodes/save-the-moon/clean-master.json --package-primary-only
```

Drive's `02_After_Editing/00_Shared_Master/` contains both clean-picture variants. Language folders `en/`, `zh/` and `ms/` contain the corresponding full mixed WAV and full-timeline SRT. Use those packaged SRTs directly: the two-second opening offset is already included. The story-only subtitle files in the working tree use a different time origin and must not be substituted. SRT carries text and timing; the player controls its visual styling and placement.

The current vertical episode fits [YouTube's up-to-three-minute Shorts format](https://support.google.com/youtube/answer/15424877?hl=en). This child-directed series should use the appropriate [Made for Kids audience setting](https://support.google.com/youtube/answer/9527654?hl=en); that affects platform features such as comments, not the already rendered logo ending.

## Instagram/Facebook Reels and TikTok

The episode does not need to be shortened to 60 seconds merely to distribute it as a Reel. Meta documents [Instagram video/Reels support longer than this episode](https://about.fb.com/news/2022/07/new-ways-to-create-instagram-reels-remix/) and [Facebook's unified Reels publishing flow](https://about.fb.com/news/2025/06/making-it-easier-create-videos-facebook/). [TikTok Studio's upload documentation](https://support.tiktok.com/en/using-tiktok/creating-videos/creator-tools-on-tiktok) also supports this episode's duration and resolution. Current precise maximum lengths need not be assumed to establish that 75 seconds fits. Instagram's current help pages were login/rate-limited during research; no account-specific upload test was performed.

For predictable use of the owner-approved voices and subtitles, the recommended starting approach is one post per language on these social platforms, with a clear language label and matching cover/caption. This is a publishing strategy recommendation, not a claim that all platform auto-translation features are absent.

Before preparing actual uploads:

- Derive separately named platform exports while retaining all original/master files.
- Prefer fixed 30 fps for the social export; this is a preparation recommendation, not a claim that changing frame rate creates new animation detail.
- Keep the complete 9:16 picture and approved story/audio content.
- Preview with the actual app interface. Existing captions are near the bottom; adjust their position in a separate platform subtitle layout if account labels, descriptions or buttons obscure them, while avoiding faces and major actions.
- Retain clean exports without platform watermarks for cross-platform distribution.

Start with YouTube, Instagram, Facebook and TikTok. Social posts can be aimed at parents discovering Family Learning Hub and co-viewing; platform performance and language demand should guide later account/channel expansion. Nothing in this plan authorizes posting automatically.
