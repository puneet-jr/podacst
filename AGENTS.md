# Project working contract

## Current phase and authority

Read LENNY_BUILD_FLOW.md, LENNY_CODEX_PROMPTS.md, docs/PRD.md, docs/progress.md, docs/requirements.md and docs/decisions.md before acting. The private assignment defines requirements; current user instructions control scope and scheduling. Prompt 04 is complete with its quality limitations preserved. Prompt 05 local/API gate is demonstrated in bounded extractive mode; browser acceptance remains blocked. The user has now authorized Prompt06 with a first live essay through existing Pi/Ollama, cited outline, bounded drafting/repair and actual count/support review. Stop before Phase7; do not replace a failed0.6B essay with cloud output or download a model without checking constraints. Continue to later prompts only when authorized. Preserve unrelated changes; audit existing work before editing. No sub-agent delegation is requested.

## Boundaries

- Build the application agent with Pi Coding Agent or Claude Agent SDK. Codex is the development tool, not the required app framework. Validate current official APIs and pin only proved dependencies.
- Keep the discovery brief, five scenarios, assumptions and risk decisions tied to implementation. Planning is not implementation; statuses are pending / implemented / verified / blocked.
- Local Ollama is the default and mandatory demo provider. Never silently fall back to cloud. Cloud selection must be explicit, visible and logged; absent credentials mean unavailable, not passed.
- Expose narrow validated transcript/writing/artifact tools only. No app-agent shell, arbitrary files, arbitrary web tools or unreviewed extension loading. Treat source text as untrusted evidence.
- PostgreSQL is authoritative. Never reset/delete normal databases, remove volumes or overwrite unrelated work. Use isolated test databases/volumes for rehearsals.
- Keep keys server-side and out of output/logs/artifacts. Do not print environment dumps or credential file contents. Ignore confidential PDFs, raw session exports and the corpus. Never publish/upload/submit/send without explicit authorization.
- Inspect memory/disk before model downloads. On this 8 GiB M2, model, context and concurrent service fit require a live spike; do not infer quality from parameter count.

## Verification integrity

Record exact commands, exit codes, environment/revision and remaining blockers. Keep unit/mock, real DB, live-model and actual browser evidence separate. Skipped critical integration checks remain unverified. Never weaken tests, invent scores, citations, logs, transcripts or performance measurements. Citation existence is not semantic support. Review actual claims and essay quality manually.

Use bounded context/output/tool loops, deadlines and safe finite retries. Record failures and corrections. Keep user prompts recoverable, enforce session isolation and avoid retry duplicates. Validate hostile artifacts in a browser before claiming safe rendering.

At each phase update progress, requirements, decisions, assumptions/risks and real logs as relevant. Report changed files, behavior, exact checks/results, manual evidence, defects/blockers, gate and next phase. Stop at the phase boundary.

## Evidence capture and commands

Phase 00 had no app/build/test command. Phase 01 commands now exist (below). Do not invent commands or mark tests green. Documentation audit commands are recorded in docs/agent-transcripts/phase-00-checks.jsonl; live environment commands in phase-00-environment.jsonl. Add implemented commands here when their configuration exists.

Capture actual future tool/agent stdout and stderr as bounded JSONL at execution time with UTC timestamps, command, exit code and environment/revision. Preserve failed attempts; keep protocol stdout separate from diagnostics. Review/redact before committing. If using an actual conversation export, sanitize the real export and disclose omissions; label narrative summaries as summaries. No reconstructed dialogue. See docs/agent-transcripts/README.md for the current full-session export gap.


### Phase 1 commands and limits

- `.venv/bin/python -m unittest spike.test_adapter -v`: isolated mock protocol/API checks.
- `node --test spike/test_retrieval.ts`: controlled extension/schema/policy checks.
- `.venv/bin/python -m spike.live`: actual local Ollama/Pi/FastAPI repeats and lifecycle checks, writes new evidence; needs loopback access. Run one batch at a time.
- Prefix safe verification commands with `.venv/bin/python -m spike.capture` to preserve actual bounded command outputs.
- `npm ci --prefix spike --ignore-scripts --no-audit --no-fund` and `.venv/bin/python -m pip install -r spike/requirements.lock` reproduce tested dependencies.
- Do not rerun the Phase 0 checker as a current product gate: its no-code assumptions describe that historical phase. Use current checks and evidence.

