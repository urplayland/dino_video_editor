#!/usr/bin/env python3
"""Versioned deterministic procedural SFX, licensed-file resolution and cue plans."""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import random
import re
import struct
import wave
import dub

RATE = 48000
GENERATORS = {'dino_footstep','bunny_hop','bunny_surprise','magic_pop','magic_whoosh',
              'puzzle_click','rainbow_restore','soft_hug','forest_ambience','river_ambience','magical_ambience'}
STATES = {'sample','draft','verified','approved'}


def digest(path):
    with path.open('rb') as stream:
        h = hashlib.sha256()
        for part in iter(lambda: stream.read(1024*1024), b''):
            h.update(part)
        return h.hexdigest()


def validate_registry(registry):
    if registry.get('schema_version') != 1 or not registry.get('effects'):
        raise ValueError('Expected SFX registry schema_version 1.')
    for key, preset in registry['effects'].items():
        if not re.fullmatch('[a-z][a-z0-9_]*', key):
            raise ValueError('Invalid stable effect ID.')
        dub.number(preset.get('default_gain_db'), 'default_gain_db', -60, 12)
        if not preset.get('license') or not preset.get('source'):
            raise ValueError('Effect requires source/licence metadata.')
        dub.relative(preset['asset_path'])
        variations = preset.get('variations', [])
        if variations and not preset.get('preset_version'):
            raise ValueError('Versioned variations need preset_version.')
        seen = set()
        for variant in variations:
            if not variant.get('id') or variant['id'] in seen:
                raise ValueError('Variation IDs must be present and unique.')
            seen.add(variant['id'])
            dub.relative(variant['asset_path'])
            dub.number(variant.get('gain_db',0), 'variation gain', -60, 12)
            dub.number(variant.get('duration_s'), 'variation duration', .01, 600)
            if variant.get('generator'):
                if variant['generator'] not in GENERATORS or not isinstance(variant.get('seed'),int):
                    raise ValueError('Unsupported generator or seed.')
            elif not re.fullmatch('[0-9a-f]{64}', variant.get('sha256','')) or not variant.get('provenance') or not variant.get('license'):
                raise ValueError('Imported variations require checksum, provenance and licence.')
    return registry


def select_variation(preset, cue):
    variants = preset.get('variations')
    if not variants:
        if cue.get('variation'):
            raise ValueError('Legacy effect has no named variations.')
        return {'id':'legacy','asset_path':preset['asset_path'],'duration_s':preset['duration_s'],'gain_db':0}
    if cue.get('variation'):
        try:return next(v for v in variants if v['id']==cue['variation'])
        except StopIteration:raise ValueError('Unknown variation: '+cue['variation']) from None
    # Cue identity, not list ordering or process RNG, selects repeatable variation.
    variants = sorted(variants,key=lambda v:v['id'])
    index = int(hashlib.sha256((cue['id']+'|'+preset['preset_version']).encode()).hexdigest(),16)%len(variants)
    return variants[index]


def synthesize(variant):
    """Project-original synthesis; no external samples, voices, API or GPU."""
    kind, duration = variant['generator'], variant['duration_s']
    rng = random.Random(variant['seed'])
    pitch = variant.get('pitch_scale',1)
    count = round(duration*RATE)
    audio = bytearray()
    low, slow, phase = 0., 0., 0.
    for n in range(count):
        t=n/RATE;p=n/max(1,count-1)
        noise=rng.uniform(-1,1)
        low += .12*(noise-low);slow += .002*(noise-slow)
        if kind=='dino_footstep':
            value=(.7*math.sin(2*math.pi*85*pitch*t)*math.exp(-26*t)+low*.6*math.exp(-35*t))
        elif kind=='bunny_hop':
            phase+=2*math.pi*(230-130*p)*pitch/RATE
            value=.6*math.sin(phase)*math.exp(-18*t)+low*.2*math.exp(-35*t)
        elif kind=='bunny_surprise':
            phase+=2*math.pi*(430+360*math.sin(math.pi*p))*pitch/RATE
            value=.5*math.sin(phase)*math.sin(math.pi*p)**2+.08*math.sin(phase*2)
        elif kind=='magic_pop':
            phase+=2*math.pi*(650-430*p)*pitch/RATE
            value=(math.sin(phase)*.65+low*.15)*math.exp(-22*t)
        elif kind=='magic_whoosh':
            value=(low*1.8+.12*math.sin(2*math.pi*(100+90*p)*t))*math.sin(math.pi*p)**2
        elif kind=='puzzle_click':
            value=(.65*math.sin(2*math.pi*1100*pitch*t)+low*.7)*math.exp(-80*t)
        elif kind=='rainbow_restore':
            value=0.
            for index,f in enumerate((523.25,659.25,783.99,1046.5,1318.5)):
                age=t-index*.18
                if age>=0:value+=.22*math.sin(2*math.pi*f*pitch*age)*math.exp(-2.1*age)
            value+=.08*low*math.sin(math.pi*p)
        elif kind=='soft_hug':
            value=sum(.12*math.sin(2*math.pi*f*pitch*t) for f in (196,246.94,293.66))*math.sin(math.pi*p)**2+slow*.8
        elif kind=='forest_ambience':
            age=(t+variant['seed']%5)%4.3
            bird=.12*math.sin(2*math.pi*(1600+500*math.sin(24*age))*age)*math.exp(-24*(age-.6)**2)
            value=slow*3+low*.12+bird
        elif kind=='river_ambience':
            value=low*.9+slow*2+noise*.035+.035*math.sin(2*math.pi*(420+140*math.sin(t*2.1))*t)
        elif kind=='magical_ambience':
            value=sum(.08*math.sin(2*math.pi*f*pitch*t)*(.5+.5*math.sin(.6*t+index)) for index,f in enumerate((523.25,783.99,1046.5)))+slow*.25
        else:raise ValueError('Unknown procedural recipe.')
        fade=min(1,t/.012,(duration-t)/.04)
        if kind.endswith('ambience'):fade=min(1,t/.1,(duration-t)/.1)
        value=max(-.85,min(.85,value*fade*.65))
        # Slight decorrelation without altering cue duration or adding delay.
        left=value;right=value*(.96+.04*math.sin(.7*t+variant['seed']))
        audio.extend(struct.pack('<hh',round(left*32767),round(right*32767)))
    buffer=io.BytesIO()
    with wave.open(buffer,'wb') as stream:
        stream.setparams((2,2,RATE,0,'NONE','not compressed'));stream.writeframes(audio)
    return buffer.getvalue()


