"""Actual loopback API and read-only DB proofs; logs no raw passages/messages."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import httpx

PROOF = '''
from backend.app.config import load_settings
from backend.app.db import make_engine
from sqlalchemy import text
from hashlib import sha256
import json
engine=make_engine(load_settings())
with engine.connect() as c:
 messages=[tuple(r) for r in c.execute(text("SELECT id,session_id,content,created_at FROM messages ORDER BY id"))]
 sessions=[tuple(r) for r in c.execute(text("SELECT id,user_id,title,created_at,updated_at FROM sessions ORDER BY id"))]
 valid=c.scalar(text("SELECT bool_and(c.original_text=substring(v.original_text from c.char_start+1 for c.char_end-c.char_start) AND vector_dims(c.embedding)=768) FROM chunks c JOIN episode_versions v ON v.episode_id=c.episode_id AND v.version=c.version WHERE c.active"))
 print(json.dumps({'message_count':len(messages),'message_digest':sha256(json.dumps(messages,default=str).encode()).hexdigest(),'session_digest':sha256(json.dumps(sessions,default=str).encode()).hexdigest(),'all_active_source_spans_vectors_valid':valid}))
engine.dispose()
'''


def main():
    folder=Path('docs/agent-transcripts/phase-04')
    checks=[]
    def check(name,condition,detail=None):
        checks.append({'name':name,'passed':bool(condition),'detail':detail})
        if not condition:raise AssertionError(name)
    client=httpx.Client(base_url='http://127.0.0.1:8080',timeout=45,trust_env=False)
    try:
        ready=client.get('/api/health/ready')
        data=ready.json()
        check('Current dependency readiness',ready.status_code==200 and data['scope']=='phase_4_retrieval' and not data['product_ready'] and data['checks']['ollama']['reachable_from_api'],data)
        source='episodes/sean-ellis/transcript.md'
        response=client.post('/api/retrieval/search',json={'query':'Lookout antivirus onboarding changes','source_path':source})
        data=response.json()
        check('Default sparse through HTTP proxy',response.status_code==200 and data['mode']=='sparse' and data['passages'] and all(p['source_path']==source for p in data['passages']) and data['estimated_tokens']<=3200 and not data['support_verified'],{'status':response.status_code,'mode':data.get('mode'),'count':len(data.get('passages',[])),'estimated_tokens':data.get('estimated_tokens')})
        response=client.post('/api/retrieval/search',json={'query':'Shreyas Doshi leverage neutral overhead','mode':'hybrid'})
        data=response.json()
        check('Explicit real local hybrid through HTTP',response.status_code==200 and data['passages'] and data['embedding_digest'] and data['candidate_counts']['dense']>0 and data['candidate_counts']['sparse']>0,{'status':response.status_code,'count':len(data.get('passages',[])),'timings_ms':data.get('timings_ms'),'embedding_digest':data.get('embedding_digest')})
        response=client.post('/api/retrieval/search',json={'query':'quartz','episode_id':str(uuid4())})
        check('Empty exact scope has bounded evidence limitation',response.status_code==200 and response.json()['status']=='empty_evidence' and not response.json()['passages'])
        response=client.post('/api/retrieval/search',json={'query':'growth','guest':"' OR 1=1 --"})
        check('Filter values remain parameterized data',response.status_code==200 and not response.json()['passages'])
        response=client.post('/api/retrieval/search',json={'query':'growth','source_path':'../../secrets'})
        check('Unsafe source scope rejected safely',response.status_code==422 and response.json()['error']['request_id']==response.headers['X-Request-ID'])
        proc=subprocess.run([sys.executable,'scripts/docker.py','compose','exec','-T','api','python','-c',PROOF],capture_output=True,text=True,timeout=15)
        if proc.returncode:raise RuntimeError('Read-only DB proof failed')
        proof=json.loads(proc.stdout)
        old=[json.loads(l) for l in Path('docs/agent-transcripts/phase-03/smoke-20261106T053920/results.jsonl').read_text().splitlines()]
        prior=next(r['proof'] for r in old if r['kind']=='actual_smoke_summary')
        check('Saved Phase 3 conversations remain identical',all(proof[k]==prior[k] for k in ('message_count','message_digest','session_digest')),proof)
        check('All active exact source spans/vectors valid',proof['all_active_source_spans_vectors_valid'])
        status=client.get('/api/ingestion/status').json()
        check('Partial nine-episode scope accurately reported',status['active_episodes']==9 and status['active_chunks']==373 and status['latest']['discovered']==303,{'active_episodes':status['active_episodes'],'active_chunks':status['active_chunks'],'discovered':status['latest']['discovered']})
    finally:
        client.close()
        report={'captured_at':datetime.now(timezone.utc).isoformat(),'checks':checks,'passed':len(checks)==9 and all(c['passed'] for c in checks),'limits':'No browser, generated answer or semantic support claim.'}
        (folder/'live-api.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))


if __name__=='__main__':main()
