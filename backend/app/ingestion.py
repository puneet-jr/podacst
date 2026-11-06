"""Episode-atomic local ingestion; previous exact evidence is never erased on refresh."""
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
import time
from uuid import uuid4, uuid5

from sqlalchemy import text

from backend.app.embedding import DOCUMENT_PREFIX, EmbeddingError, OllamaEmbedder
from backend.app.transcripts import PARSER_VERSION, CHUNK_VERSION, ParseError, parse_transcript, chunk_episode

LOCK_KEY = 741_303_003
PIPELINE_VERSION = PARSER_VERSION + '/' + CHUNK_VERSION


class IngestionError(ValueError):
    pass


def emit(event, **fields):
    print(json.dumps({'timestamp': datetime.now(timezone.utc).isoformat(), 'event': event, **fields}, default=str), flush=True)


@contextmanager
def ingestion_lock(engine):
    with engine.connect() as connection:
        if not connection.scalar(text('SELECT pg_try_advisory_lock(:key)'), {'key': LOCK_KEY}):
            connection.rollback()
            raise IngestionError('ingestion_busy')
        connection.commit()
        try: yield
        finally:
            try:
                connection.execute(text('SELECT pg_advisory_unlock(:key)'), {'key': LOCK_KEY})
                connection.commit()
            except Exception:
                connection.invalidate()


def outcome(connection, run_id, path, status, *, source_hash=None, episode_id=None, chunks=0, error=None, warnings=None):
    connection.execute(text('''INSERT INTO ingestion_items(run_id,source_path,source_hash,status,episode_id,chunks,error_code,warnings)
      VALUES(:run,:path,:hash,:status,:episode,:chunks,:error,CAST(:warnings AS jsonb))
      ON CONFLICT(run_id,source_path) DO UPDATE SET status=excluded.status,source_hash=excluded.source_hash,
      episode_id=excluded.episode_id,chunks=excluded.chunks,error_code=excluded.error_code,warnings=excluded.warnings,updated_at=now()'''),
      {'run':run_id,'path':path,'hash':source_hash,'status':status,'episode':episode_id,'chunks':chunks,'error':error,'warnings':json.dumps(warnings or [])})


def check_profile(connection, settings, digest):
    schema_type = connection.scalar(text("SELECT format_type(atttypid,atttypmod) FROM pg_attribute WHERE attrelid='chunks'::regclass AND attname='embedding'"))
    if schema_type != 'vector(768)' or settings.embedding_dimensions != 768:
        raise IngestionError('index_dimension_mismatch')
    existing = connection.execute(text('SELECT * FROM knowledge_config WHERE singleton')).mappings().first()
    if existing and (existing['embedding_model'] != settings.embedding_model or existing['embedding_digest'] != digest or existing['dimensions'] != 768 or existing['document_prefix'] != DOCUMENT_PREFIX):
        raise IngestionError('index_embedding_identity_mismatch')


def update_counts(connection, run_id):
    counts = connection.execute(text("SELECT status,count(*) AS count FROM ingestion_items WHERE run_id=:run GROUP BY status"), {'run':run_id}).all()
    values = dict(counts)
    connection.execute(text('UPDATE ingestion_runs SET loaded=:loaded,skipped=:skipped,failed=:failed,deleted=:deleted,heartbeat_at=now() WHERE id=:run'),
                       {'run':run_id,'loaded':values.get('loaded',0),'skipped':values.get('unchanged',0),'failed':values.get('failed',0),'deleted':values.get('deleted',0)})


