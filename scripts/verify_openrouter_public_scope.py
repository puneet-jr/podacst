"""Prove the planned cloud smoke is limited to publicly published episode data.

No OpenRouter request or credentials. Print hashes/paths/counts only.
"""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
import httpx
revision='be8ab89a890a833cbba2c892178f823fff178c65';path='episodes/sean-ellis/transcript.md'
url=f'https://raw.githubusercontent.com/ChatPRD/lennys-podcast-transcripts/{revision}/{path}'
with httpx.Client(timeout=30,trust_env=False) as client:
    public=client.get(url);public.raise_for_status();sha=hashlib.sha256(public.content).hexdigest()
    cached=Path('.cache/corpus')/revision/path;assert hashlib.sha256(cached.read_bytes()).hexdigest()==sha
    r=client.post('http://127.0.0.1:8080/api/retrieval/search',json={'query':'According to Sean Ellis, what question identifies people who consider a product a must-have?','source_path':path,'mode':'hybrid','limit':8,'token_budget':3200});r.raise_for_status()
    passages=r.json()['passages'];assert passages
    assert all(p['source_path']==path and p['source_hash']==sha and p['corpus_revision']==revision for p in passages)
    assert all(p['original_text']==public.content.decode('utf-8')[p['char_start']:p['char_end']] for p in passages)
    record={'captured_at':datetime.now(timezone.utc).isoformat(),'public_source_url':url,'source_path':path,'corpus_revision':revision,'source_sha256':sha,'local_file_matches_public':True,'all_retrieved_candidates_match_public_hash':True,'all_retrieved_spans_match_public_content':True,'retrieved_ids':[p['id'] for p in passages],'planned_question':'According to Sean Ellis, what question identifies people who consider a product a must-have?','planned_session':'new empty session; no prior user history','excluded':['assignment PDF','local .env/credentials','other sessions','private company data'],'planned_destinations':['OpenRouter','upstream Google Gemini model via OpenRouter'],'inference_requests':0}
    Path('docs/agent-transcripts/phase-09/openrouter-public-scope.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
