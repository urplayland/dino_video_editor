from pathlib import Path
import hashlib,json,re,subprocess,sys,gc
import av,numpy as np
from PIL import Image,ImageDraw
from faster_whisper import WhisperModel
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from assemble_en_v2 import loudness,norm
out=ROOT/'archive/reviews/EN_v002/Milo_EP01_EN_Review_v002.mp4'
plan=json.loads((ROOT/'production-en-v002.json').read_text())
def run(args,timeout=900):
 r=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if r.returncode:raise RuntimeError(r.stderr[-1800:])
 return r
probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]).stdout)
v=next(s for s in probe['streams'] if s['codec_type']=='video'); a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],int(v['nb_frames']))==(1280,720,1315)
assert v['avg_frame_rate']=='24/1' and abs(float(v['duration'])-1315/24)<.001
assert int(a['sample_rate'])==48000 and a['channels']==2
# Entire file decode with black-frame scan.
dec=run(['ffmpeg','-hide_banner','-nostdin','-threads','1','-filter_threads','1','-i',str(out),'-vf','blackdetect=d=0.05:pix_th=0.05','-f','null','-'])
black=[s for s in dec.stderr.splitlines() if 'black_start:' in s]
assert not black,black
# Compare every story frame above the caption area with unchanged source picture.
graph='[0:v]trim=start_frame=48:end_frame=1255,setpts=PTS-STARTPTS,crop=1280:610:0:0[f];[1:v]setpts=PTS-STARTPTS,crop=1280:610:0:0[s];[f][s]ssim=stats_file='+str(ROOT/'reports/story-frame-ssim-v002.log')
r=run(['ffmpeg','-hide_banner','-nostdin','-threads','1','-i',str(out),'-threads','1','-i',str(ROOT/plan['picture']),'-filter_complex_threads','1','-filter_complex',graph,'-an','-f','null','-'],timeout=900)
ssim=[float(x) for x in re.findall(r'All:([0-9.]+)',(ROOT/'reports/story-frame-ssim-v002.log').read_text())]
assert len(ssim)==1207,len(ssim)
assert min(ssim)>.94, min(ssim)
levels=loudness(out)
assert float(levels['input_tp'])<=-.8,levels
assert abs(float(levels['input_i'])+16)<=1.1,levels
# Decode every frame and collect opening/ending, every dialogue midpoint, all splice boundaries.
fitted=json.loads((ROOT/'reports/fitted-dialogue-en-v002.json').read_text())['lines']
indices=set([0,24,47,48,49,1254,1255,1256,1280,1314])
for seconds in [7.9166667,15.8333333,20.2083333,34.0416667,38.375,42.375]:
 idx=48+round(seconds*24); indices.update([idx-1,idx,idx+1])
for line in fitted:indices.add(round((2+(line['start_s']+line['end_s'])/2)*24))
indices=sorted(indices); canvas=Image.new('RGB',(5*320,((len(indices)+4)//5)*202),'white'); draw=ImageDraw.Draw(canvas)
count=0; last=None; identical=[]; black_means=[]; diffs=[]
with av.open(str(out)) as container:
 for frame in container.decode(video=0):
  assert abs(float(frame.time)-count/24)<.002
  im=frame.to_image(); small=np.asarray(im.resize((64,36)),dtype=np.float32)
  if last is not None:
   diff=float(np.mean(np.abs(small-last))); diffs.append(diff)
   if diff<.01:identical.append(count)
  last=small
  if count in indices:
   j=indices.index(count); x=j%5*320; y=j//5*202; canvas.paste(im.resize((320,180)),(x,y));draw.text((x+4,y+183),f'{count/24:.3f}s / frame {count}',fill='black')
  count+=1
assert count==1315
canvas.save(ROOT/'reports/review-contact-sheet-v002.jpg')
# Verify original intake files remain byte-identical.
for item in json.loads((ROOT/'reports/source-inventory-v001.json').read_text()):
 p=ROOT/item['path']; assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
report={'status':'technical_checks_passed_pending_owner_review','video':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'duration_s':float(v['duration']),'frames':count,'resolution':[1280,720],'fps':24,'audio':{'codec':a['codec_name'],'sample_rate':48000,'channels':2,'loudness':levels},'full_decode':True,'unexpected_black_runs':black,'story_frames_compared_to_source':len(ssim),'story_upper_frame_ssim_min':min(ssim),'story_upper_frame_ssim_average':sum(ssim)/len(ssim),'source_original_hashes_unchanged':True,'subtitle_cues':len(fitted),'max_voice_tempo_factor':max(x['tempo_factor'] for x in fitted),'max_voice_start_shift_s':max(abs(x['start_s']-x['source_start_s']) for x in fitted),'voice':'Achernar','limitations':['Machine transcript and visual sampled-frame checks do not replace owner listening approval.','Accepted original Square-to-Oval framing change retained.','Circle removed from derived ending; voice and subtitles now recap six shapes. Original master preserved.'],'nearly_identical_adjacent_frames':identical}
(ROOT/'reports/technical-review-en-v002.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
# Independent encoded-mix transcript after technical checks, using one small recognizer.
ref=ROOT/'work/en-v002/final-mix-asr.wav'
run(['ffmpeg','-v','error','-nostdin','-threads','1','-i',str(out),'-vn','-ar','16000','-ac','1','-c:a','pcm_s16le','-y',str(ref)])
model=WhisperModel('base.en',device='cpu',compute_type='int8',cpu_threads=2,num_workers=1,download_root=str(ROOT/'work/whisper'))
import wave
with wave.open(str(ref),'rb') as w:
 rate=w.getframerate();pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
segments,_=model.transcribe(pcm[2*rate:round((2+1207/24)*rate)],beam_size=5)
segments=[{'start':s.start+2,'end':s.end+2,'text':s.text} for s in segments]
text=' '.join(x['text'].strip() for x in segments)
expected=' '.join(x['text'] for x in plan['lines'])
transcript={'method':'Independent base.en ASR from the final encoded AAC mix','text':text,'segments':segments,'expected':expected,'exact_normalized_match':norm(text)==norm(expected)}
(ROOT/'reports/final-encoded-dialogue-en-v002.json').write_text(json.dumps(transcript,indent=2)+'\n')
print(json.dumps(transcript),flush=True)