def publish_episode(engine, run_id, episode, chunks, vectors, snapshot, settings, digest, fingerprint):
    with engine.begin() as connection:
        check_profile(connection, settings, digest)
        connection.execute(text('''INSERT INTO knowledge_config(singleton,source_url,embedding_model,embedding_digest,dimensions,document_prefix)
          VALUES(true,:source,:model,:digest,768,:prefix) ON CONFLICT(singleton) DO NOTHING'''),
          {'source':snapshot.source_url,'model':settings.embedding_model,'digest':digest,'prefix':DOCUMENT_PREFIX})
        previous = connection.execute(text('SELECT current_version FROM episodes WHERE id=:id FOR UPDATE'), {'id':episode.id}).scalar_one_or_none()
        version = (previous or 0) + 1
        connection.execute(text('''INSERT INTO episodes(id,source_path,source_hash,title,guest,published_on,video_url)
          VALUES(:id,:path,:hash,:title,:guest,:date,:url) ON CONFLICT(id) DO NOTHING'''),
          {'id':episode.id,'path':episode.path,'hash':episode.source_hash,'title':episode.title,'guest':episode.guest,'date':episode.published_on,'url':episode.video_url})
        metadata = {'title':episode.title,'guest':episode.guest,'published_on':str(episode.published_on) if episode.published_on else None,
                    'video_url':episode.video_url,'warnings':episode.warnings,'fingerprint':fingerprint,'source_metadata':episode.metadata}
        connection.execute(text('''INSERT INTO episode_versions(episode_id,version,source_path,source_hash,corpus_revision,original_text,metadata,parser_version,chunker_version)
          VALUES(:id,:version,:path,:hash,:revision,:original,CAST(:metadata AS jsonb),:parser,:chunker)'''),
          {'id':episode.id,'version':version,'path':episode.path,'hash':episode.source_hash,'revision':snapshot.revision,'original':episode.original,'metadata':json.dumps(metadata,default=str),'parser':PARSER_VERSION,'chunker':CHUNK_VERSION})
        connection.execute(text('UPDATE chunks SET active=false WHERE episode_id=:id AND active'), {'id':episode.id})
        records=[]
        for chunk, vector in zip(chunks, vectors, strict=True):
            records.append({'id':uuid5(episode.id,f'{version}:{chunk.ordinal}:{fingerprint}'),'episode':episode.id,'run':run_id,'ordinal':chunk.ordinal,'version':version,
              'hash':episode.source_hash,'original':chunk.original,'search':chunk.search_text,'speakers':json.dumps(chunk.speakers),'start':chunk.start_seconds,'end':chunk.end_seconds,
              'vector':json.dumps(vector),'model':settings.embedding_model,'digest':digest,'revision':snapshot.revision,'char_start':chunk.start,'char_end':chunk.end,
              'line_start':chunk.line_start,'line_end':chunk.line_end,'tokens':chunk.estimated_tokens,'sponsor':chunk.sponsor})
        connection.execute(text('''INSERT INTO chunks(id,episode_id,ingestion_run_id,ordinal,version,source_hash,original_text,search_text,speakers,start_seconds,end_seconds,
          embedding,embedding_model,active,char_start,char_end,line_start,line_end,estimated_tokens,sponsor,embedding_digest,corpus_revision)
          VALUES(:id,:episode,:run,:ordinal,:version,:hash,:original,:search,CAST(:speakers AS jsonb),:start,:end,CAST(:vector AS vector),:model,true,
          :char_start,:char_end,:line_start,:line_end,:tokens,:sponsor,:digest,:revision)'''), records)
        connection.execute(text('''UPDATE episodes SET source_hash=:hash,title=:title,guest=:guest,published_on=:date,video_url=:url,
          current_version=:version,deleted_at=NULL,updated_at=now() WHERE id=:id'''),
          {'id':episode.id,'hash':episode.source_hash,'title':episode.title,'guest':episode.guest,'date':episode.published_on,'url':episode.video_url,'version':version})
        outcome(connection, run_id, episode.path, 'loaded', source_hash=episode.source_hash, episode_id=episode.id, chunks=len(chunks), warnings=episode.warnings)
        update_counts(connection, run_id)


