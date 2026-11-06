"""Bounded, read-only local retrieval. Rank scores never attest semantic support."""
from collections import Counter
from hashlib import sha256
import json
import time
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import text

from backend.app.embedding import DOCUMENT_PREFIX, QUERY_PREFIX, EmbeddingError, OllamaEmbedder

RETRIEVAL_VERSION = 'rrf-v3-idf-budgeted-neighbors'


class RetrievalError(ValueError):
    pass


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    query: str = Field(min_length=1, max_length=1000)
    mode: Literal['sparse', 'dense', 'hybrid'] = 'sparse'
    guest: str | None = Field(default=None, min_length=1, max_length=120)
    episode_id: UUID | None = None
    source_path: str | None = Field(default=None, pattern=r'^episodes/[a-z0-9-]+/transcript\.md$', max_length=240)
    candidates: int = Field(default=20, ge=5, le=100)
    limit: int = Field(default=8, ge=1, le=10)
    token_budget: int = Field(default=3200, ge=300, le=8000)
    per_episode: int = Field(default=6, ge=1, le=10)
    neighbor_radius: int = Field(default=1, ge=0, le=1)
    max_neighbors: int = Field(default=2, ge=0, le=2)
    rrf_constant: int = Field(default=60, ge=1, le=100)
    include_sponsors: bool = True
    deadline_seconds: float = Field(default=25, ge=1, le=45)

    @field_validator('query', 'guest')
    @classmethod
    def trim(cls, value):
        if value is None: return value
        value = value.strip()
        if not value or '\x00' in value: raise ValueError('nonempty text required')
        return value


class Passage(BaseModel):
    id: UUID
    episode_id: UUID
    ordinal: int
    version: int
    source_path: str
    source_hash: str
    corpus_revision: str
    title: str
    guest: str | None
    video_url: str | None
    speakers: list[str]
    start_seconds: float | None
    end_seconds: float | None
    char_start: int
    char_end: int
    line_start: int
    line_end: int
    original_text: str
    text_sha256: str
    estimated_tokens: int
    sponsor: bool
    metadata_warnings: list[str]
    dense_rank: int | None = None
    sparse_rank: int | None = None
    rank_score: float
    kind: Literal['ranked', 'neighbor']
    neighbor_of: UUID | None = None


class SearchResult(BaseModel):
    status: Literal['empty_evidence', 'review_required']
    guidance: str
    mode: str
    retrieval_version: str
    passages: list[Passage]
    estimated_tokens: int
    candidate_counts: dict[str, int]
    corpus: dict
    timings_ms: dict[str, float]
    embedding_model: str | None
    embedding_digest: str | None
    support_verified: Literal[False] = False


def reciprocal_rank_fusion(rankings, constant=60):
    """One vote per ID per index, stable UUID tie breaks, no score calibration."""
    fused = {}
    for name, rows in rankings.items():
        seen = set()
        rank = 0
        for row in rows:
            key = str(row['id'])
            if key in seen: continue
            seen.add(key); rank += 1
            item = fused.setdefault(key, {**row, 'dense_rank': None, 'sparse_rank': None, 'rank_score': 0., 'kind': 'ranked', 'neighbor_of': None})
            item[name+'_rank'] = rank
            item['rank_score'] += 1/(constant+rank)
    return sorted(fused.values(), key=lambda r: (-r['rank_score'], min(r.get('dense_rank') or 10**9, r.get('sparse_rank') or 10**9), str(r['id'])))


def overlaps(a, b):
    if a['source_hash'] != b['source_hash'] or str(a['episode_id']) != str(b['episode_id']) or a['version'] != b['version']: return False
    common = max(0, min(a['char_end'], b['char_end']) - max(a['char_start'], b['char_start']))
    return common / max(1, min(a['char_end']-a['char_start'], b['char_end']-b['char_start'])) >= .6


def select_passages(rows, request, *, existing=(), capacity=None):
    selected, hashes, counts = list(existing), set(), Counter(str(r['episode_id']) for r in existing)
    hashes.update(sha256(' '.join(r['original_text'].casefold().split()).encode()).digest() for r in existing)
    used = sum(r['estimated_tokens'] for r in existing)
    for row in rows:
        if len(selected) >= (request.limit if capacity is None else capacity): break
        digest = sha256(' '.join(row['original_text'].casefold().split()).encode()).digest()
        if digest in hashes or any(str(row['id']) == str(r['id']) or overlaps(row,r) for r in selected): continue
        cap = request.limit if request.episode_id or request.source_path else request.per_episode
        if counts[str(row['episode_id'])] >= cap: continue
        if used + row['estimated_tokens'] > request.token_budget: continue
        selected.append(row); hashes.add(digest); counts[str(row['episode_id'])] += 1; used += row['estimated_tokens']
    return selected


