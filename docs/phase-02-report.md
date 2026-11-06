# Prompt 02: reproducible stack and persisted sessions

Completed 6 November 2026 India time. **Phase 2 gate PASSED:** documented local stack starts, real PostgreSQL migrations/persistence/session isolation and API contracts pass. Stopped at Phase 2; no ingestion or Phase 3 work started. Browser inspection is explicitly unverified.

## Brief and output

Built a minimal React/TypeScript/Vite session workspace, FastAPI API, separate Pi adapter boundary, PostgreSQL/pgvector database, immutable Alembic migration, pinned dependency locks, image digests, Dockerfiles, Compose and safe local configuration. The UI creates/opens sessions and saves messages. It does not pretend to answer transcript questions. Provider/model, dependency availability and empty corpus are visible.

Phase 1's spike and evidence were preserved: all 14 spike source/lock files still match their Phase 1 manifest; a separate Phase 2 adapter copy adapts the localhost endpoint to the container-to-host address. Autonomous routing, essay quality and real retrieval remain unverified. No cloud inference was used.

Local workspace: **http://localhost:8080/**. API/OpenAPI: http://localhost:8000/docs. Host PostgreSQL **5432** was already accepting connections and remains so. New project: **lenny-phase2**, database publish **127.0.0.1:55432**, volume **lenny-phase2_pgdata**. The volume and test databases were retained, not reset or deleted. Ollama remains running on the Mac.

## Exact commands and actual results

Commands ran at the project root; append-only [commands.jsonl](agent-transcripts/phase-02/commands.jsonl) records timestamps, exit codes, bounded actual output and failures. `scripts/docker.py` uses the isolated anonymous Docker config described below. Commands shown here are the actual verification entrypoints, not proposed tests.

| Command | Actual result |
| --- | --- |
| `pg_isready -h 127.0.0.1 -p 5432 -t 2` | Accepting connections before and after the work; no credentials, schema queries or writes to the host instance. |
| `python3 scripts/bootstrap.py --prepare-only` | Created ignored mode-0600 .env with a random DB password; no values printed. Repeated invocation preserved it. |
| `python3 scripts/docker.py compose config --quiet` | Exit 0; resolved credentials were not dumped. |
| `python3 scripts/docker.py compose up -d db` | Created the isolated network/container/new volume and published 55432. |
| `python3 scripts/docker.py compose --progress plain build` | API/Pi and web images built successfully from digest-pinned public bases and exact dependency locks. Frontend build/typecheck also ran inside the image. |
| `python3 scripts/docker.py compose up -d api web` | Started API and frontend; automatic real DB migration `0001_foundation` completed. Repeated startup/recreation preserved data. |
| `python3 scripts/docker.py compose exec -T db psql -U lenny -d lenny -c 'SELECT version();'` | Real PostgreSQL **16.15**, Linux aarch64. Readiness/schema tests reported pgvector **0.8.7**. |
| `python3 scripts/docker.py compose exec -T api python -m backend.contract_check` | Final sequential run: **12 tests passed in 3.122 s**: 5 adapter/config/protocol checks and 7 API/schema checks against a freshly created/migrated real test DB, `lenny_contract_58e9d230b364`. Retained, not dropped. |
| `.venv-phase2/bin/python scripts/verify_phase2.py` | Final live gate passed: two sessions/messages, safe retries, app restart persistence/isolation, DB outage and recovery, unchanged metadata/timestamps, failed-write rollback, frontend HTTP/proxy and structured errors. |
| `python3 scripts/docker.py compose exec -T api python -m backend.agent_smoke` | Real containerized Pi 1.5.0 -> Mac Ollama 0.30.11 -> fixture tool -> correct answer; **3.945 s**. Actual protocol and separate diagnostics copied out before container recreation. |
| `npm --prefix frontend run typecheck` | Exit 0, TypeScript 5.9.3. |
| `npm --prefix frontend run build` | Exit 0; Vite 7.2.2, React 19.2.0. Production assets built; no visual/browser pass inferred. |
| `python3 scripts/docker.py compose exec -T api python -m pip check` | Exit 0: no broken requirements. Tested Linux-only greenlet 3.5.6 was added to the lock. |
| `python3 scripts/docker.py compose exec -T web nginx -t` | Exit 0; final structured web log configuration valid. |
| `python3 scripts/bootstrap.py` | Normal one-command startup checked on the prepared stack; fresh evaluator/clean checkout rehearsal remains Phase 11. |

