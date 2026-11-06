"""Verify saved corrected essay sources match the running image before the one live run."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import httpx

paths=['backend/app/agent.py','backend/app/essays.py','backend/app/writing.py','backend/app/main.py','backend/app/conversation.py','backend/app/schema.py','backend/migrations/versions/0004_essays.py','backend/contract_check.py','backend/tests/test_writing.py','backend/tests/test_writing_rpc.py','backend/tests/test_essays_db.py','agent/essay.ts','agent/conversation_policy.ts','agent/skills/ship30/SKILL.md','agent/skills/ship30/config.json','agent/package-lock.json','backend/requirements.lock']
hashes={p:sha256(Path(p).read_bytes()).hexdigest() for p in paths}
code="from pathlib import Path; from hashlib import sha256; import json,sys; print(json.dumps({p:sha256(Path(p).read_bytes()).hexdigest() for p in json.loads(sys.argv[1])}))"
result=subprocess.run([sys.executable,'scripts/docker.py','compose','exec','-T','api','python','-c',code,json.dumps(paths)],capture_output=True,text=True,check=True,timeout=20)
inside=json.loads(result.stdout);mismatches=[p for p in hashes if inside[p]!=hashes[p]]
with httpx.Client(base_url='http://127.0.0.1:8000',timeout=20,trust_env=False) as c:
    ready=c.get('/api/health/ready');ready.raise_for_status();health=ready.json()
report={'captured_at':datetime.now(timezone.utc).isoformat(),'git_repository':Path('.git').exists(),'host_source_hashes':hashes,'runtime_mismatches':mismatches,'readiness':health,'passed':not mismatches and health['checks']['database']['schema_revision']=='0004_essays' and health['checks']['corpus']['active_episodes']==9 and health['checks']['ollama']['reachable_from_api'],'limits':'Source identity and dependency readiness only; no essay-quality inference.'}
Path('docs/agent-transcripts/phase-06/pre-run-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'runtime_mismatches':mismatches,'source_files_verified':len(hashes),'readiness':health}))
if not report['passed']:raise SystemExit(1)
