"""Safe default diagnostics: metadata only; private raw traces are separate."""
from contextvars import ContextVar
from datetime import datetime,timezone
import json,logging,re
request_id=ContextVar('request_id',default=None)
session_id=ContextVar('session_id',default=None)
FIELDS={'request_id','session_id','run_id','stage','code','provider','model','duration_ms','status','outcome','method','route','error_type','message_id','database_ready','agent_ready','model_ready','count','process_reaped','bridge_closed','attempt','mode','source_count','source_ids'}
logger=logging.getLogger('lenny')
def emit(name,**fields):
    fields={'request_id':request_id.get(),'session_id':session_id.get(),**fields}
    record={'timestamp':datetime.now(timezone.utc).isoformat(),'event':name,'phase':'api'}
    for k,v in fields.items():
        if k not in FIELDS or v is None:continue
        if k=='source_ids' and isinstance(v,list):
            try:record[k]=[str(__import__('uuid').UUID(str(i))) for i in v[:8]]
            except ValueError:pass
        elif isinstance(v,(bool,int,float)):record[k]=v
        elif len(str(v))<=180 and re.fullmatch(r'[A-Za-z0-9_./:{} -]+',str(v)):record[k]=str(v)
    logger.info(json.dumps(record))
