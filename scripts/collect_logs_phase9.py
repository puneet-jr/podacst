"""Collect actual safe API events; full diagnostic output stays private."""
import json,subprocess
from pathlib import Path
raw=subprocess.check_output(['python3','scripts/docker.py','compose','logs','--no-color','--no-log-prefix','api'])
Path('.cache/phase9-app.log').write_bytes(raw)
rows=[]
for l in raw.decode(errors='replace').splitlines():
 try:r=json.loads(l)
 except ValueError:continue
 if r.get('phase')=='api':rows.append(r)
assert rows
model=[r for r in rows if r.get('event')=='model_operation'];assert model and model[-1]['code']=='ok'
assert all(model[-1].get(k) is not None for k in ['request_id','session_id','run_id','duration_ms'])
assert any(r.get('event')=='retrieval_operation' and r.get('request_id')==model[-1]['request_id'] for r in rows)
record={'log_surface':'actual restarted API service; safe default JSON events only','events':rows,'correlated_live_model_and_retrieval':True,'limits':'HTTP middleware duration measures initial response; model_operation records full generation duration. Full process console retained privately.'}
Path('docs/agent-transcripts/phase-09/live-safe-events.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'safe_events':len(rows),'live_model_events':len(model),'correlated':True}))
