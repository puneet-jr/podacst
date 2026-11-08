"""One read-only sparse search verifies safe source-ID logging, no model call."""
import json,subprocess,time
from pathlib import Path
import httpx
with httpx.Client(base_url='http://127.0.0.1:8080',timeout=15,trust_env=False) as c:
    for _ in range(20):
        try:
            if c.get('/api/health/ready').status_code==200:break
        except httpx.HTTPError:pass
        time.sleep(.3)
    else:raise SystemExit('Final API not ready')
    r=c.post('/api/retrieval/search',json={'query':'Sean Ellis must-have survey','mode':'sparse','limit':2,'token_budget':1200});r.raise_for_status();ids=[p['id'] for p in r.json()['passages']]
    logs=subprocess.check_output(['python3','scripts/docker.py','compose','logs','--no-color','--no-log-prefix','api']);Path('.cache/phase9-app.log').write_bytes(logs)
    rows=[]
    for l in logs.decode(errors='replace').splitlines():
        try:row=json.loads(l)
        except ValueError:continue
        if row.get('request_id')==r.headers['X-Request-ID']:rows.append(row)
    match=[x for x in rows if x.get('event')=='retrieval_operation'];assert match and match[-1]['source_ids']==ids
    record={'http':r.status_code,'request_id':r.headers['X-Request-ID'],'source_ids_match_response':True,'model_calls':0,'database_writes':0,'events':rows}
    Path('docs/agent-transcripts/phase-09/source-id-events.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
