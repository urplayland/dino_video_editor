#!/usr/bin/env python3
"""Write one consistent human episode index from existing status and selected releases."""
import argparse
import json
from pathlib import Path
import dub


def build(config='config/series.json'):
    cfg=dub.load(dub.relative(config,True));seen=set()
    for item in cfg['episodes']:
        if item['number'] in seen:raise ValueError('Duplicate episode number.')
        seen.add(item['number']);slug=item['slug']
        status=dub.load(dub.relative(item['status_file'],True))
        if status['slug']!=slug:raise ValueError('Episode status belongs to another story.')
        selected=dub.load(dub.relative(f'episodes/{slug}/distribution-selection.json',True))
        release=dub.load(dub.relative(f'episodes/{slug}/youtube-release.json',True))
        d=item['drive'];url=lambda ident:'https://drive.google.com/drive/folders/'+ident
        lines=[f'# EP{item["number"]:02d} — {item["title"]}','','Status: '+status['status'],'',
            '## Story and production','',
            '- [Story Bible / source reference](story-bible.md)',
            '- [Episode guidelines](guidelines.md)',
            '- [Language statuses](episode-status.json)',
            '- [Production and approval record](edit-plan.md)',
            '- [Editing sources]('+url(d['editing'])+')','',
            '## Final product','',
            '- [Complete videos — download these to upload]('+url(d['videos'])+')',
            '- [Final subtitles]('+url(d['subtitles'])+')',
            '- [Final independent audio stems / complete mixes]('+url(d['audio'])+')',
            '- [All final-product materials]('+url(d['final_product'])+')','',
            '| Language | Selected movie | Download |','|---|---|---|']
        for lang,label in [('en','English'),('zh','中文 / BC'),('ms','Bahasa Melayu / BM')]:
            file=Path(selected['media'][lang]['file']).name;driveid=release['releases'][lang]['drive_id']
            lines.append(f'| {label} | {file} | [MP4](https://drive.google.com/file/d/{driveid}/view) |')
        lines+=['','## Publishing','',
            '[Episode covers, upload copy/checklist and website handoff]('+url(d['publishing'])+')','',
            'Owner confirmed one Family Learning Hub channel (@familylearninghub-flh) with three language playlists: Dino Adventures — English, Dino Adventures — 中文, Dino Adventures — Bahasa Melayu. Upload each separate language video to its matching playlist. This pipeline does not publish automatically.','',
            'Final MP4s already contain matching visible subtitles; standalone SRT/ASS are editable/accessibility assets. Original source/video identities and acting are unchanged.','',
            'Shared voice/branding/SFX definitions are referenced from config/ and library/. Runtime secrets and large media are not in Git. Drive is consolidated under Dino_Stories with the two existing creator editors retained, as expressly authorized. Folder links above are the actual current locations.']
        target=dub.relative(f'episodes/{slug}/EPISODE_INDEX.md');target.write_text('\n'.join(lines)+'\n')
        print('Updated',target.relative_to(dub.ROOT))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',default='config/series.json');a=p.parse_args()
    try:build(a.config)
    except (ValueError,OSError,KeyError) as exc:p.exit(1,f'Error: {exc}\n')