COLUMNS = '''c.id,c.episode_id,c.ordinal,c.version,c.source_hash,c.corpus_revision,c.original_text,
 c.char_start,c.char_end,c.line_start,c.line_end,c.speakers,c.start_seconds,c.end_seconds,c.estimated_tokens,c.sponsor,
 e.source_path,e.title,e.guest,e.video_url,v.metadata->'warnings' AS metadata_warnings'''
BASE = ''' FROM chunks c JOIN episodes e ON e.id=c.episode_id AND e.current_version=c.version
 JOIN episode_versions v ON v.episode_id=c.episode_id AND v.version=c.version
 WHERE c.active AND e.deleted_at IS NULL AND c.embedding_model=:model AND c.embedding_digest=:digest
 AND (:include_sponsors OR NOT c.sponsor)'''


def search(engine, settings, request: SearchRequest, *, embedder=None):
    started = time.monotonic(); deadline = started + request.deadline_seconds
    timings, vector, digest = {}, None, None
    def budget(connection=None):
        remaining = deadline-time.monotonic()
        if remaining <= 0: raise RetrievalError('retrieval_deadline')
        if connection is not None:
            connection.execute(text("SELECT set_config('statement_timeout',:timeout,true)"), {'timeout':str(max(1,min(3000,int(remaining*1000))))})
    with engine.connect() as connection:
        budget(connection)
        profile = connection.execute(text('SELECT * FROM knowledge_config WHERE singleton')).mappings().first()
    if profile is None:
        return SearchResult(status='empty_evidence',guidance='No indexed evidence is available. Ingest transcripts before answering.',mode=request.mode,retrieval_version=RETRIEVAL_VERSION,
            passages=[],estimated_tokens=0,candidate_counts={'dense':0,'sparse':0},corpus={'active_episodes':0,'active_chunks':0,'discovered':0,'partial':True},timings_ms={'total':(time.monotonic()-started)*1000},embedding_model=None,embedding_digest=None)
    if profile['embedding_model'] != settings.embedding_model or profile['dimensions'] != settings.embedding_dimensions or profile['dimensions'] != 768 or profile['document_prefix'] != DOCUMENT_PREFIX:
        raise RetrievalError('index_embedding_identity_mismatch')
    digest = profile['embedding_digest']
    if request.mode != 'sparse':
        owned = embedder is None
        embedder = embedder or OllamaEmbedder(settings)
        try:
            if embedder.verify_identity(deadline) != digest: raise RetrievalError('index_embedding_identity_mismatch')
            vector = embedder.embed([request.query],deadline,prefix=QUERY_PREFIX)[0]
            if embedder.verify_identity(deadline) != digest: raise RetrievalError('index_embedding_identity_mismatch')
        finally:
            if owned: embedder.close()
        timings['embedding'] = (time.monotonic()-started)*1000
    budget()
    params = {'model':settings.embedding_model,'digest':digest,'include_sponsors':request.include_sponsors,'query':request.query,'candidates':request.candidates}
    filters = ''
    if request.guest is not None: filters += ' AND lower(e.guest)=lower(:guest)'; params['guest']=request.guest
    if request.episode_id is not None: filters += ' AND e.id=:episode'; params['episode']=request.episode_id
    if request.source_path is not None: filters += ' AND e.source_path=:path'; params['path']=request.source_path
    rankings = {}
    db_started = time.monotonic()
    # Both indexes and neighbors use one read-only, consistent publication snapshot.
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as connection, connection.begin():
        connection.execute(text('SET TRANSACTION READ ONLY'))
        budget(connection)
        current_profile = connection.scalar(text('SELECT embedding_digest FROM knowledge_config WHERE singleton'))
        if current_profile != digest: raise RetrievalError('index_embedding_identity_mismatch')
        if request.mode != 'sparse':
            params['vector']=json.dumps(vector)
            rankings['dense'] = [dict(r) for r in connection.execute(text('SELECT '+COLUMNS+BASE+filters+' AND c.embedding IS NOT NULL ORDER BY c.embedding <=> CAST(:vector AS vector),c.id LIMIT :candidates'),params).mappings()]
        if request.mode != 'dense':
            budget(connection)
            # Fresh corpus-frequency weighting reduces repeated speaker-header dominance.
            # OR retains recall on natural questions; no query text becomes SQL syntax.
            lexical = """WITH terms AS (SELECT unnest(tsvector_to_array(to_tsvector('english',:query))) AS term),
             q AS (SELECT to_tsquery('english',COALESCE(string_agg(quote_literal(term),' | '),'')) AS tsq FROM terms),
             df AS (SELECT t.term,ln(1.0+(SELECT count(*) FROM chunks WHERE active)/(1.0+count(d.id))) AS weight
              FROM terms t LEFT JOIN chunks d ON d.active AND d.search_vector @@ to_tsquery('english',quote_literal(t.term)) GROUP BY t.term) """
            rankings['sparse'] = [dict(r) for r in connection.execute(text(lexical+'SELECT '+COLUMNS+BASE+filters+" AND c.search_vector @@ (SELECT tsq FROM q) ORDER BY (SELECT sum(weight) FROM df WHERE c.search_vector @@ to_tsquery('english',quote_literal(df.term))) DESC,ts_rank_cd(c.search_vector,(SELECT tsq FROM q),32) DESC,c.id LIMIT :candidates"),params).mappings()]
        fused = reciprocal_rank_fusion(rankings,request.rrf_constant)
        reserve = min(request.max_neighbors, request.limit-1) if request.neighbor_radius else 0
        # Reserve tokens as well as slots; otherwise ranked chunks starve expansion.
        neighbor_budget = min(reserve*700,request.token_budget//3)
        core_request = request.model_copy(update={'token_budget':request.token_budget-neighbor_budget})
        selected = select_passages(fused,core_request,capacity=request.limit-reserve)
        if not selected: selected = select_passages(fused,request,capacity=1)
        neighbors = []
        if request.neighbor_radius and request.max_neighbors and selected:
            for anchor in selected:
                if len(neighbors) >= request.max_neighbors: break
                budget(connection)
                neighbor_params={**params,'neighbor_episode':anchor['episode_id'],'neighbor_version':anchor['version'],'ordinal':anchor['ordinal']}
                nearby=[dict(r) for r in connection.execute(text('SELECT '+COLUMNS+BASE+filters+' AND c.episode_id=:neighbor_episode AND c.version=:neighbor_version AND abs(c.ordinal-:ordinal)=1 ORDER BY c.ordinal LIMIT 2'),neighbor_params).mappings()]
                for row in nearby:
                    row.update(dense_rank=None,sparse_rank=None,rank_score=0.,kind='neighbor',neighbor_of=anchor['id'])
                    appended=select_passages([row],request,existing=selected+neighbors)
                    if len(appended)>len(selected)+len(neighbors): neighbors.append(row)
                    if len(neighbors)>=request.max_neighbors:break
        selected += neighbors
        selected = select_passages(fused,request,existing=selected)
        corpus=dict(connection.execute(text('''SELECT (SELECT count(*) FROM episodes WHERE deleted_at IS NULL AND current_version IS NOT NULL) AS active_episodes,
         (SELECT count(*) FROM chunks WHERE active) AS active_chunks,
         COALESCE((SELECT discovered FROM ingestion_runs WHERE source_kind='corpus' ORDER BY created_at DESC LIMIT 1),0) AS discovered''')).mappings().one())
    timings['database']=(time.monotonic()-db_started)*1000
    timings['total']=(time.monotonic()-started)*1000
    budget()
    corpus['partial']=not corpus['discovered'] or corpus['active_episodes']<corpus['discovered']
    passages=[]
    for row in selected:
        row['text_sha256']=sha256(row['original_text'].encode()).hexdigest()
        row['metadata_warnings']=row['metadata_warnings'] or []
        passages.append(Passage.model_validate(row))
    return SearchResult(status='review_required' if passages else 'empty_evidence',guidance=(
        'Candidate passages require claim-by-claim support review. Rank scores are not probabilities. Sponsor flags can mark mixed passages: advertisements are not substantive product evidence. If the requested fact is absent, state the evidence limitation; do not infer private facts, current facts or guarantees from related text.'
        if passages else 'No passages matched within the selected scope and bounds. State that evidence is insufficient; ask for a supported reformulation or broader explicit scope.'),
        mode=request.mode,retrieval_version=RETRIEVAL_VERSION,passages=passages,estimated_tokens=sum(p.estimated_tokens for p in passages),
        candidate_counts={name:len(rankings.get(name,[])) for name in ('dense','sparse')},corpus=corpus,timings_ms=timings,
        embedding_model=settings.embedding_model if vector is not None else None,embedding_digest=digest)
