"""Frozen local release journeys and reviewed answer sample. No silent retries.

Raw answers/passages stay in ignored .cache/phase10. Scenario scores require
separate direct semantic/artifact review; transport success never implies pass.
"""
import argparse,json,time,hashlib
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4
import httpx
ROOT=Path('.cache/phase10/live');ROOT.mkdir(parents=True,exist_ok=True)
BASE='http://127.0.0.1:8080'
def now():return datetime.now(timezone.utc).isoformat()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
class Live:
 def __init__(self,folder):
  self.folder=ROOT/folder;self.folder.mkdir(exist_ok=False);self.client=httpx.Client(base_url=BASE,timeout=105,trust_env=False);self.record={'started_at':now(),'fixture':False,'session_ids':[],'answers':[],'artifacts':[],'errors':[],'manual_review':'pending','score':'pending'};self.save()
  r=self.client.get('/api/health/ready');(self.folder/'preflight.json').write_text(json.dumps({'status':r.status_code,'body':r.json()},indent=2));r.raise_for_status();provider=self.client.get('/api/providers').json();assert provider['selected']=='ollama' and not provider['automatic_fallback'];assert r.json()['checks']['corpus']['ready'];self.record['preflight']={'provider':provider['selected'],'model':provider['model'],'essay_model':provider['essay_model'],'checks':r.json()['checks']};self.save()
 def save(self): (self.folder/'run.json').write_text(json.dumps(self.record,indent=2,default=str)+'\n')
 def create(self,title):
  r=self.client.post('/api/sessions',json={'title':'Phase10 '+title});r.raise_for_status();sid=r.json()['id'];self.record['session_ids'].append(sid);self.save();return sid
 def ask(self,sid,question,scope=None,name='question'):
  body={'content':question,'source_path':scope,'client_message_id':str(uuid4()),'retrieval_mode':'hybrid','timeout_seconds':90};t=time.monotonic();stamp=now();r=self.client.post(f'/api/sessions/{sid}/answers',json=body);elapsed=time.monotonic()-t;path=self.folder/(name+'-stream.ndjson');path.write_bytes(r.content);r.raise_for_status();events=[json.loads(v) for v in r.text.splitlines() if v.strip()];rid=events[0]['run_id'];saved=self.client.get(f'/api/sessions/{sid}/runs/{rid}');saved.raise_for_status();run=saved.json();(self.folder/(name+'-run.json')).write_text(json.dumps(run,indent=2));messages=self.client.get(f'/api/sessions/{sid}/messages').json();reply=next((m for m in messages if m['id']==run.get('assistant_message_id')),None)
  if reply:(self.folder/(name+'-reply.json')).write_text(json.dumps(reply,indent=2))
  record={'name':name,'started_at':stamp,'session_id':sid,'question':question,'source_scope':scope,'run_id':rid,'request_seconds':elapsed,'status':run['status'],'output_status':(run.get('output') or {}).get('status'),'answer':reply['content'] if reply else None,'message_id':reply['id'] if reply else None,'source_ids':[],'context_message_ids':run['context_message_ids'],'user_message_id':run['user_message_id'],'resolved_query':run['resolved_query'],'retrieval_mode':run['retrieval_mode'],'error_code':run['error_code'],'provider':run['metadata'].get('provider'),'model':run['metadata'].get('model'),'process_reaped':run['metadata'].get('process_reaped'),'bridge_closed':run['metadata'].get('bridge_closed'),'retrieval_timings':run['metadata'].get('retrieval_timings_ms'),'manual_support':'pending'}
  for cite in reply.get('citations',[]) if reply else []:
   response=self.client.get(f"/api/sessions/{sid}/messages/{reply['id']}/sources/{cite['source_label']}");response.raise_for_status();source=response.json();(self.folder/(name+'-source-'+cite['source_label']+'.json')).write_text(json.dumps(source,indent=2));exact=all(source['original_text'][s['char_start']-source['metadata']['char_start']:s['char_end']-source['metadata']['char_start']]==s['text'] for s in source['quote_spans']);assert exact
   record['source_ids'].append({'label':cite['source_label'],'chunk_id':source['chunk_id'],'path':source['metadata']['source_path'],'source_hash':source['metadata']['source_hash'],'exact_span':exact})
  self.record['answers'].append(record);self.save();print(json.dumps({k:v for k,v in record.items() if k not in ['answer','resolved_query','question']}),flush=True)
  return record
 def artifact(self,sid,answer,kind):
  if not answer.get('message_id'):return None
  r=self.client.post(f'/api/sessions/{sid}/artifacts',json={'message_id':answer['message_id'],'format':kind});r.raise_for_status();a=r.json();(self.folder/(str(a['id'])+'-artifact.json')).write_text(json.dumps(a,indent=2));again=self.client.get(f"/api/sessions/{sid}/artifacts/{a['id']}");again.raise_for_status();assert again.json()['content']==a['content'];assert not __import__('re').search(r'<script|<form|<iframe',a['preview_html'],__import__('re').I)
  record={'session_id':sid,'id':a['id'],'type':kind,'content_sha256':hashlib.sha256(a['content'].encode()).hexdigest(),'preview_sha256':hashlib.sha256(a['preview_html'].encode()).hexdigest(),'source_labels':a['source_metadata']['citation_ids'],'saved_and_reopened_http':True,'browser_render':'pending','relevant_to_request':'pending'};self.record['artifacts'].append(record);self.save();return record
 def essay(self,sid,case):
  body={'topic':case['question'],'audience':'A new growth product manager','constraints':'Preserve the reported Lookout survey wording and qualifications. Distinguish quoted historical facts from application advice; frame expected benefits as hypotheses.','client_message_id':str(uuid4()),'source_path':case['source_path'],'focus_questions':[],'timeout_seconds':600,'use_session_context':True};t=time.monotonic();r=self.client.post(f'/api/sessions/{sid}/essays',json=body,timeout=630);(self.folder/'essay-stream.ndjson').write_bytes(r.content);r.raise_for_status();events=[json.loads(v) for v in r.text.splitlines() if v.strip()];rid=events[0]['run_id'];response=self.client.get(f'/api/sessions/{sid}/essays/{rid}');response.raise_for_status();e=response.json();(self.folder/'essay-raw.json').write_text(json.dumps(e,indent=2));(self.folder/'essay-raw.md').write_text(e.get('draft_md') or '')
  sources=self.client.get(f'/api/sessions/{sid}/essays/{rid}/sources');sources.raise_for_status();(self.folder/'essay-sources.json').write_text(json.dumps(sources.json(),indent=2));self.record['essay']={'id':rid,'session_id':sid,'request_seconds':time.monotonic()-t,'status':e['status'],'error_code':e['error_code'],'word_count':(e.get('validation') or {}).get('word_count'),'validation':e.get('validation'),'completed_sections':len(e['sections']),'model':e['metadata'].get('model'),'provider':e['metadata'].get('provider'),'manual_edits':0,'review':'pending'};self.save();print(json.dumps(self.record['essay']),flush=True)
 def finish(self,start):self.record.update(ended_at=now(),automated_steps_seconds=time.monotonic()-start);self.save();self.client.close()
