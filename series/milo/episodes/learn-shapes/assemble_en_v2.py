#!/usr/bin/env python3
"""Assemble a versioned Milo English review from source-based lines and selected voice takes."""
from pathlib import Path
from workspace_paths import WORKSPACE, DINO
import hashlib,json,math,re,subprocess,sys,wave,gc
import numpy as np
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
sys.path.insert(0,str(DINO/'tools'))
import dub
ROOT=Path(__file__).resolve().parent
RATE=48000

def run(args):
 if args[0]=='ffmpeg':
  args=[args[0],'-filter_threads','1','-filter_complex_threads','1',*args[1:]]
  expanded=[]
  for arg in args:
   if arg=='-i':expanded.extend(['-threads','1'])
   expanded.append(arg)
  args=expanded
 p=subprocess.run(args,capture_output=True,text=True,timeout=900)
 if p.returncode: raise RuntimeError(p.stderr[-2500:])
 return p.stdout

def loudness(path):
 p=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-threads','1','-filter_threads','1','-i',str(path),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,timeout=120)
 if p.returncode:raise RuntimeError(p.stderr[-1000:])
 return json.loads(p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}')+1])

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def norm(text):return re.findall('[a-z]+',text.lower().replace('byebye','bye bye'))
def readwav(path):
 with wave.open(str(path),'rb') as w:
  rate=w.getframerate(); channels=w.getnchannels(); width=w.getsampwidth(); assert width==2
  x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64).reshape(-1,channels)/32768
 if channels==1:x=np.repeat(x,2,axis=1)
 if rate!=RATE:x=resample_poly(x,RATE,rate,axis=0)
 return x

def writewav(path,x):
 path.parent.mkdir(parents=True,exist_ok=True)
 assert np.max(np.abs(x))<1, str(path)+' would clip'
 with wave.open(str(path),'wb') as w:
  w.setparams((2,2,RATE,0,'NONE','not compressed'));w.writeframes(np.rint(x*32767).astype('<i2').tobytes())

def transcribe(model,path):
 segments,_=model.transcribe(str(path),beam_size=5,word_timestamps=True)
 rows=[];words=[]
 for s in segments:
  rows.append({'start':s.start,'end':s.end,'text':s.text})
  for w in s.words or []:words.append({'start':w.start,'end':w.end,'word':w.word,'probability':w.probability})
 return {'segments':rows,'words':words,'text':' '.join(x['text'].strip() for x in rows)}

