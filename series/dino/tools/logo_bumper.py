#!/usr/bin/env python3
"""Render short, preschool-friendly FLH identity bumpers from existing brand art."""
from array import array
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import wave

import dub


def clamp(value):
    return max(0.0,min(1.0,value))


def make_sting(path):
    if path.exists():
        return
    rate=48000;duration=2.5;values=array('h')
    notes=[(.12,1046.50,.65),(.34,1318.51,.65),(.56,1567.98,.65),(.85,1318.51,1.05)]
    samples=[]
    for i in range(round(rate*duration)):
        t=i/rate;value=0
        for onset,freq,length in notes:
            age=t-onset
            if 0<=age<length:
                envelope=min(1,age/.008)*math.exp(-5*age)*min(1,(length-age)/.08)
                value+=(math.sin(2*math.pi*freq*age)+.18*math.sin(2*math.pi*freq*2.01*age))*envelope
        samples.append(value)
    peak=max(abs(x) for x in samples) or 1
    for value in samples:
        pcm=round(value/peak*32767*.26)
        values.extend((pcm,pcm))
    if sys.byteorder!='little':values.byteswap()
    path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),'wb') as out:
        out.setparams((2,2,rate,0,'NONE','not compressed'));out.writeframes(values.tobytes())


def render_clip(cfg,kind,target,duration):
    from PIL import Image,ImageDraw,ImageFont
    logo=Image.open(dub.relative(cfg['assets']['logo.png']['path'],True)).convert('RGBA')
    heading=ImageFont.truetype(str(dub.relative(cfg['assets']['Outfit-800.ttf']['path'],True)),44)
    body=ImageFont.truetype(str(dub.relative(cfg['assets']['Nunito-700.ttf']['path'],True)),26)
    name=Image.new('RGBA',(720,82),(0,0,0,0))
    ImageDraw.Draw(name).text((360,0),cfg['brand'],font=heading,fill='#'+cfg['text_color'],anchor='mt')
    website=Image.new('RGBA',(720,82),(0,0,0,0))
    palette=cfg.get('playful_palette')
    wd=ImageDraw.Draw(website)
    if palette:
        wd.rounded_rectangle((135,7,585,69),radius=30,fill='#'+palette['blue_rim'])
        wd.rounded_rectangle((135,0,585,61),radius=30,fill='#'+palette['blue'],outline='#'+palette['blue_rim'],width=2)
        wd.text((360,30),cfg['website'],font=body,fill='white',anchor='mm')
    else:
        wd.text((360,0),cfg['website'],font=body,fill='#'+cfg['secondary_color'],anchor='mt')
    command=[dub.tool('ffmpeg'),'-v','error','-nostdin','-n','-f','rawvideo','-pixel_format','rgb24',
        '-video_size','720x1280','-framerate','24','-i','-','-an','-frames:v',str(round(duration*24)),
        '-c:v','libx264','-preset','veryfast','-crf','17','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE,stdout=subprocess.DEVNULL)
    try:
        for number in range(round(duration*24)):
            t=number/24
            frame=Image.new('RGBA',(720,1280),'#'+cfg['background'])
            effects=Image.new('RGBA',frame.size,(0,0,0,0));draw=ImageDraw.Draw(effects)
            if palette:
                # Quiet edge shapes leave the original logo as the only central graphic.
                drift=5*math.sin(t*math.pi/2)
                draw.rounded_rectangle((-170,150+drift,110,430+drift),radius=95,fill='#'+palette['blue_tint'])
                draw.rounded_rectangle((610,925-drift,890,1205-drift),radius=95,fill='#'+palette['green_tint'])
                draw.ellipse((594,215,750,371),fill='#'+palette['yellow_tint'])
                draw.rounded_rectangle((-32,1025,65,1122),radius=30,fill='#'+palette['purple_tint'])
                for index,color in enumerate(('blue','green','yellow','purple')):
                    x=270+index*48
                    draw.rounded_rectangle((x,972,x+36,980),radius=4,fill='#'+palette[color])
            u=clamp((t-.04)/.66)
            back=1+2.45*(u-1)**3+1.45*(u-1)**2
            scale=max(.015,back)
            alpha=clamp((t-.02)/.16)
            if .12<t<.72:
                p=(t-.12)/.60;r=150+75*p
                draw.ellipse((360-r,570-r,360+r,570+r),outline=(28,176,246,round(90*(1-p))),width=5)
                strength=math.sin(math.pi*p)
                for angle in [-150,-90,-30,30,150]:
                    a=math.radians(angle);inner=196+7*p;outer=inner+16*strength
                    draw.line((360+inner*math.cos(a),570+inner*math.sin(a),360+outer*math.cos(a),570+outer*math.sin(a)),fill=(255,200,0,round(180*strength)),width=5)
            shadow=round(28*alpha)
            draw.ellipse((276,731,444,750),fill=(229,216,187,shadow*3) if palette else (26,52,68,shadow))
            frame=Image.alpha_composite(frame,effects)
            size=max(1,round(300*scale))
            mark=logo.resize((size,size),Image.Resampling.LANCZOS)
            angle=-7*(1-u)**2
            mark=mark.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
            if alpha<1:mark.putalpha(mark.getchannel('A').point([round(i*alpha) for i in range(256)]))
            y=round(570-mark.height/2+70*(1-back))
            frame.alpha_composite(mark,(round(360-mark.width/2),y))
            for layer,onset,length,ybase,rise in [(name,.46,.34,795,18),(website,.73,.28,864,8)]:
                v=clamp((t-onset)/length)
                if not v:continue
                shown=layer.copy()
                if v<1:shown.putalpha(shown.getchannel('A').point([round(i*v) for i in range(256)]))
                frame.alpha_composite(shown,(0,round(ybase+rise*(1-v))))
            process.stdin.write(frame.convert('RGB').tobytes())
        process.stdin.close()
        message=process.stderr.read().decode('utf-8',errors='replace')
        if process.wait(timeout=180):raise ValueError('Logo bumper encoding failed: '+message[-1500:])
    except BaseException:
        if process.poll() is None:process.terminate();process.wait(timeout=10)
        raise


def make_clips(manifest,cfg):
    folder=dub.relative(cfg['bumper_media_dir']);folder.mkdir(parents=True,exist_ok=True)
    stamp=folder/'provenance.json'
    identity=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
    if stamp.exists() and dub.load(stamp).get('fingerprint')!=identity:
        raise ValueError('Logo bumper configuration changed; select a new bumper asset version.')
    result=[]
    for kind,duration in [('intro',cfg['intro_duration_s']),('outro',cfg['outro_duration_s'])]:
        target=folder/(kind+'.mp4');result.append(target)
        if not target.exists():render_clip(cfg,kind,target,duration)
        info=dub.probe(target)
        frames=int(next(s for s in info['streams'] if s['codec_type']=='video')['nb_frames'])
        if frames!=round(duration*24):raise ValueError('Incomplete cached logo bumper; use a new version.')
    if not stamp.exists():dub.write_new(stamp,(json.dumps({'fingerprint':identity,'config':cfg,'clips':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in result}},indent=2)+'\n').encode())
    return tuple(result)
