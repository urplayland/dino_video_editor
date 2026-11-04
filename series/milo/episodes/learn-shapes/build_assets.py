#!/usr/bin/env python3
from pathlib import Path
from workspace_paths import WORKSPACE, DINO
import hashlib,json,math,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(DINO/'tools'))
import scene_score
ROOT=Path(__file__).resolve().parent
DURATION=1207/24

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
 r=subprocess.run(args,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stderr[-2000:])
 return r.stdout

def branding():
 cfg=json.loads((DINO/'config/branding-logo-v004.json').read_text())
 logo_path=DINO/cfg['assets']['logo.png']['path']; sting=DINO/cfg['sonic_logo']
 assert sha(logo_path)==cfg['assets']['logo.png']['sha256']
 assert sha(sting)==cfg['assets']['sonic-logo.wav']['sha256']
 folder=ROOT/'assets/branding'; folder.mkdir(parents=True,exist_ok=True)
 logo=Image.open(logo_path).convert('RGBA')
 head=ImageFont.truetype(str(folder/'fonts/Outfit-800.ttf'),46)
 body=ImageFont.truetype(str(folder/'fonts/Nunito-700.ttf'),27)
 clips={}
 for kind,duration in [('intro',2),('outro',2.5)]:
  target=folder/(kind+'-landscape-v001.mp4'); clips[kind]=str(target.relative_to(ROOT))
  if target.exists():continue
  cmd=['ffmpeg','-v','error','-nostdin','-n','-f','rawvideo','-pixel_format','rgb24','-video_size','1280x720','-framerate','24','-i','-','-an','-frames:v',str(round(duration*24)),'-c:v','libx264','-crf','17','-preset','fast','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
  for n in range(round(duration*24)):
   t=n/24; u=max(0,min(1,(t-.04)/.66)); back=1+2.45*(u-1)**3+1.45*(u-1)**2; alpha=max(0,min(1,(t-.02)/.16))
   im=Image.new('RGBA',(1280,720),'#FFFDF9'); d=ImageDraw.Draw(im)
   drift=5*math.sin(t*math.pi/2)
   d.rounded_rectangle((-120,78+drift,150,348+drift),radius=92,fill='#E4F5FE')
   d.rounded_rectangle((1130,425-drift,1400,695-drift),radius=92,fill='#EFF8DC')
   d.ellipse((1124,80,1280,236),fill='#FFF2CE')
   d.rounded_rectangle((-25,558,72,655),radius=30,fill='#F2EAF8')
   for k,color in enumerate(('#1CB0F6','#58CC02','#FFC800','#8549BA')):
    x=550+k*48; d.rounded_rectangle((x,614,x+36,622),radius=4,fill=color)
   d.ellipse((566,394,714,410),fill=(229,216,187,round(70*alpha)))
   if .12<t<.72:
    q=(t-.12)/.6; r=130+65*q; d.ellipse((640-r,270-r,640+r,270+r),outline=(28,176,246,round(90*(1-q))),width=4)
   size=max(1,round(250*max(.015,back))); mark=logo.resize((size,size),Image.Resampling.LANCZOS).rotate(-7*(1-u)**2,resample=Image.Resampling.BICUBIC,expand=True)
   mark.putalpha(mark.getchannel('A').point([round(i*alpha) for i in range(256)]))
   im.alpha_composite(mark,(round(640-mark.width/2),round(270-mark.height/2+55*(1-back))))
   for onset,length,draw_text in [(.46,.34,True),(.73,.28,False)]:
    v=max(0,min(1,(t-onset)/length))
    if not v:continue
    layer=Image.new('RGBA',im.size); ld=ImageDraw.Draw(layer)
    if draw_text:ld.text((640,439+14*(1-v)),cfg['brand'],font=head,fill='#4B4B4B',anchor='mt')
    else:
     yy=513+6*(1-v)
     ld.rounded_rectangle((415,yy+7,865,yy+69),radius=30,fill='#1899D6')
     ld.rounded_rectangle((415,yy,865,yy+61),radius=30,fill='#1CB0F6',outline='#1899D6',width=2)
     ld.text((640,yy+30),cfg['website'],font=body,fill='white',anchor='mm')
    layer.putalpha(layer.getchannel('A').point([round(i*v) for i in range(256)])); im=Image.alpha_composite(im,layer)
   p.stdin.write(im.convert('RGB').tobytes())
  p.stdin.close(); msg=p.stderr.read().decode(); rc=p.wait()
  if rc:raise RuntimeError(msg[-2000:])
  print('Rendered landscape branding:',kind,flush=True)
 (folder/'provenance-v001.json').write_text(json.dumps({'source_config':str(DINO/'config/branding-logo-v004.json'),'source_config_sha256':sha(DINO/'config/branding-logo-v004.json'),'original_logo_sha256':sha(logo_path),'original_jingle_sha256':sha(sting),'adaptation':'Same existing FLH logo/theme/pop animation/website pill; composition rebuilt at 1280x720 without stretching original art. Original four-note WAV retained unchanged.','clips':{k:{'path':v,'sha256':sha(ROOT/v)} for k,v in clips.items()}},indent=2)+'\n')

def music():
 folder=ROOT/'media/derived/score-v001'; folder.mkdir(parents=True,exist_ok=True)
 registry=json.loads((DINO/'config/music_presets.json').read_text())
 registry['instruments']={'marimba':{'channel':0,'program':12,'pan':60},'pizzicato':{'channel':1,'program':45,'pan':76},'guitar':{'channel':2,'program':24,'pan':48},'strings':{'channel':3,'program':48,'pan':64},'drums':{'channel':9,'program':0,'pan':64}}
 sections=[('triangle-curiosity',0,7.9166667,[60,64,67,72],112),('square-discovery',7.9166667,15.8333333,[65,69,72,76],112),('oval-wonder',15.8333333,20.2083333,[57,60,64,69],108),('rectangle-discovery',20.2083333,28.1666667,[62,65,69,74],112),('star-delight',28.1666667,34.0416667,[60,64,67,76],116),('kite-anticipation',34.0416667,42.375,[67,71,74,79],116),('recap-resolution',42.375,DURATION,[60,64,67,72],112)]
 cues=[]
 for i,(name,start,end,chord,bpm) in enumerate(sections):
  layers=[{'kind':'pattern','instrument':'pizzicato','notes':[chord[0]-12,chord[2]-12,chord[1]-12,chord[2]-12],'step_beats':.5,'gate':.38,'velocity':39,'accents':[3,-4,-1,-4]}, {'kind':'pad','instrument':'strings','chords':[[x-12 for x in chord]],'velocity':20,'tail_s':.12}, {'kind':'pattern','instrument':'guitar','notes':[chord[0],chord[2],chord[1],chord[2]],'step_beats':1,'gate':.6,'velocity':34,'accents':[2,-3,-1,-3]}]
  # Short, sparse discovery figures rather than a constant competing lead melody.
  if i in (0,1,2,4,5,6):layers.append({'kind':'phrase','instrument':'marimba','offset_s':min(.2,(end-start)/10),'velocity':41,'events':[[0,chord[0]+12,.45,0],[.5,chord[1]+12,.4,-2],[1,chord[2]+12,.65,1],[2,chord[1]+12,.5,-2]]})
  cues.append({'id':name,'start_s':start,'end_s':end,'bpm':bpm,'layers':layers})
 plan={'schema_version':1,'title':'Milo EP01 — original playful discovery underscore v001','duration_s':DURATION,'seed':20261104,'cues':cues}
 scene_score.validate_plan(plan,registry); notes=scene_score.arrange(plan,registry); midi=scene_score.midi_bytes(plan,registry,notes)
 (folder/'score.mid').write_bytes(midi); (folder/'score-plan.json').write_text(json.dumps(plan,indent=2)); (folder/'instrument-registry.json').write_text(json.dumps(registry,indent=2))
 bank=Path('/usr/share/sounds/sf2/FluidR3_GM.sf2'); assert sha(bank)==registry['soundfont']['sha256']
 wav=folder/'score-raw.wav'
 if not wav.exists():run(['fluidsynth','-ni','-q','-r','48000','-g','.4','-C','0','-R','1','-o','synth.reverb.room-size=.4','-o','synth.reverb.level=.12','-F',str(wav),'-T','wav','-O','float',str(bank),str(folder/'score.mid')])
 (folder/'provenance.json').write_text(json.dumps({'composition':'Original deterministic seven-section instrumental MIDI score for this picture; no external song recording.','midi_sha256':sha(folder/'score.mid'),'soundfont_sha256':sha(bank),'soundfont_license_notice':str(DINO/'library/licenses/fluidr3-gm.txt'),'notes':len(notes)},indent=2))
 print('Rendered original scene score:',len(notes),'notes',flush=True)

if __name__=='__main__':branding();music()
