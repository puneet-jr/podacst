"""Real HTTP lifecycle/retry checks; actual local generation, no model mocks."""
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from uuid import uuid4

import httpx


def main():
    folder=Path('docs/agent-transcripts/phase-05')/('lifecycle-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'))
    folder.mkdir(exist_ok=False)
    def record(row):
        with (folder/'results.jsonl').open('a') as f:f.write(json.dumps(row,default=str)+'\n')
        print(json.dumps(row,default=str),flush=True)
    def check(name,passed,**detail):
        record({'name':name,'passed':bool(passed),**detail})
        if not passed:raise AssertionError(name)
    with httpx.Client(base_url='http://127.0.0.1:8000',timeout=100,trust_env=False) as client:
        r=client.post('/api/sessions',json={'title':'Phase 5 real lifecycle '+uuid4().hex[:6]});r.raise_for_status();sid=r.json()['id']
        base={'content':'According to Sean Ellis, what question identifies people who consider a product a must-have?','retrieval_mode':'hybrid','source_path':'episodes/sean-ellis/transcript.md'}
        def stream(body,action=None,trigger=None):
            events=[];start=time.monotonic()
            with client.stream('POST',f'/api/sessions/{sid}/answers',json=body) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:continue
                    e=json.loads(line);events.append(e['type']);rid=e['run_id']
                    if action and e['type']==trigger:
                        if action=='cancel':
                            cancel=client.post(f'/api/sessions/{sid}/runs/{rid}/cancel');cancel.raise_for_status()
                        else:break
            deadline=time.monotonic()+10
            while True:
                r=client.get(f'/api/sessions/{sid}/runs/{rid}');r.raise_for_status();run=r.json()
                if run['status']!='running' or time.monotonic()>deadline:break
                time.sleep(.1)
            meta=run['metadata']
            return run,{'run_id':rid,'session_id':sid,'events':events,'seconds_including_cleanup':time.monotonic()-start,
                'status':run['status'],'error_code':run['error_code'],'retrieval_mode':run['retrieval_mode'],'attempt':run['attempt'],
                'process_pid':meta.get('process_pid'),'process_reaped':meta.get('process_reaped'),'bridge_closed':meta.get('bridge_closed'),
                'retrieved_passage_ids':meta.get('retrieved_passage_ids',[]),'pi_session_id':meta.get('pi_session_id')}
        timed,detail=stream({**base,'client_message_id':str(uuid4()),'timeout_seconds':.1})
        check('actual_timeout_cleanup',timed['status']=='failed' and timed['error_code']=='answer_timeout' and detail['process_reaped'] and detail['bridge_closed'],**detail)
        cancel_body={**base,'client_message_id':str(uuid4())}
        cancelled,detail=stream(cancel_body,'cancel','retrieving')
        check('actual_explicit_cancel_cleanup',cancelled['status']=='cancelled' and 'retrieving' in detail['events'] and detail['process_reaped'] and detail['bridge_closed'],**detail)
        disconnected,detail=stream({**base,'client_message_id':str(uuid4())},'disconnect','evidence_ready')
        check('actual_stream_disconnect_cleanup',disconnected['status']=='cancelled' and 'evidence_ready' in detail['events'] and detail['process_reaped'] and detail['bridge_closed'],**detail)
        retried,detail=stream({**cancel_body,'retry':True})
        check('actual_retry_same_saved_user',retried['status']=='completed' and retried['attempt']==2 and retried['user_message_id']==cancelled['user_message_id'] and len(retried['metadata'].get('attempt_history',[]))==1,**detail)
        replay,detail=stream({**cancel_body,'retry':True})
        check('completed_retry_replays_without_inference',replay['assistant_message_id']==retried['assistant_message_id'] and replay['attempt']==2 and detail['events']==['completed'],**detail)
        empty,detail=stream({**base,'source_path':'episodes/unindexed-phase-five/transcript.md','content':'What is the evidence for this unindexed source?','client_message_id':str(uuid4())})
        check('actual_empty_retrieval_gap',empty['status']=='completed' and empty['output']['status']=='insufficient_evidence' and not empty['metadata']['retrieved_passage_ids'] and not empty['output']['source_labels'],**detail)
        response=client.get(f'/api/sessions/{sid}/messages');response.raise_for_status();messages=response.json()
        # Four distinct saved user prompts, two successful assistant replies; failed/cancelled attempts add no reply.
        check('no_duplicate_messages_after_retry',len(messages)==6 and sum(m['role']=='user' for m in messages)==4 and sum(m['client_message_id']==cancel_body['client_message_id'] for m in messages)==1,message_count=len(messages))
        citation=client.get(f"/api/sessions/{sid}/messages/{retried['assistant_message_id']}/sources/{retried['output']['source_labels'][0]}");citation.raise_for_status()
        snapshot={'session_id':sid,'run_id':retried['id'],'messages':messages,'source':citation.json()}
        (folder/'restart-before.json').write_text(json.dumps(snapshot,indent=2))
        check('restart_baseline_saved',True,evidence_directory=str(folder))


if __name__=='__main__':main()
