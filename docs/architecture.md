# Architecture: Phase 5 local extractive conversation

The implemented stack is a local React/TypeScript/Vite UI served by Nginx, a FastAPI/Python API with a Pi subprocess boundary, and PostgreSQL 16/pgvector in a dedicated Compose project. Host Ollama stays outside Docker on the Mac. No independent agent microservice is needed; Node/Pi runs inside the API container. Phase 1's spike/evidence remain separate and preserved.

## Data and transactions

Alembic revisions 0001_foundation, 0002_ingestion and additive 0003_conversation use explicit DDL and run before API startup; earlier migrations remain immutable. PostgreSQL is authoritative; browser state and ephemeral Pi histories are not persistence. All entity IDs use UUIDs and timestamps use timestamptz/UTC.

| Entity | Actual schema boundary |
| --- | --- |
| users | Local fixed evaluator ID, display name, JSON metadata and creation time. No production authentication/SSO. |
| sessions | User FK (restrict deletion), title, creation/update times; index by user/update/ID. |
| messages | Session FK (cascade), client retry UUID, role/content/status, creation time; unique session/client-ID and ordered session/time index. |
| episodes | Stable UUID5/source path, current hash/title/guest/date/video, current version and retirement time. |
| episode_versions | Immutable full original, source path/hash/revision, metadata/warnings/fingerprint and parser/chunker version; composite episode/version identity. |
| chunks | Episode/version/run FKs, stable ordinal/version IDs, exact and normalized text, character/line spans, source hash/revision, speaker/observed time ranges, sponsor flag, vector(768), model/digest and generated English full-text vector. Partial uniqueness protects active episode/ordinal. |
| ingestion_runs / ingestion_items | Corpus revision/source/kind, discovered/selected/loaded/skipped/failed/deleted counts, per-file status/warnings/errors, heartbeat and finite run outcomes. |
| knowledge_config | Singleton source/model/digest/dimension/document-prefix identity; incompatible profiles refused. |
| answer_sources | Message/chunk FKs, server label, exact original passage, immutable metadata/quote-span snapshots and unique association. |
| answer_runs | Session/user/assistant identity, hybrid query/scope, bounded prior-user context IDs, running/completed/failed/cancelled state, finite attempts, outcome/metadata/error and UTC lifecycle times. One running run per session. |
| artifacts | Session/message FKs, constrained Markdown/HTML type, title/content/source metadata and timestamps. No artifact generation/renderer exists yet; future APIs must enforce session ownership. |

Session/message writes use transaction blocks. Saving a message first locks the owned session row, checks the client UUID, inserts the message and updates the session in one transaction. Same-ID/same-content retries return the saved message; changed content with a reused ID returns 409. Failed transactions roll back. Read/list/write queries scope sessions to the fixed local user. A second user's rows were excluded in real tests, without claiming multi-tenant authentication. No delete/reset API or destructive downgrade is provided.

## HTTP contracts

| Route | Behavior |
| --- | --- |
| GET /api/health/live | Process-only liveness. |
| GET /api/health/ready | Typed dependency/schema report, 200/503; foundation and product readiness distinguished. |
| POST /api/retrieval/search | Typed, read-only bounded candidate passages; sparse/dense/hybrid, exact scopes, no generated answer. |
| GET /api/ingestion/status | Active totals, latest run/outcomes, pending count and recent safe errors. |
| GET /api/providers | Selected local provider/model, capability/implementation flags, explicit fallback off. Cloud is disabled and unimplemented. |
| GET /api/me | Local evaluator ID/metadata/UTC creation time. |
| POST /api/sessions | Validated title; returns persisted session, 201. |
| GET /api/sessions | Scoped list with bounded limit/offset and stable ordering. |
| GET /api/sessions/{id} | Owned session or 404; malformed UUID is 422. |
| GET /api/sessions/{id}/messages | Owned ordered/paginated persisted context, run outcome and validated citation references. |
| POST /api/sessions/{id}/answers | Save user first, stream typed NDJSON progress and validated terminal content; hybrid only. |
| GET /api/sessions/{sid}/runs/{rid} | Owned persisted operation/attempt/outcome. |
| POST /api/sessions/{sid}/runs/{rid}/cancel | Request cancellation and bounded cleanup. |
| GET /api/sessions/{sid}/messages/{mid}/sources/{label} | Owned immutable stored source/quote snapshot; unknown/cross-session404. |
| POST /api/sessions/{id}/messages | Saves user text and retry UUID. It does not generate an answer. |

