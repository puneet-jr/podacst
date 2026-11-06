"""Real DB/API persistence and routing; every generation here is explicitly mocked."""
import asyncio
import json
import os
import unittest
from unittest.mock import patch
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import text

if not os.environ.get('POSTGRES_DB','').startswith('lenny_contract_'):raise RuntimeError('Requires isolated contract DB')
from backend.app.main import app,engine,settings,conversations
from backend.app.essays import EssayService,load_essay,prepare_essay,review_essay,save_progress
from backend.app.conversation import prepare,ConversationError
from backend.app.schemas import AnswerCreate
from backend.app.writing import EssayCreate,EssayReview,EssayError
from backend.tests.test_writing import outline


class EssayDatabase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):engine.dispose()

    def setUp(self):
        self.client=TestClient(app);self.addCleanup(self.client.close)
        self.sid=self.client.post('/api/sessions',json={'title':'Essay contract, mocked generation'}).json()['id']

    def body(self,**extra):return EssayCreate(topic='A synthetic quartz activation experiment',audience='Fixture product managers',client_message_id=uuid4(),**extra)

    def review(self,accepted=True):return EssayReview(reviewer='Mock contract reviewer',hook=accepted,progression=accepted,factual_support=accepted,applications_distinct=accepted,complete=accepted,notes=['Synthetic test review, not live quality evidence.'])

    def test_context_is_owned_prior_user_only_and_replay_is_idempotent(self):
        old=self.client.post(f'/api/sessions/{self.sid}/messages',json={'content':'Prefer a cautious tone.','client_message_id':str(uuid4())}).json()
        body=self.body();run,_=prepare_essay(engine,settings,self.sid,body)
        self.assertEqual(run['context_message_ids'],[old['id']]);self.assertIn('cautious',run['context_text'])
        save_progress(engine,run['id'],status='failed',error_code='mock_failure')
        same,created=prepare_essay(engine,settings,self.sid,body);self.assertFalse(created);self.assertEqual(same['id'],run['id'])
        with self.assertRaises(EssayError):prepare_essay(engine,settings,self.sid,body.model_copy(update={'audience':'Changed'}))
        other=self.client.post('/api/sessions',json={'title':'Independent essay'}).json()['id']
        fresh,_=prepare_essay(engine,settings,other,self.body());self.assertFalse(fresh['context_message_ids'])
        save_progress(engine,fresh['id'],status='failed',error_code='mock_cleanup')
        self.assertEqual(len(self.client.get(f'/api/sessions/{self.sid}/messages').json()),2)

    def test_wrong_session_and_chat_concurrency_are_rejected(self):
        run,_=prepare_essay(engine,settings,self.sid,self.body())
        other=self.client.post('/api/sessions',json={'title':'Other'}).json()['id']
        self.assertEqual(self.client.get(f"/api/sessions/{other}/essays/{run['id']}").status_code,404)
        self.assertEqual(self.client.get(f"/api/sessions/{other}/essays/{run['id']}/sources").status_code,404)
        with self.assertRaises(ConversationError):prepare(engine,settings,self.sid,AnswerCreate(content='A different chat request',client_message_id=uuid4()))
        save_progress(engine,run['id'],status='failed',error_code='mock_cleanup')

    def test_manual_review_cannot_override_failed_deterministic_rubric(self):
        run,_=prepare_essay(engine,settings,self.sid,self.body())
        save_progress(engine,run['id'],status='failed',error_code='essay_rubric_failed',draft_md='# Incomplete',validation={'passed_deterministic':False,'word_count':1,'errors':[{'code':'incomplete_sections'}]})
        with self.assertRaises(EssayError):review_essay(engine,settings,self.sid,run['id'],self.review(True))
        reviewed=review_essay(engine,settings,self.sid,run['id'],self.review(False))
        self.assertEqual(reviewed['status'],'failed');self.assertIsNone(reviewed['assistant_message_id']);self.assertEqual(reviewed['error_code'],'essay_rubric_failed')
        self.assertEqual(len(self.client.get(f'/api/sessions/{self.sid}/messages').json()),1)

    def test_mock_validated_essay_completion_is_atomic_and_inspectable(self):
        run,_=prepare_essay(engine,settings,self.sid,self.body())
        with engine.begin() as c:
            source=c.execute(text('SELECT id,original_text,char_start,char_end FROM chunks WHERE active LIMIT 1')).mappings().one()
            metadata={'char_start':source['char_start'],'char_end':source['char_end'],'title':'Synthetic contract evidence','guest':'Fixture','source_path':'episodes/retrieval-alpha/transcript.md'}
            c.execute(text("INSERT INTO essay_sources(run_id,source_label,chunk_id,original_text,source_metadata,quote_spans) VALUES(:run,'S1',:chunk,:original,CAST(:metadata AS jsonb),'[]')"),{'run':run['id'],'chunk':source['id'],'original':source['original_text'],'metadata':json.dumps(metadata)})
        # Deliberately mocked validator outcome: this checks persistence, not essay generation/quality.
        save_progress(engine,run['id'],status='needs_review',draft_md='# Mocked essay\n\nSynthetic saved output. [S1]',validation={'passed_deterministic':True,'citation_ids':['S1']})
        completed=review_essay(engine,settings,self.sid,run['id'],self.review())
        self.assertEqual(completed['status'],'completed')
        repeated=review_essay(engine,settings,self.sid,run['id'],self.review());self.assertEqual(repeated['assistant_message_id'],completed['assistant_message_id'])
        messages=self.client.get(f'/api/sessions/{self.sid}/messages').json();self.assertEqual(len(messages),2);self.assertEqual(messages[-1]['citations'][0]['source_label'],'S1')
        opened=self.client.get(f"/api/sessions/{self.sid}/messages/{completed['assistant_message_id']}/sources/S1")
        self.assertEqual(opened.status_code,200);self.assertEqual(opened.json()['original_text'],source['original_text'])

    def test_dedicated_workflow_drafts_six_sections_and_repairs_only_once(self):
        body=self.body();run,_=prepare_essay(engine,settings,self.sid,body)
        service=EssayService(engine,settings,asyncio.Lock());calls=[];events=[]
        async def fake_stage(run,name,prompt,loader,schema,tokens,metadata):
            calls.append(name);metadata['stages'].append({'stage':name,'explicit_mock':True})
            if name=='outline':await loader();return json.dumps(outline())
            return json.dumps({'body':'A deliberately short synthetic draft cannot satisfy the essay rubric. [S1]'})
        async def notify(kind,data):events.append(kind)
        sources={'S1':{'id':str(uuid4()),'original_text':'Synthetic fixture evidence.','guest':'Fixture','title':'Synthetic'}}
        packet={'retrieval_mode':'hybrid','sources':[{'id':'S1'}]}
        # At least three independent source IDs are needed by the workflow's thin-evidence policy.
        for i in [2,3]:sources['S'+str(i)]={**sources['S1'],'id':str(uuid4())}
        with patch('backend.app.essays.collect_evidence',return_value=(sources,packet,[])),patch.object(service,'stage',fake_stage):asyncio.run(service.execute(run,notify))
        actual=load_essay(engine,settings,self.sid,run['id'])
        self.assertEqual(actual['status'],'failed');self.assertEqual(actual['metadata']['repairs_used'],1)
        self.assertEqual(len(calls),8);self.assertEqual(sum(name.startswith('repair-') for name in calls),1);self.assertEqual(len(actual['sections']),6)
        self.assertIn('word_count_outside_range',{e['code'] for e in actual['validation']['errors']});self.assertIsNone(actual['assistant_message_id'])

    def test_explicit_essay_route_uses_essay_service_and_empty_evidence_stops(self):
        from backend.app.main import essays
        async def fake_stage(run,name,prompt,loader,schema,tokens,metadata):
            metadata['stages'].append({'stage':name,'explicit_mock':True});await loader()
            return json.dumps({'status':'insufficient_evidence','title':'Insufficient source evidence','sections':[]})
        with patch('backend.app.essays.collect_evidence',return_value=({}, {'retrieval_mode':'hybrid','sources':[]},[])),patch.object(essays,'stage',fake_stage):
            with self.client.stream('POST',f'/api/sessions/{self.sid}/essays',json=self.body().model_dump(mode='json')) as response:
                self.assertEqual(response.status_code,200);events=[json.loads(x) for x in response.iter_lines() if x]
        self.assertEqual(events[-1]['type'],'insufficient_evidence');self.assertEqual(events[0]['workflow'],'ship30')
        actual=self.client.get(f"/api/sessions/{self.sid}/essays/{events[0]['run_id']}").json()
        self.assertEqual(actual['error_code'],'essay_evidence_too_thin');self.assertFalse(actual['sections'])
