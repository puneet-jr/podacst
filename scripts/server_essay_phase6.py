"""One full topic-specific server-fact essay, with at most one bounded revision."""
import json,sys,subprocess
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
ROOT=Path('docs/agent-transcripts/phase-06')
RUNNER=r'''
import json,sys,asyncio,time,types,re
from pathlib import Path
from uuid import UUID,uuid4
from hashlib import sha256
from sqlalchemy import text
from backend.app.config import load_settings
from backend.app.db import make_engine
from backend.app.agent import PiRPC
from backend.app.essays import prepare_essay,collect_evidence,load_essay,save_progress,read_essay_sources
from backend.app.writing import EssayCreate,word_count,validate_essay,assemble
p=json.load(sys.stdin);settings=load_settings();engine=make_engine(settings)
if settings.generation_model!='qwen3:1.7b':raise RuntimeError('wrong model')
async def main():
 mode=p['mode']
 if mode=='prepare':
  origin=load_essay(engine,settings,UUID('1dca09bc-7a12-4118-b6b9-4322f85d1397'),UUID('bf8f692a-a48f-43b4-b116-0f8755c799e7'))
  sid=uuid4()
  with engine.begin() as c:
   if c.scalar(text("SELECT (SELECT count(*) FROM answer_runs WHERE status='running')+(SELECT count(*) FROM essay_runs WHERE status='running')")):raise RuntimeError('busy')
   c.execute(text('INSERT INTO sessions(id,user_id,title) VALUES(:id,:user,:title)'),{'id':sid,'user':settings.local_user_id,'title':'Phase6 complete server-owned cited essay'})
  run,_=prepare_essay(engine,settings,sid,EssayCreate(**origin['request'],client_message_id=uuid4()))
  started=time.monotonic()
  try:sources,packet,receipts=collect_evidence(engine,settings,run)
  except BaseException:
   save_progress(engine,run['id'],status='failed',error_code='essay_retrieval_failed');raise
  meta={**run['metadata'],'workflow':'reviewed_server_facts_pi_advice','retrieval_mode':'hybrid','retrievals':receipts,'retrieval_seconds':time.monotonic()-started,'stages':[],'repairs_used':0,'source_review':'pending human-style approval; not automatic entailment'}
  save_progress(engine,run['id'],metadata=meta)
  print(json.dumps({'session_id':str(sid),'run_id':str(run['id']),'request':run['request'],'metadata':meta,'sources':[{'source_label':l,'chunk_id':s['id'],'source_hash':sha256(s['original_text'].encode()).hexdigest(),'source_metadata':{k:v for k,v in s.items() if k!='original_text'}} for l,s in sources.items()]}));return
 sid,rid=UUID(p['session_id']),UUID(p['run_id']);run=load_essay(engine,settings,sid,rid)
 sources={s['source_label']:s for s in read_essay_sources(engine,settings,sid,rid)}
 m=types.ModuleType('backend.app.approved_writing');exec(compile(p['module'],'backend/app/approved_writing.py','exec'),m.__dict__)
 plan=p['plan'];meta=run['metadata'];sections=run['sections'] or [];stages=meta['stages'];dest=Path('/app/evidence/private-chat/server-essays')/str(rid);dest.mkdir(parents=True,exist_ok=True)
 for s in plan['sections']:m.validate_facts(s['facts'],sources)
 for label,h in plan['source_hashes'].items():
  if sha256(sources[label]['original_text'].encode()).hexdigest()!=h:raise RuntimeError('Source drift')
 extension=dest/'application_advice.ts';extension.write_text(p['extension'])
 indexes=range(6) if mode=='draft' else [p['section_index']]
 if mode=='draft' and stages:raise RuntimeError('draft already attempted')
 if mode=='expand':
  if meta.get('repairs_used',0)>=1:raise RuntimeError('bounded revision already used')
  meta['repairs_used']=1;meta['pre_revision_sections']=sections
 started=time.monotonic()
 try:
  async with asyncio.timeout(600):
   for i in indexes:
    s=plan['sections'][i];name=('application-' if mode=='draft' else 'expanded-')+str(i+1)
    rpc=PiRPC(dest/name,tool_name='',extension=extension,system='Write proposed application advice only.',max_tokens=384,require_tool=False,extra_env={'LENNY_ADVICE_OUTPUT_TOKENS':'384'})
    stage={'stage':name,'section':i+1,'prompt':s['prompt'] if mode=='draft' else p['revision_prompt']};stages.append(stage);t=time.monotonic();raw='';response={}
    try:
     async with asyncio.timeout(90):
      state=await rpc.start();stage['initial_message_count']=state.get('messageCount');response=await rpc.ask(stage['prompt']);raw=response['model_text']
    finally:
     await rpc.close();stage.update(seconds=time.monotonic()-t,process_reaped=rpc.process.returncode is not None if rpc.process else True,pi_session_id=rpc.session_id)
    (dest/(name+'.md')).write_text(raw);stage['model_text']=raw
    last=next((v for v in reversed(response.get('messages',[])) if v.get('role')=='assistant'),{})
    stage.update(usage={k:v for k,v in last.get('usage',{}).items() if k!='cost'},stop_reason=last.get('stopReason'))
    # Full essay length is the gate; individual advice counts are targets.
    if not raw.strip() or re.search(r'[\[\]<>`#*]|https?://|\b(?:Application|Purpose|Target):',raw,re.I):raise RuntimeError('advice_format_invalid')
    if re.search(r'\b(?:Lookout|Ellis|Xobni|guarantee\w*|ensur\w*)\b',raw,re.I):stage['manual_attention']='history/outcome keyword; review required'
    factual='\n\n'.join(f['statement']+' ['+f['source_id']+']' for f in s['facts'])
    # Server owns labels and optional line layout; retain actual raw advice.
    if i==5:
     sentences=re.split(r'(?<=[.!?])\s+',raw.strip());advice='\n'.join('- Application: '+v for v in sentences if v)
    else:advice='Application: '+raw.strip()
    if i==2:advice='Application: **Test a hypothesis, not a promise.** '+raw.strip()
    item={'heading':s['heading'],'body':factual+'\n\n'+advice,'source_ids':sorted({f['source_id'] for f in s['facts']}),'error':None}
    if mode=='draft':sections.append(item)
    else:sections[i]=item
    save_progress(engine,rid,sections=sections,draft_md=assemble(plan['title'],sections),metadata=meta)
  validation=validate_essay(plan['title'],sections,{l:{'original_text':v['original_text']} for l,v in sources.items()})
  save_progress(engine,rid,status='needs_review' if validation['passed_deterministic'] else 'failed',error_code=None if validation['passed_deterministic'] else 'essay_rubric_failed',outline={'status':'ready','title':plan['title'],'sections':[{'heading':s['heading'],'purpose':s['purpose'],'source_ids':sorted({f['source_id'] for f in s['facts']})} for s in plan['sections']]},validation=validation,metadata=meta)
 except BaseException as e:
  meta['failure_type']=type(e).__name__;save_progress(engine,rid,status='failed',error_code='full_essay_draft_failed',metadata=meta)
  raise
 finally:meta.setdefault('drafting_durations',[]).append(time.monotonic()-started);save_progress(engine,rid,metadata=meta)
 final=load_essay(engine,settings,sid,rid)
 print(json.dumps({'session_id':str(sid),'run_id':str(rid),'run':{k:v for k,v in final.items() if k in ['status','error_code','outline','sections','draft_md','validation','metadata']}},default=str))
asyncio.run(main());engine.dispose()
'''
def main():
 mode=sys.argv[1]
 if mode=='prepare':
  if list(ROOT.glob('server-essay-*')):raise SystemExit('Full essay exists; inspect instead of creating a duplicate')
  folder=ROOT/('server-essay-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'));folder.mkdir()
  payload={'mode':mode}
 else:
  folder=next(ROOT.glob('server-essay-*'));prepared=json.loads((folder/'prepare.json').read_text());payload={'mode':mode,'session_id':prepared['session_id'],'run_id':prepared['run_id'],'plan':json.loads((folder/'plan.json').read_text()),'module':Path('backend/app/approved_writing.py').read_text(),'extension':Path('agent/application_advice.ts').read_text()}
  if mode=='expand':payload.update(json.loads((folder/'revision-request.json').read_text()))
 if (folder/(mode+'.json')).exists():raise SystemExit('Stage already captured; do not rerun')
 cmd=[sys.executable,'scripts/docker.py','compose','exec','-T','-e','GENERATION_MODEL=qwen3:1.7b','api','python','-c',RUNNER]
 result=subprocess.run(cmd,input=json.dumps(payload),capture_output=True,text=True,timeout=650)
 (folder/(mode+'-command.json')).write_text(json.dumps({'command':cmd[:-1]+['<RUNNER in scripts/server_essay_phase6.py>'],'exit_code':result.returncode,'stderr':result.stderr},indent=2)+'\n')
 (folder/(mode+'-stdout.json')).write_text(result.stdout)
 if not result.stdout.strip():raise SystemExit('No stdout; inspect preserved trace; no blind retry')
 data=json.loads(result.stdout);(folder/(mode+'.json')).write_text(json.dumps(data,indent=2)+'\n')
 if mode!='prepare':(folder/(mode+'.md')).write_text(data['run']['draft_md'] or '')
 print(json.dumps({'folder':str(folder),**data} if mode=='prepare' else {'folder':str(folder),'status':data['run']['status'],'validation':data['run']['validation'],'stages':[{'stage':s['stage'],'seconds':s['seconds']} for s in data['run']['metadata']['stages']]}),flush=True)
 if result.returncode:raise SystemExit(result.returncode)
if __name__=='__main__':main()