def ingest(engine, settings, snapshot, *, limit=None, source_paths=None, batch_size=4, deadline_seconds=600, embedder=None):
    if limit is not None and limit < 1 or not 1 <= batch_size <= 8 or not 1 <= deadline_seconds <= 3600:
        raise IngestionError('invalid_ingestion_bounds')
    files = sorted(snapshot.files)
    if not files or not snapshot.complete: raise IngestionError('complete_nonempty_manifest_required')
    if source_paths is not None and (not source_paths or len(source_paths) != len(set(source_paths)) or any(path not in snapshot.files for path in source_paths)):
        raise IngestionError('invalid_source_selection')
    scoped = sorted(source_paths) if source_paths is not None else files
    selected = scoped[:limit] if limit else scoped
    run_id, started = uuid4(), time.monotonic()
    deadline = started + deadline_seconds
    own_embedder = embedder is None
    with ingestion_lock(engine):
        embedder = embedder or OllamaEmbedder(settings)
        try:
            with engine.begin() as connection:
                connection.execute(text("UPDATE ingestion_runs SET status='interrupted',last_error_code='previous_process_interrupted',completed_at=now() WHERE status='running'"))
                connection.execute(text('''INSERT INTO ingestion_runs(id,corpus_revision,status,discovered,selected,embedding_model,embedding_dimensions,pipeline_version,source_url,source_kind,manifest_complete)
                  VALUES(:id,:revision,'running',:discovered,:selected,:model,768,:pipeline,:url,:kind,true)'''),
                  {'id':run_id,'revision':snapshot.revision,'discovered':len(files),'selected':len(selected),'model':settings.embedding_model,'pipeline':PIPELINE_VERSION,'url':snapshot.source_url,'kind':snapshot.kind})
                for path in selected: outcome(connection, run_id, path, 'pending', source_hash=snapshot.files[path])
            digest = embedder.preflight()
            with engine.begin() as connection:
                check_profile(connection, settings, digest)
                connection.execute(text('UPDATE ingestion_runs SET embedding_digest=:digest WHERE id=:id'), {'id':run_id,'digest':digest})
            for index, path in enumerate(selected):
                try:
                    if time.monotonic() >= deadline: raise IngestionError('run_deadline')
                    data = snapshot.read(path)
                    fingerprint = sha256((snapshot.files[path] + PIPELINE_VERSION + settings.embedding_model + digest + DOCUMENT_PREFIX).encode()).hexdigest()
                    with engine.connect() as connection:
                        old = connection.execute(text('''SELECT e.id,e.deleted_at,v.metadata FROM episodes e JOIN episode_versions v ON v.episode_id=e.id AND v.version=e.current_version
                          WHERE e.source_path=:path'''), {'path':path}).mappings().first()
                    if old and old['deleted_at'] is None and old['metadata'].get('fingerprint') == fingerprint:
                        with engine.begin() as connection:
                            outcome(connection, run_id, path, 'unchanged', source_hash=snapshot.files[path], episode_id=old['id'])
                            update_counts(connection, run_id)
                        emit('episode_unchanged', run_id=run_id, source_path=path, completed=index+1, selected=len(selected))
                        continue
                    episode = parse_transcript(data, path)
                    chunks = chunk_episode(episode)
                    vectors = []
                    episode_deadline = min(deadline, time.monotonic() + 180)
                    for offset in range(0, len(chunks), batch_size):
                        vectors.extend(embedder.embed([c.search_text for c in chunks[offset:offset+batch_size]], episode_deadline))
                        with engine.begin() as connection:
                            connection.execute(text('UPDATE ingestion_runs SET heartbeat_at=now() WHERE id=:id'), {'id':run_id})
                        emit('embedding_progress', run_id=run_id, source_path=path, completed_chunks=len(vectors), total_chunks=len(chunks))
                    embedder.verify_identity()
                    publish_episode(engine, run_id, episode, chunks, vectors, snapshot, settings, digest, fingerprint)
                    emit('episode_loaded', run_id=run_id, source_path=path, chunks=len(chunks), warnings=episode.warnings, completed=index+1, selected=len(selected))
                except Exception as exc:
                    code = str(exc) if isinstance(exc, (ParseError, EmbeddingError, IngestionError)) else 'episode_processing_failed'
                    with engine.begin() as connection:
                        outcome(connection, run_id, path, 'failed', source_hash=snapshot.files[path], error=code)
                        update_counts(connection, run_id)
                    emit('episode_failed', run_id=run_id, source_path=path, code=code)
            # Reconcile against the complete manifest, never the --limit subset.
            with engine.begin() as connection:
                old_files = connection.execute(text('SELECT id,source_path FROM episodes WHERE deleted_at IS NULL')).all()
                for episode_id, path in old_files:
                    if path not in snapshot.files:
                        connection.execute(text('UPDATE chunks SET active=false WHERE episode_id=:id'), {'id':episode_id})
                        connection.execute(text('UPDATE episodes SET deleted_at=now() WHERE id=:id'), {'id':episode_id})
                        outcome(connection, run_id, path, 'deleted', episode_id=episode_id)
                update_counts(connection, run_id)
                connection.execute(text("UPDATE ingestion_runs SET status=CASE WHEN failed>0 THEN 'failed' WHEN selected<discovered THEN 'partial' ELSE 'completed' END,completed_at=now() WHERE id=:id"), {'id':run_id})
        except Exception as exc:
            code = str(exc) if isinstance(exc, (EmbeddingError, IngestionError)) else 'ingestion_failed'
            with engine.begin() as connection:
                connection.execute(text("UPDATE ingestion_runs SET status='failed',last_error_code=:code,completed_at=now() WHERE id=:id"), {'id':run_id,'code':code})
            emit('ingestion_failed', run_id=run_id, code=code)
        finally:
            if own_embedder: embedder.close()
        with engine.connect() as connection:
            result = dict(connection.execute(text('SELECT * FROM ingestion_runs WHERE id=:id'), {'id':run_id}).mappings().one())
            result['active_episodes'] = connection.scalar(text('SELECT count(*) FROM episodes WHERE deleted_at IS NULL AND current_version IS NOT NULL'))
            result['active_chunks'] = connection.scalar(text('SELECT count(*) FROM chunks WHERE active'))
        result['unattempted'] = result['selected'] - result['loaded'] - result['skipped'] - result['failed']
        result['duration_seconds'] = time.monotonic() - started
        emit('ingestion_result', **result)
        return result
