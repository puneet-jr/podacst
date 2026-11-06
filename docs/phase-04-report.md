# Prompt 04 — retrieval and reviewed baseline

6 November 2026. **Phase 4 implementation/baseline gate PASSED; proposed retrieval quality target NOT met. Stop before Prompt 05.** The supplied build flow §4.2–4.3 requires real search/source integrity and measured reviewed evaluation at this gate; it does not permit treating an evaluation process exit as a quality score. Product readiness remains false.

## Brief and delivered output

Implemented native pgvector cosine search, PostgreSQL English full-text search, deterministic reciprocal rank fusion (RRF), duplicate/substantial-overlap handling, episode caps and bounded neighboring passages. Added typed read-only `POST /api/retrieval/search` with explicit guest/episode/path filters, exact source UUIDs/hashes/spans/attribution, finite budgets and safe diagnostic events. Model identity and local-only query embeddings use the existing Nomic profile; sparse mode needs no inference. No reranker or generated answer was added.

The baseline deliberately uses **9 of 303 episodes, 373 active passages**. The three Phase 3 smoke sources remain; six additional files cover the predefined scenarios and named frameworks. This is a development subset, not random or full-corpus evaluation. Full ingestion remains Phase 10; **294 episodes are unindexed**. Source commit remains `be8ab89a890a833cbba2c892178f823fff178c65`, with the complete validated manifest controlling retirement even during selective ingestion.

Before tuning, froze **24 answerable questions** (16 tuning/eight held out), **32 original support spans** and **four separate unsupported requests** in [retrieval-cases.json](../eval/retrieval-cases.json). Questions include exact frameworks, paraphrases, cross-episode synthesis, follow-ups and sponsor traps. Labels came from direct source reading by Codex, not independent expert/participant review or an automated answer judge. [Freeze metadata](agent-transcripts/phase-04/judgment-freeze.json) records SHA-256 `02663c353fb868dad771d8eaf2d27d713f230faf0d462bb56c6786819659b0e6`; it stayed unchanged through evaluation. Follow-up queries use fixed reviewer rewrites, not an implemented conversational resolver.

## Actual measured output

Final candidate: `rrf-v3-idf-budgeted-neighbors`; 20 candidates per retriever, up to eight output passages, **3,200 estimated source-text tokens**, episode cap six (explicit single-episode scopes can use their limit), up to two radius-one neighbors, RRF constant 60. All modes use identical packet limits. Five–six passages usually fit; the service does not pad to eight or exceed the budget. This is a retrieval budget, not proof the complete future prompt fits qwen3's tokenizer/context.

| Mode | Tuning Recall@8 (n=16) | Held-out Recall@8 (n=8) | Held-out MRR@8 | Held-out nDCG@8 | Held-out median / p95 ms |
| --- | --- | --- | --- | --- | --- |
| **Sparse — selected default** | **68.75%** | **62.50%** | 0.5625 | 0.5789 | 69.55 / 263.96 |
| Dense | 62.50% | 87.50% | 0.7125 | 0.7422 | 83.33 / 103.14 |
| Hybrid | 65.63% | 93.75% | 0.6917 | 0.7202 | 105.80 / 352.50 |

Sparse was selected from tuning results because it had the best recall/ranking scores and lower median latency (41.71 ms vs dense 79.50/hybrid 116.06). Its [selection/source/config freeze](../eval/retrieval-selection.json) preceded held-out execution. The held-out result exposes **selection instability and weak unscoped sparse recall**: scoped held-out recall was 100% (n=4), unscoped 25% (n=4). The default was not secretly reselected after seeing the holdout. Dense/hybrid remain explicit options, without automatic fallback.

Across all 24 cases, descriptive macro Recall@8 was sparse **66.67%**, dense **70.83%**, hybrid **75.00%**. These combine tuning and test data, so are not independent test estimates. Hybrid's eight-case held-out score exceeds 85% numerically, but neither the chosen default nor all-case performance meets the proposed quality target. No broad achievement claim follows from that tiny selected subset. New independently reviewed cases/full-corpus distractors are needed before revising the mode policy or making product-quality claims.

Metrics count exact frozen passage IDs resolved from source spans, not expected guests. Overlapping containing chunks can be alternative relevant IDs; anchor coverage is reported separately. Unjudged valid passages receive no metric credit, so a strict miss is not automatically an incorrect answer. Supplemental review found partial alternative evidence in H22/H23 but retained the original labels/scores. Definitions, hand-calculated metric tests, manual rubric, scope breakdowns and limitations are in [eval/README.md](../eval/README.md); complete measured results are [metrics-summary.json](agent-transcripts/phase-04/metrics-summary.json).