OpenAPI at /docs and /openapi.json defines typed inputs/outputs, including health/provider contracts. Non-health failures use error {code,message,request_id,retryable}, matching X-Request-ID. Request bodies/unknown fields, UUIDs, lengths and pagination are validated. No credentials/DSNs/raw exception text are returned. Readiness's structured dependency report intentionally differs from the error envelope.

## Runtime, readiness and networking

Compose project lenny-phase2 owns its network and pgdata volume. DB is loopback 55432 externally and db:5432 internally; the existing host 5432 database remains untouched. Web/API are loopback 8080/8000. Base images are digest-pinned, JS dependencies locked and Python dependencies pinned including the tested Linux greenlet dependency. Runtime API uses an unprivileged evaluator user; local DB administrator credentials are generated into ignored .env, server-side only.

The app container was proved to reach host.docker.internal:11434, discover actual models and run the controlled fixture through Pi to host Ollama. Foundation readiness checks DB migration/pgvector, installed Pi 1.5.0 and actual Ollama/model/embedding-dimension metadata. Phase 3 reports empty/partial/available corpus independently of dependency readiness, validates the pinned embedding identity and keeps product_ready=false; a model availability check or indexed chunk count cannot establish answer quality. DB outage keeps liveness up, readiness/writes fail safely, and pooled/pre-ping connections recover when DB returns without an API restart. Graceful app/test teardown disposes connection pools.

## Pi boundary and trust

A fresh Pi1.5.0 subprocess/config/history per answer selects only the approved local Ollama endpoint and one reviewed conversation extension. Default shell/filesystem/web tools, external extension discovery, MCP, skills/context files, cloud credentials/proxies, automatic retry/compaction and telemetry/catalog refresh are disabled. The original Phase1 fixture spike is preserved separately.

Pi registers and actually executes `search_transcripts({query:"current"})`. The query/scope are pinned server-side to the saved question and only the relevant prior user subject/scope from that same PostgreSQL session. Prior assistant messages are never factual evidence. A random per-operation capability authorizes one loopback bridge call into real hybrid retrieval. Pi's tool-result continuation asks the model to select one server-assigned exact excerpt ID or NONE. This is meaningful framework tool execution, not an import-only integration.

Observed qwen serialization sometimes needs a strict first-turn textual-function-request normalizer through Pi's documented message_end replacement hook. It accepts only the exact approved tool/argument shape, never a source, tool result or final answer. Raw request serialization is retained privately. One final follow-up used a native call, while other final requests needed normalization; reliable native/autonomous routing is not established. The server validates selected ID/spans and renders exact quotes rather than model-written factual prose. A narrow private-fact guard corrected the measured unsupported request. General relevance, completeness and unsupported recognition remain quality risks.

One API worker permits one active model request. Deadline75s/default,90s/max; one tool, two provider turns, model4096 context/128 output tokens, prompt-message12800-byte cap, at most16 exact excerpt groups/6000 text bytes. Hybrid retrieval has its own15s deadline and eight-passage/3200-estimated-token budget. Groups cannot combine different speaker turns. These byte/estimated-token bounds supplement the model context setting; actual token usage is measured separately.

JSONL correlates response IDs/commands, bounds frames/total bytes/events/output and handles malformed/error/EOF paths. Abort is cooperative, followed by owned-process termination/reaping. Cancellation/disconnect uses shielded final cleanup, closes the bridge, persists the terminal state and releases the generation lock. A read-only DB search thread may finish within its own deadline after cancellation; no arbitrary write worker exists. No claim is made that killing Pi immediately stops all GPU activity inside Ollama.

