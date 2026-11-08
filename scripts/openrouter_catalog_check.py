"""Public model metadata only: no key and no inference request."""
import json
from pathlib import Path
from datetime import datetime,timezone
import httpx
with httpx.Client(timeout=30,trust_env=False) as client:
    r=client.get('https://openrouter.ai/api/v1/models');r.raise_for_status()
    model=next(m for m in r.json()['data'] if m['id']=='google/gemini-2.5-flash-lite')
    required={'tools','tool_choice','response_format','max_tokens','temperature'}
    supported=set(model['supported_parameters']);assert required<=supported
    record={'captured_at':datetime.now(timezone.utc).isoformat(),'source':'https://openrouter.ai/api/v1/models','id':model['id'],'context_length':model.get('context_length'),'supported_parameters':model['supported_parameters'],'required_parameters_available':True,'inference_requests':0,'requires_key':False,'limits':'Public catalog capability metadata; does not establish this account/model route or actual inference success.'}
    Path('docs/agent-transcripts/phase-09/openrouter-model-catalog.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
