"""Run the single Pi/Ollama Markdown probe once and retain failure output unchanged."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys

folder=Path('docs/agent-transcripts/phase-06')/('markdown-section-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'))
folder.mkdir(exist_ok=False)
command=[sys.executable,'scripts/docker.py','compose','exec','-T','api','python','-m','backend.markdown_section_check']
result=subprocess.run(command,capture_output=True,text=True,timeout=130)
(folder/'command.json').write_text(json.dumps({'command':command,'exit_code':result.returncode,'stderr':result.stderr},indent=2)+'\n')
if result.stdout.strip():
    try:
        data=json.loads(result.stdout);(folder/'result.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n');(folder/'section.md').write_text(data['raw_markdown'])
        print(json.dumps({'evidence_directory':str(folder),'word_count':data['word_count'],'elapsed_seconds':data['elapsed_seconds'],'automatic_section_checks_passed':data['automatic_section_checks_passed'],'checks':data['checks'],'failure':data['failure'],'section':data['raw_markdown']},ensure_ascii=False),flush=True)
    except ValueError:
        (folder/'stdout-unparsed.txt').write_text(result.stdout);print('Output was not valid result JSON; retained for inspection.',flush=True)
if result.stderr:print(result.stderr,file=sys.stderr)
sys.exit(result.returncode)