def scenarios(selected=None):
 frozen=json.loads(Path('docs/scenario-inputs.json').read_text());caps=json.loads(Path('docs/agent-transcripts/phase-10/scenario-protocol.json').read_text())['caps_seconds']
 for case in frozen['scenarios']:
  if selected and case['id'] not in selected:continue
  name=case['id'];live=Live(name);t=time.monotonic();live.record.update(scenario_id=name,duration_cap=caps[name],input_freeze_sha256=hashlib.sha256(Path('docs/scenario-inputs.json').read_bytes()).hexdigest());live.save()
  try:
   if name=='SC-01-D':
    a=live.create(name+' independent A');first=live.ask(a,case['session_a_question']+'\nSession context marker: '+case['session_a_context_marker'],case['session_a_source'],'session-a');live.artifact(a,first,'markdown');b=live.create(name+' independent B');second=live.ask(b,case['question'],case['source_path'],'session-b');live.artifact(b,second,'html');live.record['isolation']={'distinct_sessions':a!=b,'b_no_prior_context':not second['context_message_ids'],'marker_absent_from_b':case['session_a_context_marker'] not in (second['answer'] or '')+second['resolved_query'],'restart_check':'pending'}
   else:
    sid=live.create(name)
    if name=='SC-01-E':
     first=live.ask(sid,case['question'],None,'unsupported');second=live.ask(sid,case['supported_reformulation'],case['source_path'],'reformulation');live.artifact(sid,second,'markdown')
    elif name=='SC-01-C':
     live.ask(sid,case['question'],case['source_path'],'research');live.essay(sid,case)
    else:
     first=live.ask(sid,case['question'],case['source_path'],'initial')
     if name=='SC-01-B':second=live.ask(sid,case['follow_up'],None,'follow-up');live.artifact(sid,second,'html')
     else:live.artifact(sid,first,'markdown')
  except Exception as e:live.record['errors'].append({'type':type(e).__name__,'message':str(e)[:500]})
  finally:live.finish(t)
def quality(selected=None):
 protocol=json.loads(Path('docs/agent-transcripts/phase-10/quality-sample-protocol.json').read_text())
 supplemental=json.loads(Path('docs/agent-transcripts/phase-10/quality-new-corpus-protocol.json').read_text())['cases']
 for case in protocol['answerable_cases']+supplemental+protocol['unsupported_cases']:
  if selected and case['id'] not in selected:continue
  live=Live('quality-'+case['id']);t=time.monotonic()
  try:
   sid=live.create('quality '+case['id']);question=case.get('resolved_query',case['question']);live.ask(sid,question,case.get('filters',{}).get('source_path'),'answer');live.record['case_id']=case['id'];live.record['original_question']=case['question'];live.record['kind']=case.get('kind','unsupported')
  except Exception as e:live.record['errors'].append({'type':type(e).__name__,'message':str(e)[:500]})
  finally:live.finish(t)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('suite',choices=['scenarios','quality']);parser.add_argument('--scenario',action='append');parser.add_argument('--quality-case',action='append');parser.add_argument('--attempt',default='first',choices=['first','post-fix']);args=parser.parse_args();ROOT=ROOT/args.attempt;ROOT.mkdir(exist_ok=True);scenarios(args.scenario) if args.suite=='scenarios' else quality(args.quality_case)
