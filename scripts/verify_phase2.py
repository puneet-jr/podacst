"""Real Compose persistence/outage checks. Never removes databases or volumes."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4

import httpx

ROOT=Path(__file__).resolve().parent.parent


def main():
    run=ROOT/'docs/agent-transcripts/phase-02'/('live-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'))
    run.mkdir(parents=True,exist_ok=False)
    records=[]
    def record(kind,**fields):
        item={'captured_at':datetime.now(timezone.utc).isoformat(),'kind':kind,**fields}
        records.append(item)
        with (run/'results.jsonl').open('a') as stream:stream.write(json.dumps(item)+'\n')
        print(json.dumps(item),flush=True)
    def compose(*args):
        command=[sys.executable,'scripts/docker.py','compose',*args]
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=90)
        record('actual_command',command=command,exit_code=result.returncode,stdout=result.stdout[-10000:],stderr=result.stderr[-5000:])
        if result.returncode:raise RuntimeError('Compose check failed; see recorded command')
        return result.stdout.strip()
    def check(name,condition,**fields):
        record(name,passed=bool(condition),**fields)
        if not condition:raise AssertionError(name)
    config={}
    for line in (ROOT/'.env').read_text().splitlines():
        if line.startswith(('API_HOST_PORT=','WEB_HOST_PORT=')):
            key,value=line.split('=',1);config[key]=int(value)
    base=f"http://127.0.0.1:{config.get('API_HOST_PORT',8000)}"
    web=f"http://127.0.0.1:{config.get('WEB_HOST_PORT',8080)}"
    client=httpx.Client(timeout=15,trust_env=False)
    def request(method,path,**kwargs):
        response=client.request(method,base+path,**kwargs)
        record('actual_http',method=method,path=path,status=response.status_code,request_id=response.headers.get('X-Request-ID'),body=response.json())
        return response
    def await_ready():
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            try:
                response=client.get(base+'/api/health/ready')
                if response.status_code==200:
                    record('ready_observed',status=response.status_code,body=response.json());return response.json()
            except httpx.TransportError:pass
            time.sleep(.5)
        raise RuntimeError('Readiness deadline exceeded')
    db_stopped=False
    try:
        db_id=compose('ps','-q','db')
        label=subprocess.run([sys.executable,'scripts/docker.py','inspect','--format','{{index .Config.Labels "com.docker.compose.project"}}',db_id],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
        check('isolated_compose_project',label=='lenny-phase2',database_container=db_id,project=label)
        ready=await_ready()
        check('container_model_readiness',ready['checks']['ollama']['ready'] and ready['checks']['ollama']['reachable_from_api'] and not ready['product_ready'],body=ready)
        user=request('GET','/api/me').json()
        before=[]
        for name in ['A','B']:
            response=request('POST','/api/sessions',json={'title':f'Phase 2 persistence {name}'})
            check('session_created_'+name,response.status_code==201)
            chat=response.json()
            content=f'Phase 2 isolated note {name} '+uuid4().hex[:8]
            payload={'content':content,'client_message_id':str(uuid4())}
            message=request('POST',f"/api/sessions/{chat['id']}/messages",json=payload)
            check('message_saved_'+name,message.status_code==201)
            retry=request('POST',f"/api/sessions/{chat['id']}/messages",json=payload)
            check('safe_retry_'+name,retry.json()['id']==message.json()['id'])
            before.append({'session':chat,'message':message.json()})
        check('two_independent_sessions',before[0]['session']['id']!=before[1]['session']['id'],sessions=before,user=user)
        compose('restart','api')
        await_ready()
        for item in before:
            ident=item['session']['id']
            response=request('GET',f'/api/sessions/{ident}/messages')
            check('persisted_isolated_message_after_app_restart',response.status_code==200 and response.json()==[item['message']],session_id=ident)
            session=request('GET',f'/api/sessions/{ident}')
            check('session_identity_and_created_time_retained',session.json()['id']==ident and session.json()['created_at']==item['session']['created_at'])
        after_user=request('GET','/api/me').json()
        check('user_metadata_persisted',user==after_user)
        compose('stop','db');db_stopped=True
        live=request('GET','/api/health/live')
        down=request('GET','/api/health/ready')
        check('db_outage_liveness_and_readiness',live.status_code==200 and down.status_code==503 and not down.json()['checks']['database']['ready'])
        failed=request('POST','/api/sessions',json={'title':'This failed write must not appear'})
        check('safe_db_write_failure',failed.status_code==503 and failed.json()['error']['code']=='database_unavailable' and failed.json()['error']['retryable'])
        compose('start','db');db_stopped=False
        await_ready()
        for item in before:
            ident=item['session']['id']
            response=request('GET',f'/api/sessions/{ident}/messages')
            check('persisted_after_db_returns_without_app_restart',response.json()==[item['message']],session_id=ident)
        listing=request('GET','/api/sessions?limit=100')
        check('failed_transaction_not_committed',not any(s['title']=='This failed write must not appear' for s in listing.json()))
        response=client.get(web)
        check('served_frontend',response.status_code==200 and 'The Lenny Growth Assistant' in response.text,status=response.status_code)
        response=client.get(web+'/api/sessions')
        check('frontend_proxy_api',response.status_code==200,status=response.status_code)
        response=request('GET','/api/sessions/not-a-uuid')
        check('structured_error_and_request_correlation',response.status_code==422 and response.json()['error']['request_id']==response.headers['X-Request-ID'])
        record('phase_2_live_gate',passed=True,scope='Real PostgreSQL/Compose/API persistence, isolation and outage recovery; not product RAG or essay quality.')
    except Exception as exc:
        record('phase_2_live_gate',passed=False,error_type=type(exc).__name__,message=str(exc))
        raise
    finally:
        if db_stopped:compose('start','db')
        client.close()


if __name__=='__main__':main()
