from pathlib import Path
import av,numpy as np,json,subprocess
from PIL import Image
from remove_circle_v2 import retouch
ROOT=Path(__file__).resolve().parent
folder=ROOT/'media/derived/picture-v002';folder.mkdir(parents=True,exist_ok=True)
output=folder/'ending-six-shapes-lossless-v002.mkv'
if output.exists():raise SystemExit('Derived ending exists; do not overwrite.')
plate=Image.open(ROOT/'media/derived/picture-v002/sky-plate-frame1200.png').convert('RGB')
cmd=['ffmpeg','-v','error','-nostdin','-n','-f','rawvideo','-pixel_format','rgb24','-video_size','1280x720','-framerate','24','-i','-','-an','-c:v','ffv1','-level','3','-g','1','-threads','1','-pix_fmt','bgr0',str(output)]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE);count=0;state=None;changed=[]
try:
 with av.open(str(ROOT/'media/originals/production/Milo_EP01_Silent_Master.mp4')) as c:
  c.seek(int(43*1e6))
  for f in c.decode(video=0):
   index=round(float(f.time)*24)
   if index<1052:continue
   im=f.to_image();fixed,state=retouch(im,float(f.time),plate,state)
   if fixed is not im:changed.append(index)
   p.stdin.write(np.asarray(fixed,dtype='uint8').tobytes());count+=1
 p.stdin.close();err=p.stderr.read().decode();rc=p.wait()
 if rc:raise RuntimeError(err[-1000:])
except BaseException:
 if p.poll() is None:p.terminate();p.wait()
 raise
assert count==155,count
(folder/'retouch-provenance-v002.json').write_text(json.dumps({'source':'media/originals/production/Milo_EP01_Silent_Master.mp4','clean_plate_source_frame':1200,'start_frame':1052,'frames':155,'changed_frames':changed,'method':'Same-shot clean sky plate, measured animated ellipse mask, protected foreground ear and yellow star. No image/video generation. Original source unchanged.'},indent=2)+'\n')
print('Rendered six-shape lossless ending:',count,'frames',flush=True)
