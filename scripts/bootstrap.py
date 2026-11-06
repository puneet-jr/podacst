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
if '--prepare-only' in sys.argv:
    sys.exit(0)
subprocess.run([sys.executable, 'scripts/docker.py', 'compose', 'config', '--quiet'], check=True)
subprocess.run([sys.executable, 'scripts/docker.py', 'compose', 'up', '-d', '--build'], check=True)
print('Local workspace: http://localhost:8080. Check /api/health/ready before use. Existing databases and volumes preserved.')
