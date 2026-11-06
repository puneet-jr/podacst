"""Actual local environment/evidence inventory before any essay generation; no downloads."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import httpx

root=Path('docs/agent-transcripts/phase-06')
queries=['Sean Ellis must-have product market fit survey how would you feel no longer use very disappointed',
         'Sean Ellis Lookout antivirus positioning onboarding first value',
         'Sean Ellis survey customer segments benefits product market fit focus']
result={'captured_at':datetime.now(timezone.utc).isoformat(),'topic':'Use must-have customer feedback to improve positioning and onboarding','audience':'early-stage product managers','retrieval_mode':'hybrid','runs':[]}
with httpx.Client(base_url='http://127.0.0.1:8000',timeout=45,trust_env=False) as client:
    ready=client.get('/api/health/ready');ready.raise_for_status();result['ready']=ready.json()
    for query in queries:
        response=client.post('/api/retrieval/search',json={'query':query,'mode':'hybrid','source_path':'episodes/sean-ellis/transcript.md','limit':4,'max_neighbors':1,'token_budget':2400});response.raise_for_status();result['runs'].append(response.json())
with httpx.Client(base_url='http://127.0.0.1:11434',timeout=10,trust_env=False) as client:
    response=client.get('/api/tags');response.raise_for_status();result['models']=response.json()
result['host']={}
for name,args in [('hardware',['sysctl','-n','hw.model','hw.memsize','hw.ncpu','machdep.cpu.brand_string']),('swap',['sysctl','vm.swapusage']),('memory',['memory_pressure','-Q'])]:
    process=subprocess.run(args,capture_output=True,text=True,check=True);result['host'][name]=process.stdout.strip()
result['host']['disk_free_bytes']=shutil.disk_usage('.').free
program="""from backend.app.config import load_settings
from backend.app.db import make_engine
from sqlalchemy import text
from hashlib import sha256
import json,sys
e=make_engine(load_settings())
with e.connect() as c:
 m=[tuple(r) for r in c.execute(text('SELECT id,session_id,content,created_at FROM messages ORDER BY id'))]
 s=[tuple(r) for r in c.execute(text('SELECT id,user_id,title,created_at,updated_at FROM sessions ORDER BY id'))]
 print(json.dumps({'message_count':len(m),'message_digest':sha256(json.dumps(m,default=str).encode()).hexdigest(),'session_digest':sha256(json.dumps(s,default=str).encode()).hexdigest()}))
e.dispose()
"""
process=subprocess.run([sys.executable,'scripts/docker.py','compose','exec','-T','api','python','-c',program],capture_output=True,text=True,check=True)
result['prior_conversations']=json.loads(process.stdout)
(root/'preflight.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'host':result['host'],'models':[{k:m.get(k) for k in ('name','digest','size')} for m in result['models']['models']],'readiness':result['ready'],'retrievals':[{'mode':r['mode'],'passages':[{'id':p['id'],'ordinal':p['ordinal'],'text':p['original_text']} for p in r['passages']]} for r in result['runs']],'prior_conversations':result['prior_conversations']},ensure_ascii=False))
