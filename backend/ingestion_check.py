"""Real PostgreSQL + Ollama integrity checks in a new retained database; synthetic sources."""
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import time
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from backend.app.config import load_settings
from backend.app.db import make_engine
from backend.app.embedding import EmbeddingError, OllamaEmbedder
from backend.app.ingestion import LOCK_KEY, IngestionError, ingest, ingestion_lock
from backend.app.snapshot import Snapshot


def main():
    settings = load_settings()
    if settings.db_host != 'db': raise SystemExit('Requires isolated Compose db service')
    admin = make_engine(settings)
    database = 'lenny_ingest_' + uuid4().hex[:12]
    with admin.connect().execution_options(isolation_level='AUTOCOMMIT') as connection:
        connection.execute(text('CREATE DATABASE ' + database))
    admin.dispose()
    test_settings = settings.model_copy(update={'db_name': database})
    engine = make_engine(test_settings)
    # Alembic uses the test engine explicitly, leaving the application DB untouched.
    import os
    previous = os.environ.get('POSTGRES_DB')
    os.environ['POSTGRES_DB'] = database
    try: command.upgrade(Config('backend/alembic.ini'), 'head')
    finally:
        if previous is None: os.environ.pop('POSTGRES_DB', None)
        else: os.environ['POSTGRES_DB'] = previous
    report = {'database': database, 'source_kind': 'synthetic_fixture', 'actual_postgresql': True, 'actual_ollama': True, 'checks': []}
    def check(name, condition, **detail):
        row = {'name': name, 'passed': bool(condition), **detail}; report['checks'].append(row)
        print(json.dumps({'event': 'ingestion_integrity_check', **row}), flush=True)
        if not condition: raise AssertionError(name)
    def active():
        with engine.connect() as connection:
            return [dict(r) for r in connection.execute(text('SELECT id,episode_id,source_hash,version,ordinal,original_text,embedding_digest FROM chunks WHERE active ORDER BY episode_id,ordinal')).mappings()]
    with tempfile.TemporaryDirectory(prefix='ingest-fixture-') as directory:
        root = Path(directory)
        paths = ['episodes/fixture-a/transcript.md','episodes/fixture-b/transcript.md']
        for index,path in enumerate(paths):
            file = root/path;file.parent.mkdir(parents=True)
            body = f'---\nguest: Fixture {index}\ntitle: Fixture {index} synthetic research\n---\n## Transcript\nGuest (00:01):\n'
            body += ('A synthetic experiment should use a clear success metric and record its evidence. ' * 140)
            file.write_text(body)
        def snapshot(revision):
            files = {str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in sorted(root.glob('episodes/*/transcript.md'))}
            return Snapshot(root, 'fixture:'+revision, files, kind='fixture')
        try:
            initial = ingest(engine, test_settings, snapshot('initial'), limit=1)
            check('smoke_count_is_not_full_coverage', initial['status']=='partial' and initial['discovered']==2 and initial['selected']==1 and initial['loaded']==1)
            before = active()
            repeated = ingest(engine, test_settings, snapshot('initial'), limit=1)
            check('unchanged_skips_without_duplicate_chunks', repeated['loaded']==0 and repeated['skipped']==1 and active()==before)
            loaded = ingest(engine, test_settings, snapshot('initial'))
            check('resume_completes_remaining_episode', loaded['loaded']==1 and loaded['skipped']==1 and loaded['active_episodes']==2)
            with engine.connect() as connection:
                valid = connection.scalar(text('''SELECT bool_and(c.original_text=substring(v.original_text from c.char_start+1 for c.char_end-c.char_start))
                  FROM chunks c JOIN episode_versions v ON v.episode_id=c.episode_id AND v.version=c.version WHERE c.active'''))
                dimensions = connection.scalar(text('SELECT bool_and(vector_dims(embedding)=768 AND search_vector IS NOT NULL) FROM chunks WHERE active'))
            check('exact_source_spans_vectors_and_fulltext', valid and dimensions)
            old = active()
            file = root/paths[0];file.write_text(file.read_text()+'\nGuest (00:02):\nChanged synthetic source evidence.\n')
            refreshed = ingest(engine, test_settings, snapshot('changed'))
            new = active()
            with engine.connect() as connection:
                inactive = connection.scalar(text('SELECT count(*) FROM chunks WHERE NOT active'))
                versions = connection.scalar(text('SELECT max(n) FROM (SELECT count(DISTINCT version) n FROM chunks WHERE active GROUP BY episode_id) s'))
            check('changed_episode_replaces_active_version_retains_old_evidence',refreshed['loaded']==1 and refreshed['skipped']==1 and inactive>0 and versions==1 and {r['id'] for r in old}!={r['id'] for r in new})
            # Failure occurs after a real embedding batch; no replacement can publish.
            file.write_text(file.read_text()+'Another changed source sentence.\n')
            stable = active()
            real = OllamaEmbedder(test_settings)
            class FaultAfterBatch:
                digest = None
                calls = 0
                def preflight(self):self.digest=real.preflight();return self.digest
                def embed(self,texts,deadline):
                    self.calls+=1
                    if self.calls>=2:raise EmbeddingError('injected_after_real_embedding_batch')
                    return real.embed(texts,deadline)
                def verify_identity(self):return real.verify_identity()
            fault = FaultAfterBatch()
            try: failed = ingest(engine,test_settings,snapshot('failed-refresh'),embedder=fault,batch_size=1)
            finally: real.close()
            check('failed_embedding_does_not_publish_partial_episode',failed['status']=='failed' and failed['failed']==1 and fault.calls==2 and active()==stable,
                  fault='Intentional failure injection after one actual Ollama batch; not a naturally observed provider outage.')
            resumed = ingest(engine,test_settings,snapshot('failed-refresh'))
            check('resume_after_failure_publishes_complete_version',resumed['loaded']==1 and resumed['skipped']==1)
            stable = active()
            incompatible = test_settings.model_copy(update={'embedding_model':'qwen3:0.6b'})
            mismatch = ingest(engine,incompatible,snapshot('incompatible'))
            check('actual_incompatible_local_model_rejected',mismatch['status']=='failed' and mismatch['last_error_code']=='embedding_model_not_supported' and active()==stable)
            # Same dimensions but different digest/profile must also fail before a publish.
            real = OllamaEmbedder(test_settings)
            class WrongIdentity:
                def preflight(self):real.preflight();return 'intentionally-incompatible-fixture-digest'
            try: mismatch = ingest(engine,test_settings,snapshot('profile-change'),embedder=WrongIdentity())
            finally: real.close()
            check('same_dimension_different_identity_rejected',mismatch['status']=='failed' and mismatch['last_error_code']=='index_embedding_identity_mismatch' and active()==stable)
            (root/paths[1]).unlink()
            deleted = ingest(engine,test_settings,snapshot('deleted'),limit=1)
            with engine.connect() as connection:
                versions_retained = connection.scalar(text('SELECT count(*) FROM episode_versions'))
            check('complete_manifest_deletion_retires_not_erases',deleted['deleted']==1 and deleted['active_episodes']==1 and versions_retained>=4)
            with ingestion_lock(engine):
                busy = False
                try: ingest(engine,test_settings,snapshot('concurrent'))
                except IngestionError as exc: busy = str(exc)=='ingestion_busy'
            check('concurrent_ingestion_rejected',busy)
            # A real stale-run row is recovered after obtaining the exclusive writer lock.
            with engine.begin() as connection:
                abandoned = uuid4()
                connection.execute(text("INSERT INTO ingestion_runs(id,corpus_revision,status,embedding_model,embedding_dimensions) VALUES(:id,'fixture:abandoned','running',:model,768)"),{'id':abandoned,'model':test_settings.embedding_model})
            ingest(engine,test_settings,snapshot('recover-stale'))
            with engine.connect() as connection:
                stale = connection.scalar(text('SELECT status FROM ingestion_runs WHERE id=:id'),{'id':abandoned})
            check('abandoned_run_recorded_as_interrupted',stale=='interrupted')
        finally:
            engine.dispose()
            target=Path('/app/evidence')/('ingestion-integrity-'+database)
            target.mkdir(parents=True,exist_ok=True)
            report['passed'] = bool(report['checks']) and all(r['passed'] for r in report['checks'])
            (target/'result.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps({'event':'ingestion_integrity_result','passed':report['passed'],'evidence_directory':str(target),'database_retained':database}),flush=True)


if __name__=='__main__':main()
