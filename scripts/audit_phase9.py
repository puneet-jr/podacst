"""Secret/path scan; reports locations/counts, never matching values or lines."""
import json,os,re,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
configured=[]
if Path('.env').exists():
 for line in Path('.env').read_text().splitlines():
  if '=' not in line or line.lstrip().startswith('#'):continue
  k,v=line.split('=',1);v=v.strip().strip('\"\'')
  if any(t in k for t in ('PASSWORD','KEY','TOKEN','SECRET')) and len(v)>=12:configured.append(v.encode())
for k in ['OPENROUTER_API_KEY','ANTHROPIC_API_KEY','OPENAI_API_KEY','GH_TOKEN','GITHUB_TOKEN']:
 if len(os.environ.get(k,''))>=12:configured.append(os.environ[k].encode())
patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b',rb'\bgithub_pat_[A-Za-z0-9_]{25,}\b',rb'\bsk-(?:ant-)?[A-Za-z0-9_-]{24,}\b',rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b']
findings=[]
def check(data,location):
 if any(v in data for v in configured) or any(re.search(p,data) for p in patterns):findings.append({'location':location,'kind':'possible_secret'})
if '--logs-only' not in sys.argv:
 rows=subprocess.check_output(['git','rev-list','--objects','--all'],text=True).splitlines();blobs=0
 for row in rows:
  oid,_,path=row.partition(' ')
  if subprocess.check_output(['git','cat-file','-t',oid],text=True).strip()!='blob':continue
  blobs+=1;check(subprocess.check_output(['git','cat-file','blob',oid]),{'blob':oid,'path':path})
 paths=subprocess.check_output(['git','ls-files','-z'],text=False).decode().split('\0');tracked=0
 for name in paths:
  if name and Path(name).is_file():tracked+=1;check(Path(name).read_bytes(),{'working_path':name})
logs=[*Path('docs/agent-transcripts/phase-09').glob('*.jsonl')]
if Path('.cache/phase9-app.log').exists():logs.append(Path('.cache/phase9-app.log'))
for p in logs:check(p.read_bytes(),{'log':str(p)})
if '--logs-only' in sys.argv:
 previous=json.loads(Path('docs/agent-transcripts/phase-09/secret-audit.json').read_text());blobs=previous['all_reachable_git_blobs_scanned'];tracked=previous['tracked_working_files']
record={'captured_at':datetime.now(timezone.utc).isoformat(),'all_reachable_git_blobs_scanned':blobs,'tracked_working_files':tracked,'logs_scanned':[str(p) for p in logs],'configured_values_checked':len(set(configured)),'findings':findings,'passed':not findings,'history_reviewed_at':previous.get('history_reviewed_at',previous['captured_at']) if '--logs-only' in sys.argv else datetime.now(timezone.utc).isoformat(),'review_scope':'New runtime logs plus previous unchanged Git history scan' if '--logs-only' in sys.argv else 'Git history, tracked working files and available logs','limits':'Exact configured-secret/common credential patterns; no values printed. Not universal security proof; private historical raw RPC traces are retained separately and excluded from publication.'}
Path('docs/agent-transcripts/phase-09/secret-audit.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record));raise SystemExit(bool(findings))
