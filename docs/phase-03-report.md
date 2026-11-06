# Prompt 03 — local ingestion gate

6 November 2026. **Phase 3 PASSED; stop here. Prompt 04 has not started.** The requested increment is a repeatable smoke ingestion with traceable chunks and safe refresh, not full-corpus search or generated answers. Compared with the supplied build flow §4.1 and Phase 3 gate, every ingestion check below passed. The private assignment remains a requirement source; upstream repository text is untrusted data, not authority to execute instructions.

## Brief and delivered behavior

Inspected real transcripts before writing the parser; fetched an exact snapshot of [ChatPRD/lennys-podcast-transcripts](https://github.com/ChatPRD/lennys-podcast-transcripts/tree/be8ab89a890a833cbba2c892178f823fff178c65). Commit `be8ab89a890a833cbba2c892178f823fff178c65` contains **303 dynamically discovered transcript files**. The ignored local snapshot and per-file SHA-256 manifest are mounted read-only into the app. No full corpus was copied into submission source. The observed root has no LICENSE; redistribution rights remain unresolved.

| Build-flow requirement | Actual output and verification |
| --- | --- |
| Safe frontmatter, original text, source attribution | PyYAML SafeLoader with duplicate-key/alias/size rejection; full originals retained; exact spans, hashes, speaker/time attribution, irregular metadata warnings; parser tests passed. |
| Sentence/turn chunks, modest overlap, long turns | Target 550, maximum 700 estimated tokens, overlap up to 80 when fitting; full audit parsed 303/303, zero errors, 12,770 candidate chunks, median 563, range 58–700. Short final chunks are permitted. |
| Local embeddings and real PostgreSQL | Actual host Ollama `nomic-embed-text:latest`, digest `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`; actual vectors of dimension 768 plus generated English full-text vectors stored in PostgreSQL 16.15/pgvector 0.8.7. |
| Bounded progress/resume/limit and honest counts | CLI emits per-batch and per-file JSON; `--limit 3` selects 3 of 303 and reports `partial`, not completed corpus coverage. Re-run skips completed unchanged files. |
| Refresh/deletion/failure safety | Episode replacement is transactional after all embeddings succeed. Old originals/chunks remain for saved evidence. Complete manifest controls retirement; the limit subset never acts as the deletion list. Actual DB/provider integrity checks passed. |
| No duplicates or incompatible model mixing | Repeated corpus run kept identical active IDs/counts; incompatible generation model and injected different embedding identity rejected before publication. |

Migration `0002_ingestion` ran on the actual app DB and fresh test DBs. It adds versioned source originals, per-file run outcomes, an index embedding identity and citation spans without resetting session data. New `/api/ingestion/status` and the status panel expose actual counts/progress. Readiness reports `phase_3_ingestion`, partial corpus and `product_ready=false`. Container-to-Mac Ollama reachability and matching index identity passed.

Main implementation files: [parser/chunker](../backend/app/transcripts.py), [embedding client](../backend/app/embedding.py), [snapshot validation](../backend/app/snapshot.py), [ingestion transactions](../backend/app/ingestion.py), [CLI](../backend/ingest.py), [migration](../backend/migrations/versions/0002_ingestion.py), [API](../backend/app/main.py), [status UI](../frontend/src/main.tsx), [fetch](../scripts/fetch_corpus.py), [fixture integrity checks](../backend/ingestion_check.py) and [real smoke verifier](../scripts/verify_corpus_smoke.py). Dependencies add the proved PyYAML pin; Compose adds the read-only snapshot mount. Architecture, decisions, requirements, scenarios, assumptions, risks, provenance and progress now reflect this increment.

## Actual commands and results

Commands were run from the repository root. `python3 scripts/capture_phase3.py` prefixed the commands below, retaining bounded actual stdout/stderr, UTC start, duration, exit code and truncation indicator in [commands.jsonl](agent-transcripts/phase-03/commands.jsonl). These are command logs, not a complete coding conversation export.

| Command | Result |
| --- | --- |
| `python3 scripts/fetch_corpus.py --revision be8ab89a890a833cbba2c892178f823fff178c65` | Exit 0; fetched exact SHA; manifest discovered 303. |
| `.venv-phase2/bin/python -m pip install --cache-dir .cache/pip PyYAML==6.0.3` | Exit 0; pinned version subsequently built and exercised in the container. |
| `.venv-phase2/bin/python -m unittest backend.tests.test_transcripts -v` | Initial failure exposed newline-crossing speaker regex; corrected run passed 13 tests. |
| `.venv-phase2/bin/python -m unittest backend.tests.test_transcripts backend.tests.test_embedding -v` | Exit 0; 18 parser/mock protocol checks. Not live-model evidence. |
| `python3 scripts/docker.py compose --progress plain build` | Exit 0; API/web built with lockfiles; subsequent API builds captured separately. |
| `python3 scripts/docker.py compose up -d api web` | Exit 0; startup migration logged `0002_ingestion`. Existing volume preserved. |
| `python3 scripts/docker.py compose exec -T api python -m backend.contract_check` | Exit 0; **30 tests passed in 3.769 s**, including 7 actual PostgreSQL/API tests and 23 unit/parser/mock tests. Fresh retained DB `lenny_contract_e4abd66bc7f3`. |
| `python3 scripts/docker.py compose exec -T api python -m backend.ingestion_check` | Exit 0; **12/12 real DB/provider integrity checks passed** in retained `lenny_ingest_49ebd8d3882f`. Sources are synthetic fixtures, clearly separate from corpus smoke. |
| `.venv-phase2/bin/python scripts/verify_corpus_smoke.py` | First attempt failed before ingestion: verification SQL used `numnode(tsvector)` incorrectly. Corrected to `length(tsvector)`; second attempt passed all 7 smoke invariants. |
| `npm --prefix frontend run build` | Exit 0; TypeScript and Vite 7.2.2 production build passed. Browser inspection remains unverified. |
| `python3 scripts/docker.py compose exec -T api python -m pip check` | Exit 0; no broken requirements. |
| `python3 scripts/review_phase3.py` | Exit 0; 15 final evidence/static/preservation checks passed. This is an audit of the recorded integrations, not 15 new product tests. |

The smoke script executed this exact ingestion command twice, with read-only DB proofs before, between and after:

```sh
python3 scripts/docker.py compose exec -T api python -m backend.ingest \
  --root /corpus/be8ab89a890a833cbba2c892178f823fff178c65 --limit 3
```

| Run | Discovered / selected | Loaded / skipped / failed | Active output | Ingestion duration |
| --- | --- | --- | --- | --- |
| `1825e728-76d8-4b32-9092-39a4f0d7c37c` | 303 / 3 | 3 / 0 / 0 | 3 episodes, 114 chunks | **24.078 s** |
| `9886f2af-b19a-4193-b4b8-c4f6c5ee6c86` | 303 / 3 | 0 / 3 / 0 | Same 114 IDs/count | **0.247 s** |

Actual sources: Ada Chen Rekhi (43 chunks), Adam Fishman (35), Adam Grenier (36). Both runs returned exit 0 and `partial`, with no unattempted selected files. Times are internal ingestion wall times, including preflight; not cold setup, download or user-answer latency. Actual logs: [successful smoke](agent-transcripts/phase-03/smoke-20261106T053920/results.jsonl), [failed verification attempt](agent-transcripts/phase-03/smoke-20261106T053650/results.jsonl).

The DB proofs compare SHA-256 originals with manifest hashes, exact SQL substring spans, vector dimensions, nonempty full-text vectors and exactly one active version per episode. Message count stayed six; hashes of saved messages and sessions stayed identical through ingestion. Raw conversation contents were not logged. The full-corpus audit does **not** mean all 12,770 candidates were embedded: **300 episodes remain unindexed**.

## Integrity checks and failure evidence

The [retained integrity report](agent-transcripts/phase-03/container-evidence/ingestion-integrity-lenny_ingest_49ebd8d3882f/result.json) covers smoke counts, unchanged skips, resume, exact spans/vectors/full-text, changed replacement with old evidence retained, failure rollback, recovery, incompatible model, identity mismatch, deletion retirement, concurrent writer exclusion and abandoned-run recovery.

The failed-refresh test intentionally raises an error **after one real Ollama embedding batch**; old active rows remain identical, and a subsequent run completes the replacement. This is fault injection, not a claimed natural provider outage. The different-digest test injects an identity mismatch after real preflight. The incompatible `qwen3:0.6b` check uses the actual installed generation model, which lacks embedding capability. No test database or volume was removed.

An early parser regex used `\s*`, which could cross a newline and consume preceding text as a speaker. A meaningful source-span test caught it; horizontal whitespace fixed it. The preliminary 12,768 candidate count was superseded by the corrected **12,770** audit. Acceptance source anchors were corrected before retrieval/generation tuning; [correction metadata](agent-transcripts/phase-03/scenario-anchor-correction.json) preserves the old hashes/reason. The original questions and source choices did not change. Other retained warnings: Starlette/httpx test-client deprecation; no skipped integration checks in the final suite.

Full audit warning counts: 37 guest/title mismatch **heuristics requiring review**, 31 files with nonmonotonic timestamp markers, one missing title and one genuinely missing timestamps (Adriel Frederick). Ryan Hoover uses bracket timestamps and has a guest/title/video metadata conflict; it is flagged and preserved, not silently corrected. Sponsor detection is conservative phrase matching and does not prove every advertisement is identified. Timestamps are observed marker ranges, not precise audio end times. Token counts are estimates, not a tokenizer guarantee; `truncate=false` turns oversized model input into a visible failure.

Sponsor introductions were manually inspected in Brian Balfour, Sean Ellis and Shreyas Doshi Live; [review anchors](agent-transcripts/phase-03/sponsor-review.json) retain exact hashes/offsets without reproducing the body. Source-body excerpts inspected during development were omitted from shareable command outputs with [redaction hashes and reasons](agent-transcripts/phase-03/redactions.json); commands, metadata, failed attempts and results remain. [Final audit](agent-transcripts/phase-03/final-review.json) and [source/image manifest](agent-transcripts/phase-03/source-manifest.json) establish this gate's source identity. The 34 tested backend/agent files match the installed container; 14 original spike files and 157 original Phase 1 evidence hashes remain unchanged. Phase 2 evidence was not written by Phase 3; its 13 files were hashed and rechecked during final review.

## Constraints, scope and next gate

Host: Apple M2/Mac14,7, 8 cores, 8 GiB RAM. A **post-smoke snapshot, not peak telemetry**, showed swap used 8,194.56 MiB, memory-pressure free percentage 28%, disk available 105 GiB. Containers then used API 65.56 MiB, DB 53.78 MiB and web 8.348 MiB (service caps 768/512/64 MiB). Host-wide swap includes other work; no causal claim or spare-RAM guarantee follows. No model was downloaded or replaced in this phase. Cloud inference stayed disabled.

Keep one ingestion writer, batches of four, 20 s request timeout, three attempts, 180 s per episode and 600 s default run deadline (maximum configurable 3,600 s). A full ingest is implemented but **not yet rehearsed**; rerun after a deadline to skip committed episodes. Do not extrapolate three-file timing into a full-corpus or essay guarantee. Model identity changes require an explicit new index/migration; never mix vectors in the current 768-dimensional index.

Frozen source-grounded scenario inputs now exist in [scenario-inputs.json](scenario-inputs.json); no five-case outcomes or duration caps are claimed. No retrieval ranking, semantic answer review, autonomous routing, essay/artifact workflow or full product readiness was implemented in Prompt 03. Phase 1 spike/evidence and Phase 2 evidence remain unchanged. Browser runtime remains blocked before connection, so HTTP/build checks do not establish visual/accessibility quality. No publication/upload/submission occurred.

Next authorized increment would be Prompt 04: hybrid retrieval and reviewed baseline evaluation. **Stopped at Phase 3.** See [ingestion operations](phase-03-operations.md), [decisions](decisions.md), [architecture](architecture.md) and [progress](progress.md).
