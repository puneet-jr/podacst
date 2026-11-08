"""Failure/recovery against isolated PostgreSQL. No normal DB/daemon is stopped."""
import os,io,json,logging,time,unittest
from unittest.mock import patch
from uuid import uuid4
from sqlalchemy import text
from fastapi.testclient import TestClient
if not os.environ.get('POSTGRES_DB','').startswith('lenny_contract_'):raise RuntimeError('New retained contract DB required')
from backend.app import main
from backend.app.db import make_engine
from backend.app.retrieval import SearchRequest,search,RetrievalError
from backend.app.observability import request_id,session_id

class OperationsDatabase(unittest.TestCase):
    def setUp(self):
        self.client=TestClient(main.app);self.addCleanup(self.client.close)
        self.stream=io.StringIO();self.handler=logging.StreamHandler(self.stream);main.logger.addHandler(self.handler)
        self.addCleanup(main.logger.removeHandler,self.handler)
        self.sid=self.client.post('/api/sessions',json={'title':'Isolated operational fixture'}).json()['id']

    def record(self,name,response,recovery):
        rows=[json.loads(x) for x in self.stream.getvalue().splitlines() if x.startswith('{')]
        self.assertNotIn('SENSITIVE',self.stream.getvalue());self.assertNotIn(main.settings.db_password.get_secret_value(),self.stream.getvalue())
        self.assertTrue(any(r.get('request_id')==response.headers['X-Request-ID'] for r in rows))
        print(json.dumps({'phase9_case':name,'database':os.environ['POSTGRES_DB'],'http':response.status_code,'request_id':response.headers['X-Request-ID'],'error':response.json().get('error',{}).get('code'),'recovery_http':recovery.status_code,'events':rows}))

    def test_absent_cloud_key_is_visible_and_has_zero_writes_then_recovers(self):
        bad=main.settings.model_copy(update={'default_provider':'anthropic','anthropic_api_key':__import__('pydantic').SecretStr('')})
        body={'content':'Synthetic operational request','client_message_id':str(uuid4()),'retrieval_mode':'hybrid'}
        with patch.object(main,'settings',bad):
            r=self.client.post(f'/api/sessions/{self.sid}/answers',json=body)
            self.assertEqual(r.status_code,503);self.assertEqual(r.json()['error']['code'],'cloud_key_missing')
            essay=self.client.post(f'/api/sessions/{self.sid}/essays',json={'topic':'Synthetic cloud essay','audience':'Product managers','client_message_id':str(uuid4())});self.assertEqual(essay.status_code,503)
            ready=self.client.get('/api/health/ready');self.assertEqual(ready.status_code,503);self.assertEqual(ready.json()['checks']['provider']['code'],'cloud_key_missing')
            provider=self.client.get('/api/providers').json();self.assertEqual(provider['selected'],'anthropic');self.assertFalse(provider['automatic_fallback']);self.assertNotIn('api_key',provider)
        recovered=self.client.get('/api/providers');self.assertEqual(recovered.json()['selected'],'ollama')
        self.assertEqual(self.client.get(f'/api/sessions/{self.sid}/messages').json(),[])
        self.record('absent_cloud_key',r,recovered)

    def test_openrouter_key_missing_rejects_before_writes(self):
        from pydantic import SecretStr
        selected=main.settings.model_copy(update={'default_provider':'openrouter','openrouter_api_key':SecretStr('')})
        with patch.object(main,'settings',selected):
            providers=self.client.get('/api/providers').json();self.assertEqual(providers['selected'],'openrouter');self.assertIn('OpenRouter',providers['privacy']);self.assertFalse(providers['automatic_fallback'])
            response=self.client.post(f'/api/sessions/{self.sid}/answers',json={'content':'Synthetic router question','client_message_id':str(uuid4())});self.assertEqual(response.status_code,503);self.assertEqual(response.json()['error']['code'],'cloud_key_missing')
            self.assertEqual(self.client.get(f'/api/sessions/{self.sid}/messages').json(),[])
        self.record('openrouter_key_missing',response,self.client.get('/api/providers'))

    def test_real_unreachable_postgres_endpoint_and_recovery(self):
        bad=make_engine(main.settings.model_copy(update={'db_host':'127.0.0.1','db_port':1}))
        try:
            with patch.object(main,'engine',bad):
                r=self.client.get(f'/api/sessions/{self.sid}/essays');self.assertEqual(r.status_code,503);self.assertEqual(r.json()['error']['code'],'database_unavailable')
                ready=self.client.get('/api/health/ready');self.assertEqual(ready.status_code,503);self.assertFalse(ready.json()['checks']['database']['ready'])
                self.assertEqual(self.client.get('/api/health/live').status_code,200)
        finally:bad.dispose()
        recovery=self.client.get(f'/api/sessions/{self.sid}/essays');self.assertEqual(recovery.status_code,200);self.record('postgres_unreachable',r,recovery)

    def test_real_unreachable_ollama_endpoint_and_recovery(self):
        with patch.object(main,'settings',main.settings.model_copy(update={'ollama_url':'http://127.0.0.1:1'})):
            r=self.client.get('/api/health/ready');self.assertEqual(r.status_code,503);self.assertEqual(r.json()['checks']['ollama']['code'],'ollama_unavailable')
        recovered=self.client.get('/api/health/ready');self.assertTrue(recovered.json()['checks']['ollama']['reachable_from_api']);self.record('ollama_unreachable',r,recovered)

    def test_real_missing_model_and_embedding_mismatch_recovery(self):
        for name,changes,field in [('missing_model',{'generation_model':'phase9-not-installed','essay_model':'phase9-not-installed'},'generation_model_available'),('embedding_mismatch',{'embedding_dimensions':767},'embedding_dimensions_compatible')]:
            with patch.object(main,'settings',main.settings.model_copy(update=changes)):
                r=self.client.get('/api/health/ready');self.assertEqual(r.status_code,503);self.assertFalse(r.json()['checks']['ollama'][field])
            recovered=self.client.get('/api/health/ready');self.assertTrue(recovered.json()['checks']['ollama'][field]);self.record(name,r,recovered)

    def test_empty_corpus_is_honest_and_recovers(self):
        with main.engine.begin() as c:
            active=list(c.scalars(text('SELECT id FROM chunks WHERE active')));c.execute(text('UPDATE chunks SET active=false WHERE active'))
        try:
            r=self.client.get('/api/health/ready');self.assertFalse(r.json()['checks']['corpus']['ready']);self.assertEqual(r.json()['checks']['corpus']['status'],'empty');self.assertFalse(r.json()['product_ready'])
        finally:
            with main.engine.begin() as c:
                for id in active:c.execute(text('UPDATE chunks SET active=true WHERE id=:id'),{'id':id})
        recovered=self.client.get('/api/health/ready');self.record('empty_corpus',r,recovered)

    def test_malformed_oversized_artifact_has_correlated_error_and_recovery(self):
        message=self.client.post(f'/api/sessions/{self.sid}/messages',json={'content':'Synthetic document fixture','client_message_id':str(uuid4())}).json()
        # Only a completed assistant reply can be formatted.
        with main.engine.begin() as c:c.execute(text("UPDATE messages SET role='assistant' WHERE id=:id"),{'id':message['id']})
        a=self.client.post(f'/api/sessions/{self.sid}/artifacts',json={'message_id':message['id'],'format':'html'});self.assertEqual(a.status_code,201,a.text)
        aid=a.json()['id'];path=f'/api/sessions/{self.sid}/artifacts/{aid}';original=a.json()['content']
        with main.engine.begin() as c:c.execute(text('UPDATE artifacts SET content=:body WHERE id=:id'),{'body':'SENSITIVE'+('x'*100001),'id':aid})
        try:
            r=self.client.get(path);self.assertEqual(r.status_code,422);self.assertEqual(r.json()['error']['code'],'artifact_too_large')
        finally:
            with main.engine.begin() as c:c.execute(text('UPDATE artifacts SET content=:body WHERE id=:id'),{'body':original,'id':aid})
        recovered=self.client.get(path);self.assertEqual(recovered.status_code,200);self.record('malformed_artifact',r,recovered)

    def test_timeout_cancel_disconnect_reap_real_mock_processes_and_allow_retry(self):
        import asyncio,sys,tempfile
        from pathlib import Path
        from backend.app.agent import PiRPC
        from backend.app.conversation import ConversationService,prepare,load_run
        from backend.app.schemas import AnswerCreate
        from backend.app.observability import request_id,session_id
        async def scenario(mode):
            service=ConversationService(main.engine,main.settings)
            sid=self.client.post('/api/sessions',json={'title':'Isolated '+mode}).json()['id']
            body=AnswerCreate(content='Synthetic lifecycle fixture',client_message_id=uuid4(),timeout_seconds=2)
            run,_=prepare(main.engine,main.settings,sid,body)
            instances=[]
            def factory(log_dir,**kwargs):
                rpc=PiRPC(log_dir,[sys.executable,str(Path(__file__).with_name('fake_rpc.py')),'stubborn'],**kwargs);instances.append(rpc);return rpc
            class Disconnect:
                async def is_disconnected(self):return bool(instances and instances[0].process)
            rt=request_id.set('phase9-'+mode);st=session_id.set(sid)
            try:
                with patch('backend.app.conversation.PiRPC',factory):
                    if mode=='disconnect':
                        async for _ in service.events(run,Disconnect()):pass
                    else:
                        async def notify(*args):pass
                        task=asyncio.create_task(service.execute(run,notify))
                        if mode=='cancel':
                            while not instances or not instances[0].process:await asyncio.sleep(.01)
                            task.cancel()
                        await task
                saved=load_run(main.engine,main.settings,sid,run['id'])
                self.assertEqual(saved['status'],'failed' if mode=='timeout' else 'cancelled')
                self.assertEqual(saved['error_code'],'answer_timeout' if mode=='timeout' else 'cancelled')
                self.assertTrue(saved['metadata']['process_reaped']);self.assertTrue(saved['metadata']['bridge_closed']);self.assertFalse(service.lock.locked());self.assertFalse(service.tasks)
                self.assertTrue(instances and instances[0].process.returncode is not None)
                retry,created=prepare(main.engine,main.settings,sid,body.model_copy(update={'retry':True}))
                self.assertTrue(created);self.assertEqual(retry['user_message_id'],run['user_message_id'])
                from backend.app.conversation import terminate
                terminate(main.engine,retry,'cancelled','test_cleanup',{})
                self.assertEqual(len(self.client.get(f'/api/sessions/{sid}/messages').json()),1)
                print(json.dumps({'phase9_case':mode,'inference':'mock Python subprocess; real OS process/bridge/PostgreSQL','run_id':str(run['id']),'request_id':'phase9-'+mode,'status':saved['status'],'code':saved['error_code'],'process_reaped':True,'bridge_closed':True,'retry_same_saved_message':True}))
            finally:request_id.reset(rt);session_id.reset(st);await service.shutdown()
        for mode in ['timeout','cancel','disconnect']:
            with self.subTest(mode=mode):asyncio.run(scenario(mode))