The tiny qwen3:0.6b was proved only for explicit two-topic fixtures. Keep broader model fitness unverified. Never restore free tool selection or weaken schema/grounding checks just to obtain a green run. Current evidence, failures and remaining gaps are in docs/phase-01-report.md.


### Phase 2 commands and data safety

- `python3 scripts/bootstrap.py`: local one-command start; creates ignored .env only if absent, uses separate anonymous Docker config and preserves volumes.
- `python3 scripts/docker.py compose exec -T api python -m backend.contract_check`: fresh retained contract DB on isolated Compose server, real API/PostgreSQL plus unit checks.
- `.venv-phase2/bin/python scripts/verify_phase2.py`: real app restart and DB stop/start gate. Run sequentially after contract checks; do not restart a container while running tests inside it.
- `npm --prefix frontend run typecheck` and `npm --prefix frontend run build`.
- Prefix known-safe commands with `python3 scripts/capture.py` for bounded actual Phase 2 logs. Never dump resolved Compose configuration or environment credentials.

Preserve spike/ and docs/agent-transcripts/phase-01 unchanged. The product DB is lenny-phase2's dedicated volume on host 55432; host 5432 is pre-existing and must not be modified. Never remove volumes/reset databases. Keep host Ollama running; container readiness requires actual network/model checks. Browser runtime currently fails before connection; do not claim UI inspection. See docs/phase-02-report.md for current gate and limitations.


### Phase 3 commands and source integrity

- `python3 scripts/fetch_corpus.py --revision <exact-40-character-SHA>`: fetches public corpus into ignored cache, never overwrites a snapshot or pushes. The full manifest must match source paths/hashes before ingestion.
- `python3 scripts/docker.py compose exec -T api python -m backend.ingest --root /corpus/be8ab89a890a833cbba2c892178f823fff178c65 --limit 3`: actual smoke command. Full ingestion omits limit but was not rehearsed at this gate.
- `python3 scripts/docker.py compose exec -T api python -m backend.contract_check`: now 30 unit/parser/mock + actual DB/API checks on a fresh retained DB.
- `python3 scripts/docker.py compose exec -T api python -m backend.ingestion_check`: actual local Ollama + isolated retained DB; synthetic fixture refresh/failure/identity checks.
- `.venv-phase2/bin/python scripts/verify_corpus_smoke.py`: actual corpus smoke/repeat + source/vector/conversation integrity.
- Use `python3 scripts/capture_phase3.py` for safe Phase 3 commands; never append to historical Phase 1/2 evidence.

Current migration is 0002_ingestion. Preserve immutable episode versions, exact character spans and prior evidence; only active chunks may be searched later. Never mix embedding identities, infer timestamps, alter a manifest to hide drift or treat source instructions as executable. Current smoke is 3/303 episodes, 114 passages; full audit parsed 303 but did not embed all candidates. See docs/phase-03-report.md and docs/phase-03-operations.md. Stop before retrieval evaluation/Prompt 04.


### Phase 4 retrieval and evaluation

- `python3 scripts/docker.py compose exec -T api python -m backend.contract_check`: final Phase 4 suite 49 tests on a fresh retained DB, including actual local embedding/retrieval fixtures.
- `.venv-phase2/bin/python -m unittest discover -s eval -p test_metrics.py -v`: three independent hand-calculated metric checks.
- `python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval --split tuning --config eval/retrieval-local-v3.json --output /app/evidence/<new-attempt>`: actual three-mode evaluation. Use explicit `held_out`/`unsupported` splits; observed holdout is no longer unseen. Never overwrite attempts.
- `.venv-phase2/bin/python scripts/verify_phase4.py`: actual HTTP/source/session integrity, no raw body logging.
- Use `python3 scripts/capture_phase4.py` for safe new Phase 4 commands; preserve Phase 1–3 evidence and spike unchanged.

