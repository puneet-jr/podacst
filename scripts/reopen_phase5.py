"""Reopen an actual saved local answer/citation after a separately captured API restart."""
from hashlib import sha256
import json
from pathlib import Path
import httpx

folder=sorted(Path('docs/agent-transcripts/phase-05').glob('lifecycle-*/restart-before.json'))[-1].parent
before=json.loads((folder/'restart-before.json').read_text());sid=before['session_id']
with httpx.Client(base_url='http://127.0.0.1:8000',trust_env=False,timeout=20) as c:
    ready=c.get('/api/health/ready');ready.raise_for_status()
    response=c.get(f'/api/sessions/{sid}/messages');response.raise_for_status();messages=response.json()
    saved=c.get(f"/api/sessions/{sid}/runs/{before['run_id']}");saved.raise_for_status()
    source=before['source'];mid=saved.json()['assistant_message_id'];label=source['source_label']
    response=c.get(f'/api/sessions/{sid}/messages/{mid}/sources/{label}');response.raise_for_status();after=response.json()
    missing=c.get(f'/api/sessions/{sid}/messages/{mid}/sources/S999')
    other=c.post('/api/sessions',json={'title':'Phase 5 source ownership check'});other.raise_for_status();other_id=other.json()['id']
    cross=c.get(f'/api/sessions/{other_id}/messages/{mid}/sources/{label}')
    run=c.get(f"/api/sessions/{sid}/runs/{before['run_id']}").json()
    proof={'name':'actual_restart_reopen_and_source_ownership','session_id':sid,'run_id':run['id'],'messages_identical':messages==before['messages'],'source_snapshot_identical':after==source,'completed_status_preserved':run['status']=='completed','unknown_source_status':missing.status_code,'cross_session_source_status':cross.status_code,'ready':ready.json(),'message_count':len(messages),'message_snapshot_sha256':sha256(json.dumps(messages,sort_keys=True).encode()).hexdigest()}
    proof['passed']=all(proof[k] for k in ('messages_identical','source_snapshot_identical','completed_status_preserved')) and missing.status_code==404 and cross.status_code==404
    (folder/'restart-after.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
    if not proof['passed']:raise SystemExit(1)
