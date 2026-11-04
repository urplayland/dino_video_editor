#!/usr/bin/env python3
"""Fit complete localized takes, mix, caption, and render the approved six-shape edit."""
from pathlib import Path
from workspace_paths import WORKSPACE, DINO
import argparse,gc,json,math,subprocess,sys,wave
import numpy as np
from scipy.signal import resample_poly
ROOT=Path(__file__).resolve().parent
RATE=48000

def run(args,timeout=900):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(p.stderr[-2500:])
 return p

def readwav(path):
 with wave.open(str(path),'rb') as w:
  assert w.getsampwidth()==2
  rate=w.getframerate();channels=w.getnchannels()
  x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32).reshape(-1,channels)/32768
 if channels==1:x=np.repeat(x,2,axis=1)
 if rate!=RATE:x=resample_poly(x,RATE,rate,axis=0)
 return x

def writewav(path,x):
 assert np.max(np.abs(x))<1,str(path)+' clips'
 with wave.open(str(path),'wb') as w:
  w.setparams((2,2,RATE,0,'NONE','not compressed'));w.writeframes(np.rint(x*32767).astype('<i2').tobytes())

def stamp(t,ass=False):
 if ass:
  cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def align(lang):
 plan=json.loads((ROOT/f'production-{lang.lower()}-final-v001.json').read_text())
 out=ROOT/f'exports/{lang}_Final_v001';out.mkdir(parents=True,exist_ok=True)
 work=ROOT/f'work/{lang.lower()}-final-v001';work.mkdir(parents=True,exist_ok=True)
 n=round(plan['duration_s']*RATE);bus=np.zeros((n,2),dtype=np.float32);fitted=[];previous_end=0
 for i,line in enumerate(plan['lines']):
  raw=ROOT/f'media/derived/voice-{lang.lower()}-final-v001'/f'{line["id"]}.wav'
  x=readwav(raw);amp=np.max(np.abs(x),axis=1)
  active=np.flatnonzero(amp>max(.0011,float(amp.max())*.006));assert len(active),'Silent line'
  # Whole independent take: trim only external silence, with generous consonant/breath margins.
  a=max(0,int(active[0])-round(.10*RATE));b=min(len(x),int(active[-1])+round(.14*RATE));clip=x[a:b].copy()
  desired=line['source_start_s'];next_start=plan['lines'][i+1]['source_start_s'] if i+1<len(plan['lines']) else plan['duration_s']
  limit=next_start-.08;start=max(desired,previous_end+.065)
  needed=len(clip)/RATE
  if needed>limit-start:
   start=max(previous_end+.065,desired-.30,min(desired,limit-needed))
  speed=max(1,needed/(limit-start))
  if speed>1.10:raise ValueError(f'{lang} {line["id"]} cannot fit naturally: {needed:.2f}s in {limit-start:.2f}s')
  if speed>1.001:
   trimmed=work/f'{line["id"]}-whole.wav';processed=work/f'{line["id"]}-fitted.wav';writewav(trimmed,clip)
   run(['ffmpeg','-v','error','-nostdin','-y','-threads','1','-filter_threads','1','-i',str(trimmed),'-af',f'atempo={speed:.8f}','-ar',str(RATE),'-ac','2','-c:a','pcm_s16le',str(processed)])
   clip=readwav(processed)
  mask=np.max(np.abs(clip),axis=1)>.008;assert mask.any()
  rms=float(np.sqrt(np.mean(clip[mask]**2)));gain=min(.105/rms,.65/float(np.max(np.abs(clip))));clip*=gain
  fade=min(round(.005*RATE),len(clip)//4);clip[:fade]*=np.linspace(0,1,fade,dtype=np.float32)[:,None];clip[-fade:]*=np.linspace(1,0,fade,dtype=np.float32)[:,None]
  begin=round(start*RATE);end=begin+len(clip);assert end<=n
  bus[begin:end]+=clip;previous_end=end/RATE
  fitted.append(dict(line,start_s=start,end_s=previous_end,tempo_factor=speed,gain_db=20*math.log10(gain),raw_excerpt_s=[a/RATE,b/RATE],audio_handling='Complete independently recorded line; no internal word cuts.'))
  print(lang,line['id'],f'{start:.2f}-{previous_end:.2f}s tempo {speed:.3f}',flush=True)
 writewav(out/'dialogue.wav',bus)
 (ROOT/f'reports/fitted-dialogue-{lang.lower()}-final-v001.json').write_text(json.dumps({'voice':'Achernar','lines':fitted},ensure_ascii=False,indent=2)+'\n')
 captions(lang,fitted,out)
 # Use original un-ducked instrumental and apply language-specific dialogue envelopes.
 music=readwav(ROOT/'media/derived/score-v001/score-pcm-48k.wav');music=np.pad(music,((0,max(0,n-len(music))),(0,0)))[:n]
 music*=10**(16.74/20)
 music[:round(.2*RATE)]*=np.linspace(0,1,round(.2*RATE),dtype=np.float32)[:,None]
 tail=round(.65*RATE);music[-tail:]*=np.linspace(1,0,tail,dtype=np.float32)[:,None]
 duck=np.ones(n,dtype=np.float32)
 for line in fitted:
  a=max(0,round((line['start_s']-.09)*RATE));b=min(n,round((line['end_s']+.08)*RATE));duck[a:b]=np.minimum(duck[a:b],.45)
  pre=max(0,a-round(.14*RATE));post=min(n,b+round(.3*RATE))
  if a>pre:duck[pre:a]=np.minimum(duck[pre:a],np.linspace(1,.45,a-pre,dtype=np.float32))
  if post>b:duck[b:post]=np.minimum(duck[b:post],np.linspace(.45,1,post-b,dtype=np.float32))
 music*=duck[:,None];writewav(out/'music.wav',music)
 sfx=readwav(ROOT/'exports/EN_Final_v001/sfx.wav');writewav(out/'sfx.wav',sfx);writewav(out/'ambience.wav',np.zeros_like(bus))
 total=np.zeros((round((2+plan['duration_s']+2.5)*RATE),2),dtype=np.float32);total[2*RATE:2*RATE+n]=bus+music+sfx
 jingle=readwav(DINO/'library/media/audio/branding/flh-logo-sting-v001.wav')
 total[:2*RATE]+=jingle[:2*RATE];tailstart=2*RATE+n;count=min(len(jingle),len(total)-tailstart);total[tailstart:tailstart+count]+=jingle[:count]
 writewav(out/'premix.wav',total)
 print('Prepared localized dialogue, subtitles and premix:',lang,flush=True)

def captions(lang,fitted,out):
 font='Noto Sans CJK SC' if lang=='ZH' else 'Nunito ExtraLight'
 header=f'''[Script Info]\nScriptType: v4.00+\nPlayResX: 1280\nPlayResY: 720\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,{font},36,&H00FFFFFF,&H00FFFFFF,&H00191919,&H80000000,-1,0,0,0,100,100,0,0,1,2.5,1.5,2,60,60,25,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
 events=[];srt=[]
 for i,line in enumerate(fitted):
  a=line['start_s']+2;b=line['end_s']+2;text=line['text'];events.append(f'Dialogue: 0,{stamp(a,True)},{stamp(b,True)},Default,,0,0,0,,{text}')
  srt.append(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{text}\n')
 (out/f'Milo_EP01_{lang}_Final_v001.ass').write_text(header+'\n'.join(events)+'\n')
 (out/f'Milo_EP01_{lang}_Final_v001.srt').write_text('\n'.join(srt))

def levels(path):
 p=run(['ffmpeg','-hide_banner','-nostdin','-threads','1','-filter_threads','1','-i',str(path),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],180)
 return json.loads(p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}')+1])

def master(lang):
 out=ROOT/f'exports/{lang}_Final_v001';measurement=levels(out/'premix.wav')
 gain=min(-16-float(measurement['input_i']),-1.8-float(measurement['input_tp']))
 output=out/'master.wav'
 if not output.exists():run(['ffmpeg','-v','error','-nostdin','-n','-threads','1','-filter_threads','1','-i',str(out/'premix.wav'),'-af',f'volume={gain:.8f}dB','-ar','48000','-ac','2','-c:a','pcm_s24le',str(output)])
 report={'premix':measurement,'gain_db':gain,'master':levels(output),'brand_audio':'Exact approved FLH sonic logo; no tempo or pitch changes.','music':'Original EN instrumental with localized dialogue ducking.'}
 (ROOT/f'reports/mix-{lang.lower()}-final-v001.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

def render(lang):
 plan=json.loads((ROOT/f'production-{lang.lower()}-final-v001.json').read_text());out=ROOT/f'exports/{lang}_Final_v001';output=out/f'Milo_EP01_{lang}_Final_v001.mp4'
 ass=out/f'Milo_EP01_{lang}_Final_v001.ass';fonts=ROOT/'assets/branding/fonts'
 graph=f'[0:v]setpts=PTS-STARTPTS,setsar=1[i];[1:v]trim=end_frame=1052,setpts=PTS-STARTPTS,setsar=1[s0];[4:v]setpts=PTS-STARTPTS,setsar=1[s1];[s0][s1]concat=n=2:v=1:a=0[s];[2:v]setpts=PTS-STARTPTS,setsar=1[o];[i][s][o]concat=n=3:v=1:a=0,ass={ass}:fontsdir={fonts}[v]'
 args=['ffmpeg','-hide_banner','-nostdin','-n','-filter_threads','1','-filter_complex_threads','1']
 for path in [ROOT/'assets/branding/intro-landscape-v001.mp4',ROOT/plan['picture'],ROOT/'assets/branding/outro-landscape-v001.mp4',out/'master.wav',ROOT/plan['retouched_ending']]:args+=['-threads','1','-i',str(path)]
 args+=['-filter_complex',graph,'-map','[v]','-map','3:a:0','-c:v','libx264','-crf','18','-preset','veryfast','-threads','2','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-metadata:s:a:0',f'language={"zho" if lang=="ZH" else "msa"}','-movflags','+faststart',str(output)]
 result=run(args);(ROOT/f'reports/render-{lang.lower()}-final-v001.log').write_text(result.stderr)
 assert 'Glyph 0x' not in result.stderr,'Missing subtitle glyph'
 print('Rendered',output,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['align','master','render']);p.add_argument('language',choices=['ZH','MS']);a=p.parse_args()
 {'align':align,'master':master,'render':render}[a.action](a.language)
