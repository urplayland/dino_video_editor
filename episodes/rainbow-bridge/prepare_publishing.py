#!/usr/bin/env python3
"""Verify the existing clean picture against current finals and attach approved EN audio."""
import json
from fractions import Fraction
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import dub
from export_clean_master import sha, package_primary
from prepare_youtube_copy import prepare

B='episodes/rainbow-bridge/'
CONFIG=B+'clean-master-release-v001.json'

def write_handoff(selected):
    root=dub.relative(B+'exports/Publishing_Kit_v001')
    release=dub.load(dub.relative(B+'youtube-release.json',True))
    profile=dub.load(dub.relative('config/channel-profile.json',True))
    handoff=dict(episode=2,slug='rainbow-bridge',brand=profile['brand'],
        website_status='pending_later_in_family_learning_hub_project',
        youtube_status='prepared_not_uploaded_by_this_pipeline',languages={})
    rows=[]
    for lang,spec in release['releases'].items():
        label=profile['publishing']['languages'][lang]['label']
        playlist=profile['publishing']['playlist_title_template'].format(series=release['series'],language_label=label)
        handoff['languages'][lang]=dict(title=spec['episode_title'],description=spec['description'],
            playlist=playlist,playlist_position='after Episode1',youtube_url=None,
            video_drive_url='https://drive.google.com/file/d/'+spec['drive_id']+'/view',
            video_sha256=selected['media'][lang]['sha256'],
            cover_portrait=f'02_Episode_Covers/episode-cover-{lang}-2160x3840.jpg',
            cover_landscape=f'02_Episode_Covers/episode-cover-{lang}-3840x2160.jpg')
        rows.append(f'| {label} | {Path(selected["media"][lang]["file"]).name} | {playlist} | Prepared; not uploaded here |')
    (root/'WEBSITE_HANDOFF.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n')
    text='''# Dino Adventures — release list

Current Drive structure: 01_Editing (sources, current stems/subtitles, clean masters), 02_Final_Product (only the three current captioned movies), 03_Publishing_Kit (covers and upload copy). Original sources retained; obsolete production/review versions removed from the active workspace at the owner's request. Root00_START_HERE.md is the main entry point.

## EP1 — Dino Saves the Moon

Existing episode; no rework. Reuse the current FLH avatar/banner and the three permanent language playlists.
Existing setup kit: https://drive.google.com/drive/folders/1nvkNb6O4p_RJE-8QCekH68U4VxuQTv1d
No existing channel, upload or website state was changed or independently verified here.

## EP2 — Dino and the Broken Rainbow Bridge

Publishing kit: https://drive.google.com/drive/folders/1qC3hJHK2mdYk50KmeMFTkJQ4meMaYeyy
Current full finals: https://drive.google.com/drive/folders/1XW0jJFadQ2FSofsezIKG8_grjA70Apqw

| Language | Selected video | Existing playlist | Release status |
|---|---|---|---|
'''+ '\n'.join(rows)+'''

- [x] Three complete captioned videos and translated BC/BM endings.
- [x] Three-language covers, titles, descriptions and hashtags prepared.
- [x] Upload checklist and final-file hashes provided.
- [x] Clean silent master verified; latest approved EN audio packaged without captions.
- [ ] Owner viewing/listening review of localized finals and new covers.
- [ ] Upload the three videos; add each after EP1 in its matching existing playlist.
- [ ] Record the actual published YouTube URLs.
- [ ] Add EP2 to Family Learning Hub later, using WEBSITE_HANDOFF.json and published URLs.

Nothing was published to YouTube, social media or the FLH website. Do not create new language playlists just for EP2. All files are individual downloads, no ZIP.
'''
    (root/'RELEASE_LIST.md').write_text(text)
    (root/'README_START_HERE.md').write_text('''# EP2 publishing kit

1. Open RELEASE_LIST.md for progress and the website task deferred to later.
2. View the six covers in 02_Episode_Covers. 03_Previews is for review only.
3. Use 04_Copy_And_Setup/UPLOAD_CHECKLIST.txt and episode-02-en/zh/ms.txt.
4. Download the exact current captioned MP4s from media-download-links.txt; ENv001, BCv002, BMv002. The videos already contain the intended subtitle design. Keep player CC off for the initial layout check.
5. Add each to its existing language playlist after Dino Saves the Moon. Reuse the established FLH channel branding.
6. After publishing, put the actual YouTube URLs into WEBSITE_HANDOFF.json and add EP2 in the Family Learning Hub project later. Null URLs mean not supplied; Drive download URLs are not video-player embed URLs.

The Drive layout is 01_Editing, 02_Final_Product and 03_Publishing_Kit. Clean masters live separately in 01_Editing/Clean_Masters:
https://drive.google.com/drive/folders/1ZsfBoSEoFN5OOqDkj_feQMT7uHoQHvTO
The local package stages these under00_Shared_Master. These are editing/alternate-workflow assets, not the default three-language upload files. Their shared ending remains English; the ready-to-upload BC/BM finals have their translated endings. Old review/production versions were removed from the active Drive workspace at the owner's request; raw sources remain in Editing.

05_Editable_Source contains outlined SVG layouts, the actual EP2 still, settings and source notes. Portrait2160x3840 and landscape3840x2160 JPEGs are each under2MB. Artwork layout sizes do not increase the source film detail. Choose a cover/upload option supported by your account; no account feature access was tested or changed.

English performance was approved by the owner; localized acting/accent and these new covers remain available for owner review. Technical checks are not creative approval. No new TTS, paid API, generated animation or website deployment was used.
''')

