import json
import time
import unittest
from unittest.mock import patch

import httpx
from backend.app.config import Settings
from backend.app.embedding import EmbeddingError, OllamaEmbedder


class EmbeddingProtocolTests(unittest.TestCase):
    def embedder(self, handler):
        item=OllamaEmbedder(Settings(db_password='unit-placeholder'))
        item.client.close()
        item.client=httpx.Client(base_url='http://fixture',transport=httpx.MockTransport(handler))
        self.addCleanup(item.close)
        return item

    def test_array_response_and_no_truncation(self):
        def handler(request):
            payload=json.loads(request.content)
            self.assertFalse(payload['truncate'])
            self.assertEqual(len(payload['input']),2)
            self.assertTrue(all(t.startswith('search_document: ') for t in payload['input']))
            return httpx.Response(200,json={'model':'nomic-embed-text:latest','embeddings':[[.01]*768,[.02]*768]})
        self.assertEqual(len(self.embedder(handler).embed(['one','two'],time.monotonic()+10)),2)

    def test_bad_dimensions_count_model_and_nonfinite_rejected(self):
        values=[{'model':'nomic-embed-text:latest','embeddings':[[.01]*767]},
                {'model':'nomic-embed-text:latest','embeddings':[]},
                {'model':'other','embeddings':[[.01]*768]},
                {'model':'nomic-embed-text:latest','embeddings':[[0.]*768]}]
        for value in values:
            with self.subTest(value=str(value)[:40]),self.assertRaises(EmbeddingError):
                self.embedder(lambda request:httpx.Response(200,json=value)).embed(['one'],time.monotonic()+10)

    def test_retry_budget_is_finite(self):
        calls=[]
        def handler(request):calls.append(request);return httpx.Response(503)
        with patch('backend.app.embedding.time.sleep'),self.assertRaises(EmbeddingError):
            self.embedder(handler).embed(['one'],time.monotonic()+10)
        self.assertEqual(len(calls),3)

    def test_input_error_is_not_retried_or_silently_truncated(self):
        calls=[]
        def handler(request):calls.append(request);return httpx.Response(400,json={'error':'input too long'})
        with self.assertRaises(EmbeddingError):self.embedder(handler).embed(['one'],time.monotonic()+10)
        self.assertEqual(len(calls),1)

    def test_expired_deadline_never_calls_provider(self):
        calls=[]
        def handler(request):calls.append(request);return httpx.Response(200)
        with self.assertRaises(EmbeddingError):self.embedder(handler).embed(['one'],time.monotonic()-1)
        self.assertEqual(calls,[])

    def test_query_prefix_and_identity_deadline(self):
        from backend.app.embedding import QUERY_PREFIX
        seen=[]
        def handler(request):
            seen.append(json.loads(request.content)['input'][0])
            return httpx.Response(200,json={'model':'nomic-embed-text:latest','embeddings':[[.01]*768]})
        item=self.embedder(handler)
        item.embed(['a query'],time.monotonic()+10,prefix=QUERY_PREFIX)
        self.assertEqual(seen,['search_query: a query'])
        with self.assertRaisesRegex(EmbeddingError,'embedding_deadline'):item.verify_identity(time.monotonic()-1)