Every returned passage in all recorded evaluations passed real PostgreSQL exact-original/span/hash/current-version verification. Latencies include retrieval-service embedding/SQL/selection, exclude evaluation-only verification, HTTP transport and generation. Explicit model warmup was recorded separately (held-out 447.61 ms); mode order rotated per question. With n=8, nearest-rank p95 is the maximum, not a reliable tail estimate. No cloud inference occurred.

## Genuine development failures, corrections and residuals

The first measured v1 baseline had sparse/dense/hybrid recall 53.13/56.25/59.38% on the 16 tuning cases. Inspection found repeated speaker names distorting full-text ranking, exclusion of mixed sponsor/substantive chunks, a restrictive three-passage episode cap, and neighbor expansion starved by already-consumed tokens. Corrected fresh frequency weighting for lexical term coverage, retained visible sponsor flags with optional exclusion, increased the cap, reduced the local budget from 4,800 to 3,200 and reserved both slots and tokens for neighbors. Original v1/v2 and final v3 attempts remain separate; no failures or low scores were overwritten. Multiple changes occurred together, so the observed gain is not a causal ablation of each fix.

RRF uses rank positions, not calibrated relevance probabilities. Lexical weighting is fresh document-frequency-weighted term coverage followed by `ts_rank_cd` tie ordering; it is not claimed to be BM25. Dense search is exact pgvector scanning at this scale; no approximate index/reranker or full-corpus latency claim. Major remaining misses include cross-episode evidence completeness and unfiltered specific passages. Neighbor context can displace useful ranked hits under a small budget. These remain documented quality defects, not hidden behind passing integration checks.

Sponsor flags are heuristics, and a flagged chunk may contain both useful discussion and an advertisement. Default retrieval retains it with an explicit warning; `include_sponsors=false` filters flagged chunks when requested. This fixes silent loss of useful discussion but can return advertisements. Promotions cannot establish factual effectiveness or guarantees. H19's live transcript has suspicious reused title/video metadata; evaluations rely on exact path/hash/body, not an invented correction or verified video attribution.

## Unsupported requests and semantic limits

All **12 diagnostic searches** (four requests × three modes) returned nonempty bounded candidates with `review_required` and `support_verified=false`. This is not an abstention success rate. The requests concerned private startup churn, future API releases, a fabricated framework and a sponsor-based PMF guarantee. [Direct review notes](agent-transcripts/phase-04/support-review.json) inspect top-three sparse excerpts and explain absent support; they are sampled excerpt reviews, not complete packet/all-mode certification. Historical predictions, generic advice and sponsors do not supply the requested facts.

Empty scopes return `empty_evidence` with an evidence limitation, without silently broadening filters. For related but insufficient material the contract requires claim-by-claim review and a bounded limitation; no arbitrary similarity threshold declares support. The Phase 5 agent must implement and test that judgment/abstention. No generated answers, semantic claim-support rate, autonomous routing, essays or five-scenario outcomes are claimed here.

## Exact commands and verification

Known-safe commands were prefixed with `python3 scripts/capture_phase4.py`; [commands.jsonl](agent-transcripts/phase-04/commands.jsonl) preserves actual UTC times, separate bounded stdout/stderr, exit codes, durations and truncation indicators. Repeated builds/tests are retained, not reconstructed. No dependencies or new model weights were installed; existing pins remain proved by the current container suite.

```sh
python3 scripts/docker.py compose --progress plain build api
python3 scripts/docker.py compose up -d api
python3 scripts/docker.py compose exec -T api python -m backend.ingest \
  --root /corpus/be8ab89a890a833cbba2c892178f823fff178c65 \
  --source-path episodes/april-dunford/transcript.md \
  --source-path episodes/brian-balfour/transcript.md \
  --source-path episodes/julie-zhuo/transcript.md \
  --source-path episodes/sean-ellis/transcript.md \
  --source-path episodes/shreyas-doshi/transcript.md \
  --source-path episodes/shreyas-doshi-live/transcript.md --deadline-seconds 600
```

