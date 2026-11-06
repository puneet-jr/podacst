import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

os.environ.setdefault("POSTGRES_PASSWORD", "unit-test-placeholder")
from backend.app.agent import PiRPC, ProtocolError, decode_frame, local_environment
from backend.app.config import Settings


class ConfigTests(unittest.TestCase):
    def test_local_endpoint_and_provider_policy(self):
        for url in ["https://cloud.invalid", "http://user:secret@localhost:11434", "http://host.docker.internal:11434/path"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                Settings(db_password="fixture", ollama_url=url)
        with self.assertRaises(ValueError):
            Settings(db_password="fixture", default_provider="anthropic")
        self.assertEqual(Settings(db_password="fixture").ollama_url, "http://host.docker.internal:11434")

    def test_secret_representation_and_child_environment(self):
        self.assertNotIn("fixture-password", repr(Settings(db_password="fixture-password")))
        env = local_environment("/tmp/fixture")
        self.assertNotIn("POSTGRES_PASSWORD", env)
        self.assertNotIn("ANTHROPIC_API_KEY", env)
        self.assertEqual(env["PI_OFFLINE"], "1")

    def test_strict_frames(self):
        value = {"type": "event", "text": "é\u2028行\u2029"}
        self.assertEqual(decode_frame(json.dumps(value, ensure_ascii=False).encode()+b"\r\n"), value)
        for raw in [b"bad", b"[]", b'{"type":"response"}', b"x"*1048577]:
            with self.subTest(raw=raw[:40]), self.assertRaises(ProtocolError):
                decode_frame(raw)


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_copied_boundary_fragmentation_and_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            rpc = PiRPC(Path(directory)/"logs", [sys.executable,str(Path(__file__).with_name('fake_rpc.py')),"fragmented"])
            try:
                await rpc.start()
                result = await rpc.ask("fixture")
                self.assertEqual(result['sources'], ['mock'])
                with self.assertRaises(ProtocolError):
                    await rpc.call('bash', command='anything')
            finally:
                await rpc.close()
            self.assertIsNotNone(rpc.process.returncode)
            self.assertFalse(rpc.pending)

    async def test_stubborn_process_reaped_after_timeout(self):
        with tempfile.TemporaryDirectory() as directory:
            rpc = PiRPC(Path(directory)/"logs", [sys.executable,str(Path(__file__).with_name('fake_rpc.py')),"stubborn"])
            try:
                await rpc.start()
                with self.assertRaises(TimeoutError):
                    await asyncio.wait_for(rpc.ask('fixture'), .05)
            finally:
                await rpc.close()
            self.assertIsNotNone(rpc.process.returncode)