def prepare_clean():
    cfg=dub.load(dub.relative(CONFIG,True))
    picture=dub.relative(cfg['output'],True)
    if sha(picture)!=cfg['source_sha256']:
        raise ValueError('Existing clean picture master changed.')
    streams=dub.probe(picture)['streams']
    if len(streams)!=1 or streams[0]['codec_type']!='video':
        raise ValueError('Expected the existing video-only master.')
    def clock(path):
        info=dub.probe(path);v=next(s for s in info['streams'] if s['codec_type']=='video')
        raw=dub.run([dub.tool('ffprobe'),'-v','error','-select_streams','v:0',
            '-show_entries','packet=pts','-of','json',str(path)]).stdout
        return sorted(Fraction(p['pts'])*Fraction(v['time_base']) for p in json.loads(raw)['packets'])
    timestamps=clock(picture)
    selected=dub.load(dub.relative(cfg['selection_manifest'],True))
    for lang,item in selected['media'].items():
        movie=dub.relative(item['file'],True)
        if sha(movie)!=item['sha256'] or clock(movie)!=timestamps:
            raise ValueError('Selected final checksum or picture clock differs: '+lang)
    dub.run([dub.tool('ffmpeg'),'-v','error','-xerror','-i',str(picture),'-f','null','-'],timeout=600)
    report=dub.relative(cfg['report']);report.parent.mkdir(parents=True,exist_ok=True)
    data=dict(status='verified',output_sha256=sha(picture),frames=len(timestamps),duration_s=166.5,
        audio_streams=0,burned_subtitles_applied=False,source='Existing clean silent master; no new picture render.',
        all_current_final_picture_timestamps_match=True)
    encoded=json.dumps(data,indent=2)+'\n'
    if report.exists() and report.read_text()!=encoded:raise ValueError('Existing clean QA differs.')
    if not report.exists():report.write_text(encoded)
    target=dub.relative(cfg['primary_output']);target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        previous=dub.load(target.with_suffix('.json'))
        if previous['output_sha256']!=sha(target) or previous['selected_audio_source']!=selected['media']['en']['file']:
            raise ValueError('Existing primary differs.')
    else:package_primary(CONFIG)
    def audio_packets(path):
        return dub.run([dub.tool('ffprobe'),'-v','error','-select_streams','a:0',
            '-show_entries','packet=pts,dts','-of','json',str(path)]).stdout
    if audio_packets(target)!=audio_packets(dub.relative(selected['media']['en']['file'],True)):
        raise ValueError('Clean primary changed the approved audio clock.')
    prepare('config/channel-profile.json',B+'youtube-release.json',B+'exports/Publishing_Kit_v001')
    write_handoff(selected)

if __name__=='__main__':prepare_clean()
