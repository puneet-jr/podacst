"""Documented local-only API smoke. Raw evidence stays in ignored output storage.

No automatic semantic approval, retry, import, DB reset or model fallback.
"""
import argparse,json,time,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from http.client import HTTPException
from uuid import uuid4
p=argparse.ArgumentParser();p.add_argument('--base-url',default='http://127.0.0.1:8000');p.add_argument('--output',required=True);p.add_argument('--reopen',action='store_true');a=p.parse_args();root=Path(a.output);root.mkdir(parents=True,exist_ok=True)
if not a.base_url.startswith(('http://127.0.0.1:','http://localhost:')):raise SystemExit('Use the local API only')
def call(path,body=None,timeout=100):
 req=Request(a.base_url+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
 with urlopen(req,timeout=timeout) as r:return r.read()
def get(path):return json.loads(call(path))
def post(path,body,timeout=100):return json.loads(call(path,body,timeout))
def h(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
def ready():
 deadline=time.monotonic()+30
 for _ in range(60):
  if time.monotonic()>=deadline:break
  try:
   r=json.loads(call('/api/health/ready',timeout=min(5,max(.1,deadline-time.monotonic()))))
   if r['status']=='ready':return r
  except (HTTPError,URLError,TimeoutError,HTTPException,ConnectionError):pass
  time.sleep(.5)
 raise RuntimeError('Readiness did not recover within the bounded poll')
def snapshot(report):
 sid=report['session_id'];paths=[f'/api/sessions/{sid}',f'/api/sessions/{sid}/messages',f'/api/sessions/{sid}/artifacts']
 for answer in report['answers']:
  for source in answer['sources']:paths.append(f"/api/sessions/{sid}/messages/{answer['message_id']}/sources/{source['label']}")
 if report.get('essay'):paths.extend([f"/api/sessions/{sid}/essays/{report['essay']['id']}",f"/api/sessions/{sid}/essays/{report['essay']['id']}/sources"])
 return {path:get(path) for path in paths}
if a.reopen:
 report=json.loads((root/'report.json').read_text());ready();state=snapshot(report);old=json.loads((root/'before-restart.json').read_text());assert state==old,'Saved objects changed after restart'
 result={'reopen_pass':True,'objects_checked':len(state),'snapshot_sha256':h(state),'session_id':report['session_id']};(root/'reopen.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));raise SystemExit
if (root/'report.json').exists():raise SystemExit('Existing attempt preserved; choose another output directory only for an explicitly authorized new run')
health=ready();providers=get('/api/providers');assert providers['selected']=='ollama' and not providers['automatic_fallback'];assert health['checks']['corpus']['ready']
sid=post('/api/sessions',{'title':'README rehearsal · local, not a quality benchmark'})['id'];report={'session_id':sid,'provider':'ollama-local','model':providers['model'],'essay_model':providers['essay_model'],'corpus':health['checks']['corpus'],'answers':[],'artifacts':[],'essay':None,'semantic_review':'pending;exit0 is not factual or essay acceptance'}
def save():(root/'report.json').write_text(json.dumps(report,indent=2))
save()
for name,question,scope in [('question','What does Sean Ellis ask in the must-have survey?','episodes/sean-ellis/transcript.md'),('follow-up','How did they change onboarding at Lookout?',None)]:
 t=time.monotonic();raw=call(f'/api/sessions/{sid}/answers',{'content':question,'source_path':scope,'client_message_id':str(uuid4()),'retrieval_mode':'hybrid','timeout_seconds':90});(root/(name+'-stream.ndjson')).write_bytes(raw);events=[json.loads(v) for v in raw.decode().splitlines()];run=get(f"/api/sessions/{sid}/runs/{events[0]['run_id']}");(root/(name+'-run.json')).write_text(json.dumps(run,indent=2));messages=get(f'/api/sessions/{sid}/messages');reply=next((m for m in messages if m['id']==run['assistant_message_id']),None);sources=[]
 if reply:
  (root/(name+'-reply.json')).write_text(json.dumps(reply,indent=2))
  for citation in reply['citations']:
   label=citation['source_label'];source=get(f"/api/sessions/{sid}/messages/{reply['id']}/sources/{label}");(root/(name+'-source-'+label+'.json')).write_text(json.dumps(source,indent=2))
   assert all(source['original_text'][s['char_start']-source['metadata']['char_start']:s['char_end']-source['metadata']['char_start']]==s['text'] for s in source['quote_spans'])
   sources.append({'label':label,'chunk_id':source['chunk_id'],'source_hash':source['metadata']['source_hash'],'exact_spans':True})
 record={'name':name,'question':question,'run_id':run['id'],'status':run['status'],'output_status':(run.get('output') or {}).get('status'),'message_id':run['assistant_message_id'],'context_message_ids':run['context_message_ids'],'seconds':time.monotonic()-t,'sources':sources,'error_code':run['error_code']};report['answers'].append(record);save();print(json.dumps(record),flush=True)
message=next((v['message_id'] for v in reversed(report['answers']) if v['message_id']),None)
if message:
 for kind in ['markdown','html']:
  artifact=post(f'/api/sessions/{sid}/artifacts',{'message_id':message,'format':kind});again=get(f"/api/sessions/{sid}/artifacts/{artifact['id']}");assert again==artifact;(root/(kind+'-artifact.json')).write_text(json.dumps(artifact,indent=2));report['artifacts'].append({'id':artifact['id'],'type':kind,'sha256':hashlib.sha256(artifact['content'].encode()).hexdigest()});save()
topic='Use must-have customer feedback to improve onboarding and speed to value for a new growth PM.'
t=time.monotonic();raw=call(f'/api/sessions/{sid}/essays',{'topic':topic,'audience':'A new growth product manager','constraints':'Keep factual quotes in context. Applications are advice with benefits framed as hypotheses.','client_message_id':str(uuid4()),'source_path':'episodes/sean-ellis/transcript.md','focus_questions':[],'timeout_seconds':600,'use_session_context':True},timeout=630);(root/'essay-stream.ndjson').write_bytes(raw);events=[json.loads(v) for v in raw.decode().splitlines()];essay=get(f"/api/sessions/{sid}/essays/{events[0]['run_id']}");(root/'essay-raw.json').write_text(json.dumps(essay,indent=2));(root/'essay-raw.md').write_text(essay.get('draft_md') or '');sources=get(f"/api/sessions/{sid}/essays/{essay['id']}/sources");(root/'essay-sources.json').write_text(json.dumps(sources,indent=2));report['essay']={'id':essay['id'],'status':essay['status'],'error_code':essay['error_code'],'seconds':time.monotonic()-t,'validation':essay.get('validation'),'manual_edits':0,'accepted':False,'review':'pending;do not infer quality from deterministic validation'};save();(root/'before-restart.json').write_text(json.dumps(snapshot(report),indent=2));print(json.dumps({'essay':report['essay'],'artifacts':report['artifacts'],'automatic_acceptance':False}),flush=True)
