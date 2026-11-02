#!/usr/bin/env python3
"""Finalize an approved soundtrack on the original picture; no TTS or remixing."""
import argparse
import hashlib
import json
from pathlib import Path

import dub
from brand_video import caption_filter
from review_audio import immutable_json, sha


def finalize(config_path):
    cfg=dub.load(config_path)
    if cfg.get('schema_version')!=1 or not cfg.get('owner_approval'):
        raise ValueError('An explicit owner-approved source is required.')
    def source(spec):
        path=dub.relative(spec['path'],True)
        if sha(path)!=spec['sha256']:raise ValueError('Approved source checksum changed.')
        return path
    approved=source(cfg['approved_review']);picture=source(cfg['picture_master'])
    subtitle_source=source(cfg['approved_ass']);srt_source=source(cfg['approved_srt'])
    output=dub.relative(cfg['output']);output.parent.mkdir(parents=True,exist_ok=True)
    work=dub.relative(cfg['work_dir']);work.mkdir(parents=True,exist_ok=True)
    inputs={'config':sha(config_path),'approved':sha(approved),'picture':sha(picture),
        'ass':sha(subtitle_source),'srt':sha(srt_source),'tool':sha(Path(__file__))}
    immutable_json(work/'inputs.json',inputs)
    settings=dub.load(dub.relative(cfg['subtitle_settings'],True))
    for suffix,original in [('ass',subtitle_source),('srt',srt_source)]:
        target=output.with_suffix('.'+suffix)
        if target.exists() and sha(target)!=sha(original):raise ValueError('Final subtitle already differs.')
        if not target.exists():dub.write_new(target,original.read_bytes())
    settings['ass_path']=output.with_suffix('.ass').relative_to(dub.ROOT).as_posix()
    immutable_json(work/'subtitle-settings.json',settings)
    graph=caption_filter({'subtitles':(work/'subtitle-settings.json').relative_to(dub.ROOT).as_posix()})
    if not output.exists():
        dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-i',str(picture),'-i',str(approved),
            '-map','0:v:0','-map','1:a:0','-t',str(cfg['duration_s']),'-vf',graph,
            '-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p',
            '-c:a','copy','-movflags','+faststart',str(output)],timeout=1800)
    dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-threads','2','-i',str(output),'-f','null','-'],timeout=900)
    def audio_hash(path):
        return dub.run([dub.tool('ffmpeg'),'-v','error','-i',str(path),'-map','0:a:0',
            '-c:a','copy','-f','hash','-hash','sha256','-']).stdout.strip()
    if audio_hash(output)!=audio_hash(approved):raise ValueError('Final AAC differs from approved audio.')
    info=dub.probe(output);v=next(x for x in info['streams'] if x['codec_type']=='video')
    if (v['width'],v['height'],int(v['nb_frames']))!=(720,1280,3996) or abs(float(v['duration'])-cfg['duration_s'])>.001:
        raise ValueError('Final picture geometry/timing changed.')
    measured=dub.loudness_info(output)
    if float(measured['input_tp'])>-.8 or abs(float(measured['input_i'])+16)>1:
        raise ValueError('Final audio headroom/loudness validation failed.')
    report={'status':'verified_final','owner_approval':cfg['owner_approval'],'inputs':inputs,
        'output_sha256':sha(output),'bytes':output.stat().st_size,'width':720,'height':1280,
        'frames':3996,'duration_s':cfg['duration_s'],'audio_packets_identical_to_approved':True,
        'source_picture_packets_sha256':dub.video_hash(picture),'loudness':measured,
        'picture':'Original picture and edit; only approved full-frame subtitle overlay re-encoded at CRF18.'}
    immutable_json(dub.relative(cfg['report']),report)
    print('Verified owner-approved final:',output,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('config');a=p.parse_args()
    try:finalize(dub.relative(a.config,True))
    except (ValueError,OSError,KeyError) as exc:p.exit(1,f'Error: {exc}\n')
