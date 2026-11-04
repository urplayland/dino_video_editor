#!/usr/bin/env python3
"""Upload only verified Milo EP01 finals as private; no publish/delete/playlist writes."""
from pathlib import Path
from workspace_paths import WORKSPACE, DINO
import argparse,hashlib,importlib.util,json,os,re,sys
from urllib import request,error,parse
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('yt_manager',WORKSPACE/'tools/publishing/youtube-manager.py')
manager=importlib.util.module_from_spec(spec);spec.loader.exec_module(manager)
METADATA={
 'EN':{'title':"Milo Series EP01 — Let's Learn Shapes! | English",'description':'Join Milo on a little shape-finding adventure! Learn six shapes: triangle, square, oval, rectangle, star and diamond.\n\nEnglish dialogue and subtitles. A short learning story for young children from Family Learning Hub.\n\n#Milo #LearnShapes #FamilyLearningHub','language':'en'},
 'ZH':{'title':'Milo 系列 EP01 — 一起认识形状！| 中文','description':'和 Milo 一起寻找身边的形状吧！认识六种形状：三角形、正方形、椭圆形、长方形、星形和菱形。\n\n普通话配音，配中文字幕。Family Learning Hub 为小朋友准备的形状学习小故事。\n\n#Milo #认识形状 #FamilyLearningHub','language':'zh-Hans'},
 'MS':{'title':'Milo EP01 — Jom Kenali Bentuk! | Bahasa Melayu','description':'Jom ikut Milo mencari bentuk di sekeliling kita! Kenali enam bentuk: segi tiga, segi empat sama, bujur, segi empat tepat, bintang dan berlian.\n\nDialog dan sari kata dalam Bahasa Melayu Malaysia. Cerita pembelajaran pendek untuk kanak-kanak daripada Family Learning Hub.\n\n#Milo #KenaliBentuk #FamilyLearningHub','language':'ms'}}

def save_private(path,value):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
 with os.fdopen(fd,'w') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

def upload(lang):
 # Gate all uploads on completed checks for all three requested releases.
 for language in METADATA:
  qa=json.loads((ROOT/f'reports/formal-qa-{language.lower()}-v001.json').read_text())
  assert qa['status']=='technical_checks_passed'
  f=ROOT/qa['video'];assert hashlib.sha256(f.read_bytes()).hexdigest()==qa['sha256']
 video=ROOT/f'exports/{lang}_Final_v001/Milo_EP01_{lang}_Final_v001.mp4'
 sha=hashlib.sha256(video.read_bytes()).hexdigest();size=video.stat().st_size
 folder=ROOT/'work/youtube';folder.mkdir(parents=True,exist_ok=True)
 statepath=folder/f'{lang.lower()}-final-v001.json';resultpath=ROOT/f'reports/youtube-{lang.lower()}-final-v001.json'
 api=manager.YouTube();meta=METADATA[lang]
 assert 'upload_private_milo_ep01_final' in api.policy['allowed_operations']
 permission=api.policy['private_upload_authorization']
 assert permission['privacy']=='private' and lang in permission['languages'] and permission['owner_will_publish'] is True
 body={'snippet':{'title':meta['title'],'description':meta['description'],'categoryId':'27','defaultLanguage':meta['language'],'defaultAudioLanguage':meta['language'],'tags':['Milo','shapes','Family Learning Hub']},'status':{'privacyStatus':'private','selfDeclaredMadeForKids':True,'embeddable':True}}
 if resultpath.exists():
  old=json.loads(resultpath.read_text());assert old['sha256']==sha
  print('Already uploaded',lang,old['video_id']);return
 if statepath.exists():
  state=json.loads(statepath.read_text());assert state['sha256']==sha
 else:
  req=request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status&notifySubscribers=false',data=json.dumps(body,ensure_ascii=False).encode(),headers={'Authorization':'Bearer '+api.access_token,'Content-Type':'application/json; charset=UTF-8','X-Upload-Content-Type':'video/mp4','X-Upload-Content-Length':str(size)},method='POST')
  with request.urlopen(req,timeout=90) as response:location=response.headers['Location']
  assert parse.urlparse(location).scheme=='https' and parse.urlparse(location).hostname in ('www.googleapis.com','youtube.googleapis.com')
  state={'sha256':sha,'upload_url':location,'offset':0,'metadata':body};save_private(statepath,state)
 url=state['upload_url'];offset=0
 # Query the resumable session first, including on a fresh session. Never create duplicates on retry.
 req=request.Request(url,data=b'',headers={'Authorization':'Bearer '+api.access_token,'Content-Length':'0','Content-Range':f'bytes */{size}'},method='PUT')
 complete=None
 try:
  with request.urlopen(req,timeout=90) as response:complete=json.load(response)
 except error.HTTPError as exc:
  if exc.code!=308:raise
  uploaded=exc.headers.get('Range','');offset=int(uploaded.rsplit('-',1)[-1])+1 if uploaded else 0
 with video.open('rb') as stream:
  while complete is None:
   stream.seek(offset);data=stream.read(4*1024*1024);assert data
   end=offset+len(data)-1
   req=request.Request(url,data=data,headers={'Authorization':'Bearer '+api.access_token,'Content-Type':'video/mp4','Content-Length':str(len(data)),'Content-Range':f'bytes {offset}-{end}/{size}'},method='PUT')
   try:
    with request.urlopen(req,timeout=180) as response:complete=json.load(response)
   except error.HTTPError as exc:
    if exc.code!=308:raise
    uploaded=exc.headers.get('Range','');offset=int(uploaded.rsplit('-',1)[-1])+1 if uploaded else 0
    state['offset']=offset;save_private(statepath,state);print(lang,'uploaded',offset,'of',size,flush=True)
 assert complete['snippet']['channelId']==api.policy['channel_id']
 assert complete['status']['privacyStatus']=='private'
 result={'video_id':complete['id'],'url':'https://www.youtube.com/watch?v='+complete['id'],'sha256':sha,'bytes':size,'language':lang,'metadata':body,'response':complete,'playlist_assignment':'Manual owner action; no playlist writes requested by this helper.'}
 resultpath.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'language':lang,'video_id':complete['id'],'privacy':'private'}),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('language',choices=['EN','ZH','MS']);a=p.parse_args()
 try:upload(a.language)
 except error.HTTPError as exc:
  reason=''
  try:reason=','.join(e.get('reason','') for e in json.loads(exc.read()).get('error',{}).get('errors',[]))
  except Exception:pass
  raise SystemExit(f'YouTube HTTP {exc.code}: {reason}; stopped without retry. Credentials withheld.') from None
