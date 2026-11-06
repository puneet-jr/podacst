import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

import httpx
from spike.adapter import PiRPC, ProtocolError, RemoteError, decode_frame, local_environment
from spike.api import app


class FramingTests(unittest.TestCase):
    def test_unicode_separators_are_not_record_delimiters(self):
        raw = json.dumps({"type": "event", "text": "é\u2028行\u2029"}, ensure_ascii=False).encode() + b"\r\n"
        self.assertEqual(decode_frame(raw)["text"], "é\u2028行\u2029")

    def test_invalid_records_rejected(self):
        for raw in [b"no", b"[]", b'{"type":4}', b'\xff', b'{"type":"response","success":true}', b"x" * 1_048_577]:
            with self.subTest(raw=raw[:80]), self.assertRaises(ProtocolError):
                decode_frame(raw)

    def test_credentials_and_proxies_not_inherited(self):
        from unittest.mock import patch
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "mock-key", "HTTPS_PROXY": "mock-proxy"}):
            env = local_environment("/tmp/mock-config")
        self.assertNotIn("ANTHROPIC_API_KEY", env)
        self.assertNotIn("HTTPS_PROXY", env)
        self.assertEqual(env["PI_OFFLINE"], "1")


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.rpcs = []

    async def make(self, mode):
        rpc = PiRPC(Path(self.temp.name) / str(len(self.rpcs)), [sys.executable, str(Path(__file__).with_name("fake_pi.py")), mode])
        self.rpcs.append(rpc)
        await rpc.start()
        return rpc

    async def asyncTearDown(self):
        for rpc in self.rpcs:
            await rpc.close()
            self.assertIsNotNone(rpc.process.returncode)
            self.assertFalse(rpc.pending)
            self.assertTrue(all(t.done() for t in rpc.tasks))
        self.temp.cleanup()

    async def test_fragmented_multibyte_stream(self):
        rpc = await self.make("fragmented")
        result = await rpc.ask("fixture request")
        self.assertEqual(result["model_text"], "mock response")
        self.assertEqual(result["sources"], ["mock"])
        self.assertEqual(result["text"], "mock response [mock]")
        self.assertEqual(len(result["tools"]), 1)

    async def test_response_ids_allow_out_of_order_completion(self):
        rpc = await self.make("out-of-order")
        state, messages = await asyncio.gather(rpc.call("get_state", reorder=True), rpc.call("get_messages", reorder=True))
        self.assertEqual(state["messageCount"], 0)
        self.assertEqual(messages["messages"], [])

    async def test_rejected_prompt_is_not_success(self):
        rpc = await self.make("rejected")
        with self.assertRaises(RemoteError):
            await rpc.ask("fixture request")

    async def test_corrupt_streams_fail(self):
        for mode in ["malformed", "truncated", "oversize", "unknown-id"]:
            with self.subTest(mode=mode):
                rpc = await self.make(mode)
                with self.assertRaises(ProtocolError):
                    await asyncio.wait_for(rpc.ask("fixture request"), timeout=2)

    async def test_response_command_mismatch(self):
        with self.assertRaises(ProtocolError):
            await self.make("wrong-command")

    async def test_unsafe_tools_and_budgets(self):
        for mode in ["unsafe-tool", "tool-budget", "turn-budget"]:
            with self.subTest(mode=mode):
                rpc = await self.make(mode)
                with self.assertRaises(ProtocolError):
                    await rpc.ask("fixture request")

    async def test_model_and_tool_errors(self):
        for mode in ["model-error", "tool-error"]:
            with self.subTest(mode=mode):
                rpc = await self.make(mode)
                with self.assertRaises(RemoteError):
                    await rpc.ask("fixture request")

    async def test_shell_rpc_not_exposed(self):
        rpc = await self.make("normal")
        with self.assertRaises(ProtocolError):
            await rpc.call("bash", command="anything")

    async def test_timeout_reaps_stubborn_process(self):
        rpc = await self.make("stubborn")
        with self.assertRaises(TimeoutError):
            await asyncio.wait_for(rpc.ask("fixture request"), timeout=0.05)
        started = time.monotonic()
        await rpc.close()
        self.assertLess(time.monotonic() - started, 4)
        self.assertIsNotNone(rpc.process.returncode)

    async def test_task_cancellation_reaps_process(self):
        rpc = await self.make("stubborn")
        task = asyncio.create_task(rpc.ask("fixture request"))
        await asyncio.sleep(0.05)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        await rpc.close()
        self.assertIsNotNone(rpc.process.returncode)

    async def test_api_rejects_unbounded_input(self):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://fixture", trust_env=False) as client:
            for payload in [{"prompt": ""}, {"prompt": "x" * 601}, {"prompt": "x", "timeout_seconds": 91}]:
                result = await client.post("/spike/run", json=payload)
                self.assertEqual(result.status_code, 422)


if __name__ == "__main__":
    unittest.main(verbosity=2)
