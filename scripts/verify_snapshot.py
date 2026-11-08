"""Read-only verification of an existing pinned corpus; no downloads/rewrites."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',required=True);args=p.parse_args();root=Path(args.root)
m=json.loads(Path(str(root)+'.manifest.json').read_text());revision=m['corpus_revision']
assert re.fullmatch('[0-9a-f]{40}',revision)
assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==revision
seen=set()
for f in m['files']:
 name=f['path'];assert re.fullmatch(r'episodes/[\w-]+/transcript\.md',name);assert name not in seen;seen.add(name)
 assert hashlib.sha256((root/name).read_bytes()).hexdigest()==f['sha256'],name
assert len(seen)==m['discovered'];print(json.dumps({'corpus_revision':revision,'discovered':len(seen),'all_source_hashes_match':True}))