def ensure_asset(preset, variant):
    path=dub.relative(variant['asset_path'])
    if variant.get('generator'):
        recipe={'generator_version':'procedural-v002','generator_source_sha256':digest(Path(__file__)), 'variant':variant}
        fingerprint=hashlib.sha256(json.dumps(recipe,sort_keys=True).encode()).hexdigest()
        metadata=path.with_suffix('.json')
        if path.exists() or metadata.exists():
            if not path.is_file() or not metadata.is_file():raise ValueError('Partial SFX cache; retain it and choose a new asset version.')
            record=dub.load(metadata)
            if record.get('fingerprint')!=fingerprint or record.get('sha256')!=digest(path):
                raise ValueError('SFX cache changed; choose a new preset/asset version.')
        else:
            data=synthesize(variant)
            path.parent.mkdir(parents=True,exist_ok=True)
            dub.write_new(path,data)
            record={'fingerprint':fingerprint,'sha256':digest(path),'recipe':recipe,'provenance':preset['provenance'],'license':preset['license'],'approval_status':preset['approval_status']}
            dub.write_new(metadata,(json.dumps(record,indent=2)+'\n').encode())
    else:
        if not path.is_file():raise ValueError('Supply licensed/legacy asset: '+str(path))
        if variant.get('sha256') and digest(path)!=variant['sha256']:raise ValueError('Imported SFX checksum mismatch.')
    return path


def validate_plan(plan, registry, production=False):
    validate_registry(registry)
    if plan.get('schema_version')!=1 or plan.get('status') not in STATES:
        raise ValueError('Invalid SFX plan version/status.')
    duration=plan.get('duration_s')
    if duration is not None:dub.number(duration,'duration_s',.1,36000)
    if production and (plan['status'] not in ('verified','approved') or duration is None):
        raise ValueError('Review actual video, duration and cue timings before production.')
    scenes={s['id'] for s in plan['scenes']}
    if len(scenes)!=len(plan['scenes']):raise ValueError('Duplicate scene IDs.')
    seen=set();resolved=[]
    for cue in plan['cues']:
        if not cue.get('id') or cue['id'] in seen:raise ValueError('Cue IDs must be unique.')
        seen.add(cue['id'])
        if cue.get('scene_id') not in scenes or cue.get('preset_id') not in registry['effects']:
            raise ValueError('Unknown scene or SFX preset.')
        if cue.get('status') not in STATES:raise ValueError('Cue review status required.')
        preset=registry['effects'][cue['preset_id']]
        if cue.get('preset_version')!=preset.get('preset_version','v001'):
            raise ValueError('Cue preset version mismatch.')
        variant=select_variation(preset,cue)
        start,length=cue.get('timestamp_s'),cue.get('duration_s')
        if start is not None:dub.number(start,'timestamp_s',0,duration if duration is not None else 36000)
        if length is not None:dub.number(length,'duration_s',.01,duration if duration is not None else 36000)
        length=variant['duration_s'] if length is None else length
        if start is not None and duration is not None and start+length>duration+1e-6:
            raise ValueError('SFX cue extends beyond episode.')
        if length>variant['duration_s']+.01 and not cue.get('loop',False):
            raise ValueError('Long cue requires explicit looping.')
        if production and (start is None or cue['status'] not in ('verified','approved') or not cue.get('timing_basis')):
            raise ValueError('SFX cue timing needs actual-video review evidence.')
        gain=preset['default_gain_db']+variant.get('gain_db',0)+cue.get('gain_db',0)
        dub.number(cue.get('gain_db',0),'cue gain',-60,12);dub.number(gain,'effective gain',-90,24)
        resolved.append(dict(cue, path=variant['asset_path'],timestamp_s=start,duration_s=length,effective_gain_db=gain,selected_variation=variant['id']))
    return resolved


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry',default='config/sfx_presets.json')
    sub=parser.add_subparsers(dest='command',required=True)
    gen=sub.add_parser('generate');gen.add_argument('--effect',action='append')
    check=sub.add_parser('validate');check.add_argument('plan');check.add_argument('--production',action='store_true')
    args=parser.parse_args();registry=validate_registry(dub.load(dub.relative(args.registry,True)))
    if args.command=='validate':
        plan=dub.load(dub.relative(args.plan,True));rows=validate_plan(plan,registry,args.production)
        print(json.dumps({'status':plan['status'],'cue_count':len(rows),'unresolved_timestamps':[c['id'] for c in rows if c['timestamp_s'] is None]},indent=2))
    else:
        for key in args.effect or [k for k,v in registry['effects'].items() if v.get('variations')]:
            if key not in registry['effects']:raise ValueError('Unknown effect '+key)
            preset=registry['effects'][key]
            for variant in preset.get('variations',[]):ensure_asset(preset,variant)
            print('Ready',key)


if __name__=='__main__':main()
