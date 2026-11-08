# Selected candidate architecture

React/TypeScript/Vite→Nginx→FastAPI/Python→PostgreSQL16/pgvector. Pi1.5.0/Node runs inside the unprivileged API container;Ollama0.30.11 stays on the Mac. One API worker and one active generation. The selected pre-experiment Phase10 runtime matches41 saved source hashes. Multi-excerpt experiment/error typing remains quarantined,not silently merged.

## Data and transaction boundaries

Alembic0001 foundation,0002 ingestion,0003 conversation,0004 essays and additive0005 assistant-message length run at startup. PostgreSQL owns UUIDs/UTC timestamps and persistence;Pi history/browser state are not the database.

| Tables | Actual role |
| --- | --- |
| users /sessions /messages | Fixed local evaluator metadata,owned topics,client-message retry identities,role/content/status. User input remains8k;accepted assistant essays can be longer under0005. |
| episodes /episode_versions /chunks | Stable source IDs,current active version,immutable originals,exact character/line spans,speaker/observed timestamps,warnings,source hashes/revision,vector768 and generated English full-text vector. |
| ingestion_runs /ingestion_items /knowledge_config | Progress/outcomes/fingerprints and source/model/digest/dimension/document-prefix identity. |
| answer_runs /answer_sources | Owned request/attempt/context/output/lifecycle plus immutable original passage/metadata/quote snapshots linked to assistant message. |
| essay_runs /essay_sources | Saved topic/audience/constraints,outline,sections/raw draft,validation,explicit review,manual edit history and pinned evidence snapshots. |
| artifacts | Owned accepted message,format/title/content/source/provenance metadata;idempotent per message/format. |

Session locking/client UUID uniqueness prevent retry duplicates;changed content with reused identity is409. Answer message+source associations+run completion commit atomically. Cross-session/user resource access is404. Failed transactions roll back. One running operation/session and a process lock bound concurrency;this is not distributed tenancy/authentication. Startup marks interrupted operations failed. No destructive reset/delete API.

## API

| Routes | Contract |
| --- | --- |
| GET /api/health/live,/api/health/ready | Liveness versus dependency/schema/model checks(200/503). Corpus empty/partial/available and product_ready=false are explicit. |
| GET /api/providers,/api/me | Selected provider/model/privacy/no fallback;minimal local user. No secret values. |
| GET /api/ingestion/status,/api/retrieval/scopes | Actual active totals/latest ingest and indexed scope choices. |
| POST /api/retrieval/search | Read-only bounded sparse/dense/hybrid candidates;support_verified=false,not an answer. |
| POST/GET /api/sessions;GET /api/sessions/{sid} | Validated owned sessions;stable bounded pagination. |
| POST/GET .../messages | Saved user notes/ordered messages. POST alone does not infer. |
| POST .../answers;GET .../runs/{rid};POST .../runs/{rid}/cancel | Save request first,NDJSON progress,validated terminal output,explicit bounded retry/cancel. |
| GET .../messages/{mid}/sources/{label} | Owned immutable source/quote snapshot and safe pinned source/video links. |
| POST/GET .../essays;GET .../essays/{rid} | Dedicated evidence-first workflow,persisted raw draft/validation;not autoaccepted. |
| GET .../essays/{rid}/sources;POST .../review,.../advice,.../evidence,.../cancel | Explicit review/edit/cancel;source edits must select exact existing evidence spans. |
| POST/GET .../artifacts;GET .../artifacts/{aid},.../sources/{label} | Server formatting/reopen/owned source inspection;no additional inference. |

OpenAPI /docs and /openapi.json define fields. Unknown fields,IDs,lengths/scopes/budgets are validated. Non-health errors carry code/message/request_id/retryable plus X-Request-ID;no DSNs/keys/raw exception bodies. Saved error UI detail is limited. Baseline bridge can collapse retrieval failure into generic RPC rejection;experimental typed diagnostics are not part of this candidate.

## Ingestion and retrieval

Pinned303-source manifest at be8ab89a890a833cbba2c892178f823fff178c65;normal index303/12770. Parse/normalize/chunk exact source originals,embed document-prefixed text with Nomic768,verify identity,and publish each episode transactionally. Writer advisory lock,batch4,finite deadlines/retries,fingerprints skip unchanged data;old versions/evidence retained. Repeat creates no duplicates. No mixed embedding identities or invented timestamps.

PostgreSQL English sparse ranking and cosine dense candidates use immutable active versions in a consistent read-only snapshot. Explicit materialized term tsqueries/corpus-count/document frequencies bound repeated sparse work. Hybrid reciprocal-rank fusion,dedup/overlap/episode caps,token budgets and1-hop neighbors select passages;ranking scores are not probabilities. Frozen v3:20 candidates,limit8,3200token budget,6/episode,RRF60,max2 neighbors. Chat explicitly hybrid(max1 neighbor);standalone search defaults sparse. Sources include canonical Unicode/underscore paths and fixed pinned GitHub links.

## Pi,models and trust

Fresh Pi process/private home/session per request;cloud credentials/proxies/extension auto-discovery/retries/compaction stripped or disabled. Only registered search_transcripts(query=current) is active;the capability-bound loopback bridge uses the saved question and bounded prior-user context. One retrieval/two provider turns,4096 context/128 output,12800-byte prompt cap,6000 evidence-text bytes. A strict first-turn textual-call adapter is sometimes required;native/autonomous routing is unproved.

The local model selects ONE exact supplied excerpt ID or NONE. The server validates IDs/spans and renders original text with citations;the narrow private-fact guard is not general entailment. Follow-up context uses only the same session’s prior user subject/scope,not assistant prose as facts. Output can be correct quotations yet incomplete/irrelevant. General abstention/completeness fails Phase10.

Essay collection uses fresh topic evidence;server fact plan selects verbatim blocks/citation mappings. Pi1.7B drafts advice with no history/factual constraints,4000-byte prompt/384 output,one call/fresh stage,90s/stage,600s overall,one length repair. Deterministic1125–1375 words/six sections/bullets/bold/IDs checks do not prove support/readability. Explicit manual review is required. Existing1208-word result is reviewed/edited;raw1216-word drafts fail.

Provider configuration is server-only/default Ollama,no silent fallback. OpenRouter uses Pi’s approved OpenAI-compatible endpoint/google-gemini-2.5-flash-lite with no fallback routing;the successful cited smoke removed only incompatible follow-up JSON mode. Native Anthropic has config/mock coverage,not a live claim. Embeddings stay local. Switching needs explicit config/recreation;UI only discloses selected model/privacy.

## Security,diagnostics and topology

NDJSON framing/total output/tool turns/deadlines are bounded. Abort then terminate/reap owned process group;shielded final cleanup closes bridge,saves terminal state,releases lock. Killing Pi does not prove instantaneous Ollama GPU cancellation. Lifecycle failure tests use real mock subprocesses in isolated PostgreSQL;live successful cleanup is separate.

Source text is untrusted data,never tool permission. Markdown disables raw HTML;nh3 allowlist,CSP and opaque script-disabled iframe block active content/network/forms/navigation. Static supported subset,not universal browser certification. Default logs contain request/session/run correlation/codes/durations/IDs;raw RPC opt-in is sensitive/private. No arbitrary shell/filesystem/web app-agent tools.

Normal Compose lenny-phase2:loopback8080/8000/55432,pgdata+chat_traces;host5432 untouched. Evaluator uses a unique project/ports/fresh volumes with the same host Ollama and read-only pinned source cache. Source/database snapshots and experimental code never replace normal data. [README](../README.md),[Phase11 exact revision/results](phase-11-report.md).
