"""Actual FastAPI -> Pi -> local Ollama checks; new attempts never overwrite evidence."""
from datetime import datetime, timezone
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from uuid import uuid4

import httpx


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--base-url',default='http://127.0.0.1:8000',choices=['http://127.0.0.1:8000','http://127.0.0.1:8080']);args=parser.parse_args()
    folder=Path('docs/agent-transcripts/phase-05')/('live-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'))
    folder.mkdir(parents=True,exist_ok=False)
    client=httpx.Client(base_url=args.base_url,timeout=100,trust_env=False)
    checks=[]
    def safe_run(run):
        run=json.loads(json.dumps(run))
        meta=run['metadata']
        if 'candidate_sentence_spans' in meta:
            meta['candidate_sentence_spans']=[{**{k:v for k,v in i.items() if k!='text'},'text_sha256':sha256(i['text'].encode()).hexdigest()} for i in meta['candidate_sentence_spans']]
        return run
    def record(value):
        with (folder/'results.jsonl').open('a') as stream:stream.write(json.dumps(value,ensure_ascii=False,default=str)+'\n')
        print(json.dumps(value,ensure_ascii=False,default=str),flush=True)
    def create(title):
        response=client.post('/api/sessions',json={'title':title});response.raise_for_status();return response.json()['id']
    try:
        session=create('Phase 5 local cited conversation '+uuid4().hex[:6])
        inputs=[('supported','According to Sean Ellis, what question identifies people who consider a product a must-have?','episodes/sean-ellis/transcript.md','answered'),
          ('follow_up','And what changes did Lookout make to onboarding after discovering antivirus mattered?',None,'answered'),
          ('unsupported',"What was our private startup's exact 2026 churn rate, and which guest accessed our internal dashboard?",None,'insufficient_evidence')]
        previous=None
        for name,question,scope,expected in inputs:
            body={'content':question,'client_message_id':str(uuid4()),'retrieval_mode':'hybrid','source_path':scope}
            started=time.monotonic();events=[]
            with client.stream('POST',f'/api/sessions/{session}/answers',json=body) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:events.append(json.loads(line))
            elapsed=time.monotonic()-started
            if not events:raise RuntimeError('No stream events')
            run_id=events[0]['run_id']
            run_response=client.get(f'/api/sessions/{session}/runs/{run_id}');run_response.raise_for_status();run=run_response.json()
            citations=[]
            output=run.get('output') or {}
            if run['status']=='completed':
                for label in output['source_labels']:
                    source_response=client.get(f"/api/sessions/{session}/messages/{run['assistant_message_id']}/sources/{label}")
                    source_response.raise_for_status();source=source_response.json()
                    valid=all(source['original_text'][q['char_start']-source['metadata']['char_start']:q['char_end']-source['metadata']['char_start']]==q['text'] for q in source['quote_spans'])
                    citations.append({'label':label,'chunk_id':source['chunk_id'],'quote_spans':source['quote_spans'],'source_metadata':source['metadata'],'source_url':source['source_url'],'video_url':source['video_url'],'stored_span_matches':valid,'opened_http_status':source_response.status_code})
            passed=run['status']=='completed' and output.get('status')==expected and all(s['stored_span_matches'] for s in citations)
            if name=='supported':passed=passed and bool(citations) and not run['context_message_ids']
            if name=='follow_up':passed=passed and previous in run['context_message_ids'] and bool(citations)
            if name=='unsupported':passed=passed and bool(run['metadata'].get('retrieved_passage_ids')) and not citations
            answer_text=output.get('text','').casefold()
            fact_check=(('how would you feel' in answer_text or 'no longer use' in answer_text) if name=='supported' else
                ('onboarding' in answer_text and ('antivirus' in answer_text or 'first thing' in answer_text)) if name=='follow_up' else output.get('status')=='insufficient_evidence')
            passed=passed and fact_check
            row={'kind':'actual_local_check','captured_at':datetime.now(timezone.utc).isoformat(),'base_url':args.base_url,'name':name,'session_id':session,'request':body,'run':safe_run(run),
              'events':[{'type':e['type'],'run_id':e['run_id'],'retrieval_mode':e['retrieval_mode']} for e in events],
              'opened_citations':citations,'request_duration_seconds':elapsed,'passed_automatic_contract_checks':bool(passed),'named_fact_smoke_check':bool(fact_check),'semantic_support_review':'pending direct manual review; exact span/facet matching alone is not support'}
            record(row);checks.append(bool(passed));previous=run['user_message_id']
            if not passed:
                record({'kind':'live_summary','passed_automatic_contract_checks':False,'checks':checks,'stopped_after_failed_case':name,'evidence_directory':str(folder)})
                raise SystemExit(1)
        independent=create('Phase 5 independent session '+uuid4().hex[:6])
        body={'content':'According to Shreyas Doshi, what are leverage tasks?','client_message_id':str(uuid4()),'source_path':'episodes/shreyas-doshi/transcript.md','retrieval_mode':'hybrid'}
        start=time.monotonic()
        with client.stream('POST',f'/api/sessions/{independent}/answers',json=body) as response:
            response.raise_for_status();events=[json.loads(line) for line in response.iter_lines() if line]
        run=client.get(f"/api/sessions/{independent}/runs/{events[0]['run_id']}").json()
        passed=run['status']=='completed' and not run['context_message_ids'] and run['session_id']==independent
        record({'kind':'actual_session_isolation_check','session_id':independent,'run':safe_run(run),'request_duration_seconds':time.monotonic()-start,'passed_automatic_contract_checks':passed});checks.append(passed)
        record({'kind':'live_summary','passed_automatic_contract_checks':all(checks),'checks':checks,'evidence_directory':str(folder),'limits':'Manual relevance/qualification review and browser checks are separate.'})
        if not all(checks):raise SystemExit(1)
    finally:client.close()


if __name__=='__main__':main()
