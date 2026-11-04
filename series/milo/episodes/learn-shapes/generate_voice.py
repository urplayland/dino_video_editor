#!/usr/bin/env python3
"""Generate only the owner-selected Milo EN voice takes; resume exact cached requests."""
from pathlib import Path
from workspace_paths import WORKSPACE, DINO
import hashlib,json,os,sys,time
from urllib import request,error
sys.path.insert(0,str(DINO/'tools'))
import dub
ROOT=Path(__file__).resolve().parent

def main():
 plan=json.loads((ROOT/'production-en-v001.json').read_text())
 dub.load_env(WORKSPACE/'.env')
 key=os.environ['GEMINI_API_KEY']; folder=ROOT/'media/derived/voice-en-v001'
 for n,group in enumerate(plan['groups']):
  body=dub.payload({'text':group['text']},{'voice':plan['voice'],'style':{'en':plan['style']}},'en')
  identity={'model':plan['model'],'voice':plan['voice'],'request':body}
  fp=hashlib.sha256(json.dumps(identity,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
  wav=folder/(group['id']+'.wav'); record=wav.with_suffix('.json')
  if wav.exists():
   old=json.loads(record.read_text())
   if old['fingerprint']!=fp or old['sha256']!=hashlib.sha256(wav.read_bytes()).hexdigest(): raise ValueError('Cached voice mismatch; choose a new take version.')
   print('Cached verified request:',group['id'],flush=True); continue
  if record.exists(): raise ValueError('Incomplete previous voice output; inspect before retrying.')
  if n: time.sleep(21)
  print('Generating:',group['id'],flush=True)
  req=request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{plan["model"]}:generateContent',data=json.dumps(body).encode(),headers={'x-goog-api-key':key,'Content-Type':'application/json'},method='POST')
  try:
   with request.urlopen(req,timeout=120) as response: data=dub.decode_audio(json.load(response))
  except error.HTTPError as exc:
   details=[]
   try:
    provider=json.loads(exc.read()).get('error',{})
    for item in provider.get('details',[]):
     if item.get('@type','').endswith('QuotaFailure'):
      details.extend({k:v[k] for k in ('quotaMetric','quotaId','quotaValue') if k in v} for v in item.get('violations',[]))
   except Exception: pass
   raise SystemExit(json.dumps({'group':group['id'],'http':exc.code,'details':details,'automatic_retry':False})) from None
  except (error.URLError,TimeoutError): raise SystemExit('Network failure; stopped without automatic retry.') from None
  info=dub.wav_info(data)
  with wav.open('xb') as f:f.write(data)
  record.write_text(json.dumps(dict(identity,fingerprint=fp,sha256=hashlib.sha256(data).hexdigest(),text=group['text'],credential_label='GEMINI_API_KEY',status='generated_pending_local_transcription_and_owner_listening',**info),indent=2)+'\n')
  print(json.dumps({'group':group['id'],**info}),flush=True)

if __name__=='__main__': main()
