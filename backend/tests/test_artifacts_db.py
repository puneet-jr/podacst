import os,unittest
from uuid import uuid4
from sqlalchemy import text
if not os.environ.get('POSTGRES_DB','').startswith('lenny_contract_'):raise RuntimeError('Isolated contract DB required')
from fastapi.testclient import TestClient
from backend.app.main import app,engine
class ArtifactDatabase(unittest.TestCase):
 def setUp(self):
  self.c=TestClient(app);self.addCleanup(self.c.close);self.sid=self.c.post('/api/sessions',json={'title':'Artifact fixture'}).json()['id'];self.mid=str(uuid4())
  with engine.begin() as db:db.execute(text("INSERT INTO messages(id,session_id,client_message_id,role,content,status) VALUES(:id,:sid,:id,'assistant',:content,'completed')"),{'id':self.mid,'sid':self.sid,'content':'# Synthetic fixture\n\n**Safe** text.'})
 def test_formats_saved_reopened_idempotent_and_session_scoped(self):
  for kind in ['markdown','html']:
   body={'message_id':self.mid,'format':kind};r=self.c.post(f'/api/sessions/{self.sid}/artifacts',json=body);self.assertEqual(r.status_code,201);a=r.json();self.assertEqual(a['source_metadata']['provenance'],'saved_reply');self.assertIn('<h1>Synthetic fixture</h1>',a['preview_html'])
   self.assertEqual(self.c.post(f'/api/sessions/{self.sid}/artifacts',json=body).json()['id'],a['id'])
   self.assertEqual(self.c.get(f"/api/sessions/{self.sid}/artifacts/{a['id']}").json()['content'],a['content'])
   other=self.c.post('/api/sessions',json={'title':'Other'}).json()['id'];self.assertEqual(self.c.get(f"/api/sessions/{other}/artifacts/{a['id']}").status_code,404)
  self.assertEqual(len(self.c.get(f'/api/sessions/{self.sid}/artifacts').json()),2)
 def test_unknown_citation_and_wrong_session_message_rejected(self):
  with engine.begin() as db:db.execute(text('UPDATE messages SET content=:content WHERE id=:id'),{'id':self.mid,'content':'Unknown citation [S9]'})
  self.assertEqual(self.c.post(f'/api/sessions/{self.sid}/artifacts',json={'message_id':self.mid,'format':'markdown'}).status_code,409)
  other=self.c.post('/api/sessions',json={'title':'Other'}).json()['id'];self.assertEqual(self.c.post(f'/api/sessions/{other}/artifacts',json={'message_id':self.mid,'format':'html'}).status_code,404)
