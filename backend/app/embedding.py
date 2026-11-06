"""Local-only, bounded Ollama embeddings with explicit index identity."""
from math import isfinite
import time

import httpx

DOCUMENT_PREFIX = "search_document: "
QUERY_PREFIX = "search_query: "


class EmbeddingError(ValueError):
    pass


class OllamaEmbedder:
    def __init__(self, settings):
        self.settings = settings
        self.client = httpx.Client(base_url=settings.ollama_url, timeout=20, trust_env=False)
        self.digest = None

    def close(self):
        self.client.close()

    def verify_identity(self, deadline=None):
        remaining = 20 if deadline is None else min(20, deadline - time.monotonic())
        if remaining <= 0: raise EmbeddingError('embedding_deadline')
        try:
            response = self.client.get('/api/tags', timeout=remaining); response.raise_for_status()
            item = next((m for m in response.json()['models'] if m['name'] == self.settings.embedding_model), None)
            if not item: raise EmbeddingError('embedding_model_missing')
            digest = item['digest']
            if self.digest is not None and digest != self.digest:
                raise EmbeddingError('embedding_model_changed_during_run')
            return digest
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            if isinstance(exc, EmbeddingError): raise
            raise EmbeddingError('embedding_identity_unavailable') from exc

    def preflight(self):
        self.digest = self.verify_identity()
        try:
            response = self.client.post('/api/show', json={'model': self.settings.embedding_model}); response.raise_for_status()
            data = response.json()
            if 'embedding' not in data.get('capabilities', []):
                raise EmbeddingError('embedding_model_not_supported')
            dimensions = next((v for k, v in data.get('model_info', {}).items() if k.endswith('.embedding_length')), None)
            if dimensions != self.settings.embedding_dimensions or dimensions != 768:
                raise EmbeddingError('embedding_dimension_mismatch')
            self.embed(['compatibility probe.'], time.monotonic() + 60)
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            if isinstance(exc, EmbeddingError): raise
            raise EmbeddingError('embedding_preflight_failed') from exc
        return self.digest

    def embed(self, texts, deadline, *, prefix=DOCUMENT_PREFIX):
        if not 1 <= len(texts) <= 8:
            raise EmbeddingError('embedding_batch_out_of_bounds')
        if prefix not in (DOCUMENT_PREFIX, QUERY_PREFIX): raise EmbeddingError('invalid_embedding_task')
        payload = {'model': self.settings.embedding_model, 'input': [prefix + t for t in texts], 'truncate': False,
                   'keep_alive': '2m', 'options': {'num_ctx': 2048}}
        for attempt in range(3):
            remaining = deadline - time.monotonic()
            if remaining <= 0: raise EmbeddingError('embedding_deadline')
            try:
                response = self.client.post('/api/embed', json=payload, timeout=min(20, remaining))
                if response.status_code == 429 or response.status_code >= 500:
                    if attempt < 2:
                        time.sleep(min(.25 * 2 ** attempt, max(0, deadline - time.monotonic())))
                        continue
                    raise EmbeddingError('embedding_provider_unavailable')
                response.raise_for_status()
                data = response.json()
                if data.get('model') != self.settings.embedding_model: raise EmbeddingError('embedding_response_model_mismatch')
                vectors = data['embeddings']
                if len(vectors) != len(texts): raise EmbeddingError('embedding_batch_count_mismatch')
                for vector in vectors:
                    if len(vector) != 768 or any(type(x) not in (int, float) or not isfinite(x) for x in vector) or sum(x*x for x in vector) == 0:
                        raise EmbeddingError('embedding_invalid_vector')
                return vectors
            except httpx.TimeoutException as exc:
                if attempt == 2: raise EmbeddingError('embedding_timeout') from exc
            except httpx.HTTPError as exc:
                raise EmbeddingError('embedding_request_rejected') from exc
            except (KeyError, TypeError, ValueError) as exc:
                if isinstance(exc, EmbeddingError): raise
                raise EmbeddingError('embedding_malformed_response') from exc
        raise EmbeddingError('embedding_timeout')
