"""One actual local smoke, no automatic retry; raw output stays private."""
import hashlib,json,time,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4
import httpx
root=Path('docs/agent-transcripts/phase-09');private=Path('.cache/phase9-live');private.mkdir(parents=True,exist_ok=True)
with httpx.Client(base_url='http://127.0.0.1:8080',timeout=100,trust_env=False) as client:
    ready=client.get('/api/health/ready');ready.raise_for_status()
    provider=client.get('/api/providers').json();assert provider['selected']=='ollama' and not provider['automatic_fallback']
    sid=client.post('/api/sessions',json={'title':'Phase09 local operational smoke'}).json()['id']
    question='According to Sean Ellis, what question identifies people who consider a product a must-have?'
    body={'content':question,'client_message_id':str(uuid4()),'retrieval_mode':'hybrid'};started=time.monotonic()
    response=client.post(f'/api/sessions/{sid}/answers',json=body);elapsed=time.monotonic()-started
    (private/'response.ndjson').write_text(response.text)
    response.raise_for_status();events=[json.loads(x) for x in response.text.splitlines() if x.strip()];terminal=events[-1]
    record={'captured_at':datetime.now(timezone.utc).isoformat(),'provider':provider,'readiness':ready.json(),'session_id':sid,'request_id':response.headers.get('X-Request-ID'),'elapsed_seconds':elapsed,'http':response.status_code,'events':[{'type':e['type'],'run_id':e['run_id']} for e in events],'raw_output_sha256':hashlib.sha256(response.content).hexdigest(),'raw_output':'private .cache/phase9-live/response.ndjson','sources':[],'success':False}
    if terminal['type']=='completed':
        run=terminal['data']['run'];messages=client.get(f'/api/sessions/{sid}/messages').json();reply=messages[-1];(private/'reply.json').write_text(json.dumps(reply))
        assert 'how would you feel if you could no longer use this product' in reply['content'].lower()
        for cite in reply['citations']:
            source=client.get(f"/api/sessions/{sid}/messages/{reply['id']}/sources/{cite['source_label']}").json();spans=source['quote_spans'];assert spans
            assert all(source['original_text'][s['char_start']-source['metadata']['char_start']:s['char_end']-source['metadata']['char_start']]==s['text'] for s in spans)
            record['sources'].append({'id':cite['source_label'],'chunk_id':cite['chunk_id'],'exact_spans':True,'support_review':'Exact quoted survey question supports this answer; not a general quality score.'})
        saved=client.get(f"/api/sessions/{sid}/runs/{run['id']}").json();record['process_reaped']=saved['metadata']['process_reaped'];record['bridge_closed']=saved['metadata']['bridge_closed'];assert record['process_reaped'] and record['bridge_closed']
        again=client.post(f'/api/sessions/{sid}/answers',json=body);assert json.loads(again.text.splitlines()[-1])['type']=='completed'
        assert len(client.get(f'/api/sessions/{sid}/messages').json())==2;record['same_id_replay_no_duplicate']=True;record['success']=True
    record['machine']={'architecture':subprocess.check_output(['uname','-m'],text=True).strip(),'memory_bytes':int(subprocess.check_output(['sysctl','-n','hw.memsize'],text=True).strip()),'disk_free_bytes':shutil.disk_usage('.').free,'swap_snapshot':subprocess.check_output(['sysctl','-n','vm.swapusage'],text=True).strip()}
    (root/'live-local.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
    if not record['success']:raise SystemExit('Local smoke failed; preserve private response, do not automatically retry')
