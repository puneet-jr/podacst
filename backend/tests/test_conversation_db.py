"""Real DB transactions/scoping; model selection is explicitly mocked in these tests."""
import asyncio
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from uuid import uuid4

if not os.environ.get('POSTGRES_DB','').startswith('lenny_contract_'):
    raise RuntimeError('Requires newly isolated contract DB')

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from backend.app.main import app,engine,settings
from backend.app.conversation import ConversationError, ConversationService, complete, load_run, prepare, sentence_items, terminate, validate_selection
from backend.app.retrieval import SearchRequest,search
from backend.app.schemas import AnswerCreate


class ConversationDatabase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):engine.dispose()

    def setUp(self):
        self.client=TestClient(app)
        self.addCleanup(self.client.close)
        self.session=self.client.post('/api/sessions',json={'title':'Conversation contract'}).json()['id']

    def body(self,content='What is the quartz activation experiment?',**extra):
        return AnswerCreate(content=content,client_message_id=uuid4(),**extra)

    def completed(self,body=None):
        body=body or self.body(source_path='episodes/retrieval-alpha/transcript.md')
        run,_=prepare(engine,settings,self.session,body)
        found=search(engine,settings,SearchRequest(query='quartz activation',mode='sparse',source_path='episodes/retrieval-alpha/transcript.md'))
        items,sources=sentence_items(found,'quartz activation')
        selection,chosen=validate_selection('{"evidence_id":"'+items[0]['id']+'"}',items)
        output=complete(engine,run,selection,chosen,sources,{'test_mode':'mocked model selection; actual source/DB'})
        return body,load_run(engine,settings,self.session,run['id']),output

    def test_replay_is_idempotent_and_changed_input_conflicts(self):
        body,run,_=self.completed()
        repeated,created=prepare(engine,settings,self.session,body)
        self.assertFalse(created);self.assertEqual(repeated['assistant_message_id'],run['assistant_message_id'])
        self.assertEqual(len(self.client.get(f'/api/sessions/{self.session}/messages').json()),2)
        with self.assertRaisesRegex(ConversationError,'idempotency_conflict'):
            prepare(engine,settings,self.session,body.model_copy(update={'content':'Changed content'}))

    def test_follow_up_uses_only_owned_prior_user_context_and_inherits_scope(self):
        _,first,_=self.completed()
        second,_=prepare(engine,settings,self.session,self.body('And how did they measure that?'))
        self.assertEqual(second['context_message_ids'],[str(first['user_message_id'])])
        self.assertIn('quartz',second['resolved_query']);self.assertEqual(second['source_path'],'episodes/retrieval-alpha/transcript.md')
        terminate(engine,second,'failed','test_cleanup',{})
        other=self.client.post('/api/sessions',json={'title':'Independent'}).json()['id']
        independent,_=prepare(engine,settings,other,self.body('And how did they measure that?'))
        self.assertFalse(independent['context_message_ids']);self.assertIsNone(independent['source_path'])
        terminate(engine,independent,'failed','test_cleanup',{})

    def test_failed_retry_keeps_user_identity_history_and_finite_budget(self):
        body=self.body();run,_=prepare(engine,settings,self.session,body)
        terminate(engine,run,'failed','injected_model_failure',{'diagnostic':'mock only'})
        replay,created=prepare(engine,settings,self.session,body)
        self.assertFalse(created);self.assertEqual(replay['status'],'failed')
        retry,created=prepare(engine,settings,self.session,body.model_copy(update={'retry':True}))
        self.assertTrue(created);self.assertEqual(retry['user_message_id'],run['user_message_id']);self.assertEqual(retry['attempt'],2)
        self.assertEqual(retry['metadata']['attempt_history'][0]['error_code'],'injected_model_failure')
        terminate(engine,retry,'cancelled','cancelled',{})
        third,_=prepare(engine,settings,self.session,body.model_copy(update={'retry':True}));terminate(engine,third,'failed','test_failure',{})
        with self.assertRaisesRegex(ConversationError,'retry_budget_exhausted'):prepare(engine,settings,self.session,body.model_copy(update={'retry':True}))
        self.assertEqual(len(self.client.get(f'/api/sessions/{self.session}/messages').json()),1)

    def test_source_snapshot_resolves_and_wrong_session_or_unknown_id_is_rejected(self):
        _,run,output=self.completed();label=output['source_labels'][0]
        path=f"/api/sessions/{self.session}/messages/{run['assistant_message_id']}/sources/"
        response=self.client.get(path+label);self.assertEqual(response.status_code,200)
        source=response.json();self.assertTrue(source['quote_spans'])
        for quote in source['quote_spans']:
            self.assertEqual(source['original_text'][quote['char_start']-source['metadata']['char_start']:quote['char_end']-source['metadata']['char_start']],quote['text'])
        self.assertEqual(self.client.get(path+'S999').status_code,404)
        other=self.client.post('/api/sessions',json={'title':'Other'}).json()['id']
        self.assertEqual(self.client.get(f"/api/sessions/{other}/messages/{run['assistant_message_id']}/sources/{label}").status_code,404)
        self.assertEqual(self.client.get(f"/api/sessions/{other}/runs/{run['id']}").status_code,404)

    def test_saved_source_survives_retirement_and_sources_commit_atomically(self):
        _,run,output=self.completed();label=output['source_labels'][0]
        source=self.client.get(f"/api/sessions/{self.session}/messages/{run['assistant_message_id']}/sources/{label}").json()
        with engine.begin() as c:c.execute(text('UPDATE chunks SET active=false WHERE id=:id'),{'id':source['chunk_id']})
        try:
            again=self.client.get(f"/api/sessions/{self.session}/messages/{run['assistant_message_id']}/sources/{label}")
            self.assertEqual(again.status_code,200);self.assertEqual(again.json()['original_text'],source['original_text'])
        finally:
            with engine.begin() as c:c.execute(text('UPDATE chunks SET active=true WHERE id=:id'),{'id':source['chunk_id']})
        new_session=self.client.post('/api/sessions',json={'title':'Atomic'}).json()['id']
        pending,_=prepare(engine,settings,new_session,self.body())
        found=search(engine,settings,SearchRequest(query='quartz',mode='sparse'))
        items,sources=sentence_items(found,'quartz');item=items[0];sources[item['source_id']]=sources[item['source_id']].model_copy(update={'id':uuid4()})
        selection,chosen=validate_selection('{"evidence_id":"'+item['id']+'"}',items)
        with self.assertRaises(IntegrityError):complete(engine,pending,selection,chosen,sources,{})
        self.assertEqual(len(self.client.get(f'/api/sessions/{new_session}/messages').json()),1)
        self.assertIsNone(load_run(engine,settings,new_session,pending['id'])['assistant_message_id'])
        terminate(engine,pending,'failed','injected_citation_failure',{})

    def test_empty_gap_has_no_fabricated_citations(self):
        run,_=prepare(engine,settings,self.session,self.body())
        selection,chosen=validate_selection('{"evidence_id":"NONE"}',[])
        output=complete(engine,run,selection,chosen,{}, {'test_mode':'mock model; actual DB'})
        self.assertEqual(output['status'],'insufficient_evidence');self.assertFalse(output['source_labels'])
        messages=self.client.get(f'/api/sessions/{self.session}/messages').json()
        self.assertFalse(messages[-1]['citations'])

    def test_mocked_timeout_cleans_bridge_and_persists_terminal_failure(self):
        body=self.body(timeout_seconds=.1);run,_=prepare(engine,settings,self.session,body)
        class HangingPi:
            def __init__(self,log_dir,**kwargs):self.log_dir=log_dir;self.process=SimpleNamespace(pid=None,returncode=None);self.last_model_text=None
            async def start(self):self.log_dir.mkdir(parents=True,exist_ok=True);await asyncio.sleep(100)
            async def close(self):self.process.returncode=0
        async def scenario():
            service=ConversationService(engine,settings);events=[]
            async def notify(kind,data):events.append(kind)
            with patch('backend.app.conversation.PiRPC',HangingPi):await service.execute(run,notify)
            self.assertFalse(service.lock.locked());self.assertEqual(events[-1],'failed')
        asyncio.run(scenario())
        saved=load_run(engine,settings,self.session,run['id'])
        self.assertEqual(saved['error_code'],'answer_timeout');self.assertTrue(saved['metadata']['bridge_closed']);self.assertTrue(saved['metadata']['process_reaped'])

    def test_startup_records_abandoned_operation_without_duplicate_messages(self):
        run,_=prepare(engine,settings,self.session,self.body())
        with TestClient(app):pass
        saved=load_run(engine,settings,self.session,run['id'])
        self.assertEqual((saved['status'],saved['error_code']),('failed','app_restarted'))
        self.assertEqual(len(self.client.get(f'/api/sessions/{self.session}/messages').json()),1)