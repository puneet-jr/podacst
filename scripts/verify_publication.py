"""Read-only release-tree audit; never prints credential values."""
import argparse,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--tree',required=True);p.add_argument('--revision',required=True);p.add_argument('--secret-env',action='append',default=[]);p.add_argument('--baseline',required=True);p.add_argument('--output',required=True);args=p.parse_args();tree=Path(args.tree);baseline=json.loads(Path(args.baseline).read_text())['source_file_hashes'];secrets=[]
for envpath in [Path('.env'),*[Path(n) for n in args.secret_env]]:
 if envpath.exists():
  for line in envpath.read_text().splitlines():
   if '=' not in line or line.lstrip().startswith('#'):continue
   key,value=line.split('=',1);value=value.strip().strip('"\'')
   if any(k in key.upper() for k in ['KEY','TOKEN','SECRET','PASSWORD']) and len(value)>=12:secrets.append(value.encode())
patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b',rb'\bgithub_pat_[A-Za-z0-9_]{25,}\b',rb'\bsk-(?:or-v1-|ant-)?[A-Za-z0-9_-]{24,}\b',rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'];findings=[];hashes={}
for path in sorted(tree.rglob('*')):
 if not path.is_file():continue
 name=str(path.relative_to(tree));data=path.read_bytes();hashes[name]=hashlib.sha256(data).hexdigest()
 if path.is_symlink() or any(x in {'.git','.cache','node_modules','corpus','models','dist','__pycache__'} or x.startswith('.venv') for x in path.relative_to(tree).parts) or path.name.startswith('.env') and path.name!='.env.example' or path.suffix in {'.pdf','.gguf','.pyc','.pem','.key'}:findings.append({'file':name,'kind':'excluded_path'})
 if any(v in data for v in secrets):findings.append({'file':name,'kind':'configured_secret'})
 if any(re.search(pattern,data) for pattern in patterns):findings.append({'file':name,'kind':'credential_pattern'})
 if b'\0' in data or len(data)>8_000_000:findings.append({'file':name,'kind':'binary_or_large'})
 if name.startswith('docs/agent-transcripts/') and path.suffix in {'.json','.jsonl'}:
  def walk(v):
   if isinstance(v,dict):
    for k,x in v.items():
     if k in {'original_text','evidence_text','raw_model_text','model_text','stdout','stderr','context_text','authorization','headers','request_body'} and isinstance(x,str) and x:findings.append({'file':name,'kind':'historical_payload_field','field':k})
     walk(x)
   elif isinstance(v,list):
    for x in v:walk(x)
  try:
   for value in ([json.loads(data)] if path.suffix=='.json' else [json.loads(line) for line in data.decode().splitlines() if line.strip()]):walk(value)
  except (ValueError,UnicodeDecodeError):findings.append({'file':name,'kind':'invalid_json'})
matches=0
for name,expected in baseline.items():
 if hashes.get(name)==expected:matches+=1
 else:findings.append({'file':name,'kind':'baseline_runtime_mismatch'})
for key in ['ANTHROPIC_API_KEY','OPENROUTER_API_KEY']:
 values=[line.split('=',1)[1] for line in (tree/'.env.example').read_text().splitlines() if line.startswith(key+'=')]
 if values!=['']:findings.append({'file':'.env.example','kind':'nonempty_key_example','field':key})
result={'base_revision':args.revision,'file_count':len(hashes),'configured_values_checked':len(set(secrets)),'baseline_runtime_hashes_matched':matches,'expected_runtime_hashes':len(baseline),'findings':findings,'passed':not findings,'scope':'Standalone export only; exact configured values, common credential patterns, excluded paths, raw historical payload keys and baseline hashes. Not a universal security or redistribution-rights assurance.','file_sha256':hashes};Path(args.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='file_sha256'}));raise SystemExit(0 if result['passed'] else 1)
