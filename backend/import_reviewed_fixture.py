"""Import the labelled reviewed essay into an intended isolated demo database.
No inference, private source export, existing-session update or overwrite.
"""
import argparse,hashlib,json,re
from pathlib import Path
from uuid import uuid4
from sqlalchemy import text
from backend.app.config import load_settings
from backend.app.db import make_engine
from backend.app.writing import word_count
from backend.app.artifacts import preview
from backend.app.retrieval import COLUMNS,BASE
p=argparse.ArgumentParser();p.add_argument('--expected-database',required=True);args=p.parse_args();s=load_settings()
if s.db_name!=args.expected_database or not s.db_name.startswith('lenny_release_'):raise SystemExit('Fixture import requires the explicitly named isolated lenny_release_* database')
v=json.loads((Path(__file__).parent/'fixtures/reviewed-essay-1208.json').read_text());assert v['fixture'] and v['provenance']=='reviewed_fixture' and v['manual_edits']==9;assert word_count(v['markdown'])==v['word_count']==1208;assert hashlib.sha256(v['markdown'].encode()).hexdigest()==v['markdown_sha256'];assert hashlib.sha256(v['html'].encode()).hexdigest()==v['html_sha256'];labels=set(re.findall(r'\[(S\d+)\]',v['markdown']));assert labels=={x['source_label'] for x in v['sources']};sid=uuid4();mid=uuid4();e=make_engine(s);snapshots=[]
with e.begin() as c:
 assert not c.scalar(text('SELECT 1 FROM sessions WHERE user_id=:user AND title=:title'),{'user':s.local_user_id,'title':v['label']}),'Reviewed fixture already exists; refuse duplicate import'
 for item in v['sources']:
  row=dict(c.execute(text('SELECT '+COLUMNS+BASE+' AND c.id=:chunk'),{'model':s.embedding_model,'digest':c.scalar(text('SELECT embedding_digest FROM knowledge_config WHERE singleton')),'include_sponsors':True,'chunk':item['chunk_id']}).mappings().one());assert row['source_hash']==item['source_hash'] and row['corpus_revision']==item['corpus_revision'] and row['version']==item['version'] and row['source_path']==item['source_path'];spans=[]
  for q in item['spans']:
   a=q['char_start']-row['char_start'];b=q['char_end']-row['char_start'];assert 0<=a<b<=len(row['original_text']);quote=row['original_text'][a:b];assert hashlib.sha256(quote.encode()).hexdigest()==q['text_sha256'];spans.append({'id':q['id'],'text':quote,'char_start':q['char_start'],'char_end':q['char_end'],'speaker':q.get('speaker')})
  original=row.pop('original_text');row['text_sha256']=hashlib.sha256(original.encode()).hexdigest();row['metadata_warnings']=row['metadata_warnings'] or [];snapshots.append((item,original,row,spans))
 c.execute(text('INSERT INTO sessions(id,user_id,title) VALUES(:id,:user,:title)'),{'id':sid,'user':s.local_user_id,'title':v['label']});c.execute(text("INSERT INTO messages(id,session_id,client_message_id,role,content,status) VALUES(:id,:sid,:client,'assistant',:body,'completed')"),{'id':mid,'sid':sid,'client':uuid4(),'body':v['markdown']})
 sources=[]
 for item,original,metadata,spans in snapshots:
  c.execute(text('INSERT INTO answer_sources(message_id,chunk_id,source_label,evidence_text,source_metadata,quote_spans) VALUES(:mid,:chunk,:label,:body,CAST(:meta AS jsonb),CAST(:spans AS jsonb))'),{'mid':mid,'chunk':item['chunk_id'],'label':item['source_label'],'body':original,'meta':json.dumps(metadata,default=str),'spans':json.dumps(spans)});sources.append({'source_label':item['source_label'],'chunk_id':item['chunk_id'],'source_metadata':metadata})
 hashes={}
 for kind in ['markdown','html']:
  content=v[kind];preview(content,kind,v['title']);metadata={'provenance':'reviewed_fixture','manual_edits':9,'word_count':1208,'review_label':v['label'],'edit_disclosure':v['edit_disclosure'],'citation_ids':sorted(labels),'sources':sources,'formatting':'Historical reviewed export unchanged; no new inference'};c.execute(text('INSERT INTO artifacts(id,session_id,message_id,type,title,content,source_metadata) VALUES(:id,:sid,:mid,:kind,:title,:body,CAST(:meta AS jsonb))'),{'id':uuid4(),'sid':sid,'mid':mid,'kind':kind,'title':v['title'],'body':content,'meta':json.dumps(metadata,default=str)});hashes[kind]=hashlib.sha256(content.encode()).hexdigest()
print(json.dumps({'fixture':True,'word_count':1208,'manual_edits':9,'new_inference':0,'session_id':str(sid),'message_id':str(mid),'source_count':len(snapshots),'artifacts':hashes}));e.dispose()
