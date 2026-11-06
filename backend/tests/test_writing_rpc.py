"""Explicit adapter boundary: normal retrieval still requires tools; pinned writing forbids them."""
import os
os.environ.setdefault('POSTGRES_PASSWORD','unit-test-placeholder')
from pathlib import Path
import unittest
from unittest.mock import AsyncMock
from backend.app.agent import PiRPC,RemoteError,ProtocolError


class WritingRPC(unittest.IsolatedAsyncioTestCase):
    def adapter(self,require_tool):
        rpc=PiRPC(Path('/unused-mock-log'),tool_name='search_transcripts',require_tool=require_tool)
        rpc.call=AsyncMock(side_effect=[{}, {'messages':[{'role':'assistant','content':[{'type':'text','text':'{"body":"Synthetic fixture output."}'}],'stopReason':'stop'}]}])
        return rpc

    async def test_existing_retrieval_default_still_rejects_toolless_output(self):
        rpc=self.adapter(True);await rpc.events.put({'type':'agent_settled'})
        with self.assertRaises(RemoteError):await rpc.ask('Mock prompt')

    async def test_explicit_snapshot_writing_returns_actual_model_text_without_fake_tool_trace(self):
        rpc=self.adapter(False);await rpc.events.put({'type':'agent_settled'})
        result=await rpc.ask('Mock pinned-source prompt')
        self.assertEqual(result['tools'],[]);self.assertEqual(result['model_text'],'{"body":"Synthetic fixture output."}')

    async def test_writing_cannot_execute_an_unexpected_tool(self):
        rpc=self.adapter(False);await rpc.events.put({'type':'tool_execution_start','toolName':'search_transcripts'})
        with self.assertRaises(ProtocolError):await rpc.ask('Mock pinned-source prompt')
