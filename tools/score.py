#!/usr/bin/env python3
"""Deterministic CPU-only original underscore and night ambience; no sampled assets."""
from array import array
import math
from pathlib import Path
import random
import sys
import wave

RATE = 24000


def save(path, samples, gain):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError(f'Refusing to overwrite {path}')
    peak = max(abs(x) for x in samples) or 1
    pcm = array('h', (round(max(-1, min(1, x/peak * gain))*32767) for x in samples))
    if sys.byteorder != 'little':
        pcm.byteswap()
    with wave.open(str(path), 'wb') as out:
        out.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
        out.writeframes(pcm.tobytes())


def compose(duration, music, ambience):
    """Soft celeste over C/Am/F/G pads, with original unpitched night texture."""
    count = round(duration*RATE)
    score, night = array('f', [0])*(count*2), array('f', [0])*(count*2)
    def tone(start, length, midi, amplitude, pan=0, pad=False):
        freq = 440 * 2**((midi-69)/12)
        offset, frames = round(start*RATE), round(length*RATE)
        for n in range(min(frames, count-offset)):
            t = n/RATE
            if pad:
                env = min(1, t/.8, (length-t)/.9)
                value = (math.sin(2*math.pi*freq*t)+.12*math.sin(2*math.pi*freq*2*t)) * env * amplitude
            else:
                env = min(1, t/.012)*math.exp(-2.5*t)
                value = (math.sin(2*math.pi*freq*t)+.22*math.sin(2*math.pi*freq*2.002*t)+.06*math.sin(2*math.pi*freq*3*t))*env*amplitude
            index=(offset+n)*2
            score[index] += value*math.sqrt((1-pan)/2)
            score[index+1] += value*math.sqrt((1+pan)/2)
    # 80 BPM; resolve to the tonic for the ending. Sparse motif leaves speech space.
    chords = [(48,55,60,64),(45,52,57,60),(41,48,53,57),(43,50,55,59)]
    for bar in range(math.ceil(duration/6)):
        start=bar*6
        chord=chords[bar%4] if start < duration-10 else chords[0]
        for index,note in enumerate(chord):
            tone(start,min(6.5,duration-start),note,.09,(-.5 if index%2 else .5),True)
        notes=[chord[2]+12,chord[3]+12,chord[1]+12,chord[2]+12]
        for beat,note in enumerate(notes):
            onset=start+beat*1.5
            if onset<duration:
                tone(onset,min(2.8,duration-onset),note,.25,(-.25 if beat%2 else .25))
    rng=random.Random(20261025)
    left=right=0
    for n in range(count):
        t=n/RATE
        envelope=max(0,min(1,t/2,(duration-t)/3))
        left=.998*left+.002*rng.uniform(-1,1)
        right=.998*right+.002*rng.uniform(-1,1)
        # Very soft intermittent insect-like texture, not a dialogue source.
        chirp=(max(0,math.sin(2*math.pi*.29*t))**18)*math.sin(2*math.pi*3100*t)*.0015
        night[2*n]=(left*.15+chirp)*envelope
        night[2*n+1]=(right*.15+chirp*.8)*envelope
        score[2*n]*=envelope
        score[2*n+1]*=envelope
    save(music,score,.13)
    save(ambience,night,.012)
