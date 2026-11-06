# Phase 5 conversation operations

Run `python3 scripts/bootstrap.py` with Docker and host Ollama available. Existing models are sufficient; no Phase 5 model download. API8000, web8080, isolated PostgreSQL55432; host5432 is unrelated. Migration `0003_conversation` runs on startup. Preserve `pgdata` and `chat_traces`; never use `down -v` or reset a database.

One API worker allows one active local generation. `POST /api/sessions/{sid}/answers` accepts `{content, client_message_id, retrieval_mode:"hybrid", source_path?, retry?, timeout_seconds?}`. Content is at most1000 characters, mode fixed hybrid, optional scope an exact safe corpus path. The UI searches all indexed episodes; the focused live checks explicitly scope Sean Ellis through the API and inherit that scope on follow-up. Naming a guest in UI text is a relevance hint, not an exact API filter.

Newline-delimited JSON events: `started`, `retrieving`, `evidence_ready`, `generating`, then `completed`, `failed` or `cancelled`. Validated content arrives with completion; raw model tokens are not displayed. HTTP200 starts a stream; inspect the terminal event/run for the actual outcome. Nginx buffering is disabled and its100s read timeout exceeds the app deadline.

`GET /api/sessions/{sid}/runs/{rid}` reads saved outcome; `POST /api/sessions/{sid}/runs/{rid}/cancel` requests cleanup. Disconnect also cancels. The user question remains saved; failed/cancelled attempts create no assistant reply. Retry the same UUID/content/scope with `retry:true`, maximum three attempts. Completed retries replay the saved answer without inference. Changed content/scope with an old UUID is409. PostgreSQL permits one running operation per session. Startup marks abandoned operations failed; graceful shutdown cleans owned tasks. This deployment assumes one worker, not distributed job ownership.

Reopen through the messages route. For an assistant's server label, use `GET /api/sessions/{sid}/messages/{mid}/sources/S1`. Labels belong to that answer. Exact passage, selected quote spans, speaker/guest/title, version/hash, observed markers and approved source/video links are returned. Unknown/cross-session references are404. Retired-source snapshots remain readable; a failed association write rolls back the assistant transaction.

Limits: deadline75s default/90s maximum; one retrieval; two provider requests; model context4096, output128 tokens, thinking off;12800 serialized prompt bytes. Search uses at most eight passages/3200 estimated source tokens, episode cap6, at most one neighbor and15s deadline. The model sees at most16 exact excerpt groups/6000 text bytes. Groups cannot cross a speaker header. Byte/estimated-token bounds are not a universal tokenizer guarantee; actual usage is recorded. Pi JSONL frames are bounded to1MiB/8MiB total with finite command/cleanup timeouts. Automatic retries, compaction and cloud fallback are disabled.

Pi exposes only `search_transcripts({query:"current"})`. Query/scope are pinned to saved input, not model-controlled SQL/URLs/paths. A random per-operation capability permits one loopback read-only call. A strict documented Pi hook adapts the observed exact textual function request only on the first assistant turn; source/tool-result/final-answer text cannot authorize it. Pi then executes its registered tool and continues the model. The final selection must be a supplied ID or NONE. Unknown IDs/instruction-like selections fail closed. A narrow private-fact policy returns an evidence gap for unavailable internal metrics. These controls do not establish general semantic adequacy or reliable native/autonomous routing.

Raw RPC stdout and diagnostics contain prompts/evidence. They are separate files under `/app/evidence/private-chat/<run>/<attempt>/` on `chat_traces`, parent0700/UID10001. Do not publish that volume. Earlier development traces live in ignored `.cache/phase5-private`, parent0700. Retention is deferred; trace storage grows. Safe metadata/hashes are shareable evidence; default HTTP/access logs omit request content and credentials. This is fixed local-user scoping, not production authentication or OS egress confinement.

Verification commands (capture safe commands with `python3 scripts/capture_phase5.py`):

```sh
python3 scripts/docker.py compose exec -T api python -m backend.contract_check
python3 scripts/docker.py compose exec -T api node --test agent/test_conversation_policy.ts
.venv-phase2/bin/python scripts/live_phase5.py --base-url http://127.0.0.1:8080
.venv-phase2/bin/python scripts/lifecycle_phase5.py
python3 scripts/docker.py compose restart api
.venv-phase2/bin/python scripts/reopen_phase5.py
python3 scripts/docker.py compose exec -T api python -m backend.conversation_check
.venv-phase2/bin/python scripts/inspect_phase5.py
python3 scripts/review_phase5.py
npm --prefix frontend run build
```

Run model batches sequentially; never restart during active verification. Contract/hostile checks create retained test databases. Live checks add titled application sessions. Reopen uses the latest lifecycle baseline and needs a separately captured restart. Browser remains blocked before navigation; build/HTTP evidence does not replace browser verification. See [results](phase-05-report.md). Stop before Prompt06.
