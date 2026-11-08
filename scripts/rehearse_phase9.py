"""Safe warm bootstrap rehearsal: preserves env, normal DB and volumes."""
from pathlib import Path
import hashlib,json,subprocess,time,sys
from datetime import datetime,timezone
import httpx
root=Path('docs/agent-transcripts/phase-09');started=time.monotonic()
before=hashlib.sha256(Path('.env').read_bytes()).hexdigest()
with httpx.Client(timeout=10,trust_env=False) as client:
    baseline=client.get('http://127.0.0.1:8080/api/ingestion/status').json()
subprocess.run([sys.executable,'scripts/bootstrap.py'],check=True)
with httpx.Client(timeout=10,trust_env=False) as client:
    for attempt in range(40):
        try:
            r=client.get('http://127.0.0.1:8080/api/health/ready')
            if r.status_code==200:break
        except httpx.HTTPError:pass
        time.sleep(.5)
    else:raise SystemExit('Readiness did not recover after bootstrap; preserve services/data')
    after=client.get('http://127.0.0.1:8080/api/ingestion/status').json();provider=client.get('http://127.0.0.1:8080/api/providers').json()
    assert before==hashlib.sha256(Path('.env').read_bytes()).hexdigest()
    assert baseline['active_episodes']==after['active_episodes'] and baseline['active_chunks']==after['active_chunks']
    assert provider['selected']=='ollama'
    record={'captured_at':datetime.now(timezone.utc).isoformat(),'command':'python3 scripts/bootstrap.py','elapsed_seconds':time.monotonic()-started,'environment_file_unchanged':True,'normal_corpus_unchanged':{'episodes':after['active_episodes'],'chunks':after['active_chunks']},'ready_http':r.status_code,'checks':r.json()['checks'],'provider':provider,'rehearsal_scope':'warm existing local tree and prerequisites; not fresh checkout, model download, full ingestion or Linux validation'}
    (root/'bootstrap.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