Actual ingestion run `56810b6a-3a8e-46c0-a24f-30c877be6c7f`: 303 discovered, six selected/loaded, zero failed/deleted, 259 new chunks, nine total episodes/373 chunks, `partial`, **43.533 s**, exit 0. Existing three episodes were not retired. Complete original spans and 768-dimensional vectors passed final DB proof.

| Actual command | Result |
| --- | --- |
| `.venv-phase2/bin/python -m unittest backend.tests.test_retrieval backend.tests.test_embedding -v` | 15 focused unit/mock checks passed before live evaluation. |
| `python3 scripts/docker.py compose exec -T api python -m backend.contract_check` | Final **49 tests passed in 6.292 s**: 33 unit/parser/mock and 16 real PostgreSQL/API checks; retrieval fixtures use real local Ollama, and outage injection is explicitly mocked. Fresh DB `lenny_contract_38c907210618` retained. |
| `.venv-phase2/bin/python -m unittest discover -s eval -p test_metrics.py -v` | Three separate hand-calculated metric checks passed on host; no model calls. |
| `python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval --split tuning --output /app/evidence/tuning-v1` | Historical v1 runner default used baseline-v1; 48 actual searches, low scores retained. |
| `python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval --split tuning --config eval/retrieval-local-v2.json --output /app/evidence/tuning-v2-local` | 48 actual searches; intermediate budget/lexical policy recorded. |
| `python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval --split tuning --config eval/retrieval-local-v3.json --output /app/evidence/tuning-v3-local` | Final 48 actual searches; all source integrity checks passed; selection made before holdout. |
| `python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval --split held_out --config eval/retrieval-local-v3.json --output /app/evidence/held-out-v3-first` | First held-out attempt: 24 actual searches, unchanged frozen candidate/judgments, source checks passed. |
| `python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval --split unsupported --config eval/retrieval-local-v3.json --output /app/evidence/unsupported-v3-first` | 12 actual diagnostic searches; no generated answers or positive fact-support claim. |
| `.venv-phase2/bin/python scripts/verify_phase4.py` | Nine actual live HTTP/proxy/DB checks passed: default sparse, explicit local hybrid, bounded empty scope, parameterized filter, invalid path rejection, partial counts and unchanged saved session/message hashes. |

The suite also checks stable fusion/ties, duplicate votes, overlap/source integrity, exact filters, token/episode bounds, neighbor lineage/version, retirement exclusion, current query prefix, finite identity deadline, safe errors/logs and explicit mode behavior under mocked embedding outage. Sparse is an intentional default, not a hidden response to a failed hybrid call. Starlette/httpx test-client deprecation remains disclosed. Browser inspection was not attempted/claimed; no frontend code changed.

## Machine, preservation and gate comparison

Actual host remains Apple M2/Mac14,7, eight cores/8 GiB; Ollama 0.30.11 on the Mac. Local embedding model `nomic-embed-text:latest`, digest `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`, 768 dimensions, `search_query: ` vs ingestion `search_document: `. Container-to-host model calls passed. Post-evaluation snapshot, not peak telemetry: swap used 8,520.81 MiB, memory-pressure free percentage 29%, disk available 105 GiB; API/DB/web 77.83/87.31/8.387 MiB. Host-wide swap includes other applications; no causal memory/headroom or essay-fit claim.

Build-flow checks: dense+sparse+RRF implemented; duplicate/overlap/diversity/neighbor bounds and explicit filters tested; traceable exact sources and bounded weak/empty contract present; ≥20 reviewed answerable questions plus separate unsupported cases frozen; tuning/holdout separated; real metrics/counts/latency and manual rubric recorded. **This satisfies the Phase 4 implementation/baseline gate while leaving quality defects open.** No unmeasured quality target is marked achieved.

Phase 1 spike and Phase 1–3 evidence remain unchanged. Original migrations/data/volumes and existing host PostgreSQL 5432 are preserved; isolated Compose DB remains 55432. Six saved messages and all saved session hashes match the Phase 3 proof. No raw corpus/PDF, credentials, publication, upload or submission were added. Final source/image identities and evidence checks are linked from [Phase 4 evidence](agent-transcripts/phase-04/README.md).

Next work would be Prompt 05, only when authorized. Before treating retrieval as production quality, address unscoped/multi-source misses, mode-selection instability, incomplete judgments and full-corpus distractors with a fresh independent evaluation; do not reuse this observed holdout as unseen data. See [operations](phase-04-operations.md), [architecture](architecture.md), [decisions](decisions.md), [risks](risks.md) and [progress](progress.md).
