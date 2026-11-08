"""Validate actual DB sources, then persist the directly reviewed essay atomically."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path('docs/agent-transcripts/phase-06')
CODE=r'''
import json,sys
from uuid import UUID
from hashlib import sha256
from backend.app.config import load_settings
from backend.app.db import make_engine
from backend.app.essays import load_essay,save_progress,read_essay_sources,review_essay
from backend.app.writing import validate_essay,assemble,EssayReview
p=json.load(sys.stdin);settings=load_settings();engine=make_engine(settings);sid,rid=UUID(p['session_id']),UUID(p['run_id'])
run=load_essay(engine,settings,sid,rid);sources={s['source_label']:s for s in read_essay_sources(engine,settings,sid,rid)};checks=[]
for section,prepared in zip(p['sections'],p['plan']['sections']):
 for fact in prepared['facts']:
  s=sources[fact['source_id']];assert str(s['chunk_id'])==fact['chunk_id'];assert fact['evidence_anchor'] in s['original_text'];assert sha256(s['original_text'].encode()).hexdigest()==p['plan']['source_hashes'][fact['source_id']]
  assert section['body'].count(fact['statement']+' ['+fact['source_id']+']')==1
  checks.append({'fact_id':fact['id'],'source_id':fact['source_id'],'chunk_id':fact['chunk_id'],'exact_fact_and_adjacent_citation':True,'actual_snapshot_hash_matches':True})
validation=validate_essay(p['plan']['title'],p['sections'],{label:{'original_text':s['original_text']} for label,s in sources.items()})
if not validation['passed_deterministic']:raise RuntimeError('Reviewed essay still fails rubric')
metadata={**run['metadata'],'editorial_revision':p['editorial'],'repairs_used':1,'model_repairs_used':0,'editorial_revision_passes':1,'source_review':'15 factual blocks directly reviewed against fresh topic snapshots; fixed content/citations preserved','manual_curation_required':True}
save_progress(engine,rid,sections=p['sections'],draft_md=assemble(p['plan']['title'],p['sections']),validation=validation,metadata=metadata,status='needs_review',error_code=None)
review=EssayReview(reviewer='Codex direct source and narrative review',hook=True,progression=True,factual_support=True,applications_distinct=True,complete=True,notes=p['review_notes'])
accepted=review_essay(engine,settings,sid,rid,review)
with engine.connect() as c:
 from sqlalchemy import text
 count=c.scalar(text('SELECT count(*) FROM answer_sources WHERE message_id=:mid'),{'mid':accepted['assistant_message_id']})
 message=c.scalar(text('SELECT content FROM messages WHERE id=:id'),{'id':accepted['assistant_message_id']})
 assert message==accepted['draft_md']
print(json.dumps({'session_id':str(sid),'run_id':str(rid),'status':accepted['status'],'assistant_message_id':str(accepted['assistant_message_id']),'saved_assistant_matches_essay':True,'persisted_answer_source_count':count,'validation':validation,'review':accepted['review'],'source_checks':checks,'metadata':metadata},default=str))
engine.dispose()
'''
p=next(ROOT.glob('server-essay-*'));prepared=json.loads((p/'prepare.json').read_text())
if (p/'accepted.json').exists():raise SystemExit('Already accepted; inspect instead of repeating')
payload={'session_id':prepared['session_id'],'run_id':prepared['run_id'],'plan':json.loads((p/'plan.json').read_text()),'sections':json.loads((p/'final-sections.json').read_text()),'editorial':json.loads((p/'editorial-revision.json').read_text()),'review_notes':['Final reviewed essay1319 words, within1125–1375; six complete sections, reader-question hook, useful progression, six action bullets and one selective bold span.','All15 factual blocks manually reviewed against freshly retrieved six owned snapshots. Exact facts/citations preserved; no measured Lookout engagement/conversion gain or isolated onboarding causality invented.','Application prose is labelled and benefits are hypotheses, not facts. One transparent editorial pass removed an unqualified benefit claim, instruction leakage and weak inference from explanation frequency. Original raw model outputs and1325-word draft remain unchanged.','This is a human-reviewed server-fact/local-Pi workflow, not proof of autonomous factual approval, general model reliability or production UI essay routing.']}
cmd=[sys.executable,'scripts/docker.py','compose','exec','-T','api','python','-c',CODE]
r=subprocess.run(cmd,input=json.dumps(payload),capture_output=True,text=True,timeout=45)
(p/'acceptance-command.json').write_text(json.dumps({'command':cmd[:-1]+['<CODE in scripts/finalize_server_essay_phase6.py>'],'exit_code':r.returncode,'stderr':r.stderr},indent=2)+'\n')
if not r.stdout.strip():raise SystemExit('No acceptance result; inspect saved error')
data=json.loads(r.stdout);(p/'accepted.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({k:v for k,v in data.items() if k not in ['metadata','source_checks']}))
if r.returncode:raise SystemExit(r.returncode)
