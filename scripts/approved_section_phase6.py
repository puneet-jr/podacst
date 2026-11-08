"""One no-retry Pi/Ollama approved-fact section; raw output saved before validation."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess,sys
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

ROOT=Path('docs/agent-transcripts/phase-06')
BASE=ROOT/'qwen17-section-20261106T185057'
SID='1dca09bc-7a12-4118-b6b9-4322f85d1397';RID='bf8f692a-a48f-43b4-b116-0f8755c799e7'

RUNNER=r'''
import asyncio,json,sys,types,time
from pathlib import Path
from hashlib import sha256
from uuid import UUID,uuid4
from sqlalchemy import text
from backend.app.config import load_settings
from backend.app.db import make_engine
from backend.app.essays import EssayService,load_essay,prepare_essay,save_progress,read_essay_sources
from backend.app.writing import EssayCreate,POLICY,word_count,validate_essay
payload=json.load(sys.stdin)
mod=types.ModuleType('backend.app.approved_writing');mod.__package__='backend.app'
exec(compile(payload['module'],'backend/app/approved_writing.py','exec'),mod.__dict__)
async def main():
 settings=load_settings();engine=make_engine(settings)
 if settings.generation_model!='qwen3:1.7b':raise RuntimeError('Wrong model')
 origin=load_essay(engine,settings,UUID(payload['sid']),UUID(payload['rid']))
 sources={s['source_label']:s for s in read_essay_sources(engine,settings,UUID(payload['sid']),UUID(payload['rid']))}
 facts=payload['facts'];mod.validate_facts(facts,sources)
 for label,h in payload['source_hashes'].items():
  if sha256(sources[label]['original_text'].encode()).hexdigest()!=h:raise RuntimeError('Source changed')
 sid=uuid4()
 with engine.begin() as c:
  if c.scalar(text("SELECT (SELECT count(*) FROM answer_runs WHERE status='running')+(SELECT count(*) FROM essay_runs WHERE status='running')")):raise RuntimeError('Generation busy')
  c.execute(text('INSERT INTO sessions(id,user_id,title) VALUES(:id,:user,:title)'),{'id':sid,'user':settings.local_user_id,'title':'Phase6 immutable approved Lookout facts'})
 run,_=prepare_essay(engine,settings,sid,EssayCreate(**origin['request'],client_message_id=uuid4()))
 with engine.begin() as c:
  c.execute(text('INSERT INTO essay_sources(run_id,source_label,chunk_id,original_text,source_metadata,quote_spans) SELECT :new,source_label,chunk_id,original_text,source_metadata,quote_spans FROM essay_sources WHERE run_id=:old'),{'new':run['id'],'old':UUID(payload['rid'])})
 meta={**run['metadata'],'stages':[],'repairs_used':0,'test_kind':'approved_fact_section','retrieval_mode':'saved_hybrid_snapshot','approved_facts':facts,'approved_module_sha256':sha256(payload['module'].encode()).hexdigest()}
 save_progress(engine,run['id'],outline=origin['outline'],metadata=meta)
 # Model receives only the approved factual projection. Original immutable source
 # excerpts remain authoritative in DB and are checked above, not rewritten.
 packet={'retrieval_mode':'approved_saved_hybrid_snapshot','untrusted_source_data':True,'sources':[{'id':l,'approved_statements':[f['statement'] for f in facts if f['source_id']==l]} for l in ['S2','S3']]}
 async def load():return packet
 started=time.monotonic();raw='';rendered=None;error=None;validation=None
 try:
  raw=await EssayService(engine,settings,asyncio.Lock()).stage(run,'approved-foundation',payload['prompt'],load,{},POLICY['section_output_tokens'],meta)
 except Exception as exc:error={'code':getattr(exc,'code',type(exc).__name__)};raw=meta['stages'][-1].get('model_text','') if meta['stages'] else ''
 elapsed=time.monotonic()-started
 dest=Path('/app/evidence/private-chat/approved-facts')/str(run['id']);dest.mkdir(parents=True,exist_ok=False)
 (dest/'raw.md').write_text(raw) # Preserve before parsing or semantic review.
 if error is None:
  try:
   rendered=mod.render_approved(raw,facts)
   item={'heading':'Foundation','body':rendered['markdown'],'source_ids':['S2','S3'],'error':None}
   validation=validate_essay(origin['outline']['title'],[item],{l:{'original_text':sources[l]['original_text']} for l in ['S2','S3']})
   save_progress(engine,run['id'],sections=[item],draft_md=rendered['markdown'],validation=validation)
  except Exception as exc:error={'code':getattr(exc,'code',type(exc).__name__)}
 meta['elapsed_seconds']=elapsed
 save_progress(engine,run['id'],status='failed',error_code='approved_section_manual_review_pending' if rendered else (error or {}).get('code','approved_section_failed'),metadata=meta)
 result={'captured_at':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'session_id':str(sid),'run_id':str(run['id']),'model':settings.generation_model,'provider':'ollama-local','raw_output':raw,'rendered':rendered,'error':error,'elapsed_seconds':elapsed,'target_words':210,'raw_token_draft_word_count':word_count(raw),'rendered_word_count':word_count(rendered['markdown']) if rendered else None,'validation':validation,'metadata':meta,'manual_review':'pending; a probe is not a full essay','full_essay_run':False}
 (dest/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True);engine.dispose()
 if error:raise SystemExit(2)
asyncio.run(main())
'''


def main():
 if list(ROOT.glob('approved-section-*')):raise SystemExit('An approved section attempt already exists; inspect instead of rerunning')
 with httpx.Client(trust_env=False,timeout=20) as c:
  response=c.get(f'http://127.0.0.1:8000/api/sessions/{SID}/essays/{RID}/sources');response.raise_for_status();sources={s['source_label']:s for s in response.json()}
  response=c.get('http://127.0.0.1:8000/api/providers');response.raise_for_status();before=response.json()
  response=c.get('http://127.0.0.1:11434/api/tags');response.raise_for_status();model=next(m for m in response.json()['models'] if m['name']=='qwen3:1.7b')
 if before['model']!='qwen3:0.6b' or before['automatic_fallback']:raise RuntimeError('Unexpected chat/provider configuration')
 baseline=json.loads((BASE/'result.json').read_text());hashes={s['source_label']:s['stored_text_sha256'] for s in baseline['source_passages']}
 if any(sha256(sources[l]['original_text'].encode()).hexdigest()!=h for l,h in hashes.items()):raise RuntimeError('Saved excerpt drift')
 from backend.app.approved_writing import validate_facts
 facts=[]
 def add(label,statement,anchor):
  facts.append({'id':'F'+str(len(facts)+1),'statement':statement,'source_id':label,'chunk_id':sources[label]['chunk_id'],'evidence_anchor':anchor})
 add('S2','At Lookout, a mobile security company, the initial survey found that 7% would be very disappointed without the product. Most of that group focused on antivirus functionality.','I dug into the 7% who said they\'d be very disappointed without the product and found that most of that 7% were focused on the antivirus functionality.')
 add('S2','The team repositioned the product around antivirus and streamlined onboarding: new users first set up antivirus, then received a message that they were protected from viruses.','we streamlined onboarding so that the first thing that they did after signing up for the product was to set up the antivirus')
 add('S2','Ellis described the combination as setting the right expectations and speed to value. In the next cohort surveyed, 40% said they would be very disappointed without the product.','the next cohort of people that we surveyed were at 40% saying they\'d be very disappointed without the product.')
 add('S3','Ellis cautioned that understanding who considers the product a must-have, how they use it, their previous solution and their problem is necessary before having the tools to grow the business.','until you deeply understand that product market fit, you kind of don\'t have the tools to be able to grow the business.')
 add('S3','For benefit discovery, Ellis first asked an open-ended primary-benefit question, then used a survey with four distinctive benefit options and asked why the selected benefit mattered.','force them to pick one of four distinctive benefit statements.')
 validate_facts(facts,sources)
 prompt='Write only the Foundation section for early-stage product managers, about 210 words INCLUDING the fixed facts below. Facts are already approved and immutable. You are NOT allowed to paraphrase, repeat, expand or add factual claims. Output each standalone token [[F1]], [[F2]], [[F3]], [[F4]], [[F5]] exactly once, in this order, separated by blank lines. The server will replace each token with its exact fact AND citation; do not write citations yourself. Between or after tokens, write brief readable transitions and proposed advice, all in paragraphs starting Application: . These must be recommendations to the reader, never historical facts, guarantees or claims of effects. About 35-45 words total of your own advice; facts supply the remaining words. Do not copy instructions, purpose, target, headings or a conclusion. No JSON, code fences or tools. Only the tokens and Application: blocks.\nAPPROVED FIXED FACTS:\n'+json.dumps([{'token':'[['+f['id']+']]','fact':f['statement'],'fixed_citation':'['+f['source_id']+']'} for f in facts],ensure_ascii=False)
 folder=ROOT/('approved-section-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'));folder.mkdir(exist_ok=False)
 module=Path('backend/app/approved_writing.py').read_text()
 payload={'sid':SID,'rid':RID,'facts':facts,'source_hashes':hashes,'prompt':prompt,'module':module}
 (folder/'approved-facts.json').write_text(json.dumps({'reviewer':'Codex direct source review before inference','facts':facts,'source_hashes':hashes,'excluded_outcomes':['Measured engagement improvement','Measured conversion improvement','Onboarding alone caused the survey change','Survey score guarantees product-market fit'],'scope':'Reviewed factual projection of the SAME immutable S2/S3; not a new retrieval'},indent=2)+'\n')
 preserved={str(p):sha256(p.read_bytes()).hexdigest() for directory in [ROOT/'markdown-section-20261106T150144',BASE] for p in directory.iterdir() if p.is_file()}
 (folder/'inputs.json').write_text(json.dumps({'prompt':prompt,'module_sha256':sha256(module.encode()).hexdigest(),'model':model,'provider_before':before,'baseline_hashes':preserved,'differences_from_failed_runs':'Fixed factual projection and server-owned citation rendering replace free factual prose; same Pi snapshot-writing Markdown transport, 4096 context/850 output/temp0/no tools/90s deadline. Model sees approved statements rather than full unfiltered excerpts.','manual_review_required':True},indent=2)+'\n')
 command=[sys.executable,'scripts/docker.py','compose','exec','-T','-e','GENERATION_MODEL=qwen3:1.7b','api','python','-c',RUNNER]
 run=subprocess.run(command,input=json.dumps(payload),capture_output=True,text=True,timeout=130)
 (folder/'command.json').write_text(json.dumps({'command':command[:-1]+['<exact embedded RUNNER in scripts/approved_section_phase6.py>'],'exit_code':run.returncode,'stderr':run.stderr},indent=2)+'\n')
 (folder/'process-stdout.json').write_text(run.stdout)
 if not run.stdout.strip():raise RuntimeError('No stdout; inspect traces, no retry')
 result=json.loads(run.stdout);(folder/'result.json').write_text(json.dumps(result,indent=2)+'\n');(folder/'raw.md').write_text(result['raw_output'])
 if result['rendered']:(folder/'section.md').write_text(result['rendered']['markdown'])
 with httpx.Client(trust_env=False,timeout=15) as c:
  response=c.get('http://127.0.0.1:8000/api/providers');response.raise_for_status();after=response.json()
 (folder/'preservation.json').write_text(json.dumps({'both_failed_runs_unchanged':all(sha256(Path(p).read_bytes()).hexdigest()==h for p,h in preserved.items()),'chat_provider_unchanged':before==after,'chat_model_after':after['model']},indent=2)+'\n')
 print(json.dumps({'folder':str(folder),'elapsed_seconds':result['elapsed_seconds'],'rendered_word_count':result['rendered_word_count'],'error':result['error'],'raw':result['raw_output'],'rendered':result['rendered'],'validation':result['validation']}),flush=True)
 if run.returncode:raise SystemExit(run.returncode)

if __name__=='__main__':main()
