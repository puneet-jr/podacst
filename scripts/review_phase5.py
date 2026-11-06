"""Read-only final proof: preserve old work, actual versions/constraints, safe protocol metadata."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys

BASE=Path('docs/agent-transcripts/phase-05')
baseline=json.loads((BASE/'preservation-baseline.json').read_text())
changed=[p for p,h in baseline['files'].items() if not Path(p).is_file() or sha256(Path(p).read_bytes()).hexdigest()!=h]
def command(args):
    p=subprocess.run(args,capture_output=True,text=True,timeout=40)
    if p.returncode:raise RuntimeError('Probe failed: '+repr(args[:3]))
    return p.stdout.strip()
code=r'''
from backend.app.config import load_settings
from backend.app.db import make_engine
from sqlalchemy import text
from hashlib import sha256
import importlib.metadata as md
import json,os,sys
from pathlib import Path
import httpx
s=load_settings();e=make_engine(s)
with e.connect() as c:
 messages=[tuple(r) for r in c.execute(text('SELECT id,session_id,content,created_at FROM messages WHERE created_at < :cutoff ORDER BY id'),{'cutoff':sys.argv[1]})]
 sessions=[tuple(r) for r in c.execute(text('SELECT id,user_id,title,created_at,updated_at FROM sessions WHERE created_at < :cutoff ORDER BY id'),{'cutoff':sys.argv[1]})]
 valid=c.scalar(text('SELECT bool_and(c.original_text=substring(v.original_text from c.char_start+1 for c.char_end-c.char_start) AND vector_dims(c.embedding)=768) FROM chunks c JOIN episode_versions v ON v.episode_id=c.episode_id AND v.version=c.version WHERE c.active'))
 counts=dict(c.execute(text('SELECT count(DISTINCT episode_id) episodes,count(*) chunks FROM chunks WHERE active')).mappings().one())
 revision=c.scalar(text('SELECT version_num FROM alembic_version'))
old={'message_count':len(messages),'message_digest':sha256(json.dumps(messages,default=str).encode()).hexdigest(),'session_digest':sha256(json.dumps(sessions,default=str).encode()).hexdigest()}
versions={n:md.version(n) for n in ('fastapi','pydantic','SQLAlchemy','alembic','psycopg','pgvector','httpx','starlette','PyYAML')}
versions['python']=sys.version.split()[0];versions['pi']=json.loads(Path('agent/node_modules/@earendil-works/pi-coding-agent/package.json').read_text())['version']
with httpx.Client(base_url=s.ollama_url,trust_env=False,timeout=10) as client:
 tags=client.get('/api/tags');tags.raise_for_status();models=tags.json()['models']
 ps=client.get('/api/ps');ps.raise_for_status()
root=Path('/app/evidence/private-chat');protocols=[]
for f in sorted(root.glob('*/*/stdout.jsonl')):
 raw=f.read_bytes();lines=raw.splitlines();frames=[];bad=0
 for line in lines:
  try:frames.append(json.loads(line))
  except ValueError:bad+=1
 diagnostics=[];stderr=f.with_name('stderr.log')
 for line in stderr.read_text().splitlines() if stderr.exists() else []:
  try:
   d=json.loads(line)
   diagnostics.append({k:v for k,v in d.items() if k in ('event','active','provider','model','request','max_tokens','prompt_bytes','mode','candidates')})
  except ValueError:pass
 protocols.append({'run_id':f.parts[-3],'attempt':f.parts[-2],'stdout_sha256':sha256(raw).hexdigest(),'stdout_bytes':len(raw),'frames':len(frames),'invalid_frames':bad,'ends_lf':raw.endswith(b'\n') if raw else True,'event_types':sorted(set(str(m.get('type')) for m in frames)),'stderr_sha256':sha256(stderr.read_bytes()).hexdigest() if stderr.exists() else None,'diagnostics':diagnostics})
running=[]
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   cmd=(p/'cmdline').read_bytes()
   if b'--mode\x00rpc' in cmd and (b'pi-coding-agent' in cmd or b'/bin/pi' in cmd):running.append(int(p.name))
  except (FileNotFoundError,PermissionError,ProcessLookupError):pass
doc=Path('agent/node_modules/@earendil-works/pi-coding-agent/docs/extensions.md')
print(json.dumps({'prior_conversations':old,'active_counts':counts,'active_originals_vectors_valid':valid,'schema_revision':revision,'versions':versions,'models':[{k:m.get(k) for k in ('name','digest','size','details','remote_model')} for m in models],'loaded_models':ps.json(),'private_trace_directory_mode':oct(root.stat().st_mode & 0o777),'private_trace_directory_uid':root.stat().st_uid,'protocols':protocols,'running_pi_rpc_pids':running,'installed_extension_docs_sha256':sha256(doc.read_bytes()).hexdigest()}))
e.dispose()
'''
inside=json.loads(command([sys.executable,'scripts/docker.py','compose','exec','-T','api','python','-c',code,baseline['captured_at']]))
phase4=json.loads(Path('docs/agent-transcripts/phase-04/live-api.json').read_text())
prior=next(c['detail'] for c in phase4['checks'] if c['name']=='Saved Phase 3 conversations remain identical')
same=all(inside['prior_conversations'][k]==prior[k] for k in ('message_count','message_digest','session_digest'))
private=Path('.cache/phase5-private')
if private.exists():private.chmod(0o700)
report={'captured_at':datetime.now(timezone.utc).isoformat(),'preserved_prior_files':len(baseline['files']),'changed_prior_files':changed,'prior_conversations_identical':same,'container':inside,
 'host':{'sysctl':command(['sysctl','-n','hw.model','hw.memsize','hw.ncpu','machdep.cpu.brand_string']),'swap':command(['sysctl','vm.swapusage']),'memory_pressure_query':command(['memory_pressure','-Q']),'disk_free_bytes':shutil.disk_usage('.').free},
 'docker_stats':command([sys.executable,'scripts/docker.py','stats','--no-stream','--format','{{.Name}} {{.MemUsage}}']),
 'api_image_id':command([sys.executable,'scripts/docker.py','inspect','--format','{{.Image}}','lenny-phase2-api-1']),
 'limits':'Host snapshots, not peak measurement or causal swap attribution; raw RPC is private, hashes/metadata only here.'}
report['passed']=not changed and same and inside['active_counts']=={'episodes':9,'chunks':373} and inside['active_originals_vectors_valid'] and inside['schema_revision']=='0003_conversation' and not inside['running_pi_rpc_pids'] and all(p['invalid_frames']==0 for p in inside['protocols']) and inside['private_trace_directory_mode']=='0o700'
(BASE/'runtime-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='container'},indent=2))
print(json.dumps({'versions':inside['versions'],'active_counts':inside['active_counts'],'prior_conversations':inside['prior_conversations'],'private_protocol_count':len(inside['protocols']),'running_pi_rpc_pids':inside['running_pi_rpc_pids']}))
if not report['passed']:raise SystemExit(1)
