"""Provider policy mocks and metadata privacy; not live cloud evidence."""
import os
os.environ.setdefault('POSTGRES_PASSWORD','unit-test-placeholder')
import io,json,logging,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from backend.app.agent import PiRPC,ProviderUnavailable,local_environment
from backend.app.config import Settings
from backend.app.observability import emit,logger,request_id,session_id

class ProviderPolicy(unittest.IsolatedAsyncioTestCase):
    async def test_missing_cloud_key_starts_no_process_and_writes_no_trace(self):
        with tempfile.TemporaryDirectory() as d:
            rpc=PiRPC(Path(d)/'absent',settings=Settings(db_password='fixture',default_provider='anthropic'))
            with self.assertRaises(ProviderUnavailable):await rpc.start()
            self.assertIsNone(rpc.process);self.assertFalse(rpc.log_dir.exists())
            await rpc.close()

    def test_settings_select_exact_model_without_fallback(self):
        local=Settings(db_password='fixture',anthropic_api_key='SYNTHETIC_KEY_DO_NOT_LOG')
        cloud=local.model_copy(update={'default_provider':'anthropic'})
        self.assertEqual(local.selected_model(),'qwen3:0.6b');self.assertEqual(local.selected_model(True),'qwen3:1.7b')
        self.assertEqual(cloud.selected_model(True),cloud.cloud_model)
        self.assertEqual(cloud.model_base_url,'https://api.anthropic.com')
        self.assertNotIn('SYNTHETIC_KEY_DO_NOT_LOG',repr(cloud))
        with patch.dict(os.environ,{'ANTHROPIC_API_KEY':'SYNTHETIC_AMBIENT','HTTP_PROXY':'http://proxy.invalid'}):
            env=local_environment('/tmp/fixture');self.assertNotIn('ANTHROPIC_API_KEY',env);self.assertNotIn('HTTP_PROXY',env)
        for model in ['!echo secret','$ENV','x'*121]:
            with self.assertRaises(ValueError):Settings(db_password='fixture',cloud_model=model)

    def test_structured_events_drop_payloads_and_retain_correlation(self):
        stream=io.StringIO();h=logging.StreamHandler(stream);logger.addHandler(h);prior=logger.level;logger.setLevel(logging.INFO)
        rt=request_id.set('fixture-request');st=session_id.set('fixture-session')
        try:
            emit('render_operation',code='artifact_too_large',duration_ms=1.2,source_ids=['00000000-0000-4000-8000-000000000001'],prompt='SENSITIVE_PROMPT',original_text='SENSITIVE_SOURCE',api_key='SENSITIVE_KEY')
            data=json.loads(stream.getvalue());self.assertEqual(data['request_id'],'fixture-request');self.assertEqual(data['session_id'],'fixture-session');self.assertEqual(data['duration_ms'],1.2)
            self.assertEqual(data['source_ids'],['00000000-0000-4000-8000-000000000001']);self.assertNotIn('SENSITIVE',stream.getvalue())
        finally:request_id.reset(rt);session_id.reset(st);logger.removeHandler(h);logger.setLevel(prior)

    async def test_default_protocol_projection_excludes_model_text(self):
        import sys
        with tempfile.TemporaryDirectory() as d:
            rpc=PiRPC(Path(d)/'logs',[sys.executable,str(Path(__file__).with_name('fake_rpc.py')),'fragmented'],settings=Settings(db_password='fixture'))
            try:
                await rpc.start();await rpc.ask('SENSITIVE_PROMPT_SENT_ONLY_TO_CHILD')
            finally:await rpc.close()
            output=(rpc.log_dir/'stdout.jsonl').read_text()+(rpc.log_dir/'stderr.log').read_text()
            self.assertNotIn('SENSITIVE_PROMPT',output);self.assertNotIn('mock response',output)
            for row in (rpc.log_dir/'stdout.jsonl').read_text().splitlines():self.assertLessEqual(set(json.loads(row)),{'type','id','command','success','toolName'})

    async def test_essay_database_failure_always_releases_lock(self):
        import asyncio
        from uuid import uuid4
        from unittest.mock import AsyncMock
        from backend.app.evidence_first import EvidenceFirstService
        from sqlalchemy.exc import OperationalError
        service=EvidenceFirstService(None,Settings(db_password='fixture'),asyncio.Lock())
        run={'id':uuid4(),'session_id':uuid4(),'metadata':{},'request':{'timeout_seconds':1,'topic':'fixture'}}
        with patch('backend.app.evidence_first.collect_evidence',side_effect=OperationalError('fixture',{},None)),patch('backend.app.evidence_first.save_progress',side_effect=OperationalError('fixture',{},None)):
            with self.assertRaises(OperationalError):await service.execute(run,AsyncMock())
        self.assertFalse(service.lock.locked());self.assertFalse(service.tasks)

    async def test_cloud_adapter_reports_actual_provider_in_result(self):
        from unittest.mock import AsyncMock
        rpc=PiRPC(Path('/unused'),require_tool=False,settings=Settings(db_password='fixture',default_provider='anthropic',anthropic_api_key='synthetic'))
        rpc.call=AsyncMock(side_effect=[{}, {'messages':[{'role':'assistant','stopReason':'stop','content':[{'type':'text','text':'Fixture advice only.'}]}]}])
        await rpc.events.put({'type':'agent_settled'})
        result=await rpc.ask('Synthetic fixture, not a cloud request')
        self.assertEqual(result['provider'],'anthropic-cloud');self.assertEqual(result['model'],rpc.settings.cloud_model)

    async def test_openrouter_uses_its_own_secret_model_and_endpoint(self):
        local=Settings(db_password='fixture',anthropic_api_key='synthetic-anthropic')
        missing=local.model_copy(update={'default_provider':'openrouter'})
        with self.assertRaises(ValueError):missing.require_provider()
        configured=Settings(db_password='fixture',default_provider='openrouter',openrouter_api_key='SYNTHETIC_ROUTER_KEY')
        configured.require_provider();self.assertEqual(configured.provider_id,'openrouter');self.assertEqual(configured.model_base_url,'https://openrouter.ai/api/v1');self.assertEqual(configured.provider_api,'openai-completions');self.assertEqual(configured.selected_model(True),'google/gemini-2.5-flash-lite')
        self.assertNotIn('SYNTHETIC_ROUTER_KEY',repr(configured))
        self.assertNotIn('OPENROUTER_API_KEY',local_environment('/tmp/fixture'))
        with tempfile.TemporaryDirectory() as d:
            rpc=PiRPC(Path(d)/'missing',settings=missing)
            with self.assertRaises(ProviderUnavailable):await rpc.start()
            self.assertIsNone(rpc.process);self.assertFalse(rpc.log_dir.exists())

    async def test_provider_failure_exposes_only_safe_status_code(self):
        from unittest.mock import AsyncMock
        from backend.app.agent import RemoteError
        rpc=PiRPC(Path('/unused'),require_tool=False)
        rpc.call=AsyncMock(side_effect=[{}, {'messages':[{'role':'assistant','stopReason':'error','errorMessage':'402 Payment required SENSITIVE_PROVIDER_DETAIL'}]}])
        await rpc.events.put({'type':'agent_settled'})
        with self.assertRaises(RemoteError) as caught:await rpc.ask('fixture')
        self.assertEqual(caught.exception.code,'provider_http_402');self.assertNotIn('SENSITIVE',str(caught.exception))