The command capture prefix was `python3 scripts/capture.py` for the entries retained in commands.jsonl. The local unit command `.venv-phase2/bin/python -m unittest backend.tests.test_unit -v` also passed 5 tests before container testing. No SQLite or mocked persistence substitutes were used.

## Real persistence and outage evidence

Final run: [live-20261106T050703/results.jsonl](agent-transcripts/phase-02/live-20261106T050703/results.jsonl), **10:37:04-10:37:10 India time**. Exact HTTP requests/statuses/bodies, IDs and mutation commands are retained. Earlier successful runs remain separate.

1. Created sessions `93d31abb-4683-493d-a8a7-4d8a09bee319` and `a4e0e1bf-4ed9-4d24-b0aa-02de99a16229`; saved distinct synthetic messages and retried the same client IDs without duplicates.
2. Ran `python3 scripts/docker.py compose restart api`; reopened both sessions and compared exact message objects, original session IDs/timestamps and user metadata. All unchanged and isolated.
3. Ran `python3 scripts/docker.py compose stop db` on the verified lenny-phase2 project. Liveness stayed **200**; readiness became **503/database_unavailable**; a write returned a structured **503**, retryable=true, with a correlated request ID.
4. Ran `python3 scripts/docker.py compose start db`. Readiness returned **200** and existing connections recovered **without another API restart**. Both stored messages were unchanged; the failed write did not appear.

Final readiness distinguishes `scope: phase_2_foundation`, ready DB/schema/extension, Pi 1.5.0 and actual container-to-host Ollama/model metadata. Corpus status is **empty**, active_chunks=0 and **product_ready=false**. Installed embedding dimensions match 768, but no real embeddings or indexing were generated in this phase.

## Failures, corrections and remaining verification limits

- Initial public image pulls hung in Docker Desktop's credential helper. Only identified owned pull/helper processes were terminated; the failed commands remain logged. Separate `.cache/docker-public` config with empty auths and the existing local daemon solved the pulls. User Docker credentials/context/settings were not modified. Public bases are now digest-pinned.
- An initial test run emitted a pooled-connection ResourceWarning. Explicit pool disposal was added for app shutdown and test teardown. Final tests passed without that warning.
- One final contract-check attempt was accidentally launched beside a restart test and exited **137** when its container restarted. It was not counted as passed. The checks were rerun sequentially, then passed. Run these checks sequentially in future.
- The pinned Starlette test-client compatibility path emits a deprecation warning for HTTPX; tests pass, warning retained and not suppressed. Future framework upgrades need revalidation.
- Browser setup failed before connection: `Importing module "node:process" is not allowed in node_repl`. The exact failure is saved separately. No DOM/screenshot/responsive/accessibility verification is claimed; HTTP/typecheck/build do not replace it.
- Native Linux host-Ollama networking is documented, not tested. Full clean-checkout startup, real corpus/parser/embedding/retrieval, generated conversation follow-ups, essays, artifact rendering, cloud integration and full operational failure matrix remain future gates.
- Logs are genuine bounded command/runtime output, not a complete Codex conversation export. The pre-existing full-export gap remains disclosed. No Git commit or publication is claimed; source/image identity is recorded at this gate.

## Changed files and stopping point

Added backend app/contracts/config/DB models, Alembic migration and real verification modules; agent runtime copy and lock; minimal frontend source/lock and proxy; Dockerfiles/Compose/.dockerignore/.env.example; bootstrap, isolated Docker helper, capture and live gate scripts. Updated README, project rules, architecture/design/test notes, assumptions/risks/decisions, environment/provenance, requirements and progress. Phase 1 source/evidence were not rewritten.

See [operations](phase-02-operations.md) for startup/config/networking and [architecture](architecture.md) for schema/API/transaction boundaries. The Phase 2 gate passes within its documented scope. **Stop here. Next is Prompt 03 only when authorized.**
