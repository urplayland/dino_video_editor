#!/usr/bin/env python3
"""Create the EP2 acceptance summary and individual-file release manifest."""
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import dub
import production
from package_release import export

B=Path('episodes/rainbow-bridge')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare():
    episode=dub.load(B/'production.json');common=dub.load(B/'audio-production.json')
    test_log=B/'reports/regression-tests-final.log'
    tests=test_log.read_text()
    count=re.search(r'^Ran (\d+) tests',tests,re.M)
    if not count or not re.search(r'^OK(?: \(.*\))?$',tests,re.M) or re.search(r'^FAILED',tests,re.M):
        raise ValueError('Run and pass the regression suite before packaging.')
    files=[];destinations=set()
    def add(source,destination):
        source=Path(source)
        if destination in destinations:return
        if not source.is_file():raise ValueError('Missing delivery input: '+str(source))
        destinations.add(destination);files.append({'source':str(source),'destination':destination})
    summaries={}
    for lang in ('en','zh','ms'):
        movie=B/f'exports/dino_broken_bridge_{lang}_flh_v001.mp4'
        report=dub.load(movie.with_suffix('.json'))
        integrity=dub.load(B/f'reports/final-mix-v001/{lang}-waveform-integrity.json')
        if report['actual_video_frames']!=3996 or not report['audio_packets_preserved'] or integrity['status']!='passed_automated':
            raise ValueError('Final video acceptance checks incomplete: '+lang)
        if report['output_sha256']!=sha(movie):raise ValueError('Final video changed: '+lang)
        rows=production.language_manifest(episode,lang)['dialogue']
        if any(c['audio_review_status']!='verified_automated' for c in rows):raise ValueError('Unverified dialogue: '+lang)
        clean_report=dub.load(dub.relative(common['exports'][lang]).with_suffix('.json'))
        summaries[lang]={'video':str(movie),'sha256':sha(movie),'duration_s':166.5,'frames':3996,
            'dialogue_lines':len(rows),'loudness':report['encoded_audio_measurement'],
            'minimum_encoded_dialogue_correlation':integrity['minimum_correlation'],
            'audio_packets_preserved_in_subtitle_export':True,
            'common_music_sha256':clean_report['common_music_sha256'],'common_sfx_sha256':clean_report['common_sfx_sha256']}
        add(movie,f'{lang}/{movie.name}')
        add(B/f'exports/dino_broken_bridge_{lang}_flh_v001.srt',f'{lang}/dino_broken_bridge_{lang}_flh_v001.srt')
        add(B/f'media/derived/full-mixes-v001/{lang}-full_mix-exact.wav',f'{lang}/full_mix.wav')
        add(common['dialogue'][lang]['path'],f'Editable_Audio/Dialogue/{lang}.wav')
        for cue in rows:
            audio=dub.relative(cue.get('audio_path') or f"{episode['output_dir']}/{lang}/{cue['id']}.wav")
            add(audio.relative_to(ROOT),f"Editable_Audio/Dialogue_Lines/{lang}/{cue['id']}.wav")
            add(audio.with_suffix('.json').relative_to(ROOT),f"Editable_Audio/Dialogue_Lines/{lang}/{cue['id']}.json")
            add(cue['audio_verification_report'],f"Editable_Audio/Dialogue_Lines/{lang}/{cue['id']}.audio-check.json")
        add(movie.with_suffix('.json'),f'Production_Notes/QA/{lang}-video.json')
        add(B/f'reports/final-mix-v001/{lang}-waveform-integrity.json',f'Production_Notes/QA/{lang}-waveform-integrity.json')
        for name in (f'{lang}-final-dialogue-check.json',f'{lang}-final-dialogue-cues-check.json'):
            src=B/'reports/final-mix-v001'/name
            if src.exists():add(src,f'Production_Notes/Diagnostics/{name}')
    if len({x['common_music_sha256'] for x in summaries.values()})!=1 or len({x['common_sfx_sha256'] for x in summaries.values()})!=1:
        raise ValueError('Background stems differ between languages.')
    baseline={'en':'bbdd8ed57c0620e191387974a9b67e1ebae07ce8f8a37f01995a315d054439ab',
              'zh':'4ec4ded8d0825a40a95d20c6d23a5ae95ef6f3fb6afe7910e58a2f7c90c70107',
              'ms':'a96a12ae6ecb09af13ccf45b9b469cb18a3107a3eebcd4e9c987c1f57922903a'}
    for lang,version in [('en','007'),('zh','009'),('ms','007')]:
        old=Path(f'episodes/save-the-moon/exports/dino_saves_the_moon_{lang}_flh_v{version}.mp4')
        if sha(old)!=baseline[lang]:raise ValueError('Released EP1 changed: '+lang)
    qa={'status':'technical_acceptance_passed_owner_listening_pending','languages':summaries,
        'automated_tests_passed':int(count[1]),
        'source_picture_packet_preservation':dub.load(B/'reports/picture-v001-qa.json'),
        'original_sources_and_released_EP1_unchanged':True,
        'visual_review':'Actual final EN4.5s,ZH27.4s,MS104.9s and ending163.8s frames inspected. Full-frame outlined/shadowed bottom captions, no reserved panel; no character obstruction in sampled frames. Complete final videos decoded by renderer.',
        'audio_review':'All81 selected source WAVs passed per-line ASR. Every spoken cue was directly correlated against actual mastered AAC (minimum>=0.95, alignment allowance0.5ms), then final subtitle AAC packets were verified unchanged. Shared ducked backgrounds identical across languages.',
        'recognizer_diagnostics':'Continuous VAD and some short cue ASR show spelling/segmentation disagreements, including Chinese homophones and a short Malay Betulkah. These are retained under Diagnostics; they are not relabelled as perfect transcripts. Known source speech is verified present by waveform integrity. Owner should listen for name pronunciation, accent, acting and music preference.',
        'creative_approval':'Pending owner listening; no human approval fabricated.',
        'music_sections':20,'editable_music_section_wavs':19,'sfx_cues':16,
        'no_animation_regeneration':True,'no_social_publishing':True,'no_archive_created':True}
    (B/'reports/delivery-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
    add(B/'reports/delivery-qa.json','Production_Notes/QA_SUMMARY.json')
    add(test_log,'Production_Notes/QA/regression-tests.txt')
    readme='''Dino Adventures EP2 — Dino and the Broken Rainbow Bridge
完整三语成片 v001 / Full three-language production review

每版166.5秒（2:46.5），720×1280，24fps。原画面和2秒FLH片头保留，追加4.5秒THE END动画片尾。
en/、zh/、ms/：对应语言字幕成片MP4、SRT、整片full_mix.wav。
字幕已压进成片。SRT另附供编辑。对白：Dino=Puck，女生Bunny/邦妮=Leda。
00_Shared_Master/：无声音无固定字幕master；英文完整声音无固定字幕primary。
Editable_Audio/：独立对白、音乐、环境、音效、每句WAV及生成/核对记录、MIDI及19段配乐WAV。
Production_Notes/：配置、许可、可复用代码、实际检查报告和预览。

配乐有20个连续段落，以不同速度、配器及力度表现求助、解谜、幽默、修桥高潮和团聚。三语共用同一音乐/音效，自动避让对白。
技术验收包括全片解码、3996帧、约-16LUFS、峰值安全、81句源录音检查、最终每句波形保留及字幕版AAC保持不变。
部分整片/短句ASR仍有识别拼写或断句歧义；原始诊断保留，不冒充人工听审。请试听确认中文名字、马来西亚口音、表演和配乐平衡。
首集已发布版本没有修改。没有上传YouTube/Facebook/Instagram。

所有文件逐个提供，没有新ZIP。FILE_MANIFEST.json记录实际源路径、大小及SHA256。
可根据manifest的source字段把文件放回repo路径重现制作；Workspace中附生产代码/配置、字体及声库，API key不在交付中。
原始162秒无声/原声参考文件及原始Footages保留在Dino_Stories/EP2；HQ源byte parts见：
https://drive.google.com/drive/folders/1yOBAba84wt021XVxozHEaQxW-XPKkKVH
Follow README_HQ_ASSEMBLY.md and ASSEMBLY_MANIFEST.json to restore originals; do not use older178.96s review exports or append branding twice.
'''
    (B/'reports/DELIVERY_README.txt').write_text(readme)
    add(B/'reports/DELIVERY_README.txt','README.txt')
    add(episode['source_video'],'00_Shared_Master/dino_broken_bridge_clean_silent_v001.mp4')
    add(common['exports']['en'],'00_Shared_Master/dino_broken_bridge_en_clean_primary_v001.mp4')
    work=Path(common['output_dir'])
    for name in ('common.music.wav','common.sfx.wav','music.raw.wav','sfx.raw.wav','shared.json'):
        add(work/name,'Editable_Audio/Common/'+name)
    for name in ('music.wav','effects.wav','ambience-faded.wav','ambience.json','ambience-faded.json'):
        add(B/'media/derived/background-v001'/name,'Editable_Audio/Original_Backgrounds/'+name)
    score=dub.load(B/'music-v001.json')
    for name in ('score.mid','score-report.json','underscore.wav'):
        add(Path(score['work_dir'])/name,'Editable_Audio/Music/'+name)
    for src in sorted((Path(score['work_dir'])/'sections').iterdir()):add(src,'Editable_Audio/Music/Sections/'+src.name)
    add(B/'media/derived/ending-v001/end-card.mp4','Editable_Audio/Branding/THE_END_picture.mp4')
    for src in sorted((B/'reports/final-preview-v001').glob('*.png')):add(src,'Production_Notes/Previews/'+src.name)
    for name in ('picture-v001-qa.json','transcript-review.json','font-provenance.json','music-dynamics.json','english-name-check.json'):
        add(B/'reports'/name,'Production_Notes/QA/'+name)
    for src in sorted(B.glob('*.json')):add(src,'Production_Notes/Workspace/'+str(src))
    for src in sorted(B.glob('*.md')):add(src,'Production_Notes/Workspace/'+str(src))
    add(B/'prepare_delivery.py','Production_Notes/Workspace/'+str(B/'prepare_delivery.py'))
    for folder,pattern in [('tools','*.py'),('config','*.json'),('schemas','*.json'),('templates','*'),('docs','*.md'),('tests','*.py'),('library/licenses','*')]:
        for src in sorted(Path(folder).rglob(pattern)):
            if src.is_file():add(src,'Production_Notes/Workspace/'+str(src))
    for src in [Path('README.md'),Path('.gitignore'),Path('.env.example'),*Path('.').glob('requirements*.txt')]:
        add(src,'Production_Notes/Workspace/'+str(src))
    brand=dub.load('config/branding-logo-v004.json')
    for asset in brand['assets'].values():add(asset['path'],'Production_Notes/Workspace/'+asset['path'])
    for lang in ('en','zh','ms'):
        font=dub.load(B/f'subtitles.{lang}.json')['font_path'];add(font,'Production_Notes/Workspace/'+font)
    bank=dub.load('config/music_presets.json')['soundfont']['path'];add(bank,'Production_Notes/Workspace/'+bank)
    registry=dub.load(common['sfx_registry'])
    add(common['sfx_registry'],'Production_Notes/Workspace/'+common['sfx_registry'])
    for effect in registry['effects'].values():
        for variant in effect.get('variations',[effect]):
            asset=Path(variant['asset_path'])
            if asset.exists():
                add(asset,'Production_Notes/Workspace/'+str(asset))
                if asset.with_suffix('.json').exists():add(asset.with_suffix('.json'),'Production_Notes/Workspace/'+str(asset.with_suffix('.json')))
    plan={'schema_version':1,'review_status':qa['status'],'output_dir':str(B/'exports/delivery-v001'),'files':files}
    (B/'reports/package-release.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    return export(plan)


if __name__=='__main__':
    try:prepare()
    except (ValueError,OSError,KeyError,TypeError) as error:raise SystemExit('Error: '+str(error))
