"""Fetch an immutable public transcript snapshot into ignored local cache; never push."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

SOURCE = "https://github.com/ChatPRD/lennys-podcast-transcripts"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--revision',required=True)
    args=parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}',args.revision):
        parser.error('Pass an exact 40-character source commit SHA')
    root=Path('.cache/corpus')/args.revision
    if root.exists():
        raise SystemExit('Snapshot path already exists; preserve it and inspect its manifest instead of overwriting')
    root.mkdir(parents=True)
    prefix=['git','-c','credential.helper=','-c','core.hooksPath=/dev/null','-C',str(root)]
    subprocess.run([*prefix,'init','--quiet'],check=True)
    subprocess.run([*prefix,'fetch','--depth','1',SOURCE+'.git',args.revision],check=True)
    subprocess.run([*prefix,'checkout','--quiet','--detach','FETCH_HEAD'],check=True)
    actual=subprocess.check_output([*prefix,'rev-parse','HEAD'],text=True).strip()
    if actual!=args.revision:raise RuntimeError('Fetched revision mismatch')
    files=sorted(p for p in (root/'episodes').rglob('*') if p.is_file() and p.name.casefold()=='transcript.md')
    manifest={'source_url':SOURCE,'corpus_revision':actual,'captured_at':datetime.now(timezone.utc).isoformat(),'discovered':len(files),'files':[{'path':str(p.relative_to(root)),'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files]}
    Path(str(root)+'.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'snapshot':str(root),'revision':actual,'discovered':len(files),'manifest':str(root)+'.manifest.json'}))


if __name__=='__main__':main()
