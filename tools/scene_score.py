#!/usr/bin/env python3
"""Compose timed, editable orchestral cues as MIDI; render offline with FluidSynth."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import struct

import dub

PPQ=480
TICKS_PER_SECOND=960


def vlq(value):
    if not isinstance(value,int) or not 0<=value<=0x0fffffff:
        raise ValueError('Invalid MIDI delta time.')
    result=[value&127]
    while value>>7:
        value >>= 7;result.insert(0,(value&127)|128)
    return bytes(result)


def chunk(kind,data):
    return kind+struct.pack('>I',len(data))+data


def validate_plan(plan,registry):
    if plan.get('schema_version')!=1 or registry.get('schema_version')!=1:
        raise ValueError('Unsupported score/registry version.')
    duration=dub.number(plan.get('duration_s'),'score duration',1,36000)
    last=0
    for cue in plan['cues']:
        start=dub.number(cue.get('start_s'),'cue start',0,duration)
        end=dub.number(cue.get('end_s'),'cue end',0,duration)
        if abs(start-last)>.001 or end<=start:
            raise ValueError('Music cue sheet must cover the story continuously without gaps/overlaps.')
        last=end
        dub.number(cue.get('bpm'),'cue bpm',40,200)
        for layer in cue['layers']:
            if layer['instrument'] not in registry['instruments']:
                raise ValueError('Unknown registered instrument.')
            if layer['kind'] not in ('pad','pattern','phrase','hits'):
                raise ValueError('Unknown MIDI layer recipe.')
    if abs(last-duration)>.001:
        raise ValueError('Music must reach the exact story end.')
    channels=[]
    for name,inst in registry['instruments'].items():
        channel=inst['channel']
        if not isinstance(channel,int) or not 0<=channel<=15 or channel in channels:
            raise ValueError('MIDI instruments need unique channels in 0..15.')
        channels.append(channel)
        dub.number(inst['program'],'MIDI program',0,127)
    return plan


def arrange(plan,registry):
    rng=random.Random(plan.get('seed',20261025))
    notes=[]
    def add(inst,on,length,pitch,velocity,legato=False):
        if not 0<=pitch<=127 or length<=0:
            raise ValueError('Invalid musical note.')
        on=max(0,on);end=min(plan['duration_s']-.035,on+length)
        if end<=on:return
        notes.append({'instrument':inst,'start_s':on,'end_s':end,'pitch':int(pitch),'velocity':max(1,min(110,round(velocity))),'legato':legato})
    for cue in plan['cues']:
        beat=60/cue['bpm'];length=cue['end_s']-cue['start_s']
        for layer in cue['layers']:
            inst=layer['instrument'];start=cue['start_s']+layer.get('offset_s',0);velocity=layer.get('velocity',40)
            if layer['kind']=='pad':
                chords=layer['chords'];step=(cue['end_s']-start)/len(chords)
                for i,chord in enumerate(chords):
                    for pitch in chord:
                        add(inst,start+i*step,step+layer.get('tail_s',.35),pitch,velocity+layer.get('rise',0)*i/max(1,len(chords)-1),True)
            elif layer['kind']=='pattern':
                step=beat*layer.get('step_beats',.5);i=0
                stop=cue['end_s']+layer.get('end_offset_s',0)
                while start+i*step<stop-.035:
                    pitch=layer['notes'][i%len(layer['notes'])]
                    offset=rng.uniform(-.007,.007)
                    add(inst,start+i*step+offset,step*layer.get('gate',.65),pitch,velocity+layer.get('rise',0)*(i*step/max(.1,length))+layer.get('accents',[0])[i%len(layer.get('accents',[0]))]+rng.uniform(-2,2))
                    i+=1
            elif layer['kind']=='phrase':
                for entry in layer['events']:
                    at,pitch,held,accent=entry
                    add(inst,start+at*beat,held*beat,pitch,velocity+accent)
            else:
                for at,pitch,held,accent in layer['events']:
                    add(inst,start+at,held,pitch,velocity+accent)
    # Common sustained chord tones remain held rather than being cut by overlapping note-offs.
    grouped=defaultdict(list)
    for note in notes:grouped[(note['instrument'],note['pitch'],note['legato'])].append(note)
    merged=[]
    for (inst,pitch,legato),group in grouped.items():
        group.sort(key=lambda x:x['start_s'])
        for note in group:
            if legato and merged and merged[-1]['instrument']==inst and merged[-1]['pitch']==pitch and merged[-1]['end_s']>=note['start_s']:
                merged[-1]['end_s']=max(merged[-1]['end_s'],note['end_s'])
            else:merged.append(dict(note))
    return sorted(merged,key=lambda x:(x['start_s'],x['instrument'],x['pitch']))


def midi_bytes(plan,registry,notes):
    ending=round((plan['duration_s']+2)*TICKS_PER_SECOND)
    title=plan['title'].encode('utf-8')
    conductor=b'\x00\xff\x51\x03\x07\xa1\x20'+b'\x00\xff\x03'+vlq(len(title))+title+vlq(ending)+b'\xff\x2f\x00'
    tracks=[chunk(b'MTrk',conductor)]
    for name,inst in sorted(registry['instruments'].items(),key=lambda x:x[1]['channel']):
        ch=inst['channel'];events=[]
        for cc,value in [(7,100),(10,inst.get('pan',64)),(11,110),(91,32),(93,0)]:events.append((0,0,bytes([0xb0|ch,cc,value])))
        events.append((0,0,bytes([0xc0|ch,inst['program']])))
        for n in notes:
            if n['instrument']!=name:continue
            events.append((round(n['start_s']*TICKS_PER_SECOND),2,bytes([0x90|ch,n['pitch'],n['velocity']])))
            events.append((round(n['end_s']*TICKS_PER_SECOND),1,bytes([0x80|ch,n['pitch'],0])))
        events.sort(key=lambda x:(x[0],x[1]))
        label=name.encode();data=b'\x00\xff\x03'+vlq(len(label))+label;previous=0
        for tick,_,message in events:
            data+=vlq(tick-previous)+message;previous=tick
        data+=vlq(ending-previous)+b'\xff\x2f\x00'
        tracks.append(chunk(b'MTrk',data))
    return chunk(b'MThd',struct.pack('>HHH',1,len(tracks),PPQ))+b''.join(tracks)


def render(plan_path):
    plan=dub.load(plan_path);registry=dub.load(dub.relative(plan['registry'],True));validate_plan(plan,registry)
    bank=dub.relative(registry['soundfont']['path'],True)
    if hashlib.sha256(bank.read_bytes()).hexdigest()!=registry['soundfont']['sha256']:
        raise ValueError('Instrument bank checksum changed.')
    output=dub.relative(plan['output']);folder=dub.relative(plan['work_dir']);folder.mkdir(parents=True,exist_ok=True)
    report=folder/'score-report.json'
    identity=hashlib.sha256(json.dumps({'plan':plan,'registry':registry},sort_keys=True).encode()).hexdigest()
    if output.exists():
        if report.exists():
            old=dub.load(report)
            if old.get('fingerprint')==identity and old.get('output_sha256')==hashlib.sha256(output.read_bytes()).hexdigest():
                print('Cached verified scene score:',plan['output']);return
        raise ValueError('Score output exists with different/incomplete provenance; use a new version.')
    notes=arrange(plan,registry);midi=folder/'score.mid';data=midi_bytes(plan,registry,notes)
    if midi.exists() and midi.read_bytes()!=data:raise ValueError('Existing MIDI differs; choose a new score version.')
    if not midi.exists():dub.write_new(midi,data)
    raw=folder/'instruments.float.wav'
    if not raw.exists():
        synth=dub.tool('fluidsynth');options=registry['renderer']
        dub.run([synth,'-ni','-q','-r','48000','-g',str(options['gain']),'-C','0','-R','1',
            '-o','synth.reverb.room-size='+str(options['reverb_room_size']),'-o','synth.reverb.damp='+str(options['reverb_damp']),
            '-o','synth.reverb.level='+str(options['reverb_level']),'-F',str(raw),'-T','wav','-O','float',str(bank),str(midi)],timeout=240)
    measured=dub.loudness_info(raw)
    if not all(math.isfinite(float(measured[k])) for k in ['input_i','input_tp']):raise ValueError('Score rendered silent/invalid.')
    gain=min(plan['target_integrated_lufs']-float(measured['input_i']),plan['max_true_peak_db']-float(measured['input_tp']))
    output.parent.mkdir(parents=True,exist_ok=True)
    fade=plan.get('fade_out_s',1.2);duration=plan['duration_s']
    dub.run([dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-i',str(raw),'-af',
        f'atrim=duration={duration},asetpts=N/SR/TB,volume={gain}dB,afade=t=in:d=0.2,afade=t=out:st={duration-fade}:d={fade},apad=whole_dur={duration},atrim=duration={duration}',
        '-ar','48000','-ac','2','-c:a','pcm_s24le',str(output)],timeout=180)
    final=dub.loudness_info(output)
    if float(final['input_tp'])>plan['max_true_peak_db']+.1:raise ValueError('Rendered score exceeds its peak target.')
    record={'status':'rendered_pending_english_mix_review','fingerprint':identity,'plan':plan,'registry':registry,'note_count':len(notes),
        'midi_sha256':hashlib.sha256(data).hexdigest(),'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
        'global_gain_db':gain,'source_measurement':measured,'output_measurement':final,'notes':notes,
        'license_notice':dub.relative(registry['soundfont']['license_path'],True).read_text(),
        'fluidsynth_version':dub.run([dub.tool('fluidsynth'),'--version']).stdout.splitlines()[0]}
    dub.write_new(report,(json.dumps(record,indent=2,ensure_ascii=False)+'\n').encode())
    print(f'Rendered {plan["output"]}: {len(plan["cues"])} scene cues, {len(notes)} MIDI notes; gain {gain:.2f}dB.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('plan');args=parser.parse_args()
    try:render(dub.relative(args.plan,True))
    except (ValueError,OSError,KeyError,TypeError) as exc:parser.exit(1,f'Error: {exc}\n')


if __name__=='__main__':main()
