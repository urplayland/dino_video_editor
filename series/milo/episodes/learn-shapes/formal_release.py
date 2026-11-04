#!/usr/bin/env python3
"""Versioned localized production; exact cached requests, original picture preserved."""
from pathlib import Path
from workspace_paths import WORKSPACE, DINO
import argparse, hashlib, json, os, sys, time
from urllib import request, error
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(DINO/'tools'))
import dub

TEXT={
 'ZH':['到处都有形状！','这是三角形。','看！正方形！','看看那个牌子！','这是椭圆形。','哇！','看看这扇门。','这是长方形。','哇！','看那颗星星！','这是星形。','哇！','看那个风筝！','看！','菱形！','哇！','找到六种形状啦！','我们下次见！','拜拜！'],
 'MS':['Bentuk ada di mana-mana!','Ini segi tiga.','Lihat! Segi empat sama!','Lihat papan tanda itu!','Ini bentuk bujur.','Wah!','Lihat pintu itu.','Ini segi empat tepat.','Wah!','Lihat bintang itu!','Ini bentuk bintang.','Wah!','Lihat layang-layang itu!','Lihat!','Bentuk berlian.','Wah!','Hari ini kita jumpa enam bentuk!','Jumpa lagi!','Bai-bai!']}
STYLE={
 'ZH':'Milo是一只可爱的小男孩狐狸。使用Achernar音色，说自然清晰的普通话。声音轻柔、甜甜的、年轻，有好奇心，像带着微笑跟小朋友说话。轻快可爱，有小小的惊喜，不要尖叫，不要刻意夹嗓子，不要成人播音腔，不要拖长字音。短句清楚自然，保持同一角色。只读提供的台词，不要添加内容。',
 'MS':'Milo is a cute young boy fox. Speak natural Malaysian Bahasa Melayu, not Indonesian. Use a soft, sweet, light youthful Achernar voice with gentle curiosity, a small warm smile and playful little discoveries. Sound like a child speaking to a friend, clear and conversational. Never an adult narrator, exaggerated baby talk, shouting, or squeaky. Speak the short supplied line naturally and fairly briskly without dragging syllables. Read only the exact dialogue; do not add words.'}

def plans():
 base=json.loads((ROOT/'production-en-v002.json').read_text())
 for lang,texts in TEXT.items():
  p=dict(base,language=lang.lower(),style=STYLE[lang],status='formal_production_in_progress',split_boundary_overrides_s={},groups=[])
  p['lines']=[dict(line,text=text) for line,text in zip(base['lines'],texts)]
  p['voice_approval']='Owner selected Achernar and requested formal EN/ZH/MS production after approving English v002.'
  p['source_dialogue_notes']=['Six shapes: triangle, square, oval, rectangle, star, diamond. Owner requested circle removal; approved derived picture reused.']
  p['delivery']={};p['output']=f'exports/{lang}_Final_v001/Milo_EP01_{lang}_Final_v001.mp4'
  p['groups']=[{'id':x['id'],'line_indices':[i],'text':x['text']} for i,x in enumerate(p['lines'])]
  path=ROOT/f'production-{lang.lower()}-final-v001.json'
  if not path.exists():path.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')

def generate(lang,key_name):
 plan=json.loads((ROOT/f'production-{lang.lower()}-final-v001.json').read_text())
 folder=ROOT/f'media/derived/voice-{lang.lower()}-final-v001';folder.mkdir(parents=True,exist_ok=True)
 authorization=json.loads((DINO/'episodes/rainbow-bridge/production-final-v001.json').read_text())['api_preflight']
 assert authorization['owner_confirmed_billing_disabled'] is True
 assert key_name in authorization['authorized_key_variables'], 'Credential must be in recorded owner authorization'
 dub.load_env(WORKSPACE/'.env',key_name=key_name);key=os.environ['GEMINI_API_KEY'];last_request=0
 for line in plan['lines']:
  body=dub.payload({'text':line['text']},{'voice':plan['voice'],'style':{lang.lower():plan['style']}},lang.lower())
  identity={'model':plan['model'],'voice':plan['voice'],'request':body}
  fp=hashlib.sha256(json.dumps(identity,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
  wav=folder/(line['id']+'.wav');record=wav.with_suffix('.json')
  if wav.exists():
   old=json.loads(record.read_text());assert old['fingerprint']==fp and old['sha256']==hashlib.sha256(wav.read_bytes()).hexdigest()
   print('Cached',lang,line['id'],flush=True);continue
  if record.exists():raise ValueError('Incomplete take requires inspection')
  identical=next((r for r in folder.glob('*.json') if json.loads(r.read_text()).get('fingerprint')==fp),None)
  if identical:
   old=json.loads(identical.read_text());data=identical.with_suffix('.wav').read_bytes();assert hashlib.sha256(data).hexdigest()==old['sha256']
   with wav.open('xb') as f:f.write(data)
   record.write_text(json.dumps(dict(old,reused_from=identical.stem),ensure_ascii=False,indent=2)+'\n')
   print('Reused exact matching request',lang,line['id'],flush=True);continue
  time.sleep(max(0,21-(time.monotonic()-last_request)))
  print('Generating',lang,line['id'],line['text'],flush=True);last_request=time.monotonic()
  req=request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{plan["model"]}:generateContent',data=json.dumps(body).encode(),headers={'x-goog-api-key':key,'Content-Type':'application/json'},method='POST')
  try:
   with request.urlopen(req,timeout=120) as response:data=dub.decode_audio(json.load(response))
  except error.HTTPError as exc:
   safe={'http':exc.code,'key_label':key_name,'line':line['id'],'automatic_retry':False}
   try:
    provider=json.loads(exc.read()).get('error',{});safe['status']=provider.get('status');safe['details']=[]
    for detail in provider.get('details',[]):
     if detail.get('@type','').endswith('QuotaFailure'):
      safe['details'].extend({k:v[k] for k in ('quotaMetric','quotaId','quotaValue') if k in v} for v in detail.get('violations',[]))
     if detail.get('@type','').endswith('RetryInfo'):safe['retry_delay']=detail.get('retryDelay')
   except Exception:pass
   (ROOT/f'reports/quota-{lang.lower()}-{key_name}.json').write_text(json.dumps(safe,indent=2)+'\n')
   raise SystemExit(json.dumps(safe)) from None
  except (error.URLError,TimeoutError):raise SystemExit('Network failure; stopped without retry.') from None
  info=dub.wav_info(data)
  with wav.open('xb') as f:f.write(data)
  record.write_text(json.dumps(dict(identity,fingerprint=fp,sha256=hashlib.sha256(data).hexdigest(),text=line['text'],credential_label=key_name,status='generated_pending_verification',**info),ensure_ascii=False,indent=2)+'\n')
  print(json.dumps({'language':lang,'line':line['id'],**info}),flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['plans','generate']);parser.add_argument('--language',choices=['ZH','MS']);parser.add_argument('--key',default='GEMINI_API_KEY');args=parser.parse_args()
 plans()
 if args.action=='generate':generate(args.language,args.key)
