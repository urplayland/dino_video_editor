"""Remove the ending's circle using the same shot's clean sky plate; preserve the foreground ear."""
from pathlib import Path
import json,subprocess
import av,numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import binary_opening,binary_dilation
ROOT=Path(__file__).resolve().parent

def retouch(im,t,plate,previous=None):
 if t<43.85 or t>=49.8:return im,None
 a=np.asarray(im)
 keys=[43.85,44,44.25,44.5,44.75,45,49.8]
 cx=float(np.interp(t,keys,[682,690,713,731,742,748,748]));cy=float(np.interp(t,keys,[420,361,270,202,158,139,139]));state=(cx,cy)
 mask=Image.new('L',im.size,0);d=ImageDraw.Draw(mask)
 d.ellipse((cx-70,cy-74,cx+70,cy+74),fill=255)
 mask=mask.filter(ImageFilter.GaussianBlur(1.5))
 # Preserve the foreground fox ear where the circle passes behind it.
 u=max(-.5,min(1,(t-44.25)/.75));dx=-17*u;dy=-17*u
 edge=[(681,192),(705,192),(719,201),(726,216),(730,244),(727,278),(717,311),(699,348)]
 protect=Image.new('L',im.size,255);pd=ImageDraw.Draw(protect)
 pd.polygon([(0,0),(0,720),(740,720),(699+dx,348+dy),*[(x+dx,y+dy) for x,y in reversed(edge[:-1])],(0,0)],fill=0)
 # Above the ear tip, sky remains replaceable.
 pm=np.asarray(protect,dtype=np.float32)/255
 colors=np.asarray(im,dtype=np.float32)
 yellow=(colors[:,:,0]>150)&(colors[:,:,1]>colors[:,:,0]*.68)&(colors[:,:,2]<colors[:,:,0]*.55)
 yellow=binary_dilation(binary_opening(yellow,iterations=2),iterations=2)
 star_protect=Image.fromarray((yellow*255).astype('uint8'))
 mm=np.asarray(mask,dtype=np.float32)/255*pm*(1-np.asarray(star_protect,dtype=np.float32)/255)
 result=np.asarray(im).astype(np.float32)*(1-mm[:,:,None])+np.asarray(plate).astype(np.float32)*mm[:,:,None]
 return Image.fromarray(np.rint(result).astype('uint8')),state

if __name__=='__main__':
 plate=Image.open(ROOT/'media/derived/picture-v002/sky-plate-frame1200.png').convert('RGB')
 canvas=Image.new('RGB',(3*640,2*360),'white')
 for i,t in enumerate([44,44.25,44.5,45,46,49.5]):
  im=Image.open(ROOT/'work'/f'ending-{t:.2f}.png').convert('RGB');fixed,_=retouch(im,t,plate)
  canvas.paste(fixed.resize((640,360)),(i%3*640,i//3*360))
 canvas.save(ROOT/'reports/circle-removal-preview-v002.jpg')
