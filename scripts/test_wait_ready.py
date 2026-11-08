"""Isolated polling/transport tests; no Docker, database or model requests."""
import contextlib
import io
import json
import subprocess
import unittest
from unittest.mock import patch
from scripts import wait_ready as w


class PollTests(unittest.TestCase):
    def run_poll(self, results):
        clock = [0.0]
        calls = []
        def probe(url, timeout):
            calls.append(timeout)
            return results[min(len(calls) - 1, len(results) - 1)]
        def sleep(seconds): clock[0] += seconds
        return w.wait_ready('http://localhost/api/health/ready', 3, 2, 1, probe, lambda: clock[0], sleep), calls

    def test_transient_startup_sequence(self):
        ready = {'curl_exit': 0, 'http': 200, 'status': 'ready'}
        result, calls = self.run_poll([{'curl_exit': 7}, {'curl_exit': 52}, {'curl_exit': 0, 'http': 503, 'status': 'not_ready'}, ready])
        # All three failed probes exhaust this deadline; no late success allowed.
        self.assertFalse(result['ready'])
        self.assertEqual(result['last_probe']['status'], 'not_ready')
        result, calls = self.run_poll([{'curl_exit': 52}, {'curl_exit': 0, 'http': 503, 'status': 'not_ready'}, ready])
        self.assertTrue(result['ready'])
        self.assertEqual(calls, [2, 2, 1])

    def test_late_ready_is_not_success(self):
        now = [0.0]
        def late(url, timeout):
            now[0] = 4
            return {'curl_exit': 0, 'http': 200, 'status': 'ready'}
        result = w.wait_ready('http://localhost', 3, 2, 1, late, lambda: now[0], lambda _: None)
        self.assertFalse(result['ready'])

    def test_200_not_ready_is_not_success(self):
        result, _ = self.run_poll([{'curl_exit': 0, 'http': 200, 'status': 'not_ready'}])
        self.assertFalse(result['ready'])
        self.assertEqual(result['elapsed_seconds'], 3)

    def test_ready_body_on_http_error_is_not_success(self):
        result, _ = self.run_poll([{'curl_exit': 0, 'http': 503, 'status': 'ready'}])
        self.assertFalse(result['ready'])

    @patch.object(w.subprocess, 'run')
    def test_transport_codes_and_timeouts(self, run):
        for code in [7, 52, 28]:
            run.return_value = subprocess.CompletedProcess([], code, '\n000', 'private diagnostic')
            self.assertEqual(w.probe('http://localhost', 0.1)['curl_exit'], code)
        run.side_effect = subprocess.TimeoutExpired('curl', 0.1)
        self.assertEqual(w.probe('http://localhost', 0.1)['code'], 'probe_timeout')

    @patch.object(w.subprocess, 'run')
    def test_json_validation_and_safe_summary(self, run):
        for body in ['garbage', '[]']:
            run.return_value = subprocess.CompletedProcess([], 0, body+'\n200', '')
            self.assertEqual(w.probe('http://localhost', 1)['code'], 'invalid_readiness_json')
        body = {'status': 'ready', 'secret': 'never echo', 'checks': {'database': {'ready': True, 'private': 'never echo'}}}
        run.return_value = subprocess.CompletedProcess([], 0, json.dumps(body)+'\n200', '')
        result = w.probe('http://localhost', 1)
        self.assertEqual(result['status'], 'ready')
        self.assertNotIn('never echo', json.dumps(result))
        self.assertEqual(run.call_args.kwargs['timeout'], 1)

    @patch.object(w, 'wait_ready', return_value={'ready': False, 'last_probe': {'curl_exit': 52}})
    def test_cli_deadline_exit_and_log_hint(self, wait):
        output = io.StringIO()
        with patch('sys.argv', ['wait_ready.py']), contextlib.redirect_stdout(output):
            self.assertEqual(w.main(), 1)
        self.assertIn('52', output.getvalue())
        self.assertIn('compose logs --tail 80 api', output.getvalue())


if __name__ == '__main__':
    unittest.main()
