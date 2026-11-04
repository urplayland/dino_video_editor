#!/usr/bin/env python3
"""Check final movie decode, every story frame, captions, source hashes and levels."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parent

def run(args,timeout=900):
 r=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if r.returncode:raise RuntimeError(r.stderr[-1800:])
 return r

def technical(lang):
 from assemble_localized import levels
 path=ROOT/f'exports/{lang}_Final_v001/Milo_EP01_{lang}_Final_v001.mp4'
 plan=json.loads((ROOT/'production-en-v002.json' if lang=='EN' else ROOT/f'production-{lang.lower()}-final-v001.json').read_text())
 probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]).stdout)
 v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
 assert (v['width'],v['height'],int(v['nb_frames']))==(1280,720,1315)
 assert v['avg_frame_rate']=='24/1' and abs(float(v['duration'])-1315/24)<.001
 assert int(a['sample_rate'])==48000 and a['channels']==2
 decoded=run(['ffmpeg','-hide_banner','-nostdin','-threads','1','-filter_threads','1','-i',str(path),'-vf','blackdetect=d=0.05:pix_th=0.05','-f','null','-'])
 black=[s for s in decoded.stderr.splitlines() if 'black_start:' in s];assert not black,black
 stats=ROOT/f'reports/formal-story-ssim-{lang.lower()}.log'
 graph=f'[0:v]trim=start_frame=48:end_frame=1255,setpts=PTS-STARTPTS,crop=1280:610:0:0[f];[1:v]setpts=PTS-STARTPTS,crop=1280:610:0:0[s];[f][s]ssim=stats_file={stats}'
 run(['ffmpeg','-hide_banner','-nostdin','-threads','1','-i',str(path),'-threads','1','-i',str(ROOT/plan['picture']),'-filter_complex_threads','1','-filter_complex',graph,'-an','-f','null','-'])
 scores=[float(x) for x in re.findall(r'All:([0-9.]+)',stats.read_text())];assert len(scores)==1207 and min(scores)>.94
 measure=levels(path);assert float(measure['input_tp'])<=-.8 and abs(float(measure['input_i'])+16)<=1.1,measure
 for item in json.loads((ROOT/'reports/source-inventory-v001.json').read_text()):assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
 srt=path.with_suffix('.srt').read_text();assert len(re.findall(r' --> ',srt))==19
 for line in plan['lines']:assert line['text'] in srt
 if lang=='EN':assert hashlib.sha256(path.read_bytes()).hexdigest()==hashlib.sha256((ROOT/'archive/reviews/EN_v002/Milo_EP01_EN_Review_v002.mp4').read_bytes()).hexdigest()
 report={'status':'technical_checks_passed','video':str(path.relative_to(ROOT)),'language':lang,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'resolution':[1280,720],'fps':24,'frames':1315,'duration_s':float(v['duration']),'full_decode':True,'unexpected_black_runs':black,'loudness':measure,'story_frames_compared':len(scores),'ssim_min':min(scores),'ssim_average':sum(scores)/len(scores),'subtitle_cues':19,'source_hashes_unchanged':True,'owner_review':'EN v002 approved; formal EN is byte-identical.' if lang=='EN' else 'Localized acting has not yet received owner listening approval.','publication':'Private upload only; owner will publish.'}
 (ROOT/f'reports/formal-qa-{lang.lower()}-v001.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)

def speech(lang,modelname):
 import numpy as np,wave
 from faster_whisper import WhisperModel
 m=WhisperModel(modelname,device='cpu',compute_type='int8',cpu_threads=2,num_workers=1,download_root=str(ROOT/'work/whisper'))
 out=ROOT/f'exports/{lang}_Final_v001';wav=ROOT/f'work/{lang.lower()}-final-v001/encoded-story.wav';wav.parent.mkdir(parents=True,exist_ok=True)
 run(['ffmpeg','-v','error','-nostdin','-threads','1','-filter_threads','1','-y','-ss','2','-i',str(out/f'Milo_EP01_{lang}_Final_v001.mp4'),'-t',str(1207/24),'-vn','-ar','16000','-ac','1','-c:a','pcm_s16le',str(wav)])
 segments,_=m.transcribe(str(wav),language=lang.lower(),beam_size=5,condition_on_previous_text=False,word_timestamps=True)
 rows=[]
 for s in segments:
  row={'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'text':w.word} for w in (s.words or [])]};rows.append(row);print(lang,s.text,flush=True)
 report={'model':modelname,'language':lang,'text':' '.join(s['text'].strip() for s in rows),'segments':rows,'status':'machine_transcript_pending_comparison'}
 (ROOT/f'reports/formal-encoded-speech-{lang.lower()}-v001.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['technical','speech']);p.add_argument('language',choices=['EN','ZH','MS']);p.add_argument('--model',default='small');a=p.parse_args()
 if a.action=='technical':technical(a.language)
 else:speech(a.language,a.model)
