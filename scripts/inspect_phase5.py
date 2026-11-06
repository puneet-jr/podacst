"""Read each saved citation from the final actual run; entailment is reviewed separately."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import httpx

base=Path('docs/agent-transcripts/phase-05')
source=sorted(base.glob('live-*/results.jsonl'))[-1]
opened=[]
with httpx.Client(base_url='http://127.0.0.1:8080',trust_env=False,timeout=20) as client:
    for row in map(json.loads,source.read_text().splitlines()):
        run=row.get('run')
        if not run:continue
        for label in (run.get('output') or {}).get('source_labels',[]):
            response=client.get(f"/api/sessions/{run['session_id']}/messages/{run['assistant_message_id']}/sources/{label}")
            response.raise_for_status();evidence=response.json()
            exact=all(evidence['original_text'][q['char_start']-evidence['metadata']['char_start']:q['char_end']-evidence['metadata']['char_start']]==q['text'] for q in evidence['quote_spans'])
            entry={'case':row.get('name',row['kind']),'run_id':run['id'],'session_id':run['session_id'],'http_status':response.status_code,'exact_quotes':exact,'passage_sha256':sha256(evidence['original_text'].encode()).hexdigest(),'source':evidence}
            opened.append(entry)
            print(json.dumps(entry,ensure_ascii=False))
            if not exact:raise AssertionError('Source span mismatch')
report={'captured_at':datetime.now(timezone.utc).isoformat(),'actual_live_evidence':str(source),'opened_citations':opened,'limits':'HTTP/span validity only. Manual support assessment is in support-review.json; an incomplete answer is not a semantic pass.'}
(base/'opened-sources.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
