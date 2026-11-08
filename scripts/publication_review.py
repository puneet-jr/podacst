"""Review candidate or staged Git blobs without printing credential values."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess


def git(*args):return subprocess.run(['git',*args],capture_output=True,check=True).stdout


def review(staged=False):
    files=git('diff','--cached','--name-only','--diff-filter=ACMR','-z').decode().split('\0') if staged else git('ls-files','--cached','--others','--exclude-standard','-z').decode().split('\0')
    files=sorted(set(p for p in files if p));configured=[]
    if Path('.env').exists():
        for line in Path('.env').read_text().splitlines():
            if '=' not in line or line.lstrip().startswith('#'):continue
            key,value=line.split('=',1);value=value.strip().strip('"\'')
            if any(k in key.upper() for k in ('PASSWORD','API_KEY','TOKEN','SECRET')) and len(value)>=12:configured.append(value.encode())
    for key in ('OPENROUTER_API_KEY','ANTHROPIC_API_KEY','OPENAI_API_KEY','GEMINI_API_KEY','GOOGLE_API_KEY','GITHUB_TOKEN','GH_TOKEN','AWS_SECRET_ACCESS_KEY'):
        if len(os.environ.get(key,''))>=12:configured.append(os.environ[key].encode())
    findings=[];hashes={};limited_quotes=0
    deny_parts={'.cache','node_modules','__pycache__','.git','.aws','.codex','.agents','.ollama','.huggingface','corpus','private','raw-exports','models','weights','dist'}
    token_patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b',rb'\bgithub_pat_[A-Za-z0-9_]{25,}\b',rb'\bsk-(?:ant-)?[A-Za-z0-9_-]{24,}\b',rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b']
    for name in files:
        path=Path(name)
        if path.is_symlink():findings.append({'file':name,'kind':'symlink_requires_explicit_review'});continue
        if any(p in deny_parts or p.startswith('.venv') for p in path.parts) or path.name.startswith('.env') and path.name!='.env.example' or path.suffix.lower() in {'.pdf','.pyc','.gguf','.safetensors','.ckpt','.pem','.key','.p12','.pfx'}:
            findings.append({'file':name,'kind':'excluded_path'});continue
        data=git('show',':'+name) if staged else path.read_bytes();hashes[name]=sha256(data).hexdigest()
        if len(data)>8_000_000:findings.append({'file':name,'kind':'unexpected_large_file'})
        if b'\0' in data:findings.append({'file':name,'kind':'unexpected_binary'})
        if any(secret in data for secret in configured):findings.append({'file':name,'kind':'configured_secret_match'})
        for pattern in token_patterns:
            if re.search(pattern,data):findings.append({'file':name,'kind':'credential_pattern_match'});break
        if name.endswith(('.json','.jsonl')):
            def walk(v):
                if isinstance(v,dict):
                    for k,x in v.items():
                        if k in {'original_text','evidence_text'} and isinstance(x,str) and len(x)>600:findings.append({'file':name,'kind':'full_source_payload'})
                        walk(x)
                elif isinstance(v,list):
                    for x in v:walk(x)
            try:
                if name.endswith('.json'):walk(json.loads(data))
                else:
                    for line in data.decode().splitlines():walk(json.loads(line))
            except (ValueError,UnicodeDecodeError):findings.append({'file':name,'kind':'invalid_json_evidence'})
    return {'reviewed_at':datetime.now(timezone.utc).isoformat(),'scope':'staged Git blobs' if staged else 'all publishable working-tree files','file_count':len(files),'findings':findings,'configured_values_checked_without_disclosure':len(set(configured)),'file_sha256':hashes,'passed':not findings,'limits':'Exact configured-secret and common credential pattern checks plus path/content review; not a claim that pattern matching establishes universal security.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--staged',action='store_true');p.add_argument('--output');args=p.parse_args()
    r=review(args.staged)
    if args.output:Path(args.output).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='file_sha256'},indent=2))
    if not r['passed']:raise SystemExit(1)