def align(plan):
 model=None
 folder=ROOT/'media/derived/voice-en-v002'; work=ROOT/'work/en-v002'; work.mkdir(parents=True,exist_ok=True)
 duration=plan['duration_s']; bus=np.zeros((round(duration*RATE),2)); fitted=[]
 previous_end=0
 for group in plan['groups']:
  wav=folder/(group['id']+'.wav'); record=ROOT/'reports'/('voice-'+group['id']+('-v002' if group['id']=='recap' else '')+'-asr.json')
  if record.exists():analysis=json.loads(record.read_text())
  else:
   if model is None:model=WhisperModel('base.en',device='cpu',compute_type='int8',cpu_threads=2,num_workers=1,download_root=str(ROOT/'work/whisper'))
   analysis=transcribe(model,wav); record.write_text(json.dumps(analysis,indent=2)+'\n')
  expected=norm(group['text']); actual=norm(analysis['text'])
  if actual!=expected:
   altpath=ROOT/'reports'/('voice-'+group['id']+('-v002' if group['id']=='recap' else '')+'-tiny-asr.json')
   if altpath.exists():alternative=json.loads(altpath.read_text())
   else:
    del model; gc.collect()
    model=WhisperModel('tiny.en',device='cpu',compute_type='int8',cpu_threads=2,num_workers=1,download_root=str(ROOT/'work/whisper'))
    alternative=transcribe(model,wav); altpath.write_text(json.dumps(alternative,indent=2)+'\n')
   if norm(alternative['text'])==expected:analysis=alternative
   else:raise ValueError('Voice transcript mismatch '+group['id']+': '+repr(actual)+' expected '+repr(expected))
  token_times=[]
  for word in analysis['words']:
   for token in norm(word['word']):token_times.append((token,word['start'],word['end']))
  if [x[0] for x in token_times]!=expected:raise ValueError('ASR word alignment differs from transcript.')
  source=readwav(wav); cursor=0
  if group['id']=='recap':
   # Keep the complete final scene take intact; never cut its words into separate audio snippets.
   mono=source.mean(axis=1); active=np.flatnonzero(np.abs(mono)>max(.0011,float(np.max(np.abs(mono)))*.006))
   a=max(0,active[0]-round(.06*RATE)); b=min(len(source),active[-1]+round(.08*RATE)); clip=source[a:b]
   start=plan['lines'][group['line_indices'][0]]['source_start_s']; speed=max(1,len(clip)/RATE/(duration-.06-start))
   if speed>1.10:raise ValueError('Complete recap take does not fit.')
   if speed>1.001:
    raw=work/'recap-whole.wav'; writewav(raw,clip); processed=work/'recap-whole-fitted.wav'
    run(['ffmpeg','-v','error','-nostdin','-y','-i',str(raw),'-af',f'atempo={speed:.7f}','-ar',str(RATE),'-ac','2','-c:a','pcm_s16le',str(processed)]);clip=readwav(processed)
   active_mask=np.max(np.abs(clip),axis=1)>.008; rms=float(np.sqrt(np.mean(clip[active_mask]**2)))
   gain=min(.105/max(rms,1e-6),.65/max(np.max(np.abs(clip)),1e-6));clip*=gain
   begin=round(start*RATE);bus[begin:begin+len(clip)]+=clip;ending=(begin+len(clip))/RATE
   for index in group['line_indices']:
    line=plan['lines'][index];count=len(norm(line['text'])); words=token_times[cursor:cursor+count]
    st=max(start,start+(words[0][1]-a/RATE)/speed-.04);en=min(ending,start+(words[-1][2]-a/RATE)/speed+.14)
    fitted.append(dict(line,start_s=st,end_s=en,generated_group='recap',raw_excerpt_s=[a/RATE,b/RATE],tempo_factor=speed,gain_db=20*math.log10(gain),audio_handling='Complete continuous scene take; subtitle windows only, no internal audio cuts.'))
    cursor+=count
   previous_end=ending;print('Verified complete continuous six-shape recap.',flush=True);continue
  for index in group['line_indices']:
   line=plan['lines'][index]; count=len(norm(line['text'])); selected=token_times[cursor:cursor+count]
   first=selected[0][1]; last=selected[-1][2]
   # Keep breath/fricatives; split only in the gap between adjacent spoken lines.
   left=max(0,first-.09); right=min(len(source)/RATE,last+.12)
   if cursor: left=max(left,(token_times[cursor-1][2]+first)/2)
   if cursor+count<len(token_times):right=min(right,(last+token_times[cursor+count][1])/2)
   # QA-corrected boundaries measured in true quiet gaps, not uncertain ASR word boundaries.
   gap_overrides=plan['split_boundary_overrides_s']
   local_index=group['line_indices'].index(index)
   if group['id'] in gap_overrides:
    cuts=gap_overrides[group['id']]
    if local_index>0:left=cuts[local_index-1]
    if local_index<len(cuts):right=cuts[local_index]
   if cursor==0:left=0
   if cursor+count==len(token_times):right=len(source)/RATE
   clip=source[round(left*RATE):round(right*RATE)]
   # Trim only low-level leading/trailing samples; preserve 60/80 ms air.
   mono=clip.mean(axis=1); active=np.flatnonzero(np.abs(mono)>max(.0011,float(np.max(np.abs(mono)))*.006))
   if not len(active):raise ValueError('Silent generated line '+line['id'])
   a=max(0,active[0]-round(.06*RATE)); b=min(len(clip),active[-1]+round(.08*RATE)); clip=clip[a:b]
   next_start=plan['lines'][index+1]['source_start_s'] if index+1<len(plan['lines']) else duration-.04
   limit=min(next_start-.12,duration-.04); desired=line['source_start_s']; start=max(desired,previous_end+.08)
   needed=len(clip)/RATE
   if needed/(limit-start)>1.10:
    start=max(previous_end+.08,desired-.45,limit-needed/1.10)
   available=limit-start; speed=max(1,needed/available)
   if speed>1.101:raise ValueError(f'Line {line["id"]} cannot fit: {needed:.3f}s in {available:.3f}s')
   raw=work/(line['id']+'-trimmed.wav'); writewav(raw,clip)
   processed=work/(line['id']+'-fitted.wav')
   if speed>1.001:
    run(['ffmpeg','-v','error','-nostdin','-y','-i',str(raw),'-af',f'atempo={speed:.7f}','-ar',str(RATE),'-ac','2','-c:a','pcm_s16le',str(processed)]); clip=readwav(processed)
   active_mask=np.max(np.abs(clip),axis=1)>.008
   rms=float(np.sqrt(np.mean(clip[active_mask]**2))) if active_mask.any() else 0
   gain=min(.105/max(rms,1e-6),.65/max(np.max(np.abs(clip)),1e-6)); clip*=gain
   fade=min(round(.008*RATE),len(clip)//4); clip[:fade]*=np.linspace(0,1,fade)[:,None]; clip[-fade:]*=np.linspace(1,0,fade)[:,None]
   begin=round(start*RATE); end=begin+len(clip)
   if end>len(bus):raise ValueError('Dialogue exceeds story.')
   bus[begin:end]+=clip
   ending=end/RATE; previous_end=ending
   fitted.append(dict(line,start_s=start,end_s=ending,generated_group=group['id'],raw_excerpt_s=[left+a/RATE,left+b/RATE],tempo_factor=speed,gain_db=20*math.log10(gain)))
   cursor+=count
  print('Verified and fitted voice:',group['id'],flush=True)
 writewav(ROOT/'archive/reviews/EN_v002/dialogue.wav',bus)
 (ROOT/'reports/fitted-dialogue-en-v002.json').write_text(json.dumps({'voice':'Achernar','verification':'Exact normalized dialogue matched by independent local ASR; no human acting approval implied.','lines':fitted},indent=2)+'\n')
 return fitted,bus

def beds(plan,fitted,dialogue):
 duration=plan['duration_s']; n=len(dialogue)
 raw=ROOT/'media/derived/score-v001/score-raw.wav'; converted=ROOT/'work/en-v002/score-pcm.wav'
 run(['ffmpeg','-v','error','-nostdin','-y','-i',str(raw),'-t',str(duration),'-ar',str(RATE),'-ac','2','-c:a','pcm_s16le',str(converted)])
 music=readwav(converted); music=np.pad(music,((0,max(0,n-len(music))),(0,0)))[:n]
 measure=loudness(converted); gain=10**((-25.5-float(measure['input_i']))/20); music*=gain
 music[:round(.2*RATE)]*=np.linspace(0,1,round(.2*RATE))[:,None]
 tail=round(.65*RATE); music[-tail:]*=np.linspace(1,0,tail)[:,None]
 duck=np.ones(n)
 for line in fitted:
  a=max(0,round((line['start_s']-.09)*RATE)); b=min(n,round((line['end_s']+.08)*RATE)); duck[a:b]=np.minimum(duck[a:b],.45)
  pre=max(0,a-round(.14*RATE)); post=min(n,b+round(.3*RATE))
  if a>pre:duck[pre:a]=np.minimum(duck[pre:a],np.linspace(1,.45,a-pre))
  if post>b:duck[b:post]=np.minimum(duck[b:post],np.linspace(.45,1,post-b))
 music*=duck[:,None]
 sfx=np.zeros((n,2)); cues=[(3.65,'triangle',1046.5),(9.2,'square',1174.66),(19.15,'oval',1318.51),(25.6,'rectangle',1174.66),(33.1,'star',1567.98),(40.3,'diamond',1760),(44,'recap',1318.51)]
 for onset,name,hz in cues:
  length=.4 if name!='star' else .6; t=np.arange(round(length*RATE))/RATE
  sound=(np.sin(2*np.pi*hz*t)+.22*np.sin(2*np.pi*hz*1.5*t))*np.minimum(1,t/.008)*np.exp(-9*t)*.022
  sound*=np.minimum(1,(length-t)/.05)
  i=round(onset*RATE); stop=min(n,i+len(sound)); sfx[i:stop]+=sound[:stop-i,None]
 ambience=np.zeros((n,2))
 out=ROOT/'archive/reviews/EN_v002'
 for name,bus in [('music',music),('sfx',sfx),('ambience',ambience)]:writewav(out/(name+'.wav'),bus)
 story=dialogue+music+sfx
 total=np.zeros((round((2+duration+2.5)*RATE),2)); total[2*RATE:2*RATE+n]+=story
 jingle=readwav(DINO/'library/media/audio/branding/flh-logo-sting-v001.wav')
 total[:2*RATE]+=jingle[:2*RATE]
 tailstart=2*RATE+n; count=min(len(jingle),len(total)-tailstart); total[tailstart:tailstart+count]+=jingle[:count]
 writewav(out/'premix.wav',total)
 loud=loudness(out/'premix.wav'); global_gain=min(-16-float(loud['input_i']),-1.8-float(loud['input_tp']))
 run(['ffmpeg','-v','error','-nostdin','-y','-i',str(out/'premix.wav'),'-af',f'volume={global_gain}dB','-ar',str(RATE),'-ac','2','-c:a','pcm_s24le',str(out/'master.wav')])
 (ROOT/'reports/mix-en-v002.json').write_text(json.dumps({'score':'Original seven-section MIDI/FluidR3 instrumental score','music_gain_db':20*math.log10(gain),'dialogue_duck_db':20*math.log10(.45),'sfx_cues':cues,'ambience':'Intentionally silent separate bus; no unverified external ambience recording used.','premix_loudness':loud,'global_master_gain_db':global_gain,'brand_jingle':'Exact approved original WAV, no pitch/tempo change.'},indent=2)+'\n')

def captions(fitted):
 out=ROOT/'archive/reviews/EN_v002'; header='''[Script Info]\nScriptType: v4.00+\nPlayResX: 1280\nPlayResY: 720\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Nunito ExtraLight,36,&H00FFFFFF,&H00FFFFFF,&H00191919,&H80000000,-1,0,0,0,100,100,0,0,1,2.5,1.5,2,60,60,25,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
 def stamp(t,ass=False):
  if ass:
   cs=round(t*100); return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
  ms=round(t*1000); return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 events=[]; srt=[]
 for i,line in enumerate(fitted):
  a=line['start_s']+2; b=line['end_s']+2; text=line['text']
  events.append(f'Dialogue: 0,{stamp(a,True)},{stamp(b,True)},Default,,0,0,0,,{text}')
  srt.append(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{text}\n')
 (out/'Milo_EP01_EN_Review_v002.ass').write_text(header+'\n'.join(events)+'\n')
 (out/'Milo_EP01_EN_Review_v002.srt').write_text('\n'.join(srt))

def render(plan):
 out=ROOT/'archive/reviews/EN_v002'; output=out/'Milo_EP01_EN_Review_v002.mp4'
 if output.exists():raise ValueError('Review v001 already exists; verify it or choose another version, do not overwrite.')
 fonts=ROOT/'assets/branding/fonts'; ass=out/'Milo_EP01_EN_Review_v002.ass'
 graph=f'[0:v]setpts=PTS-STARTPTS,setsar=1[i];[1:v]trim=end_frame=1052,setpts=PTS-STARTPTS,setsar=1[s0];[4:v]setpts=PTS-STARTPTS,setsar=1[s1];[s0][s1]concat=n=2:v=1:a=0[s];[2:v]setpts=PTS-STARTPTS,setsar=1[o];[i][s][o]concat=n=3:v=1:a=0,ass={ass}:fontsdir={fonts}[v]'
 run(['ffmpeg','-v','error','-nostdin','-n','-i',str(ROOT/'assets/branding/intro-landscape-v001.mp4'),'-i',str(ROOT/plan['picture']),'-i',str(ROOT/'assets/branding/outro-landscape-v001.mp4'),'-i',str(out/'master.wav'),'-i',str(ROOT/plan['retouched_ending']),'-filter_complex',graph,'-map','[v]','-map','3:a:0','-c:v','libx264','-crf','18','-preset','veryfast','-threads','2','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',str(output)])
 print('Rendered complete English review:',output,flush=True)

if __name__=='__main__':
 plan=json.loads((ROOT/'production-en-v002.json').read_text()); (ROOT/'archive/reviews/EN_v002').mkdir(parents=True,exist_ok=True)
 fitted_path=ROOT/'reports/fitted-dialogue-en-v002.json'
 if fitted_path.exists() and (ROOT/'archive/reviews/EN_v002/dialogue.wav').exists():
  fitted=json.loads(fitted_path.read_text())['lines']; dialogue=readwav(ROOT/'archive/reviews/EN_v002/dialogue.wav'); print('Resuming verified fitted dialogue.',flush=True)
 else:fitted,dialogue=align(plan)
 captions(fitted); beds(plan,fitted,dialogue); render(plan)
