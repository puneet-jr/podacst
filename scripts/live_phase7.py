"""One standard-endpoint live essay, explicitly separate from rendering fixture."""
import json,time
from uuid import uuid4
from pathlib import Path
from datetime import datetime,timezone
import httpx
ROOT=Path('docs/agent-transcripts/phase-07')
def main():
 if list(ROOT.glob('live-*')):raise SystemExit('Live attempt exists; inspect it rather than creating another')
 folder=ROOT/('live-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'));folder.mkdir()
 with httpx.Client(base_url='http://127.0.0.1:8080',trust_env=False,timeout=httpx.Timeout(110,connect=5)) as c:
  r=c.get('/api/health/ready');r.raise_for_status()
  r=c.post('/api/sessions',json={'title':'Phase7 fresh endpoint essay'});r.raise_for_status();sid=r.json()['id']
  body={'client_message_id':str(uuid4()),'topic':'Use must-have customer feedback to improve positioning and onboarding','audience':'Early-stage product managers deciding how to move users toward first value','constraints':'Explain the survey, benefit-focused follow-ups, the Lookout case and limitations. No survey score guarantees product-market fit, measured engagement/conversion improvement, or onboarding-only causality. Proposed actions must remain advice and expected benefits hypotheses.','source_path':'episodes/sean-ellis/transcript.md','focus_questions':['Sean Ellis must-have product market fit survey how would you feel no longer use very disappointed','Sean Ellis Lookout antivirus positioning onboarding first value','Sean Ellis survey customer segments benefits product market fit focus'],'timeout_seconds':600}
  (folder/'request.json').write_text(json.dumps({'session_id':sid,'endpoint':'POST /api/sessions/{sid}/essays','request':body,'fixture_used':False},indent=2)+'\n')
  started=time.monotonic();rid=None
  with c.stream('POST',f'/api/sessions/{sid}/essays',json=body) as response:
   response.raise_for_status()
   for line in response.iter_lines():
    if not line:continue
    e=json.loads(line);rid=e['run_id'];safe={**e,'data':{k:v for k,v in e['data'].items() if k!='run'},'elapsed_seconds':time.monotonic()-started}
    with (folder/'events.jsonl').open('a') as f:f.write(json.dumps(safe)+'\n')
    print(json.dumps(safe),flush=True)
  r=c.get(f'/api/sessions/{sid}/essays/{rid}');r.raise_for_status();run=r.json()
  result={'captured_at':datetime.now(timezone.utc).isoformat(),'session_id':sid,'run_id':rid,'request_seconds':time.monotonic()-started,'run':run,'manual_review':'pending; not accepted by automated citation/count screens','fixture':False}
  (folder/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');(folder/'draft.md').write_text(run['draft_md'] or '')
  print(json.dumps({'folder':str(folder),'status':run['status'],'error_code':run['error_code'],'model':run['metadata']['model'],'validation':run['validation'],'seconds':result['request_seconds'],'draft':run['draft_md']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
