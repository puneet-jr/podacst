"""First real local essay test through the dedicated FastAPI/Pi/Ollama workflow."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import time
from uuid import uuid4
import httpx


def main():
    folder=Path('docs/agent-transcripts/phase-06')/('live-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'))
    folder.mkdir(exist_ok=False)
    with httpx.Client(base_url='http://127.0.0.1:8000',timeout=httpx.Timeout(110,connect=5),trust_env=False) as client:
        ready=client.get('/api/health/ready');ready.raise_for_status()
        response=client.post('/api/sessions',json={'title':'Phase6 first real local essay '+uuid4().hex[:6]});response.raise_for_status();sid=response.json()['id']
        context=client.post(f'/api/sessions/{sid}/messages',json={'client_message_id':str(uuid4()),'content':'I am an early-stage product manager. Keep recommendations cautious, distinguish advice from observed guest experience, and avoid promises of guaranteed growth.'});context.raise_for_status()
        body={'workflow':'ship30','topic':'Use must-have customer feedback to improve positioning and onboarding',
          'audience':'Early-stage product managers deciding how to move users toward first value',
          'constraints':'Explain the survey, benefit-focused follow-ups, the Lookout case, and limitations. Do not claim a survey score guarantees product-market fit or that onboarding alone caused the outcome. Label proposed user actions Application:. Use only supplied transcript evidence; no invented stories, quotes, metrics or personal experience.',
          'client_message_id':str(uuid4()),'source_path':'episodes/sean-ellis/transcript.md',
          'focus_questions':['Sean Ellis must-have product market fit survey how would you feel no longer use very disappointed','Sean Ellis Lookout antivirus positioning onboarding first value','Sean Ellis survey customer segments benefits product market fit focus'],
          'timeout_seconds':600}
        (folder/'request.json').write_text(json.dumps({'session_id':sid,'request':body,'prior_user_message_id':context.json()['id'],'ready_before':ready.json()},indent=2)+'\n')
        events=[];started=time.monotonic()
        with client.stream('POST',f'/api/sessions/{sid}/essays',json=body) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:continue
                event=json.loads(line);events.append(event)
                projection={'captured_at':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-started,'type':event['type'],'run_id':event['run_id'],'data':{k:v for k,v in event['data'].items() if k!='run'}}
                with (folder/'events.jsonl').open('a') as f:f.write(json.dumps(projection)+'\n')
                print(json.dumps(projection),flush=True)
        elapsed=time.monotonic()-started
        if not events:raise RuntimeError('No essay events')
        rid=events[0]['run_id'];response=client.get(f'/api/sessions/{sid}/essays/{rid}');response.raise_for_status();run=response.json()
        response=client.get(f'/api/sessions/{sid}/essays/{rid}/sources');response.raise_for_status();sources=response.json()
        result={'captured_at':datetime.now(timezone.utc).isoformat(),'actual_local_inference':True,'session_id':sid,'run_id':rid,'request_duration_seconds':elapsed,'run':run,'source_passage_ids':{s['source_label']:s['chunk_id'] for s in sources},'manual_review':'pending; deterministic success is not factual/narrative quality','essay_gate':'manual_review_pending' if run['status']=='needs_review' else 'failed'}
        (folder/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
        (folder/'sources.json').write_text(json.dumps(sources,indent=2,ensure_ascii=False)+'\n')
        (folder/'outline.json').write_text(json.dumps(run['outline'],indent=2,ensure_ascii=False)+'\n')
        (folder/'validation.json').write_text(json.dumps(run['validation'],indent=2,ensure_ascii=False)+'\n')
        (folder/'draft.md').write_text(run['draft_md'] or '(No draft produced; inspect result.json for the exact failure.)\n')
        messages=client.get(f'/api/sessions/{sid}/messages');messages.raise_for_status();(folder/'messages-before-review.json').write_text(json.dumps(messages.json(),indent=2)+'\n')
        print(json.dumps({'event':'actual_local_essay_result','evidence_directory':str(folder),'status':run['status'],'error_code':run['error_code'],'model':run['metadata']['model'],'elapsed_seconds':elapsed,'validation':run['validation'],'repairs_used':run['metadata']['repairs_used'],'stages':[{'name':s['stage'],'seconds':s.get('duration_seconds'),'model_usage':s.get('usage'),'process_reaped':s.get('process_reaped'),'bridge_closed':s.get('bridge_closed'),'tool_called':s.get('tool_called')} for s in run['metadata']['stages']],'source_passage_ids':result['source_passage_ids']}),flush=True)
        if run['status']!='needs_review':raise SystemExit(2)


if __name__=='__main__':main()
