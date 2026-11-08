"""One server-assembled fixture section and a single local Pi advice request."""
import json,subprocess,sys
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
ROOT=Path('docs/agent-transcripts/phase-06')
REGISTRY=ROOT/'approved-section-20261106T193354/approved-facts.json'
SID='1dca09bc-7a12-4118-b6b9-4322f85d1397';RID='bf8f692a-a48f-43b4-b116-0f8755c799e7'
ATTEMPT_PREFIX='server-section-'
VALIDATOR='validate_application'
PROMPT='Suggest one concrete action an early-stage product manager could try: compare the promise in their own signup message with the first task in their own onboarding. Write 35-45 words, one plain paragraph, starting with an action verb. Frame it as advice, with no claims of results. Do not discuss any company, research finding or historical case. No heading, label, fact IDs or citation IDs.'
RUNNER=r'''
import asyncio,json,sys,time,types
from pathlib import Path
from uuid import UUID,uuid4
from hashlib import sha256
from sqlalchemy import text
from backend.app.agent import PiRPC
from backend.app.config import load_settings
from backend.app.db import make_engine
from backend.app.essays import load_essay,read_essay_sources,prepare_essay,save_progress
from backend.app.writing import EssayCreate,word_count
p=json.load(sys.stdin);m=types.ModuleType('backend.app.approved_writing');exec(compile(p['module'],'backend/app/approved_writing.py','exec'),m.__dict__)
async def main():
 settings=load_settings();engine=make_engine(settings)
 if settings.generation_model!='qwen3:1.7b':raise RuntimeError('unexpected model')
 origin=load_essay(engine,settings,UUID(p['sid']),UUID(p['rid']))
 sources={s['source_label']:s for s in read_essay_sources(engine,settings,UUID(p['sid']),UUID(p['rid']))}
 m.validate_facts(p['registry']['facts'],sources)
 for label,h in p['registry']['source_hashes'].items():
  if sha256(sources[label]['original_text'].encode()).hexdigest()!=h:raise RuntimeError('source drift')
 sid=uuid4()
 with engine.begin() as c:
  if c.scalar(text("SELECT (SELECT count(*) FROM answer_runs WHERE status='running')+(SELECT count(*) FROM essay_runs WHERE status='running')")):raise RuntimeError('generation busy')
  c.execute(text('INSERT INTO sessions(id,user_id,title) VALUES(:id,:user,:title)'),{'id':sid,'user':settings.local_user_id,'title':'Phase6 server-assembled Lookout section'})
 run,_=prepare_essay(engine,settings,sid,EssayCreate(**origin['request'],client_message_id=uuid4()))
 with engine.begin() as c:
  c.execute(text('INSERT INTO essay_sources(run_id,source_label,chunk_id,original_text,source_metadata,quote_spans) SELECT :new,source_label,chunk_id,original_text,source_metadata,quote_spans FROM essay_sources WHERE run_id=:old'),{'new':run['id'],'old':UUID(p['rid'])})
 dest=Path('/app/evidence/private-chat/server-sections')/str(run['id']);dest.mkdir(parents=True,exist_ok=False)
 extension=dest/'application_advice.ts';extension.write_text(p['extension'])
 rpc=PiRPC(dest/'advice',tool_name='',extension=extension,system='Write only application advice.',max_tokens=256,require_tool=False)
 started=time.monotonic();raw='';result=None;error=None;initial={}
 try:
  async with asyncio.timeout(90):
   initial=await rpc.start();result=await rpc.ask(p['prompt']);raw=result['model_text']
 except Exception as e:error={'code':getattr(e,'code',type(e).__name__)};raw=rpc.last_model_text or ''
 finally:await rpc.close()
 elapsed=time.monotonic()-started;(dest/'model-output.md').write_text(raw)
 # Save the actual assembly even if the advice is rejected; never display or
 # accept this candidate until both syntax and manual support/readability pass.
 facts=p['registry']['facts'];body='\n\n'.join(f['statement']+' ['+f['source_id']+']' for f in facts)+'\n\nApplication: '+raw
 candidate='## Foundation\n\n'+body;(dest/'assembled-section.md').write_text(candidate)
 assembled=None
 if error is None:
  try:assembled=m.assemble_server_section('Foundation',facts,raw,validator=getattr(m,p.get('validator','validate_application')))
  except Exception as e:error={'code':getattr(e,'code',type(e).__name__)}
 diagnostics=[]
 for line in (dest/'advice/stderr.log').read_text().splitlines():
  try:
   d=json.loads(line)
   if d.get('event') in ['provider_request','tool_policy']:diagnostics.append(d)
  except ValueError:pass
 last=next((msg for msg in reversed((result or {}).get('messages',[])) if msg.get('role')=='assistant'),{})
 meta={**run['metadata'],'test_kind':'server_assembled_fixture','retrieval_mode':'saved_hybrid_fixture','initial_message_count':initial.get('messageCount'),'pi_session_id':rpc.session_id,'elapsed_seconds':elapsed,'usage':{k:v for k,v in last.get('usage',{}).items() if k!='cost'},'stop_reason':last.get('stopReason'),'process_reaped':rpc.process.returncode is not None if rpc.process else True,'diagnostics':diagnostics,'provider_request_count':sum(d.get('event')=='provider_request' for d in diagnostics),'approved_facts':facts,'module_sha256':sha256(p['module'].encode()).hexdigest(),'extension_sha256':sha256(p['extension'].encode()).hexdigest()}
 save_progress(engine,run['id'],status='failed',error_code=(error or {}).get('code','section_probe_manual_review_pending'),sections=[{'heading':'Foundation','body':body,'source_ids':['S2','S3'],'error':(error or {}).get('code')}],draft_md=candidate,metadata=meta)
 out={'captured_at':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'run_id':str(run['id']),'session_id':str(sid),'model':'qwen3:1.7b','raw_output':raw,'assembled_section':candidate,'raw_advice_words':word_count(raw),'section_words':word_count(candidate),'target_words':210,'error':error,'assembly':assembled,'metadata':meta,'manual_review':'pending','full_essay_run':False}
 (dest/'result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));engine.dispose()
 if error:raise SystemExit(2)
asyncio.run(main())
'''
def main():
 if list(ROOT.glob(ATTEMPT_PREFIX+'*')):raise SystemExit('One section attempt already exists; inspect instead of rerunning')
 registry=json.loads(REGISTRY.read_text())
 with httpx.Client(trust_env=False,timeout=15) as c:
  r=c.get('http://127.0.0.1:8000/api/providers');r.raise_for_status();before=r.json()
  r=c.get('http://127.0.0.1:11434/api/tags');r.raise_for_status();model=next(m for m in r.json()['models'] if m['name']=='qwen3:1.7b')
 if before['model']!='qwen3:0.6b' or before['automatic_fallback']:raise RuntimeError('Chat config changed')
 folder=ROOT/(ATTEMPT_PREFIX+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'));folder.mkdir(exist_ok=False)
 preserved={str(p):sha256(p.read_bytes()).hexdigest() for pattern in ['markdown-section-*','qwen17-section-*','approved-section-*','server-section-*'] for directory in ROOT.glob(pattern) for p in directory.iterdir() if p.is_file()}
 payload={'sid':SID,'rid':RID,'registry':registry,'prompt':PROMPT,'validator':VALIDATOR,'module':Path('backend/app/approved_writing.py').read_text(),'extension':Path('agent/application_advice.ts').read_text()}
 (folder/'approved-facts.json').write_bytes(REGISTRY.read_bytes())
 (folder/'inputs.json').write_text(json.dumps({'prompt':PROMPT,'model':model,'provider_before':before,'preserved_files':preserved,'module_sha256':sha256(payload['module'].encode()).hexdigest(),'extension_sha256':sha256(payload['extension'].encode()).hexdigest(),'boundaries':'Server renders all facts/citations/headings/labels. Model receives NO factual statements, source IDs, fact tokens or case text. One advice request,256 output/4096 context/temp0/thinking off/no tools/no grammar/90s; no repair.'},indent=2)+'\n')
 cmd=[sys.executable,'scripts/docker.py','compose','exec','-T','-e','GENERATION_MODEL=qwen3:1.7b','api','python','-c',RUNNER]
 run=subprocess.run(cmd,input=json.dumps(payload),capture_output=True,text=True,timeout=125)
 (folder/'command.json').write_text(json.dumps({'command':cmd[:-1]+['<embedded RUNNER in scripts/server_section_phase6.py>'],'exit_code':run.returncode,'stderr':run.stderr},indent=2)+'\n');(folder/'stdout.json').write_text(run.stdout)
 if not run.stdout.strip():raise RuntimeError('No result; inspect trace, no retry')
 result=json.loads(run.stdout);(folder/'result.json').write_text(json.dumps(result,indent=2)+'\n');(folder/'model-output.md').write_text(result['raw_output']);(folder/'assembled-section.md').write_text(result['assembled_section'])
 with httpx.Client(trust_env=False,timeout=15) as c:
  r=c.get('http://127.0.0.1:8000/api/providers');r.raise_for_status();after=r.json()
 (folder/'preservation.json').write_text(json.dumps({'all_prior_runs_unchanged':all(sha256(Path(p).read_bytes()).hexdigest()==h for p,h in preserved.items()),'provider_unchanged':before==after,'chat_model_after':after['model']},indent=2)+'\n')
 print(json.dumps({'folder':str(folder),**result}),flush=True)
 if run.returncode:raise SystemExit(run.returncode)
if __name__=='__main__':main()