Answer completion inserts assistant message and immutable source associations and advances the run in one transaction. Failed/cancelled operations retain the user question. Same-ID completed retries replay; explicit failed retry reuses the user/run identity with bounded attempt history. App startup marks abandoned running operations failed. This assumes one app worker; distributed lease/job ownership is not implemented.

Private raw protocol stdout and stderr are separate under chat_traces, parent0700/UID10001, and survive container recreation. Earlier traces remain ignored/private. Safe metadata/source IDs/hashes support review; HTTP/access logs omit message content and credentials. Fixed local-user scoping is not production SSO or OS egress confinement. Full trace retention is deferred. See phase-05-operations.md and decisions D-14–16.

## Local ingestion and refresh

A host fetch script downloads an exact Git commit into ignored cache and builds a complete per-file SHA-256 manifest. API runtime mounts only that corpus cache read-only. Source files are untrusted evidence; upstream CLAUDE.md is not an application instruction. No arbitrary fetch/tool route is exposed. Snapshot loading verifies source identity, discovered paths/hashes and containment before writes.

The restricted YAML parser preserves the original UTF-8 while deriving separate search text, speakers and observed timestamps. Timestamp-only continuation inherits the preceding speaker; missing timestamps remain null. Sentence/turn atoms form roughly 550 estimated-token chunks (700 maximum, up to 80 overlap); oversized turns split. Original evidence is a contiguous source slice with exact offsets, never reconstructed normalized text. Sponsor/mismatched-metadata warnings annotate rather than silently remove or repair source material.

The single-writer CLI obtains a PostgreSQL advisory lock. It preflights actual host Ollama embedding capability/digest/dimensions and a real vector, then checks the persisted index identity. `search_document: ` prefixes local batches of four, `truncate=false`, context 2048. Calls are bounded to 20 seconds/three attempts, episodes to 180 seconds, runs to 600 by default (maximum 3600). Progress/outcomes contain safe metadata, not text/vectors. Future query embedding must use `search_query: ` with the same model/digest.

An unchanged source/pipeline/profile fingerprint skips publication. Changed episodes prepare every vector first; one transaction inserts a new immutable source version/all chunks, retires old active chunks, advances current_version and updates the run outcome. Failures retain the prior active version. Old evidence remains addressable by version/chunk ID for saved associations. Deletions compare the entire validated manifest, not the limit selection, and retire rather than erase. Only active chunks enter retrieval. An interrupted process releases its connection/lock; the next writer marks abandoned runs interrupted and skips committed episodes. Resume restarts failed episodes; no partial per-episode vector checkpoint is published.

Actual result: pinned 303-file parser audit; 3 episodes/114 chunks embedded with local nomic-embed-text:latest into PostgreSQL, unchanged repeat with no duplicate IDs, real fixture refresh/failure/deletion/identity/concurrency checks passed. At the Phase 3 gate, other 300 episodes remained unindexed; Phase 4 expanded this to nine episodes/373 chunks, leaving 294 unindexed; full ingest is implemented but unverified at scale. This is episode atomicity, not a whole-corpus atomic rollout. A different model/digest/prefix requires an explicit new index/migration; equal dimensions alone do not establish compatible vector meaning. See [operations](phase-03-operations.md), [report](phase-03-report.md), decisions D-10/11.

## Retrieval and evaluated evidence contract

`backend/app/retrieval.py` performs exact native pgvector cosine search plus PostgreSQL English full-text search, 20 candidates each by default. Lexical OR terms are safely normalized/quoted, weighted by current document frequency then cover-density tie rank. Both searches and radius-one neighbors share one read-only repeatable-read snapshot joined to active current versions. Sparse mode does not call a model; dense/hybrid use only the approved Mac Ollama endpoint and `search_query: ` with the pinned 768-dimensional profile. Identity mismatch fails, never falls back.

