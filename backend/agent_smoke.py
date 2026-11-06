"""Actual container-to-host Pi fixture proof. Separate from corpus/product inference."""
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4
from backend.app.agent import run_once


async def main():
    path=Path('/app/evidence')/('container-smoke-'+uuid4().hex[:12])
    result=await run_once('For activation, what is the review window and evidence code? Use search_fixture and cite the source_id.',path)
    result.pop('messages',None)
    passed=all(x in result['text'] for x in ['13','CEDAR-7319','FIXTURE-A'])
    record={'captured_at':datetime.now(timezone.utc).isoformat(),'passed':passed,'scope':'actual container Pi to host Ollama, synthetic fixture only','result':result}
    (path/'result.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'evidence_directory':str(path),**record}),flush=True)
    if not passed: raise SystemExit(1)


if __name__=='__main__':asyncio.run(main())
