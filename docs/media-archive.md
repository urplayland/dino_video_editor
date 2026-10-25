# Episode media archive

The owner-requested Google Drive archive is `GDrive:Dino/Dino_Saves_the_Moon/`.
This is a source/delivery archive, not a social-media publication. Media stays
outside Git; production scripts and configuration remain in this repository.

```text
Dino_Saves_the_Moon/
  README.txt
  media-manifest.json
  01_Before_Editing/
    original_video.mp4
    original_audio.wav
    original_handover.zip
  02_After_Editing/
    00_Shared_Master/  # silent clean picture + clean picture with English audio
    en/  # selected v007 MP4, matching SRT, full mixed WAV
    zh/  # selected v009 MP4, matching SRT, full mixed WAV
    ms/  # selected v007 MP4, matching SRT, full mixed WAV
```

Before editing means the original supplied animation and audio. The original
handover ZIP remains unchanged as a provenance package, including the silent
picture master and early kit material. Its samples are not the verified film
transcript. No second standalone silent MP4 is uploaded.

After editing means the existing animation with approved character dubbing,
music, ambience, effects, subtitles and FLH opening/ending. Each language has one
current delivery set. The full mixed WAV is decoded from its selected final MP4
into 48 kHz stereo PCM16, aligned to 75.427018 seconds; this does not restore
detail lost in AAC compression. It includes the opening and ending audio.

The shared clean-picture files retain approved FLH bumpers and have no fixed
subtitles. The silent version is for editing; the English-audio version is a
primary upload asset. Use the existing language-folder WAVs and full-timeline
SRTs for multilingual audio/captions. See [distribution.md](distribution.md)
for the reproducible export command and subtitle time origin.

The remote manifest records sizes and SHA-256 hashes. Existing selected MP4s,
SRTs and the source ZIP are moved within Drive, preserving file IDs and sharing
links. New uploads are checked against local sizes and SHA-256 hashes before
superseded derived deliveries are moved to Drive trash. Source files are never
deleted or overwritten. Editable stems and older working renders remain on the
production server, outside Git.

Local preparation, upload progress and final verification are retained under
`episodes/save-the-moon/reports/media-archive-v001/` (ignored by Git).
