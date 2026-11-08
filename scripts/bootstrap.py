"""Local-only setup. Never resets databases, removes volumes or overwrites .env."""
import os
from pathlib import Path
import secrets
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
os.chdir(root)
if not Path('.env').exists():
    content = Path('.env.example').read_text().replace('replace-with-generated-local-password', secrets.token_urlsafe(24))
    fd = os.open('.env', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        stream.write(content)
    print('Created ignored .env with a generated local database credential. No values printed.', flush=True)
values = dict(line.split('=', 1) for line in Path('.env').read_text().splitlines() if line and not line.startswith('#') and '=' in line)
password = values.get('POSTGRES_PASSWORD', '')
if len(password) < 16 or password.startswith('replace-with-'):
    raise SystemExit('Set a generated local POSTGRES_PASSWORD in the ignored .env; placeholder credentials are rejected. No values printed.')
provider=values.get('DEFAULT_PROVIDER','ollama')
if provider not in {'ollama','anthropic','openrouter'}:raise SystemExit('DEFAULT_PROVIDER must be ollama, anthropic or openrouter. No values printed.')
if values.get('PRIVATE_RPC_TRACES','false').lower() not in {'true','false'}:raise SystemExit('PRIVATE_RPC_TRACES must be true or false.')
for name in ('GENERATION_MODEL','ESSAY_MODEL','EMBEDDING_MODEL','CLOUD_MODEL','OPENROUTER_MODEL'):
    if name in values and not __import__('re').fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,119}',values[name]):raise SystemExit('Invalid bounded model identifier. No values printed.')
if '--prepare-only' in sys.argv:
    sys.exit(0)
subprocess.run([sys.executable, 'scripts/docker.py', 'compose', 'config', '--quiet'], check=True)
subprocess.run([sys.executable, 'scripts/docker.py', 'compose', 'up', '-d', '--build'], check=True)
print('Local workspace: http://localhost:8080. Check /api/health/ready before use. Existing databases and volumes preserved.')
