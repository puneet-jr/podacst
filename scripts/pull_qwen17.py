"""Explicitly authorized local Ollama model pull, with sampled actual progress."""
from datetime import datetime,timezone
import json
from pathlib import Path
import time
import re
import httpx

root=Path('docs/agent-transcripts/phase-06');events=[];started=time.monotonic();last_status=None;last_bytes=-1
with httpx.Client(base_url='http://127.0.0.1:11434',trust_env=False,timeout=httpx.Timeout(600,read=90)) as client:
    before=client.get('/api/tags');before.raise_for_status()
    installed=any(m['name']=='qwen3:1.7b' for m in before.json()['models'])
    if not installed:
        with client.stream('POST','/api/pull',json={'model':'qwen3:1.7b','stream':True}) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:continue
                event=json.loads(line)
                if event.get('error'):raise RuntimeError(re.sub(r'https://[^\s\"]+', '[signed model download URL omitted]', event['error']))
                status=event.get('status');completed=event.get('completed',0)
                if status!=last_status or completed-last_bytes>=32*1024*1024 or completed==event.get('total'):
                    events.append({'captured_at':datetime.now(timezone.utc).isoformat(),**event});print(json.dumps(event),flush=True);last_status=status;last_bytes=completed
    after=client.get('/api/tags');after.raise_for_status()
    model=next((m for m in after.json()['models'] if m['name']=='qwen3:1.7b'),None)
    if not model:raise RuntimeError('Authorized model missing after pull')
result={'captured_at':datetime.now(timezone.utc).isoformat(),'model':'qwen3:1.7b','already_installed':installed,'elapsed_seconds':time.monotonic()-started,'model_metadata':model,'actual_progress_samples':events,'inference_performed':False,'scope':'Model download only; no chat/default configuration changed.'}
(root/'qwen17-pull.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'model':result['model'],'already_installed':installed,'elapsed_seconds':result['elapsed_seconds'],'metadata':model}))
