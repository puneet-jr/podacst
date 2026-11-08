"""Real PostgreSQL contract tests. Run only through backend.contract_check."""
from datetime import datetime
import io
import logging
import os
import unittest
from uuid import uuid4

if not os.environ.get('POSTGRES_DB','').startswith('lenny_contract_'):
    raise RuntimeError('Refusing integration checks outside a newly isolated lenny_contract_* database')

from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.app.main import app, engine, settings, logger
from backend.app.schema import CURRENT_REVISION


class DatabaseAPI(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        engine.dispose()

    def setUp(self):
        self.client = TestClient(app)

    def create(self, title='Contract research'):
        response = self.client.post('/api/sessions',json={'title':title})
        self.assertEqual(response.status_code,201,response.text)
        return response.json()

    def test_schema_extension_and_indexes(self):
        with engine.connect() as connection:
            self.assertEqual(connection.scalar(text('SELECT version_num FROM alembic_version')),CURRENT_REVISION)
            self.assertTrue(connection.scalar(text("SELECT extversion FROM pg_extension WHERE extname='vector'")))
            tables=set(connection.scalars(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")))
            self.assertTrue({'users','sessions','messages','episodes','chunks','answer_sources','artifacts','ingestion_runs'} <= tables)
            indexes=set(connection.scalars(text("SELECT indexname FROM pg_indexes WHERE schemaname='public'")))
            self.assertIn('messages_session_created_idx',indexes)
            self.assertIn('chunks_search_idx',indexes)
            self.assertEqual(connection.scalar(text('SELECT vector_dims(array_fill(0::real,ARRAY[768])::vector)')),768)

    def test_distinct_sessions_messages_metadata_and_utc(self):
        a,b=self.create('Alpha research'),self.create('Beta research')
        self.assertNotEqual(a['id'],b['id'])
        me=self.client.get('/api/me').json()
        self.assertEqual(me['id'],a['user_id'])
        self.assertEqual(me['metadata']['deployment'],'local-single-evaluator')
        for chat,content in [(a,'Alpha isolated note'),(b,'Beta isolated note')]:
            result=self.client.post(f"/api/sessions/{chat['id']}/messages",json={'content':content,'client_message_id':str(uuid4())})
            self.assertEqual(result.status_code,201)
            message=result.json()
            self.assertEqual(datetime.fromisoformat(message['created_at']).utcoffset().total_seconds(),0)
            messages=self.client.get(f"/api/sessions/{chat['id']}/messages").json()
            self.assertEqual([m['content'] for m in messages],[content])
        self.assertEqual(self.client.get(f"/api/sessions/{a['id']}").json()['title'],'Alpha research')

    def test_idempotent_retry_and_conflict(self):
        chat=self.create(); path=f"/api/sessions/{chat['id']}/messages"
        body={'content':'A bounded saved message','client_message_id':str(uuid4())}
        a=self.client.post(path,json=body);b=self.client.post(path,json=body)
        self.assertEqual(a.json()['id'],b.json()['id'])
        self.assertEqual(len(self.client.get(path).json()),1)
        conflict=self.client.post(path,json={**body,'content':'Changed content'})
        self.assertEqual(conflict.status_code,409)
        self.assertEqual(conflict.json()['error']['code'],'idempotency_conflict')

    def test_invalid_unknown_ids_and_error_contract(self):
        cases=[('/api/sessions/not-a-uuid',422,'validation_error'),('/api/sessions/'+str(uuid4()),404,'session_not_found'),('/api/sessions?limit=101',422,'validation_error'),('/api/sessions?offset=-1',422,'validation_error'),('/unknown',404,'not_found')]
        for path,status,code in cases:
            response=self.client.get(path)
            self.assertEqual(response.status_code,status)
            error=response.json()['error']
            self.assertEqual(error['code'],code)
            self.assertEqual(error['request_id'],response.headers['X-Request-ID'])
            self.assertIsInstance(error['retryable'],bool)
        for body in [{'title':' '},{'title':'x'*161},{'title':'Research','user_id':str(uuid4())}]:
            self.assertEqual(self.client.post('/api/sessions',json=body).status_code,422)
        unknown='/api/sessions/'+str(uuid4())+'/messages'
        self.assertEqual(self.client.post(unknown,json={'content':'test','client_message_id':str(uuid4())}).status_code,404)

    def test_other_user_is_not_visible(self):
        user,session=uuid4(),uuid4()
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO users(id,display_name) VALUES(:id,'Contract other user')"),{'id':user})
            connection.execute(text("INSERT INTO sessions(id,user_id,title) VALUES(:id,:user,'Hidden contract session')"),{'id':session,'user':user})
        self.assertEqual(self.client.get('/api/sessions/'+str(session)).status_code,404)
        self.assertNotIn(str(session),[s['id'] for s in self.client.get('/api/sessions?limit=100').json()])
        path='/api/sessions/'+str(session)+'/messages'
        self.assertEqual(self.client.get(path).status_code,404)
        self.assertEqual(self.client.post(path,json={'content':'test','client_message_id':str(uuid4())}).status_code,404)

    def test_no_message_or_secret_in_structured_logs(self):
        stream=io.StringIO();handler=logging.StreamHandler(stream);logger.addHandler(handler)
        try:
            chat=self.create()
            response=self.client.post(f"/api/sessions/{chat['id']}/messages",json={'content':'SYNTHETIC_LOG_CONTENT_MUST_NOT_APPEAR','client_message_id':str(uuid4())})
            self.assertEqual(response.status_code,201)
            output=stream.getvalue()
            self.assertIn('message_saved',output)
            self.assertNotIn('SYNTHETIC_LOG_CONTENT_MUST_NOT_APPEAR',output)
            self.assertNotIn(settings.db_password.get_secret_value(),output)
        finally:
            logger.removeHandler(handler)

    def test_liveness_provider_and_openapi(self):
        self.assertEqual(self.client.get('/api/health/live').json(),{'status':'alive'})
        provider=self.client.get('/api/providers').json()
        self.assertEqual(provider['selected'],'ollama');self.assertFalse(provider['automatic_fallback'])
        self.assertTrue(provider['providers'][1]['implemented'])
        schema=self.client.get('/openapi.json').json()
        self.assertIn('ErrorOut',schema['components']['schemas'])
        self.assertIn('ReadyOut',schema['components']['schemas'])
        self.assertIn('ProvidersOut',schema['components']['schemas'])
