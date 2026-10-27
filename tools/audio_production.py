#!/usr/bin/env python3
"""Reusable common SFX/music buses and language-specific final mixes; no TTS."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import tempfile
import dub
import sfx


def file_spec(spec, duration):
    path=dub.relative(spec['path'],True)
    if spec.get('status') not in ('verified','approved') or not spec.get('provenance') or not spec.get('license'):
        raise ValueError('Audio input requires review/provenance/licence metadata.')
    if sfx.digest(path)!=spec.get('sha256'):raise ValueError('Audio input checksum changed: '+str(path))
    info=dub.probe(path)
    if not any(x['codec_type']=='audio' for x in info['streams']):raise ValueError('Expected audio input.')
    return path,float(info['format']['duration'])


def timeline(cues, output, duration, float_output=False):
    """Render reviewed asset cues at sample-accurate offsets into one bus."""
    count=round(duration*48000);inputs=[];filters=[];labels=[]
    for index,cue in enumerate(cues):
        inputs+=['-stream_loop','-1'] if cue.get('loop') else []
        inputs+=['-i',str(dub.relative(cue['path'],True))]
        start=round(cue['timestamp_s']*48000);length=round(cue['duration_s']*48000)
        if start<0 or start+length>count:raise ValueError('Timeline exceeds sample bounds.')
        fade=min(.01,cue['duration_s']/4)
        filters.append(f'[{index}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=end_sample={length},asetpts=N/SR/TB,volume={cue.get("effective_gain_db",cue.get("gain_db",0))}dB,afade=t=in:d={fade},afade=t=out:st={cue["duration_s"]-fade}:d={fade},adelay={start}S:all=1[a{index}]')
        labels.append(f'[a{index}]')
    if cues:
        graph=''.join(labels)+f'amix=inputs={len(cues)}:normalize=0,apad=whole_len={count},atrim=end_sample={count},asetpts=N/SR/TB'
        # Integer common stems always have peak headroom. Float final premix keeps dynamics.
        if not float_output:graph+=',alimiter=limit=0.85:level=false:latency=true'
        filters.append(graph+'[bus]')
        args=[*inputs,'-filter_complex',';'.join(filters),'-map','[bus]']
    else:args=['-f','lavfi','-i',f'anullsrc=r=48000:cl=stereo','-af',f'atrim=end_sample={count}']
    dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n',*args,'-ar','48000','-ac','2','-c:a','pcm_f32le' if float_output else 'pcm_s24le',str(output)],timeout=1800)


def validate(manifest, production=False):
    if manifest.get('schema_version')!=1 or manifest.get('status') not in sfx.STATES:
        raise ValueError('Invalid shared audio manifest version/status.')
    if set(manifest.get('dialogue',{}))!={'en','zh','ms'}:
        raise ValueError('Common ducking requires EN, ZH and MS dialogue inputs.')
    dub.relative(manifest['sfx_plan']);dub.relative(manifest['sfx_registry'])
    work=dub.relative(manifest['output_dir'])
    if not re.fullmatch(r'episodes/[a-z0-9-]+/media/derived/[a-zA-Z0-9_/-]+',manifest['output_dir']):
        raise ValueError('Working stems must stay in episode media/derived/.')
    for lang,path in manifest['exports'].items():
        dub.relative(path)
        if lang not in manifest['dialogue'] or not re.fullmatch(r'episodes/[a-z0-9-]+/exports/[^/]+\.mp4',path):raise ValueError('Invalid language export path.')
    if set(manifest['exports'])!={'en','zh','ms'}:raise ValueError('Three exports are required.')
    from production import validate_schema
    validate_schema(manifest, 'audio-production')
    registry=sfx.validate_registry(dub.load(dub.relative(manifest['sfx_registry'],True)))
    plan=dub.load(dub.relative(manifest['sfx_plan'],True))
    validate_schema(registry, 'sfx')
    validate_schema(plan, 'sfx-cues')
    cues=sfx.validate_plan(plan,registry,production)
    duration=manifest.get('duration_s')
    if production:
        if manifest['status'] not in ('verified','approved'):raise ValueError('Audio production needs reviewed inputs/timing.')
        dub.number(duration,'duration_s',.1,36000)
        if duration!=plan['duration_s']:raise ValueError('Plan duration differs from mix duration.')
        source=dub.relative(manifest['source_video'],True)
        if sfx.digest(source)!=manifest['source_video_sha256']:raise ValueError('Source picture changed.')
        if abs(float(dub.probe(source)['format']['duration'])-duration)>.05:raise ValueError('Full picture duration mismatch.')
        for language,spec in manifest['dialogue'].items():
            dub.number(spec.get('gain_db',0),'dialogue gain',-60,12)
            path,actual=file_spec(spec,duration)
            if abs(actual-duration)>.05:raise ValueError('Full dialogue stem duration mismatch: '+language)
            if not spec.get('provenance_report'):raise ValueError('Link the existing dialogue-render report.')
            report=dub.load(dub.relative(spec['provenance_report'],True))
            if report.get('stems',{}).get('dialogue')!=spec['path']:raise ValueError('Dialogue stem is not named in its production report.')
        scenes={x['id'] for x in plan['scenes']}
        for cue in manifest['music']+manifest.get('ambience',[]):
            file_spec(cue,duration)
            if cue.get('scene_id') not in scenes or not cue.get('timing_basis'):raise ValueError('Music/ambience cue needs scene and review evidence.')
            start=dub.number(cue.get('timestamp_s'),'bed timestamp',0,duration)
            length=dub.number(cue.get('duration_s'),'bed duration',.01,duration)
            if start+length>duration+1e-6:raise ValueError('Bed exceeds episode.')
            dub.number(cue.get('gain_db',0),'bed gain',-60,12)
            actual=float(dub.probe(dub.relative(cue['path'],True))['format']['duration'])
            if actual+.01<length and not cue.get('loop'):raise ValueError('Short bed needs explicit looping.')
        dub.number(manifest['mix']['integrated_lufs'],'LUFS',-30,-12)
        dub.number(manifest['mix']['true_peak_db'],'peak',-6,-1)
    for group in ('music','sfx'):
        config=manifest['ducking'][group]
        for name,lo,hi in [('threshold',.001,1),('ratio',1,20),('attack_ms',.01,2000),('release_ms',1,9000)]:
            dub.number(config.get(name),name,lo,hi)
    return registry,plan,cues


def prepare(manifest):
    registry,plan,cues=validate(manifest,True)
    for cue in cues:
        preset=registry['effects'][cue['preset_id']]
        variant=sfx.select_variation(preset,cue)
        asset=sfx.ensure_asset(preset,variant)
        actual=float(dub.probe(asset)['format']['duration'])
        if abs(actual-variant['duration_s'])>.05:
            raise ValueError('SFX variation duration metadata differs from the actual file.')
        cue['asset_sha256']=sfx.digest(asset)
        cue['asset_provenance']=variant.get('provenance',preset.get('provenance',{'source':preset['source']}))
        cue['asset_license']=variant.get('license',preset['license'])
    inputs={x['path']:sfx.digest(dub.relative(x['path'],True)) for x in cues+manifest['music']+manifest.get('ambience',[])+list(manifest['dialogue'].values())}
    for spec in manifest['dialogue'].values():
        inputs[spec['provenance_report']]=sfx.digest(dub.relative(spec['provenance_report'],True))
    signature={'manifest':manifest,'plan':plan,'registry':registry,'inputs':inputs,'source':manifest['source_video_sha256'],'engine_sha256':sfx.digest(Path(__file__)),'mastering_sha256':sfx.digest(Path(dub.__file__))}
    fingerprint=hashlib.sha256(json.dumps(signature,sort_keys=True).encode()).hexdigest()
    work=dub.relative(manifest['output_dir']);report_path=work/'shared.json'
    if work.exists():
        if not report_path.is_file():raise ValueError('Incomplete shared cache; preserve and choose a new output_dir.')
        report=dub.load(report_path)
        if report['fingerprint']!=fingerprint:raise ValueError('Shared inputs changed; version the output_dir.')
        for name,sha in report['files'].items():
            if sfx.digest(work/name)!=sha:raise ValueError('Shared stem cache modified.')
        return report
    work.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='common-audio-',dir=work.parent) as tmp:
        tmp=Path(tmp);duration=manifest['duration_s']
        timeline(cues+manifest.get('ambience',[]),tmp/'sfx.raw.wav',duration)
        timeline(manifest['music'],tmp/'music.raw.wav',duration)
        # Conservative union detector: dialogue from ANY language ducks the SAME beds.
        keys=[{'path':x['path'],'timestamp_s':0,'duration_s':duration,'gain_db':x.get('gain_db',0)} for x in manifest['dialogue'].values()]
        timeline(keys,tmp/'dialogue-key.wav',duration)
        for group in ('music','sfx'):
            d=manifest['ducking'][group]
            graph=f'[0:a][1:a]sidechaincompress=threshold={d["threshold"]}:ratio={d["ratio"]}:attack={d["attack_ms"]}:release={d["release_ms"]}:detection=peak:link=maximum,alimiter=limit=0.85:level=false:latency=true[a]'
            dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-i',str(tmp/(group+'.raw.wav')),'-i',str(tmp/'dialogue-key.wav'),'-filter_complex',graph,'-map','[a]','-c:a','pcm_s24le','-ar','48000','-ac','2',str(tmp/('common.'+group+'.wav'))],timeout=900)
        files={p.name:sfx.digest(p) for p in sorted(tmp.glob('*.wav'))}
        for p in tmp.glob('*.wav'):
            info=dub.probe(p)
            if abs(float(info['format']['duration'])-duration)>1/48000+.000001:raise ValueError('Common stem lost timeline samples.')
        report={'schema_version':1,'manifest':manifest,'registry_version':registry.get('registry_version'),'registry_path':manifest['sfx_registry'],'effect_provenance':{cue['preset_id']:{'license':registry['effects'][cue['preset_id']]['license'],'source':registry['effects'][cue['preset_id']]['source'],'provenance':registry['effects'][cue['preset_id']].get('provenance')} for cue in cues},'fingerprint':fingerprint,'files':files,'inputs':inputs,'resolved_cues':cues,'ducking':manifest['ducking'],'detector':'conservative union of the three aligned dialogue stems; identical ducked music/SFX reused across languages','duration_s':duration,'sample_rate':48000,'sample_count':round(duration*48000),'ffmpeg_version':dub.run([dub.tool('ffmpeg'),'-version']).stdout.splitlines()[0],'review_status':'technical_only_listening_and_scene_review_separate'}
        (tmp/'shared.json').write_text(json.dumps(report,indent=2)+'\n')
        tmp.replace(work)
    return report


def build(manifest):
    report=prepare(manifest);work=dub.relative(manifest['output_dir']);duration=manifest['duration_s'];results={}
    for lang,output in manifest['exports'].items():
        target=dub.relative(output);stamp=target.with_suffix('.json')
        spec=manifest['dialogue'][lang]
        if target.exists() or stamp.exists():
            if not target.is_file() or not stamp.is_file():raise ValueError('Partial export; choose a new version.')
            old=dub.load(stamp)
            if old.get('shared_fingerprint')!=report['fingerprint'] or old.get('output_sha256')!=sfx.digest(target) or not target.with_suffix('.mix.wav').is_file() or old.get('mixed_audio_sha256')!=sfx.digest(target.with_suffix('.mix.wav')):raise ValueError('Existing language export changed.')
            results[lang]=old;continue
        target.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='audio-release-',dir=target.parent) as tmp:
            tmp=Path(tmp)
            inputs=[{'path':spec['path'],'timestamp_s':0,'duration_s':duration,'gain_db':spec.get('gain_db',0)}]+[{'path':(work/('common.'+g+'.wav')).relative_to(dub.ROOT).as_posix(),'timestamp_s':0,'duration_s':duration,'gain_db':0} for g in ('music','sfx')]
            timeline(inputs,tmp/'mix.wav',duration,True)
            m={'kind':'dubbing_production','duration_s':duration,'source_start_s':0,'mix':manifest['mix']}
            info,measured,final,picture=dub.master_audio(m,dub.relative(manifest['source_video'],True),tmp/'mix.wav',tmp/'movie.mp4')
            info['format']['filename']=output
            dialogue_source=dub.load(dub.relative(spec['provenance_report'],True)).get('manifest')
            dialogue_manifest={key:dialogue_source[key] for key in ('language','duration_s','dialogue')} if dialogue_source else None
            result={'dialogue_manifest':dialogue_manifest,'mixed_audio_sha256':sfx.digest(tmp/'mix.wav'),'status':'technical_checks_passed_listening_review_pending','shared_fingerprint':report['fingerprint'],'common_music_sha256':report['files']['common.music.wav'],'common_sfx_sha256':report['files']['common.sfx.wav'],'dialogue':spec,'source_sha256':manifest['source_video_sha256'],'output_sha256':sfx.digest(tmp/'movie.mp4'),'encoded_audio_measurement':final,'loudness_measurement_before_normalization':measured,'picture_packet_hash':picture,'language':lang,'api_calls':0,'output_metadata':info}
            dub.write_new(target.with_suffix('.mix.wav'),(tmp/'mix.wav').read_bytes())
            dub.write_new(target,(tmp/'movie.mp4').read_bytes())
            dub.write_new(stamp,(json.dumps(result,indent=2)+'\n').encode())
            results[lang]=result
        print('Verified full mix',lang,output,flush=True)
    return results


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest');p.add_argument('command',choices=['validate','prepare','build'])
    args=p.parse_args();m=dub.load(dub.relative(args.manifest,True))
    if args.command=='validate':
        validate(m,False);print('Structurally valid; status '+m['status']+'. Unknown draft timing is not production-ready.')
    elif args.command=='prepare':print(json.dumps(prepare(m),indent=2))
    else:build(m)


if __name__=='__main__':main()
