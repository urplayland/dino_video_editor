#!/usr/bin/env python3
"""Reproduce standalone SFX/mixing acceptance media without touching any episode.

All dialogue signals are synthetic QA tones, not character voices or a transcript.
No original footage, API key, downloaded sample or GPU is used.
"""
import argparse
import json
from pathlib import Path
import dub
import sfx
import audio_production


def create(version):
    if not version.isalnum():raise ValueError('Use an alphanumeric verification version.')
    base='episodes/audio-system-verification'
    source=dub.relative(base+'/media/derived/fixture-'+version)
    if source.exists():raise ValueError('Fixture exists; use a new version or rebuild its saved audio manifest.')
    source.mkdir(parents=True)
    def save(name,value):
        p=source/name;p.write_text(json.dumps(value,indent=2)+'\n');return p.relative_to(dub.ROOT).as_posix()
    video=source/'picture.mp4'
    text='Technical audio verification - synthetic QA signals - not episode footage'
    dub.run([dub.tool('ffmpeg'),'-v','error','-f','lavfi','-i','color=c=0x172b36:s=320x568:r=24:d=12','-vf',"drawtext=text='Audio system verification':fontsize=20:fontcolor=white:x=(w-tw)/2:y=80,drawtext=text='Synthetic test signals':fontsize=16:fontcolor=white:x=(w-tw)/2:y=130",'-an','-c:v','libx264','-pix_fmt','yuv420p',str(video)])
    music=source/'music.wav'
    dub.run([dub.tool('ffmpeg'),'-v','error','-f','lavfi','-i','aevalsrc=0.04*(sin(2*PI*196*t)+sin(2*PI*246.94*t)+sin(2*PI*293.66*t)):s=48000:d=12','-ac','2','-c:a','pcm_s24le',str(music)])
    dialogue={}
    for index,lang in enumerate(['en','zh','ms']):
        path=source/('diagnostic-'+lang+'.wav')
        start=1+index*.5
        dub.run([dub.tool('ffmpeg'),'-v','error','-f','lavfi','-i',f'sine=frequency={400+index*100}:duration=12','-af',f"volume='if(between(t,{start},{start+2})+between(t,7,9),3,0)':eval=frame",'-ar','48000','-ac','2','-c:a','pcm_s24le',str(path)])
        relative=path.relative_to(dub.ROOT).as_posix()
        report=save(lang+'-diagnostic.json',{'stems':{'dialogue':relative},'status':'synthetic_diagnostic_fixture_not_character_voice','note':text})
        dialogue[lang]={'path':relative,'sha256':sfx.digest(path),'status':'verified','provenance':'Locally generated diagnostic tone; not character speech, not film dialogue','license':'Project-generated test signal, no external sample','provenance_report':report}
    events=[('dino-step-1','dino_footstep',.6),('dino-step-2','dino_footstep',1.2),('dino-step-3','dino_footstep',1.8),('bunny-hop','bunny_hop',3.8),('bunny-reaction','bunny_surprise',4.4),('pop','magic_pop',5.1),('whoosh','magic_whoosh',5.7),('click','puzzle_click',7.3),('restore','rainbow_restore',8.1),('hug','soft_hug',10.4),('forest','forest_ambience',0),('river','river_ambience',0),('magic-bed','magical_ambience',0)]
    cues=[]
    for ident,effect,when in events:
        cues.append({'id':ident,'scene_id':'diagnostic','preset_id':effect,'preset_version':'v001','timestamp_s':when,'status':'verified','timing_basis':'Explicit synthetic QA schedule, not a scripted or observed episode action','gain_db':-3 if effect.endswith('ambience') else 0})
    plan=save('sfx-cues.json',{'schema_version':1,'status':'verified','duration_s':12,'scenes':[{'id':'diagnostic','description':text}],'cues':cues})
    m=dub.load(dub.ROOT/'templates/episode/audio-production.json')
    m.update(status='verified',source_video=video.relative_to(dub.ROOT).as_posix(),source_video_sha256=sfx.digest(video),duration_s=12,sfx_plan=plan,dialogue=dialogue,output_dir=base+'/media/derived/common-'+version,exports={lang:base+'/exports/audio_verification_'+lang+'_'+version+'.mp4' for lang in dialogue})
    m['music']=[{'path':music.relative_to(dub.ROOT).as_posix(),'sha256':sfx.digest(music),'scene_id':'diagnostic','status':'verified','provenance':'Original local sine-pad diagnostic underscore, not an Episode 2 score','license':'Project-generated synthesis, no external samples','timestamp_s':0,'duration_s':12,'gain_db':-8,'timing_basis':'Synthetic QA timeline'}]
    manifest=save('audio-production.json',m)
    result=audio_production.build(m)
    save('acceptance.json',{'status':'three_language_technical_acceptance_passed','manifest':manifest,'results':result,'not_episode_content':True,'api_calls':0})
    print('Saved verification media and report:',manifest)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--version',default='v001');args=p.parse_args();create(args.version)
