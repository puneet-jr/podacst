"""One real FastAPI -> Pi -> OpenRouter answer. No inference mocks or retries.

Run via Compose with DEFAULT_PROVIDER=openrouter. Credentials are inherited only
from the service environment, never argv or reports. Main app may stay local.
"""
import json,time,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.app.main import app,engine,settings,conversations

def main():
    assert settings.default_provider=='openrouter', 'Explicit OpenRouter selection required'
    summary={'captured_at':datetime.now(timezone.utc).isoformat(),'provider':'openrouter','pi_provider':settings.provider_id,'model':settings.selected_model(),'endpoint':settings.model_base_url,'inference_mocked':False,'cloud_validation':'pending','automatic_fallback':False}
    preflight_only='--preflight-only' in sys.argv
    if not settings.openrouter_api_key.get_secret_value().strip() and not preflight_only:
        summary.update(blocker='OPENROUTER_API_KEY missing in server environment',provider_requests=0);print(json.dumps(summary));return 3
    assert settings.selected_model()=='google/gemini-2.5-flash-lite','Smoke is limited to the disclosed Google model'
    revision='be8ab89a890a833cbba2c892178f823fff178c65';source_path='episodes/sean-ellis/transcript.md'
    public_sha='6af2a6e031826805e855ec262b1f228e3773b5b99265a1d01870f0d4e6e9ceda'
    raw=(Path('/corpus')/revision/source_path).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==public_sha,'Public source hash changed; no cloud request allowed'
    from backend.app.transcripts import parse_transcript
    episode=parse_transcript(raw,source_path)
    with engine.connect() as c:
        rows=c.execute(text('SELECT c.original_text,c.char_start,c.char_end,c.source_hash,c.corpus_revision,e.guest,e.title FROM chunks c JOIN episodes e ON e.id=c.episode_id AND e.current_version=c.version WHERE c.active AND e.source_path=:path'),{'path':source_path}).mappings().all()
    assert rows and all(r['source_hash']==public_sha and r['corpus_revision']==revision and r['original_text']==episode.original[r['char_start']:r['char_end']] and r['guest']==episode.guest and r['title']==episode.title for r in rows),'Candidate data does not exactly match public transcript; no cloud request allowed'
    summary.update(public_source_path=source_path,public_source_sha256=public_sha,all_active_source_spans_verified_public=True,prior_history_sent=False)
    if preflight_only:
        summary.update(preflight_only=True,provider_requests=0,key_configured=bool(settings.openrouter_api_key.get_secret_value().strip()),active_public_chunks_verified=len(rows));print(json.dumps(summary));engine.dispose();return 0
    assert not settings.private_rpc_traces,'Use safe default trace projection for this check'
    with engine.connect() as c:
        if c.scalar(text("SELECT (SELECT count(*) FROM answer_runs WHERE status='running')+(SELECT count(*) FROM essay_runs WHERE status='running')")):
            summary.update(blocker='Existing operation active; wait before isolated smoke');print(json.dumps(summary));return 3
    folder=Path('/app/evidence/private-chat/openrouter-checks')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    folder.mkdir(parents=True,mode=0o700)
    client=TestClient(app)
    try:
        sid=client.post('/api/sessions',json={'title':'OpenRouter cited-answer verification'}).json()['id'];summary['session_id']=sid
        start=time.monotonic()
        response=client.post(f'/api/sessions/{sid}/answers',json={'content':'According to Sean Ellis, what question identifies people who consider a product a must-have?','client_message_id':str(uuid4()),'retrieval_mode':'hybrid','source_path':source_path,'timeout_seconds':90})
        summary.update(http=response.status_code,request_id=response.headers.get('X-Request-ID'),elapsed_seconds=time.monotonic()-start)
        (folder/'response.ndjson').write_text(response.text)
        summary['private_evidence_directory']=str(folder)
        if response.status_code!=200:
            summary['blocker']=response.json().get('error',{}).get('code','http_failure');print(json.dumps(summary));return 1
        events=[json.loads(l) for l in response.text.splitlines() if l.strip()];summary['events']=[e['type'] for e in events];terminal=events[-1]
        run=terminal['data'].get('run',{});summary.update(run_id=terminal['run_id'],status=run.get('status'),error_code=run.get('error_code'))
        assert not run.get('context_message_ids'),'Fresh session unexpectedly has history'
        metadata=run.get('metadata',{});summary.update(recorded_provider=metadata.get('provider'),recorded_model=metadata.get('model'),usage=metadata.get('model_usage'),process_reaped=metadata.get('process_reaped'),bridge_closed=metadata.get('bridge_closed'),text_tool_call_normalized=metadata.get('text_tool_call_normalized'))
        summary['tool_trace']=[{'tool':t['tool'],'args':t['args'],'evidence_id_count':len(t.get('result',{}).get('evidence_ids',[]))} for t in metadata.get('tool_trace',[])]
        if terminal['type']!='completed':summary['blocker']=run.get('error_code') or terminal['type'];print(json.dumps(summary));return 1
        messages=client.get(f'/api/sessions/{sid}/messages').json();reply=messages[-1];(folder/'reply.json').write_text(json.dumps(reply))
        summary['answer_sha256']=hashlib.sha256(reply['content'].encode()).hexdigest();summary['citations']=[]
        for citation in reply['citations']:
            r=client.get(f"/api/sessions/{sid}/messages/{reply['id']}/sources/{citation['source_label']}");r.raise_for_status();source=r.json()
            spans=source['quote_spans'];assert spans and all(source['original_text'][s['char_start']-source['metadata']['char_start']:s['char_end']-source['metadata']['char_start']]==s['text'] for s in spans)
            (folder/('source-'+citation['source_label']+'.json')).write_text(json.dumps(source))
            summary['citations'].append({'label':citation['source_label'],'chunk_id':citation['chunk_id'],'exact_spans':True,'source_sha256':hashlib.sha256(source['original_text'].encode()).hexdigest()})
        assert summary['citations'],'No cited answer; live validation remains pending'
        assert metadata['provider']=='openrouter' and metadata['model']==settings.selected_model()
        assert summary['tool_trace'] and summary['tool_trace'][0]['tool']=='search_transcripts'
        assert summary['process_reaped'] and summary['bridge_closed']
        summary.update(cloud_validation='pending_manual_source_review',technical_run_succeeded=True,scope='Real FastAPI ASGI request, PostgreSQL, Pi subprocess, live OpenRouter inference and local hybrid retrieval. No browser claim.')
        (folder/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary));return 0
    finally:client.close();engine.dispose()

if __name__=='__main__':sys.exit(main())