RRF counts each ID once per list, stable tie ordering; selection deduplicates normalized copies/heavy same-source overlap, caps episode concentration, and reserves slots/tokens for up to two neighbors. Exact originals are not trimmed/reconstructed. Default maximum eight passages/3200 estimated source tokens, episode cap six (explicit single-episode scope can use its limit), finite query/DB/provider deadlines. No minimum count overrides the budget. Request parameters make candidates/context/mode tunable. Default retains and flags mixed sponsorship; callers can explicitly exclude flagged chunks, accepting lost substantive context.

The typed POST route returns original passage IDs/text/hash/offsets/attribution/warnings and `support_verified=false`. Empty evidence has a bounded limitation; nonempty evidence is `review_required`. Rank scores are not probabilities. Phase5 uses this contract for bounded model-selected exact excerpts and owned source inspection. ID validity remains distinct from relevance/semantic support; measured model failures are retained.

Sparse was frozen as the default on 16 tuning cases (best recall/ranking and lower latency), before eight held-out cases. Holdout exposed selection instability: sparse 62.5%, dense 87.5%, hybrid 93.75% recall; all-24 descriptive results 66.67/70.83/75%. No overall quality target achieved; no post-holdout reselection or reranker. Twenty-four exact reviewed source judgments/four unsupported diagnostics and actual metrics/source checks are separate from synthetic-fixture tests. Current nine-episode corpus is partial, labels incomplete and not independently expert-reviewed; full-corpus and unscoped/synthesis quality remain open. See [Phase 4 report](phase-04-report.md), [retrieval operations](phase-04-operations.md), [evaluation rubric](../eval/README.md) and D-12/13.

## Deferred work and evidence

Full-corpus quality, broader conversational reasoning/abstention, writing/artifact routes, browser acceptance/isolation, cloud adapter, comprehensive operational matrix and clean evaluator handoff remain later phases. See [Phase 4 report](phase-04-report.md), [foundation operations](phase-02-operations.md), [design](design.md) and [test plan](test-plan.md). Browser inspection was blocked before connection; typecheck/build/HTTP do not establish visual/accessibility correctness.


## Phase6 work-in-progress boundary

Additive0004_essays stores essay_runs and immutable essay_sources separately from artifact generation. A dedicated POST /sessions/{sid}/essays route preserves explicit topic/audience/constraints and bounded owned prior-user context. Pi executes a real hybrid retrieval/outline tool; fresh later Pi writing turns have no active tools and receive pinned evidence snapshots. The trusted adapter's require_tool default remains strict for retrieval; explicit snapshot writing forbids unexpected tool execution. Default shell/filesystem/web tools and cloud fallback remain disabled.

Six sections, one content repair maximum,4096 context,1100 outline/850 section output tokens, per-stage90s and whole600s default/900s maximum. Failed/unreviewed drafts remain saved. Deterministic format/count/source-ID checks cannot certify support; only an explicit manual review after passing them can atomically create one assistant reply and source associations. Source inspection is owned; rejected outlines/outputs are not successful essays. The corrected local run failed on OllamaHTTP400 grammar initialization before section1; no essay or Phase7 artifact is claimed. See phase-06-report.md and operations. Shared current runtime files include changes across multiple phases and are grouped honestly in the final Git snapshot commit.

## Phase8 interaction additions

Owned essay summaries and active interview-scope reads support reopening/research without changing authoritative PostgreSQL storage or model/tool boundaries. Frontend review edits submit exact source offsets and advice separately; explicit review acceptance creates the durable answer and artifacts render deterministically. Source-offset conversion handles Unicode codepoints. Late responses cannot cross sessions; page-local unsent draft state and dirty-review protection preserve work during navigation. Essay retrieval buffers8 candidates/5600 estimated source tokens to supply six reviewed sections; advice generation retains4096 context/384 output. Full model-quality/runtime limits remain in [Phase8 report](phase-08-report.md).
