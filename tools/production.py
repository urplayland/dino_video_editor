#!/usr/bin/env python3
"""Full-episode multilingual production using the preserved kit and dubbing helper."""
import argparse
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
import time

import dub
from score import compose


def language_manifest(episode, lang):
    if episode.get('schema_version') != 1 or episode.get('kind') != 'multilingual_production':
        raise ValueError('Expected multilingual_production schema_version 1.')
    if lang not in episode.get('languages', []):
        raise ValueError('Language not configured for this episode.')
    result = {k:episode[k] for k in ('schema_version','status','source_video','source_start_s','duration_s','output_dir','original_audio','mix','beds','sfx')}
    result.update(kind='dubbing_production',language=lang,dialogue=[])
    for row in episode['dialogue']:
        if row.get('include_in_dub',True) is False:
            continue
        cue = {k:v for k,v in row.items() if k not in ('text','audio','translations','timing_overrides')}
        cue['text'] = row['text'][lang]
        audio = row.get('audio', {}).get(lang, {})
        cue.update(audio)
        result['dialogue'].append(cue)
    return result


def validate_schema(document, name):
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        raise ValueError('Install requirements-production.txt for formal JSON Schema validation.') from None
    schema = dub.load(dub.ROOT / 'schemas' / f'{name}.schema.json')
    Draft202012Validator.check_schema(schema)
    problems = list(Draft202012Validator(schema).iter_errors(document))
    if problems:
        first = problems[0]
        location = '/'.join(str(x) for x in first.absolute_path) or '<root>'
        raise ValueError(f'{name} schema at {location}: {first.message}')


def validate(episode, voices):
    validate_schema(episode, 'production')
    validate_schema(voices, 'voices')
    validate_schema(dub.load(dub.relative(episode['sfx_registry'], True)), 'sfx')
    if not episode.get('original_reference') or not episode.get('transcript_evidence'):
        raise ValueError('Production needs an original reference and transcription evidence.')
    dub.relative(episode['original_reference'], True)
    for path in episode['transcript_evidence']:
        dub.relative(path, True)
    for lang in episode['languages']:
        dub.validate(language_manifest(episode,lang),voices)
    return episode


