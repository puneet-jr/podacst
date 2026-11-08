"""Actual PostgreSQL/Ollama on synthetic evidence, only in a fresh contract database."""
from collections import Counter
from hashlib import sha256
import io
import json
import logging
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

if not os.environ.get('POSTGRES_DB','').startswith('lenny_contract_'):
    raise RuntimeError('Requires isolated contract DB')

from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.app.embedding import EmbeddingError
from backend.app.ingestion import IngestionError, ingest
from backend.app.main import app,engine,logger,settings
from backend.app.retrieval import SearchRequest, search
from backend.app.snapshot import Snapshot


class RetrievalDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='retrieval-fixture-')
        root=Path(cls.temp.name)
        for name,guest in [('alpha','Fixture Researcher A'),('beta','Fixture Researcher B'),('gamma','Fixture Researcher C')]:
            p=root/f'episodes/retrieval-{name}/transcript.md';p.parent.mkdir(parents=True)
            content=f'---\nguest: {guest}\ntitle: {guest} synthetic research\n---\n## Transcript\n'
            if name=='beta':content+='Host (00:00):\nThis episode is brought to you by SponsorQuartz. '+('An advertisement offers a discount for its product. '*60)+'\n'
            for i in range(10):
                content+=f'{guest} (00:{i+1:02d}):\n'
                topic={'alpha':'A quartz activation experiment measures onboarding outcomes with evidence. ',
                       'beta':'Accounting ledgers preserve financial transactions for auditors. ',
                       'gamma':'A crimson garden grows flowers in spring and needs regular watering. '}[name]
                content+=topic*18
                if name=='alpha' and i==4:content+='Anchorquartz describes the middle context needed to inspect the full experiment. '
                content+='\n'
            p.write_text(content)
        cls.snapshot=Snapshot(root,'fixture:retrieval',{str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in root.glob('episodes/*/transcript.md')},kind='fixture')
        result=ingest(engine,settings,cls.snapshot)
        if result['loaded']!=3 or result['failed']:raise RuntimeError('Real fixture embeddings failed')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup();engine.dispose()


    def test_precomputed_term_weights_preserve_reference_ranking(self):
        from backend.app.retrieval import LEXICAL_CTE
        reference = """WITH terms AS (SELECT unnest(tsvector_to_array(to_tsvector('english',:query))) AS term),
          df AS (SELECT t.term,ln(1.0+(SELECT count(*) FROM chunks WHERE active)/(1.0+count(d.id))) AS weight
          FROM terms t LEFT JOIN chunks d ON d.active AND d.search_vector @@ to_tsquery('english',quote_literal(t.term)) GROUP BY t.term)
          SELECT c.id,(SELECT sum(weight) FROM df WHERE c.search_vector @@ to_tsquery('english',quote_literal(df.term))) AS score
          FROM chunks c WHERE c.active ORDER BY score DESC NULLS LAST,c.id"""
        current = LEXICAL_CTE+"SELECT c.id,(SELECT sum(weight) FROM df WHERE c.search_vector @@ df.term_query) AS score FROM chunks c WHERE c.active ORDER BY score DESC NULLS LAST,c.id"
        with engine.connect() as c:
            for query in ['quartz activation','accounting garden','anchorquartz crimson','unseenrareword']:
                with self.subTest(query=query):
                    expected=list(c.execute(text(reference),{'query':query}));actual=list(c.execute(text(current),{'query':query}))
                    self.assertEqual(actual,expected)

    def test_actual_sparse_source_integrity(self):
        result=search(engine,settings,SearchRequest(query='quartz activation',mode='sparse'))
        self.assertGreater(len(result.passages),0)
        for p in result.passages:
            with engine.connect() as c:
                original=c.scalar(text('SELECT original_text FROM episode_versions WHERE episode_id=:id AND version=:version'),{'id':p.episode_id,'version':p.version})
                self.assertEqual(original[p.char_start:p.char_end],p.original_text)
                self.assertEqual(c.scalar(text('SELECT vector_dims(embedding) FROM chunks WHERE id=:id'),{'id':p.id}),768)
            self.assertEqual(sha256(p.original_text.encode()).hexdigest(),p.text_sha256)
        self.assertFalse(result.support_verified)

    def test_actual_dense_and_hybrid_local_query_embedding(self):
        for mode in ('dense','hybrid'):
            result=search(engine,settings,SearchRequest(query='activation experiment onboarding',mode=mode))
            self.assertTrue(result.passages)
            self.assertTrue(result.embedding_digest)
            self.assertGreater(result.candidate_counts['dense'],0)
            if mode=='hybrid':self.assertGreater(result.candidate_counts['sparse'],0)
            self.assertLessEqual(len(result.passages),8)

    def test_exact_filters_and_no_silent_scope_relaxation(self):
        scoped=search(engine,settings,SearchRequest(query='quartz activation',guest='fixture researcher a',mode='sparse'))
        self.assertTrue(scoped.passages)
        self.assertTrue(all(p.guest=='Fixture Researcher A' for p in scoped.passages))
        missing=search(engine,settings,SearchRequest(query='quartz activation',episode_id=uuid4(),mode='sparse'))
        self.assertEqual(missing.status,'empty_evidence');self.assertFalse(missing.passages)

    def test_budgets_and_sponsor_exclusion(self):
        result=search(engine,settings,SearchRequest(query='quartz accounting garden',mode='hybrid',token_budget=1700,per_episode=1,include_sponsors=False))
        self.assertLessEqual(result.estimated_tokens,1700)
        self.assertTrue(all(n<=1 for n in Counter(p.episode_id for p in result.passages).values()))
        self.assertFalse(any(p.sponsor for p in result.passages))
        ads=search(engine,settings,SearchRequest(query='SponsorQuartz advertisement',mode='sparse',include_sponsors=True))
        self.assertTrue(any(p.sponsor for p in ads.passages))

    def test_neighbors_are_bounded_same_version_exact_passages(self):
        result=search(engine,settings,SearchRequest(query='anchorquartz',mode='sparse',source_path='episodes/retrieval-alpha/transcript.md'))
        neighbors=[p for p in result.passages if p.kind=='neighbor']
        ranked={p.id:p for p in result.passages if p.kind=='ranked'}
        self.assertTrue(neighbors)
        self.assertLessEqual(len(neighbors),2)
        for p in neighbors:
            parent=ranked[p.neighbor_of]
            self.assertEqual((p.episode_id,p.version),(parent.episode_id,parent.version))
            self.assertEqual(abs(p.ordinal-parent.ordinal),1)
        budgeted=search(engine,settings,SearchRequest(query='anchorquartz',mode='sparse',source_path='episodes/retrieval-alpha/transcript.md',token_budget=3200))
        self.assertTrue(any(p.kind=='neighbor' for p in budgeted.passages))
        self.assertLessEqual(budgeted.estimated_tokens,3200)

    def test_rare_terms_outrank_repeated_speaker_headers(self):
        result=search(engine,settings,SearchRequest(query='Fixture Researcher A anchorquartz',mode='sparse',neighbor_radius=0))
        self.assertTrue(result.passages)
        self.assertIn('Anchorquartz',result.passages[0].original_text)

    def test_retired_episode_is_never_retrieved(self):
        with engine.begin() as c:
            ident=c.scalar(text("UPDATE episodes SET deleted_at=now() WHERE source_path='episodes/retrieval-alpha/transcript.md' RETURNING id"))
        try:
            result=search(engine,settings,SearchRequest(query='quartz activation',mode='dense',episode_id=ident))
            self.assertFalse(result.passages)
        finally:
            with engine.begin() as c:c.execute(text('UPDATE episodes SET deleted_at=NULL WHERE id=:id'),{'id':ident})

    def test_selection_uses_full_manifest_for_deletions(self):
        result=ingest(engine,settings,self.snapshot,source_paths=['episodes/retrieval-alpha/transcript.md'])
        self.assertEqual((result['discovered'],result['selected'],result['skipped'],result['deleted']),(3,1,1,0))
        self.assertEqual(result['active_episodes'],3)
        with self.assertRaisesRegex(IngestionError,'invalid_source_selection'):
            ingest(engine,settings,self.snapshot,source_paths=['episodes/missing/transcript.md'])

    def test_api_typed_bounds_safe_logs_and_no_fallback(self):
        stream=io.StringIO();handler=logging.StreamHandler(stream);logger.addHandler(handler)
        try:
            client=TestClient(app)
            secret_query='PRIVATE_QUERY_MARKER_quartz'
            result=client.post('/api/retrieval/search',json={'query':secret_query,'mode':'sparse'})
            self.assertEqual(result.status_code,200,result.text)
            self.assertNotIn(secret_query,stream.getvalue())
            self.assertEqual(client.post('/api/retrieval/search',json={'query':'quartz','limit':100}).status_code,422)
            with patch('backend.app.retrieval.OllamaEmbedder',side_effect=EmbeddingError('embedding_identity_unavailable')):
                unavailable=client.post('/api/retrieval/search',json={'query':'quartz','mode':'hybrid'})
                self.assertEqual(unavailable.status_code,503)
                self.assertEqual(unavailable.json()['error']['code'],'embedding_identity_unavailable')
                self.assertEqual(client.post('/api/retrieval/search',json={'query':'quartz','mode':'sparse'}).status_code,200)
                default=client.post('/api/retrieval/search',json={'query':'quartz'})
                self.assertEqual(default.status_code,200)
                self.assertEqual(default.json()['mode'],'sparse')
        finally:logger.removeHandler(handler)
