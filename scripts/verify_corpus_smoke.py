"""Two actual local corpus ingestions and read-only source/persistence proofs."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

SHA='be8ab89a890a833cbba2c892178f823fff178c65'
PROOF = '''
from backend.app.config import load_settings
from backend.app.db import make_engine
from sqlalchemy import text
from hashlib import sha256
import json
engine=make_engine(load_settings())
with engine.connect() as c:
 ids=list(c.scalars(text("SELECT id FROM chunks WHERE active ORDER BY id")))
 messages=[tuple(r) for r in c.execute(text("SELECT id,session_id,content,created_at FROM messages ORDER BY id"))]
 sessions=[tuple(r) for r in c.execute(text("SELECT id,user_id,title,created_at,updated_at FROM sessions ORDER BY id"))]
 sources=[dict(r) for r in c.execute(text("SELECT e.source_path,e.source_hash,e.current_version,v.original_text,v.corpus_revision FROM episodes e JOIN episode_versions v ON v.episode_id=e.id AND v.version=e.current_version WHERE e.deleted_at IS NULL ORDER BY e.source_path")).mappings()]
 hashes=all(sha256(s['original_text'].encode()).hexdigest()==s['source_hash'] for s in sources)
 for s in sources:s.pop('original_text')
 valid=c.scalar(text("SELECT bool_and(c.original_text=substring(v.original_text from c.char_start+1 for c.char_end-c.char_start) AND vector_dims(c.embedding)=768 AND length(c.search_vector)>0) FROM chunks c JOIN episode_versions v ON v.episode_id=c.episode_id AND v.version=c.version WHERE c.active"))
 versions=c.scalar(text("SELECT max(n) FROM (SELECT count(DISTINCT version) n FROM chunks WHERE active GROUP BY episode_id) x"))
 print(json.dumps({'active_chunks':len(ids),'active_ids_digest':sha256(json.dumps(ids,default=str).encode()).hexdigest(),'source_hashes_match':hashes,'spans_vectors_fulltext_valid':valid,'max_active_versions_per_episode':versions,'active_sources':sources,'message_count':len(messages),'message_digest':sha256(json.dumps(messages,default=str).encode()).hexdigest(),'session_digest':sha256(json.dumps(sessions,default=str).encode()).hexdigest()},default=str))
engine.dispose()
'''


def main():
    root=Path(__file__).resolve().parent.parent
    folder=root/'docs/agent-transcripts/phase-03'/('smoke-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'))
    folder.mkdir(parents=True,exist_ok=False)
    def record(kind,**fields):
        row={'captured_at':datetime.now(timezone.utc).isoformat(),'kind':kind,**fields}
        row=json.loads(json.dumps(row).replace(str(Path.home()),'$USER_HOME'))
        with (folder/'results.jsonl').open('a') as stream:stream.write(json.dumps(row)+'\n')
        print(json.dumps(row),flush=True)
    def run(*args):
        cmd=[sys.executable,'scripts/docker.py','compose','exec','-T','api',*args]
        result=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=650)
        record('actual_command',command=cmd,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr)
        if result.returncode:raise RuntimeError('Smoke command failed; see preserved output')
        return result.stdout
    def proof():return json.loads(run('python','-c',PROOF))
    try:
        before=proof()
        first=run('python','-m','backend.ingest','--root','/corpus/'+SHA,'--limit','3')
        first_result=next(json.loads(line) for line in first.splitlines() if json.loads(line).get('event')=='ingestion_result')
        middle=proof()
        second=run('python','-m','backend.ingest','--root','/corpus/'+SHA,'--limit','3')
        second_result=next(json.loads(line) for line in second.splitlines() if json.loads(line).get('event')=='ingestion_result')
        after=proof()
        checks={
          'smoke_not_full_corpus':first_result['discovered']>first_result['selected']==3 and first_result['status']=='partial',
          'first_selected_files_succeeded':first_result['failed']==0 and first_result['loaded']+first_result['skipped']==3,
          'repeat_skips_all_three':second_result['skipped']==3 and second_result['loaded']==0 and second_result['failed']==0,
          'no_duplicate_or_changed_chunk_ids_on_repeat':middle['active_ids_digest']==after['active_ids_digest'] and middle['active_chunks']==after['active_chunks'],
          'source_hashes_spans_vectors_fulltext_valid':after['source_hashes_match'] and after['spans_vectors_fulltext_valid'],
          'one_active_version_per_episode':after['max_active_versions_per_episode']==1,
          'conversations_untouched':before['message_digest']==after['message_digest'] and before['session_digest']==after['session_digest'],
        }
        record('actual_smoke_summary',passed=all(checks.values()),checks=checks,first=first_result,repeat=second_result,proof=after)
        if not all(checks.values()):raise AssertionError('Corpus smoke invariant failed')
    except Exception as exc:
        record('smoke_failure',passed=False,error_type=type(exc).__name__,message=str(exc));raise


if __name__=='__main__':main()
