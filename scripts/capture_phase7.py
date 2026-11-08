"""Actual bounded command capture for Phase 7; never run secret-printing commands here."""
import datetime,json,subprocess,sys,time
from pathlib import Path
started=datetime.datetime.now(datetime.timezone.utc).isoformat(); before=time.monotonic()
p=subprocess.run(sys.argv[1:],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
record={"started_at":started,"ended_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"duration_seconds":time.monotonic()-before,"command":[arg.replace(str(Path.home()),"$USER_HOME") for arg in sys.argv[1:]],"exit_code":p.returncode,"stdout":p.stdout.decode(errors="replace")[-32000:],"stderr":p.stderr.decode(errors="replace")[-20000:],"truncated":len(p.stdout)>32000 or len(p.stderr)>20000}
for k in ["stdout","stderr"]:record[k]=record[k].replace(str(Path.home()),"$USER_HOME")
log=Path("docs/agent-transcripts/phase-07/commands.jsonl");log.parent.mkdir(parents=True,exist_ok=True)
with log.open("a") as f:f.write(json.dumps(record)+"\n")
print(record["stdout"],end="");print(record["stderr"],end="",file=sys.stderr);sys.exit(p.returncode)
