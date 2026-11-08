"""Inspect framing projection/privacy for one completed local run; never print payloads."""
import json,sys
from pathlib import Path
from uuid import UUID
from sqlalchemy import text
from backend.app.config import load_settings
from backend.app.db import make_engine
settings=load_settings();assert not settings.private_rpc_traces
rid=UUID(sys.argv[1]);engine=make_engine(settings)
try:
 with engine.connect() as c:
  r=c.execute(text('SELECT metadata,attempt,status FROM answer_runs WHERE id=:id'),{'id':rid}).mappings().one()
 assert r['status']=='completed'
 directory=Path('/app/evidence/private-chat')/str(rid)/str(r['attempt'])
 frames=[json.loads(x) for x in (directory/'stdout.jsonl').read_text().splitlines()]
 assert frames and all(set(x)<={'type','id','command','success','toolName'} for x in frames)
 diagnostics=[json.loads(x) for x in (directory/'stderr.log').read_text().splitlines()]
 assert all(set(x)=={'event','bytes'} for x in diagnostics)
 print(json.dumps({'run_id':str(rid),'protocol_records':len(frames),'diagnostic_records':len(diagnostics),'default_payloads_excluded':True,'text_tool_call_normalized':r['metadata'].get('text_tool_call_normalized'),'provider':r['metadata']['provider'],'process_reaped':r['metadata']['process_reaped'],'bridge_closed':r['metadata']['bridge_closed']}))
finally:engine.dispose()
