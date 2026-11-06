# Retrieval operations

Start the existing isolated stack with `python3 scripts/bootstrap.py`. Keep host Ollama running. The current API is loopback 8000, frontend proxy 8080 and isolated DB 55432. Do not reset databases/volumes or change host PostgreSQL 5432. Corpus/model/data prerequisites and selective ingestion command are in [Phase 4 report](phase-04-report.md); base ingestion safety remains in [Phase 3 operations](phase-03-operations.md).

## Search contract

`POST /api/retrieval/search` accepts a bounded JSON query and returns **candidate evidence**, not an answer. OpenAPI at `/docs` defines the complete typed request/response. Default mode is **sparse**, intentionally selected using the tuning comparison. Dense/hybrid can be requested explicitly; errors never change modes or invoke cloud inference.

| Input | Meaning/default |
| --- | --- |
| query | Trimmed text, 1–1,000 characters. Full-text query lexemes are normalized/quoted as data; no arbitrary SQL. |
| mode | sparse / dense / hybrid; default sparse. |
| guest | Optional case-insensitive exact original guest metadata. No fuzzy/topic-based automatic restriction. |
| episode_id / source_path | Optional exact UUID/path; all supplied scopes intersect. An unknown scope remains empty, never broadens. |
| candidates / limit | 20 per retriever (5–100), maximum eight final passages by default (1–10). |
| token_budget | 3,200 estimated source-text tokens (300–8,000). Fewer passages return if necessary; no truncation/reconstruction of originals. |
| per_episode | Six by default; an explicit single-episode/path scope uses its limit. |
| neighbor_radius / max_neighbors | Radius one, at most two additions; zero disables. Both slots and tokens are reserved; unfilled space can be filled with ranked candidates. |
| include_sponsors | true by default: retain and visibly flag mixed source passages. false excludes flagged chunks; this may lose substantive evidence. |
| rrf_constant / deadline_seconds | 60 / 25 seconds, configurable bounded ranges in OpenAPI. Individual DB statements max three seconds, model calls max 20 with finite retries; pool/connect waits also have finite limits. |

Exact pgvector cosine ordering and full-text candidates use one read-only repeatable-read snapshot, joined to active current episode versions and the pinned embedding profile. Lexical OR terms use fresh corpus frequency weighting then cover-density ranking for ties; repeated guest headers should not dominate through raw frequency alone. RRF votes once per ID/index with deterministic ties, then selection removes exact normalized duplicates/heavy same-source overlap and caps episode concentration. Modest original overlap remains, with exact source spans intact.

Neighbors stay in the same episode/version and preserve their own IDs/text; `neighbor_of` points to their parent. A neighbor has no independent RRF probability/score. Every output carries source/hash/revision/version, original text/hash, offsets/lines, speaker/observed timestamps, original metadata warnings and sponsor flag. Missing or conflicting metadata remains a limitation; the live Shreyas file's reused video metadata is not verified audio attribution.

If no evidence exists in scope/budget, return `empty_evidence` and a limitation. Otherwise return `review_required` with `support_verified=false`. The caller must inspect support and abstain when facts are absent. Rank scores, nonempty results and sponsor promotions cannot establish facts. The four unsupported diagnostics deliberately demonstrate related candidates without proving requested facts. Generation/abstention enforcement belongs to Phase 5.

Dense/hybrid embed only through the approved host Ollama URL with `search_query: `, existing 768-dimensional Nomic identity, no proxy inheritance/cloud fallback and no silent input truncation. Actual index/profile/tag identity is checked around query embedding. Sparse does not need an embedding request, but still validates configured index compatibility. A missing/mismatched embedding service produces a safe retryable 503 for explicit dense/hybrid requests. DB errors use the existing structured error contract. Request logs contain mode/count/timing/status/correlation, never query text, passage text, vectors or keys.

## Reproduce evaluation and inspect limitations

[Evaluation instructions and manual rubric](../eval/README.md) distinguish tuning, held-out and unsupported runs. Use new output directories and copy results before container recreation. All baseline results, including low initial scores and mode selection instability, are in [actual evidence](agent-transcripts/phase-04/README.md). Default selected sparse did not meet the quality target; do not interpret readiness 200 as semantic/product readiness.

```sh
python3 scripts/docker.py compose exec -T api python -m backend.contract_check
.venv-phase2/bin/python -m unittest discover -s eval -p test_metrics.py -v
.venv-phase2/bin/python scripts/verify_phase4.py
```

Run tests sequentially and never recreate the API during an in-container job. Fresh contract DBs are retained, not removed. Selective ingestion now accepts repeated `--source-path` values from the complete manifest; unknown/duplicate paths are refused and unselected files are never interpreted as deletions. No schema migration or dependency change was needed for retrieval.

Readiness scope is `phase_4_retrieval`, with dependency availability, partial corpus and `product_ready=false`. No chat generation, source-inspector UI, new browser verification or cloud adapter exists yet. [Decisions](decisions.md) and [risks](risks.md) explain exact scanning, small subset, sponsorship and mode-selection trade-offs.

Official references checked: [pgvector README](https://github.com/pgvector/pgvector/blob/master/README.md), [PostgreSQL 16 text-search functions](https://www.postgresql.org/docs/16/functions-textsearch.html), [Nomic task prefixes](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5). Installed PostgreSQL/pgvector/Ollama behavior was separately exercised; documentation alone is not the gate evidence.