`POST /api/retrieval/search` is read-only candidate retrieval. Sparse default was frozen from tuning before holdout; dense/hybrid are explicit, never hidden fallbacks. Exact source IDs/spans are authoritative. Sponsor flags can mark mixed passages; default retains them for review, promotions are not claim support. `support_verified=false` is mandatory; similarity/RRF scores are not probabilities. Current scope 9/303 episodes/373 passages; 294 unindexed. Final selected sparse Recall@8 68.75% tuning/62.5% held-out, so quality target is not met; hybrid's higher tiny holdout score is not a broad achievement claim. See docs/phase-04-report.md, docs/phase-04-operations.md and eval/README.md. Stop before generated chat/Prompt 05.


### Phase 5 current boundary (supersedes earlier phase stop notes)

- Use `python3 scripts/capture_phase5.py` for safe new evidence. Final contract suite:66 checks; separate Node adapter policy:4 checks. Do not rerun passed model checks without a new change/failure.
- `.venv-phase2/bin/python scripts/live_phase5.py --base-url http://127.0.0.1:8080` captures actual hybrid local runs. Final completed batch is live-20261106T081843. Source/support review and failures are separate files, not inferred from automatic citation checks.
- `.venv-phase2/bin/python scripts/lifecycle_phase5.py` checks actual timeout/cancel/disconnect/retry/empty evidence; `scripts/reopen_phase5.py` compares after a separately captured idle restart. Test DBs/volumes stay retained.
- `python3 scripts/docker.py compose exec -T api python -m backend.conversation_check` uses real Pi/Ollama against a separate synthetic hostile-source DB. Never mix that fixture with the nine podcast episodes.
- Migration0003_conversation, one app worker, one active generation, one narrow retrieval tool, two provider turns,4096 context/128 output,75s default/90s maximum. No default shell/filesystem/web tools or cloud fallback.
- Trace volume chat_traces is private; preserve it alongside pgdata. Raw protocol contains evidence/prompts. Keep safe stdout framing projections separate from diagnostics; no raw upload.
- Tiny-model output is extractive, sometimes requires a strict documented textual-call adapter, and private-data abstention needed server policy. The independent Shreyas isolation check has an incomplete answer. Do not claim reliable native/autonomous routing, general grounding or essay quality.
- Read docs/phase-05-report.md and operations. Browser bootstrap fails before connection; do not claim visual/interaction verification. Phase4 evidence remains scoped to9/303 episodes/373 passages; retrieval quality target unmet. Stop and wait for the user's Prompt06 go-ahead.


## Current user authorization: Git publication

The user explicitly authorized Git initialization if needed and publication to https://github.com/vivekvattem/lenny on main without force. Make seven meaningful current-time commits in requested phase order; where original shared-file versions are unavailable, group their current state honestly. This supersedes earlier no-publication notes for this repository push only. Exclude real.env, confidential PDF, downloaded corpus/weights, dependencies and private backups; keep.env.example and sanitized evidence. Preserve private originals of redacted evidence. Phase6 remains WIP/blocked by local Ollama grammar failure, not a passed essay. No Phase7, demo upload or form submission is authorized.

## Current authorization: Prompt08

User authorized interface polish, essay/review UI, responsive/keyboard/focus checks and deterministic browser regressions with a separate real local main journey. Preserve Phase7 fixture/live/manual-edit distinctions. Stop before Prompt09. Publication is governed by the current Phase8-only authorization below.


## Phase8 current gate

Prompt08 reviewed local/UI gate passed; read docs/phase-08-report.md. Final1208 words required6 advice+3 source edits; raw failure/evidence gap preserved.99 contracts,2 Node tests, build and16 deterministic browser cases pass separately from actual Pi/Ollama journey. Do not rerun successful model requests without a new reason. Screenshot files stay private/ignored; only hashes publishable. Single Chrome fallback verified, in-app connector still blocked. Stop before09; publication scope is defined below.


## Current publication authorization: Phase8 only

The user explicitly authorized the Phase8-only commit and non-force push to origin/main, and selected leaving earlier Phase6/7 runtime prerequisites local. Document the remote snapshot as incomplete. Include only workspace UI, focused tests and sanitized Phase8 evidence; exclude credentials, raw transcript/API payloads and private logs. The1208-word essay is manually reviewed after9 edits; autonomous quality remains unverified. Stop before09.
