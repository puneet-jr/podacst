"""Bounded, local readiness polling. Does not run migrations or print payloads."""
import argparse
import json
import subprocess
import time
from urllib.parse import urlsplit


def probe(url, timeout):
    command = ['curl', '--noproxy', '*', '--silent', '--show-error',
               '--connect-timeout', str(timeout), '--max-time', str(timeout),
               '--max-filesize', '16384', '--write-out', '\n%{http_code}', url]
    try:
        response = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {'curl_exit': None, 'code': 'probe_timeout'}
    except OSError:
        return {'curl_exit': None, 'code': 'curl_unavailable'}
    body, _, http = response.stdout.rpartition('\n')
    result = {'curl_exit': response.returncode, 'http': int(http) if http.isdigit() else None}
    if response.returncode:
        result['code'] = 'transport_error'
        return result
    try:
        value = json.loads(body)
        if not isinstance(value, dict):
            raise ValueError('Expected object')
    except ValueError:
        result['code'] = 'invalid_readiness_json'
        return result
    result['status'] = value.get('status') if value.get('status') in {'ready', 'not_ready'} else 'unknown'
    result['checks'] = {k: {'ready': v.get('ready') is True} for k, v in value.get('checks', {}).items()
                        if k in {'database', 'agent', 'ollama', 'provider', 'corpus'} and isinstance(v, dict)} if isinstance(value.get('checks'), dict) else {}
    return result


def wait_ready(url, deadline_seconds=90, attempt_timeout=3, interval=1,
               probe_fn=probe, clock=time.monotonic, sleep=time.sleep):
    start = clock()
    end = start + deadline_seconds
    attempts = 0
    last = {'code': 'not_probed'}
    while clock() < end:
        remaining = end - clock()
        if remaining <= 0:
            break
        attempts += 1
        last = probe_fn(url, min(attempt_timeout, remaining))
        if clock() <= end and last.get('curl_exit') == 0 and last.get('http') == 200 and last.get('status') == 'ready':
            return {'ready': True, 'attempts': attempts, 'elapsed_seconds': round(clock() - start, 3), 'last_probe': last}
        remaining = end - clock()
        if remaining > 0:
            sleep(min(interval, remaining))
    return {'ready': False, 'attempts': attempts, 'elapsed_seconds': round(clock() - start, 3), 'last_probe': last}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8000/api/health/ready')
    parser.add_argument('--deadline-seconds', type=float, default=90)
    parser.add_argument('--attempt-timeout', type=float, default=3)
    args = parser.parse_args()
    url = urlsplit(args.url)
    if (url.scheme != 'http' or url.hostname not in {'localhost', '127.0.0.1', '::1'}
            or url.username or url.password or url.query or url.fragment or url.path != '/api/health/ready'):
        parser.error('Use the local HTTP /api/health/ready endpoint without credentials or query parameters')
    if not (0 < args.deadline_seconds <= 300 and 0 < args.attempt_timeout <= 10):
        parser.error('Deadline must be 0–300 seconds and attempt timeout 0–10 seconds (exclusive of zero)')
    result = wait_ready(args.url, args.deadline_seconds, args.attempt_timeout)
    print(json.dumps(result), flush=True)
    if not result['ready']:
        print('Readiness deadline reached. Inspect API startup with: python3 scripts/docker.py compose logs --tail 80 api')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
