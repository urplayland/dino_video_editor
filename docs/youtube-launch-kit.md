# FLH YouTube launch kit

Prepared on the owner's request for next-day channel setup. The local delivery
is `library/media/branding/youtube-launch-v001/`, outside Git. The Drive
destination is `GDrive:Dino/FLH_YouTube_Launch_Kit_v001/`, alongside the episode
archive. [Open the delivered folder](https://drive.google.com/drive/folders/1nvkNb6O4p_RJE-8QCekH68U4VxuQTv1d). All assets are delivered individually; the owner requested no ZIP.

The channel uses Family Learning Hub as the umbrella brand and Dino Adventures
as the first series. Existing owner-approved H/star artwork, Outfit/Nunito type
and Playful Clarity colours are retained. One background illustration was
generated with the built-in imagegen tool; exact prompt and provenance are in
the kit's `05_Editable_Source/generation-provenance.json`. All character art is
from the original silent episode at decoded frame index 1440. No new character
design, animation or TTS was generated.

Updated 2026-10-26 for the permanent release plan: one FLH channel, three
language playlists and three embedded-caption videos per episode. Video titles
end with the language label rather than the channel name. The root README,
setup guide, channel descriptions, episode copy, playlist descriptions and
media links use this plan; `UPLOAD_CHECKLIST.txt` maps every title/playlist to
the exact selected subtitled MP4. Existing artwork is unchanged. Clean masters
and standalone subtitles remain archived rather than being the main upload
recommendation. Files are updated individually in the same Drive folder.

## Delivery contents

- `01_Channel_Branding`: 2560×1440 banner, 800×800 avatar and optional 150×150
  watermark. Banner essentials fit the conservative central 1544×422 safe area.
- `02_Episode_Covers`: English, Mandarin and Malaysian Malay covers in both
  3840×2160 landscape and 2160×3840 portrait; all six JPEGs are below 2 MB.
- `03_Previews`: mobile/desktop banner crops, circular-avatar crop, complete
  artwork overview and validation results. These are review files, not uploads.
- `04_Copy_And_Setup`: ready-to-paste trilingual channel/episode text, three
  permanent language playlist descriptions, `UPLOAD_CHECKLIST.txt`, current
  embedded-caption video download links, official references and
  `TOMORROW_START_HERE.txt` with the setup sequence.
- `05_Editable_Source`: self-contained SVG layouts with outlined lettering,
  source art, config, colour palette and generation records. Font binaries are
  not redistributed. The 4K cover layouts do not add detail to the 720p film still.
- Root README and per-file SHA-256 manifest. No ZIP is needed.

Rebuild into a **new output directory/version** after installing the optional
`requirements-channel-art.txt` dependencies and providing the recorded source
assets. FFmpeg must include the librsvg decoder:

```sh
.venv/bin/python tools/channel_art.py config/youtube-channel-art-v001.json
```

The current setup guide explains the [Made for Kids watermark limitation and
branding specifications](https://support.google.com/youtube/answer/10456525?hl=en),
[thumbnail upload workflow and current dimensions](https://support.google.com/youtube/answer/72431?hl=en),
and [custom multi-language audio eligibility](https://support.google.com/youtube/answer/13338784?hl=en).
The owner confirmed `@familylearninghub-flh` on 2026-10-26; its canonical URL is
https://www.youtube.com/@familylearninghub-flh and is recorded in
`config/channel-profile.json`. Cloud setup copy uses this handle rather than
earlier candidate names. Account-specific controls remain unverified. The kit
does not create a channel, register a handle, set an audience or publish a video.
The owner performs these account actions during setup.

Publishing copy is reproducible with
`python3 tools/prepare_youtube_copy.py episodes/save-the-moon/youtube-release.json`.
The reusable channel/title rules are in `config/channel-profile.json`; the
episode's actual titles, descriptions and Drive IDs are kept under its own
episode directory.

Original sources, existing selected videos and their sharing permissions remain
unchanged. Cloud upload is authorised by the owner; all art, ZIPs and generated
inventories remain ignored by Git. Upload verification is retained locally in
the kit's `review/drive-verification.json`.