def assets(episode, registry):
    duration=episode['duration_s']
    music=dub.relative(episode['score']['music_path'])
    ambience=dub.relative(episode['score']['ambience_path'])
    if episode['score'].get('plan'):
        from scene_score import render as render_score
        plan_path=dub.relative(episode['score']['plan'],True)
        if dub.load(plan_path)['output']!=episode['score']['music_path']:
            raise ValueError('Scene score plan/output mismatch.')
        render_score(plan_path)
        if not ambience.exists():
            raise ValueError('Supply the retained ambience asset before building the scene score.')
    else:
        if music.exists()!=ambience.exists():
            raise ValueError('Incomplete score assets; choose a new score version.')
        if not music.exists():
            compose(duration,music,ambience)
    spec=importlib.util.spec_from_file_location('kit_sfx',Path(__file__).parent/'kit/make_sfx.py')
    kit=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    kit.ROOT=dub.relative(episode['output_dir'])/'kit-synth'
    for effect_id in sorted({x['effect'] for x in episode['sfx']}):
        effect=registry['effects'][effect_id]
        asset=dub.relative(effect['asset_path'])
        if asset.exists():
            continue
        if effect['source']!='local_synth' or effect_id not in ('whoosh','chime','pop','footsteps','rumble'):
            raise ValueError('Effect needs a supplied asset or implemented generator: '+effect_id)
        with redirect_stdout(io.StringIO()):
            kit.make(effect_id,effect['duration_s'],effect_id)
        generated=kit.ROOT/'output/sfx'/f'{effect_id}.wav'
        dub.write_new(asset,generated.read_bytes())
    records=[]
    for path in [music,ambience]+[dub.relative(registry['effects'][x['effect']]['asset_path']) for x in episode['sfx']]:
        records.append({'path':path.relative_to(dub.ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    asset_version=hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()[:12]
    report=dub.relative(episode['output_dir'])/('assets-'+asset_version+'.json')
    if not report.exists():
        dub.write_new(report,(json.dumps({'generator':episode['score'].get('generator','tools/score.py')+' and handover kit make_sfx.py','score_provenance':episode['score'].get('provenance'),'assets':records},indent=2)+'\n').encode())
    print('Reusable music, ambience and effects are ready.')


def normalize_words(text):
    # ASR orthography may be traditional or use a homophonous third-person pronoun.
    text = text.translate(str.maketrans({'誰':'谁','兒':'儿','麼':'么','闖':'闯','霧':'雾','謝':'谢','聽':'听','見':'见','嗎':'吗','為':'为','們':'们','幫':'帮','雲':'云','後':'后','諾':'诺','妳':'你','這':'这','裡':'里','來':'来','讓':'让','個':'个','說':'说','於':'于','與':'与','開':'开','關':'关','聲':'声','諒':'谅','他':'她'}))
    text = text.replace('迪诺','Dino')
    return ''.join(x.lower() for x in text if x.isalnum())


def transcript_similarity(expected, heard):
    from difflib import SequenceMatcher
    # Character frequency is meaningful in long speech; autojunk can discard nearly
    # every common Malay/English letter and report a false failure after one typo.
    return SequenceMatcher(None,normalize_words(expected),normalize_words(heard),autojunk=False).ratio()


def check_required_names(cue, heard):
    # Keep name checks independent of overall fuzzy transcript similarity.
    # Latin Dino and wrong initials must not silently pass as Chinese 迪诺.
    traditional=str.maketrans({'諾':'诺','敵':'敌','雲':'云','爺':'爷'})
    recognized=heard.translate(traditional)
    results=[]
    for name in cue.get('required_names',[]):
        aliases=[name]+cue.get('name_asr_aliases',{}).get(name,[])
        matched=next((alias for alias in aliases if alias.translate(traditional) in recognized),None)
        results.append({'required':name,'matched':matched,'passed':matched is not None})
    return results


def canonical_name_transcript(cue, heard):
    # ASR may choose same-tone homophonous Chinese characters for an uncommon name.
    # This scoped list never accepts a changed initial such as 李/比/伊.
    recognized=heard.translate(str.maketrans({'諾':'诺','敵':'敌','雲':'云','爺':'爷'}))
    for name in cue.get('required_names',[]):
        for alias in cue.get('name_asr_aliases',{}).get(name,[]):
            recognized=recognized.replace(alias,name)
    return recognized


def verify_audio(episode, lang, voices, model_size, existing_only=False):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ValueError('Install requirements-transcription.txt in the optional venv for local ASR verification.') from None
    import os
    model=WhisperModel(model_size,device='cpu',compute_type='int8',cpu_threads=min(8,os.cpu_count() or 4))
    m=language_manifest(episode,lang)
    report_dir=dub.relative(episode['report_dir'])
    report_dir.mkdir(parents=True,exist_ok=True)
    results=[]
    for cue in m['dialogue']:
        transcript=cue.get('spoken_text',cue['text'])
        path=dub.relative(cue.get('audio_path') or f'{m["output_dir"]}/{lang}/{cue["id"]}.wav')
        if existing_only and not path.is_file():
            print(f'Missing (not generated): {lang}/{cue["id"]}', flush=True)
            continue
        if not path.is_file():
            raise ValueError(f'Missing dialogue WAV: {lang}/{cue["id"]}')
        data=path.read_bytes();info=dub.wav_info(data)
        cached_path=report_dir/f'{lang}-{cue["id"]}-audio-check.json'
        if cached_path.is_file():
            cached=dub.load(cached_path)
            if cached.get('status')=='passed_automated' and cached.get('sha256')==hashlib.sha256(data).hexdigest() and cached.get('expected_text')==transcript and cached.get('model')==model_size and (not cue.get('required_names') or (cached.get('required_names')==cue['required_names'] and cached.get('name_checks_passed') is True and cached.get('name_asr_aliases',{})==cue.get('name_asr_aliases',{}))):
                for row in episode['dialogue']:
                    if row['id']==cue['id']:
                        row.setdefault('audio',{}).setdefault(lang,{}).update(audio_review_status='verified_automated',audio_verification_report=cached_path.relative_to(dub.ROOT).as_posix(),gain_db=cached['suggested_gain_db'])
                results.append(cached)
                print(f'{lang}/{cue["id"]}: cached matching audio verification reused.',flush=True)
                continue
        segments,_=model.transcribe(str(path),language=lang,beam_size=5,condition_on_previous_text=False)
        segments=list(segments)
        heard=' '.join(s.text.strip() for s in segments)
        comparison_transcript=canonical_name_transcript(cue,heard)
        expected=normalize_words(transcript);actual=normalize_words(comparison_transcript)
        from difflib import SequenceMatcher
        similarity=transcript_similarity(expected,actual)
        # This is a machine transcript check, not a claim of human voice/accent approval.
        name_checks=check_required_names(cue,heard)
        names_passed=all(x['passed'] for x in name_checks)
        status='passed_automated' if similarity>=.84 and names_passed else 'needs_review'
        level=dub.run([dub.tool('ffmpeg'),'-hide_banner','-nostdin','-i',str(path),'-af','volumedetect','-f','null','-']).stderr
        mean=re.search(r'mean_volume: ([-\d.]+) dB',level)
        peak=re.search(r'max_volume: ([-\d.]+) dB',level)
        if not mean or not peak:
            raise ValueError('Generated audio is silent or unreadable.')
        gain=min(9,max(-12,-22-float(mean[1])), -3-float(peak[1]))
        report={'cue':cue['id'],'language':lang,'expected_text':transcript,'requested_text':cue['text'],'recognized_text':heard,'similarity':similarity,
            'status':status,'required_names':cue.get('required_names',[]),'name_asr_aliases':cue.get('name_asr_aliases',{}),'comparison_transcript':comparison_transcript,'name_checks':name_checks,'name_checks_passed':names_passed,'sha256':hashlib.sha256(data).hexdigest(),'audio':info,'model':model_size,
            'mean_dbfs':float(mean[1]),'peak_dbfs':float(peak[1]),'suggested_gain_db':round(gain,2),
            'limits':'ASR matching does not prove voice identity, natural pronunciation, acting quality, or human approval.'}
        output=report_dir/f'{lang}-{cue["id"]}-audio-check.json'
        # Reports are refreshed only for their corresponding checks; media remains immutable.
        output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
        for row in episode['dialogue']:
            if row['id']==cue['id']:
                row.setdefault('audio',{}).setdefault(lang,{}).update(
                    audio_review_status='verified_automated' if status=='passed_automated' else 'needs_review',
                    audio_verification_report=output.relative_to(dub.ROOT).as_posix(),gain_db=round(gain,2))
        results.append(report)
        print(json.dumps({'line':cue['id'],'status':status,'similarity':round(similarity,3),'recognized':heard,'name_checks_passed':names_passed},ensure_ascii=False),flush=True)
    return results



def fit_timeline(episode, lang):
    previous_end = 0
    result = []
    for row in episode['dialogue']:
        if row.get('include_in_dub',True) is False:
            continue
        cue_audio = row.setdefault('audio', {}).setdefault(lang, {})
        path = dub.relative(cue_audio.get('audio_path') or f'{episode["output_dir"]}/{lang}/{row["id"]}.wav', True)
        lead, tail = dub.speech_bounds(path.read_bytes())
        length = tail - lead
        window = row['end_s'] - row['start_s']
        speed = min(1.10, max(1, length/window))
        start = max(row.get('timing_overrides',{}).get(lang,{}).get('start_s',row['start_s']), row['start_s'], previous_end + .06)
        end = start + length/speed + .005
        drift = start-row['start_s']
        if drift > 1.5 or end > episode['duration_s']-.15:
            raise ValueError(f'{lang}/{row["id"]} cannot fit naturally: start shift {drift:.2f}s; choose a faster delivery or review timing.')
        cue_audio.update(start_s=round(start,4), end_s=round(end,4))
        previous_end = end
        result.append({'id':row['id'], 'source_start_s':row['start_s'], 'dub_start_s':start, 'dub_end_s':end,
                       'shift_s':drift, 'tempo':speed, 'trim_start_s':lead, 'trim_end_s':tail})
    report = dub.relative(episode['report_dir']) / f'{lang}-timing-fit.json'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({'max_start_shift_s':1.5, 'max_speedup':1.10, 'cues':result},indent=2)+'\n')
    return result




def verify_export_audio(episode, lang, model_size):
    if not verified_export(episode, lang):
        raise ValueError('No verified complete export exists for this language.')
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ValueError('Install optional transcription dependencies for final audio verification.') from None
    import os
    from difflib import SequenceMatcher
    model=WhisperModel(model_size,device='cpu',compute_type='int8',cpu_threads=min(8,os.cpu_count() or 4))
    source=dub.relative(episode['exports'][lang],True)
    segments,_=model.transcribe(str(source),language=lang,beam_size=5,condition_on_previous_text=False,vad_filter=True,word_timestamps=True)
    rows=[]
    for segment in segments:
        rows.append({'start_s':segment.start,'end_s':segment.end,'text':segment.text})
        print(json.dumps(rows[-1],ensure_ascii=False),flush=True)
    heard=' '.join(r['text'].strip() for r in rows)
    expected=' '.join(r.get('spoken_text',r['text']) for r in language_manifest(episode,lang)['dialogue'])
    comparison_transcript=heard
    for cue in language_manifest(episode,lang)['dialogue']:
        comparison_transcript=canonical_name_transcript(cue,comparison_transcript)
    similarity=transcript_similarity(expected,comparison_transcript)
    status='passed_automated' if similarity>=.96 else 'needs_review'
    report={'status':status,'source':episode['exports'][lang],'output_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'model':model_size,'expected_text':expected,'recognized_text':heard,'comparison_transcript':comparison_transcript,'similarity':similarity,'segments':rows,
        'limits':'Independent ASR checks encoded mixed dialogue; this does not establish human accent/acting/music approval.'}
    dest=dub.relative(episode['report_dir'])/f'{lang}-final-dialogue-check.json'
    dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    if status!='passed_automated':
        raise ValueError(f'Final mixed dialogue needs review: similarity {similarity:.3f}. See {dest.relative_to(dub.ROOT)}.')
    print(f'{lang}: complete encoded mixed-dialogue check passed ({similarity:.3f}).')
    return report


def mixed_check_valid(episode, lang):
    path=dub.relative(episode['report_dir'])/f'{lang}-final-dialogue-check.json'
    movie=dub.relative(episode['exports'][lang])
    if not path.is_file() or not movie.is_file():
        return False
    report=dub.load(path)
    return report.get('status')=='passed_automated' and report.get('output_sha256')==hashlib.sha256(movie.read_bytes()).hexdigest()


def production_status(episode):
    result = {'complete': False, 'human_review_status':episode.get('human_review_status','pending'), 'languages': {}}
    for lang in episode['languages']:
        active=[r for r in episode['dialogue'] if r.get('include_in_dub',True) is not False]
        available, verified, missing = [], [], []
        for row in active:
            audio = row.get('audio', {}).get(lang, {})
            file = dub.relative(audio.get('audio_path') or f'{episode["output_dir"]}/{lang}/{row["id"]}.wav')
            if file.is_file():
                available.append(row['id'])
                if audio.get('audio_review_status') in ('approved', 'verified_automated'):
                    verified.append(row['id'])
            else:
                missing.append(row['id'])
        export_exists=dub.relative(episode['exports'][lang]).is_file()
        try:
            technical=verified_export(episode,lang) if export_exists else False
        except (ValueError,OSError,KeyError):
            technical=False
        result['languages'][lang] = {'total_lines': len(active), 'generated': len(available),
            'audio_checked': len(verified), 'missing': missing, 'export_exists': export_exists,
            'export_technically_verified':technical, 'mixed_dialogue_checked':mixed_check_valid(episode,lang)}
    result['complete']=all(row['export_technically_verified'] and row['mixed_dialogue_checked'] and not row['missing'] for row in result['languages'].values())
    return result


def verified_export(episode, lang):
    target = dub.relative(episode['exports'][lang])
    if not target.exists():
        return False
    report = dub.load(target.with_suffix('.json'))
    if report.get('manifest') != language_manifest(episode,lang) or report.get('output_sha256') != hashlib.sha256(target.read_bytes()).hexdigest():
        raise ValueError('Existing export differs from current manifest or checksum; choose a new export version.')
    source=dub.relative(episode['source_video'],True)
    if report.get('source_sha256') != hashlib.sha256(source.read_bytes()).hexdigest():
        raise ValueError('Picture master changed after export.')
    voices=dub.load(dub.relative(episode['voice_registry'],True))
    for cue in language_manifest(episode,lang)['dialogue']:
        path=dub.relative(cue.get('audio_path') or f'{episode["output_dir"]}/{lang}/{cue["id"]}.wav',True)
        record=dub.load(path.with_suffix('.json'))
        char=voices['characters'][cue['character']]
        identity={'model':char['model'],'voice_version':char['preset_version'],'request':dub.payload(cue,char,lang)}
        fingerprint=hashlib.sha256(json.dumps(identity,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        if record.get('fingerprint')!=fingerprint or record.get('sha256')!=hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError('Existing export has changed dialogue or voice configuration.')
    return True


def allowed_languages(episode, requested=None):
    allowed=episode.get('production_languages',episode['languages'])
    chosen=allowed if requested in (None,'all') else [requested]
    if not chosen or any(lang not in allowed for lang in chosen):
        raise ValueError('Language production is on hold pending owner approval of English.')
    return chosen


def build(manifest, episode, live, interval):
    """Resume each complete language through generation, checks, fit and render."""
    import subprocess
    def invoke(arguments):
        completed = subprocess.run([sys.executable, '-u', str(Path(__file__).resolve()), manifest, *arguments], check=False)
        if completed.returncode:
            raise ValueError('Production paused at: '+' '.join(arguments)+'. Existing sources and completed stems are retained.')
    invoke(['assets'])
    for lang in allowed_languages(episode):
        current=dub.load(dub.relative(manifest,True))
        if verified_export(current,lang):
            print(f'{lang}: existing export and provenance verified; skipping rebuild.')
            if not mixed_check_valid(current,lang):
                invoke(['verify-export', '--lang', lang, '--model', 'small.en' if lang == 'en' else 'small'])
            continue
        command = ['generate', '--lang', lang, '--interval', str(interval)]
        if live:
            command.append('--live')
        invoke(command)
        invoke(['verify-audio', '--lang', lang, '--model', 'small.en' if lang == 'en' else 'small'])
        invoke(['fit', '--lang', lang])
        invoke(['render', '--lang', lang])
        invoke(['verify-export', '--lang', lang, '--model', 'small.en' if lang == 'en' else 'small'])
    print('Enabled language render commands succeeded. Full human listening/visual review remains separate from technical validation.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--env-file', default='.env', help='Read GEMINI_API_KEY from an explicitly selected local dotenv file; never copy its contents')
    p.add_argument('--env-key', default='GEMINI_API_KEY', help='Explicitly select one authorized Gemini variable; no automatic rotation')
    p.add_argument('manifest')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('validate');sub.add_parser('assets');sub.add_parser('status')
    b=sub.add_parser('build')
    b.add_argument('--live',action='store_true')
    b.add_argument('--interval',type=float,default=21)
    for command in ('generate','verify-audio','verify-export','fit','render'):
        c=sub.add_parser(command)
        c.add_argument('--lang',choices=('en','zh','ms','all'),default='all')
        if command=='generate':
            c.add_argument('--live',action='store_true')
            c.add_argument('--line')
            c.add_argument('--regenerate',action='store_true')
            c.add_argument('--interval',type=float,default=21,help='Minimum seconds between new free-tier requests (default 21)')
        elif command in ('verify-audio','verify-export'):
            c.add_argument('--model',default='small')
            if command=='verify-audio':
                c.add_argument('--existing-only',action='store_true',help='Check available stems without claiming the language is complete')
    args=p.parse_args()
    try:
        dub.load_env(Path(args.env_file), args.env_key)
        import os
        os.environ.setdefault('DINO_CREDENTIAL_LABEL', f'{Path(args.env_file).parent.name or "project"}:{args.env_key}')
        path=dub.relative(args.manifest,True)
        episode=dub.load(path);voices=dub.load(dub.relative(episode['voice_registry'],True))
        validate(episode,voices)
        if args.command=='validate':
            print('Full-episode manifest structurally valid.')
            return
        if args.command=='status':
            print(json.dumps(production_status(episode),indent=2))
            return
        if args.command=='build':
            build(args.manifest,episode,args.live,args.interval)
            return
        if args.command=='assets':
            assets(episode,dub.load(dub.relative(episode['sfx_registry'],True)))
            return
        langs=allowed_languages(episode,args.lang)
        last_request = None
        for lang in langs:
            m=language_manifest(episode,lang)
            if args.command=='generate':
                if args.live and not episode.get('api_preflight',{}).get('owner_confirmed_billing_disabled'):
                    raise ValueError('Record reviewed billing/quota before live generation; this production run is free-tier only.')
                for cue in m['dialogue']:
                    if args.line and cue['id'] != args.line:
                        continue
                    existing = dub.relative(cue.get('audio_path') or f'{m["output_dir"]}/{lang}/{cue["id"]}.wav').exists()
                    if args.live and (not existing or args.regenerate):
                        if last_request is not None:
                            time.sleep(max(0, args.interval-(time.monotonic()-last_request)))
                        last_request=time.monotonic()
                    dub.generate(m,voices,cue['id'],args.live,args.regenerate)
            elif args.command=='verify-audio':
                results=verify_audio(episode,lang,voices,args.model,args.existing_only)
                path.write_text(json.dumps(episode,indent=2,ensure_ascii=False)+'\n')
                if any(r['status']=='needs_review' for r in results):
                    raise ValueError('Generated dialogue check has discrepancies; review reports before rendering.')
            elif args.command=='verify-export':
                verify_export_audio(episode,lang,args.model)
            elif args.command=='fit':
                results=fit_timeline(episode,lang)
                path.write_text(json.dumps(episode,indent=2,ensure_ascii=False)+'\n')
                print(f'{lang}: fit {len(results)} lines to the full picture timeline.')
            else:
                dub.render(m,voices,episode['exports'][lang])
    except (ValueError,OSError,KeyError,TypeError) as exc:
        if 'episode' in locals() and episode.get('report_dir'):
            from datetime import datetime, timezone
            report=dub.relative(episode['report_dir'])/'last-failure.json'
            report.parent.mkdir(parents=True,exist_ok=True)
            report.write_text(json.dumps({'status':'blocked_or_check_failed','command':args.command,'error':str(exc),'at':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
        p.exit(1,f'Error: {exc}\n')


if __name__=='__main__':
    main()
