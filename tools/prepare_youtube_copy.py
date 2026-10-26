#!/usr/bin/env python3
"""Prepare separate-language upload copy from reusable channel/episode settings."""
import argparse
import json
from pathlib import Path
import dub


def prepare(profile_path, release_path, kit_path, dry_run=False):
    profile = dub.load(dub.relative(profile_path, True))
    episode = dub.load(dub.relative(release_path, True))
    selected = dub.load(dub.relative(episode['selection_manifest'], True))
    publishing = profile['publishing']
    if profile.get('schema_version') != 1 or episode.get('schema_version') != 1:
        raise ValueError('Unsupported publishing configuration version.')
    if publishing['strategy'] != 'separate_language_videos' or publishing['subtitle_delivery'] != 'embedded':
        raise ValueError('This helper prepares embedded-caption separate-language releases.')
    languages = publishing['language_order']
    if set(languages) != set(episode['releases']):
        raise ValueError('Episode and channel languages differ.')
    files, checklist, playlists, downloads = {}, [], [], []
    for language in languages:
        spec = episode['releases'][language]
        label = publishing['languages'][language]['label']
        media = selected['media'][language]
        if not media.get('has_burned_subtitles'):
            raise ValueError('Selected release lacks embedded subtitles: '+language)
        title = publishing['video_title_template'].format(episode_title=spec['episode_title'], series=episode['series'], language_label=label)
        if not title or len(title) > 100 or any(c in title for c in '<>\r\n'):
            raise ValueError('Invalid video title.')
        if not publishing['append_channel_name_to_video_titles'] and title.endswith(profile['brand']):
            raise ValueError('Unexpected repeated channel-name suffix.')
        playlist = publishing['playlist_title_template'].format(series=episode['series'], language_label=label)
        url = 'https://drive.google.com/file/d/'+spec['drive_id']+'/view'
        name = Path(media['file']).name
        files['04_Copy_And_Setup/first-episode-'+language+'.txt'] = 'TITLE\n'+title+'\n\nDESCRIPTION\n'+spec['description']+'\n'
        playlists.append('NAME\n'+playlist+'\n\nDESCRIPTION\n'+spec['playlist_description'])
        checklist.append(f'{label}\nTitle: {title}\nPlaylist: {playlist}\nVideo: {name}\nDownload: {url}\nContains: matching full audio + embedded subtitles\nCover: 02_Episode_Covers/episode-cover-{language}-2160x3840.jpg')
        downloads.append(f'{label} — READY TO UPLOAD, WITH EMBEDDED SUBTITLES\n{name}\n{url}\nSHA-256: {media["sha256"]}')
    files['04_Copy_And_Setup/playlist-copy.txt'] = 'PERMANENT LANGUAGE PLAYLISTS — ONE FAMILY LEARNING HUB CHANNEL\n\n'+'\n\n---\n\n'.join(playlists)+'\n\nUse one matching playlist per video. Append future episodes in story order. Feature these three playlists on the channel Home tab. No extra mixed-language playlist is needed for this publishing plan.\n'
    files['04_Copy_And_Setup/UPLOAD_CHECKLIST.txt'] = 'READY-TO-UPLOAD CHECKLIST\n\nChannel: '+profile['brand']+'\nHandle: '+profile['youtube']['handle']+'\nChannel URL: '+profile['youtube']['url']+'\n\n'+'\n\n---\n\n'.join(checklist)+'\n\nStart each upload as Private while reviewing. Check the existing embedded subtitle layout with player CC off, so an extra caption layer does not hide it. Separate CC files remain optional accessibility assets; they do not determine the visible embedded design. No custom-thumbnail upload or audio-track switch is needed to make these videos understandable. Choose the correct audience setting, add each video to its matching playlist, and publish only when ready.\n\nExisting YouTube links may point to earlier clean-picture tests. Do not delete them as a cleanup step. A new encoded source must be uploaded separately; this kit does not replace footage behind an existing YouTube link.\n'
    files['04_Copy_And_Setup/media-download-links.txt'] = 'CURRENT PUBLISHING CHOICE — THREE SEPARATE LANGUAGE VIDEOS\n\n'+'\n\n'.join(downloads)+'\n\nARCHIVE / EDITING SOURCES\nOriginal sources, clean picture masters, full WAVs and SRT/TTML files remain in the episode archive:\nhttps://drive.google.com/drive/folders/1wJTManR5zTMW1bzZSSWCJNKvTWWcQRAm\nUse the three MP4s above for this release. The clean master and standalone caption files are editing/alternate-workflow assets.\n'
    files['04_Copy_And_Setup/channel-profile-en.txt'] = 'CHANNEL NAME\n'+profile['brand']+'\n\nCONFIRMED YOUTUBE HANDLE\n'+profile['youtube']['handle']+'\n\nCHANNEL URL\n'+profile['youtube']['url']+'\n\nWEBSITE LINK LABEL\nFamily Learning Hub\n\nWEBSITE LINK\nhttps://familylearninghub.com\n\nCHANNEL DESCRIPTION — paste only the paragraph below\n'+profile['profile_descriptions']['en']+'\n'
    files['04_Copy_And_Setup/channel-profile-zh.txt'] = '频道名称（中文翻译）\n家庭学习中心\n\n频道简介（中文翻译）\n'+profile['profile_descriptions']['zh']+'\n'
    files['04_Copy_And_Setup/channel-profile-ms.txt'] = 'NAMA SALURAN\nFamily Learning Hub\n\nPENERANGAN SALURAN\n'+profile['profile_descriptions']['ms']+'\n'
    if not dry_run:
        kit = dub.relative(kit_path)
        for name, content in files.items():
            target = kit/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding='utf-8')
    print(json.dumps({'files':list(files),'strategy':publishing['strategy'],'dry_run':dry_run}, indent=2))
    return files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('release')
    parser.add_argument('--profile', default='config/channel-profile.json')
    parser.add_argument('--kit', default='library/media/branding/youtube-launch-v001')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    prepare(args.profile, args.release, args.kit, args.dry_run)
