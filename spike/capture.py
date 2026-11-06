"""Run a known safe development command and preserve actual bounded output."""
import datetime
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    command = sys.argv[1:]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    before = time.monotonic()
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    record = {
        "started_at": started, "duration_seconds": time.monotonic() - before,
        "command": command, "exit_code": result.returncode,
        "stdout": result.stdout.decode(errors="replace")[-24000:],
        "stderr": result.stderr.decode(errors="replace")[-16000:],
        "truncated": len(result.stdout) > 24000 or len(result.stderr) > 16000,
    }
    path = Path("docs/agent-transcripts/phase-01/commands.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as stream:
        stream.write(json.dumps(record) + "\n")
    sys.stdout.write(record["stdout"])
    sys.stderr.write(record["stderr"])
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
