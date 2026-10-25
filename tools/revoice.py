#!/usr/bin/env python3
"""Resume controlled per-line retakes without losing completed generations or old takes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

import dub
import production


def identity(cue,char,lang):
    value={'model':char['model'],'voice_version':char['preset_version'],'request':dub.payload(cue,char,lang)}
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def matching_take(folder,cue,fingerprint):
    candidates=[]
    for path in folder.glob('take-*/'+cue['id']+'.json'):
        record=dub.load(path)
        if record.get('fingerprint')!=fingerprint:continue
        audio=dub.relative(record['output'],True)
        if hashlib.sha256(audio.read_bytes()).hexdigest()==record.get('sha256'):candidates.append(record)
    return max(candidates,key=lambda r:r['created_at']) if candidates else None


def run(manifest,lang,env_file,keys,live,interval,line=None):
    path=dub.relative(manifest,True);episode=dub.load(path);voices=dub.load(dub.relative(episode['voice_registry'],True))
    production.allowed_languages(episode,lang);production.validate(episode,voices)
    preflight=episode['api_preflight']
    if live and (not preflight.get('owner_confirmed_billing_disabled') or not preflight.get('owner_authorized_free_key_pool')):
        raise ValueError('Existing unbilled-key authorization is required; this tool never enables billing.')
    if any(k not in preflight.get('authorized_key_variables',[]) for k in keys):raise ValueError('Credential variable is outside the authorized allowlist.')
    key_index=-1;used=set();last_request=None
    def select_key():
        nonlocal key_index
        while key_index+1<len(keys):
            key_index+=1;os.environ.pop('GEMINI_API_KEY',None);dub.load_env(Path(env_file),keys[key_index])
            key=os.environ.get('GEMINI_API_KEY')
            if not key:continue
            digest=hashlib.sha256(key.encode()).hexdigest()
            if digest in used:continue
            used.add(digest);os.environ['DINO_CREDENTIAL_LABEL']='owner-authorized:'+keys[key_index]
            print('Using authorized free-tier variable',keys[key_index],flush=True);return
        raise ValueError('Selected free-tier credentials exhausted/unavailable; completed takes retained.')
    selected=[cue for cue in production.language_manifest(episode,lang)['dialogue'] if line is None or cue['id']==line]
    if not selected:raise ValueError('Unknown selected line.')
    for original in selected:
        current=dub.load(path);m=production.language_manifest(current,lang);cue=next(x for x in m['dialogue'] if x['id']==original['id']);char=voices['characters'][cue['character']]
        if not cue.get('delivery_style'):raise ValueError('Controlled retake needs explicit per-line direction.')
        fingerprint=identity(cue,char,lang);folder=dub.relative(m['output_dir'])/lang
        record=matching_take(folder,cue,fingerprint)
        if not live:
            print(json.dumps({'line':cue['id'],'voice':char['voice'],'cached_matching_take':bool(record)},ensure_ascii=False));continue
        while record is None:
            if key_index<0:select_key()
            if last_request is not None:time.sleep(max(0,interval-(time.monotonic()-last_request)))
            last_request=time.monotonic()
            try:dub.generate(m,voices,cue['id'],True,True)
            except ValueError as exc:
                if 'GenerateRequestsPerDayPerProjectPerModel-FreeTier' in str(exc):
                    print('Confirmed daily free-tier exhaustion for',keys[key_index],'; keeping completed takes.',flush=True);select_key();continue
                raise
            record=matching_take(folder,cue,fingerprint)
            if record is None:raise ValueError('Generation returned without a matching recoverable take.')
        row=next(x for x in current['dialogue'] if x['id']==cue['id']);audio=row.setdefault('audio',{}).setdefault(lang,{})
        audio['audio_path']=record['output'];audio['audio_review_status']='pending'
        for stale in ('audio_verification_report','gain_db','start_s','end_s','spoken_text','spoken_text_evidence'):audio.pop(stale,None)
        path.write_text(json.dumps(current,indent=2,ensure_ascii=False)+'\n')
        a,b=dub.speech_bounds(dub.relative(record['output']).read_bytes())
        print(f'{lang}/{cue["id"]}: selected {b-a:.3f}s take, {char["voice"]}; pronunciation/acting review pending.',flush=True)
    print('All selected retakes generated/recovered. Run local speech/name checks before rendering.',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest');p.add_argument('--lang',required=True,choices=('en','zh','ms'));p.add_argument('--env-file',default='.env');p.add_argument('--keys',nargs='+',required=True);p.add_argument('--line');p.add_argument('--live',action='store_true');p.add_argument('--interval',type=float,default=21);a=p.parse_args()
    try:run(a.manifest,a.lang,a.env_file,a.keys,a.live,a.interval,a.line)
    except (ValueError,OSError,KeyError) as e:p.exit(1,f'Error: {e}\n')

if __name__=='__main__':main()
