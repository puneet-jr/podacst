"""Capture actual command streams privately; publish metadata only after review."""
import datetime,json,subprocess,sys,time,threading,queue,uuid
from pathlib import Path
root=Path('.cache/phase10/commands');root.mkdir(parents=True,exist_ok=True)
started=datetime.datetime.now(datetime.timezone.utc);tag=started.strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:6];folder=root/tag;folder.mkdir()
command=sys.argv[1:];before=time.monotonic();process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE);pending=queue.Queue()
def read(stream,name):
 with (folder/(name+'.jsonl')).open('w') as output:
  for data in iter(lambda:stream.readline(8192),b''):
   line=data.decode(errors='replace');output.write(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'text':line})+'\n');output.flush();pending.put((name,line))
 pending.put((name,None))
for name in ['stdout','stderr']:threading.Thread(target=read,args=(getattr(process,name),name),daemon=True).start()
closed=0;quiet='backend.ingest' in command;last=0
while closed<2:
 name,line=pending.get()
 if line is None:closed+=1;continue
 show=not quiet
 if quiet:
  try:
   event=json.loads(line);show=event.get('event') in ['episode_failed','ingestion_failed','ingestion_result','ingestion_cli_error'] or (event.get('event') in ['episode_loaded','episode_unchanged'] and time.monotonic()-last>25)
  except ValueError:show=name=='stderr'
 if show:print(line,end='',file=sys.stderr if name=='stderr' else sys.stdout,flush=True);last=time.monotonic()
code=process.wait();record={'started_at':started.isoformat(),'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'duration_seconds':round(time.monotonic()-before,3),'command':command,'exit_code':code,'actual_streams':str(folder),'stdout_separate_from_diagnostics':True}
with Path('docs/agent-transcripts/phase-10/commands.jsonl').open('a') as output:output.write(json.dumps(record)+'\n')
print(json.dumps({'capture':record}),flush=True);sys.exit(code)
