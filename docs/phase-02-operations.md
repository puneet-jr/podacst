# Phase 2 local setup and operations

This is the session-storage foundation, not the completed transcript assistant. All commands below run at the project root. No command resets an existing database or deletes a volume.

## Start

Prerequisites: Docker Desktop/Compose, Python 3 for the bootstrap wrapper, and the Mac's existing Ollama server with qwen3:0.6b and nomic-embed-text:latest installed. Inspect hardware and existing models before downloads. The Phase 1 model and evidence are retained; no new model is needed for Phase 2.

```sh
python3 scripts/bootstrap.py
```

The wrapper creates an ignored mode-0600 .env with a random local database password only when absent, rejects placeholder passwords, validates Compose without printing resolved credentials, builds pinned images and starts the isolated lenny-phase2 project. It never overwrites .env or removes data. First setup downloads images/dependencies; ordinary restarts reuse them. The separate anonymous Docker CLI config under ignored .cache/docker-public avoids the observed Docker Desktop credential-helper hang for public images, without changing user Docker credentials/settings. It does not support pulling private images.

Open http://localhost:8080/. API docs: http://localhost:8000/docs. Foundation readiness: http://localhost:8000/api/health/ready. Readiness must be checked after startup; starting containers alone is not proof of dependency readiness. Empty transcript corpus is reported honestly and product_ready remains false.

The existing host PostgreSQL on port 5432 is preserved. Only the new Compose DB publishes 127.0.0.1:55432; container-to-container DB traffic uses db:5432 on the private project network. The dedicated volume is lenny-phase2_pgdata. API and web bind only 127.0.0.1:8000 and :8080. DB memory is capped at 512 MiB, API at 768 MiB and web at 64 MiB; these are service limits, not a full-host memory-fit guarantee.

## Configuration

| Variable | Required/default | Meaning and boundary |
| --- | --- | --- |
| POSTGRES_PASSWORD | Required; bootstrap generates it | Server-only, ignored .env; never paste into prompts/logs. Changing it does not reset an initialized volume's password. |
| POSTGRES_USER / POSTGRES_DB | Optional, lenny / lenny | Used only for the new local container. The init user is a local evaluator administrator, not a production least-privilege deployment. |
| DB_HOST_PORT | Optional, 55432 | Loopback publish; avoid the existing 5432 instance. |
| API_HOST_PORT / WEB_HOST_PORT | Optional, 8000 / 8080 | Loopback local access; change before startup if occupied. |
| OLLAMA_URL | Optional, http://host.docker.internal:11434 | Container's approved local endpoint; not the container's localhost. Native host code may use localhost explicitly. |
| GENERATION_MODEL | Optional, qwen3:0.6b | Only guided fixture quality has been demonstrated. Model changes require a new quality check. |
| EMBEDDING_MODEL | Optional, nomic-embed-text:latest | Readiness checks metadata against the schema's fixed 768 dimensions. No embedding generation was proved in Phase 2. |
| DEFAULT_PROVIDER | Optional, ollama | Only implemented choice at this gate; unsupported defaults fail validation. No automatic cloud fallback. |
| ANTHROPIC_API_KEY | Optional, blank | Server-only presence can be reported; cloud adapter remains disabled/unimplemented even if supplied. |

Do not run `docker compose config` without --quiet when recording output: resolved configuration contains the database credential. Do not print environment values or full Docker inspect output.

## Host Ollama networking

On this Mac, the existing localhost-only Ollama server was kept running. Actual containers reached host.docker.internal:11434 with the Compose host-gateway mapping; both version/model discovery and a real containerized Pi fixture call passed. This is measured evidence for this Docker Desktop installation, not a general assumption that every host loopback service is reachable.

Keep OLLAMA_NO_CLOUD=1, OLLAMA_CONTEXT_LENGTH=4096, OLLAMA_NUM_PARALLEL=1 and OLLAMA_MAX_LOADED_MODELS=1 for the small local fixture check. Do not start a second server if one is running. No model is silently downloaded or substituted by the app.

Linux: host.docker.internal maps to host-gateway via extra_hosts. Native Docker does not generally reach a host service bound only to 127.0.0.1. Bind Ollama to the intended private Docker bridge interface, restrict access to that private network and verify from the actual API container; do not expose Ollama publicly or switch to cloud as a workaround. Linux networking is documented but not exercised here.

## Migrations and data

Startup runs `python -m backend.migrate` before Uvicorn. Alembic revision 0001_foundation creates users, sessions, messages, episodes, chunks, answer_sources, artifacts and ingestion_runs, plus pgvector, UTC timestamps, foreign keys and query indexes. Repeated upgrades are idempotent. No manual SQL initialization or destructive downgrade is advertised. Existing volumes are never cleared by bootstrap.

```sh
python3 scripts/docker.py compose exec -T api python -m backend.migrate
python3 scripts/docker.py compose restart api
python3 scripts/docker.py compose stop
python3 scripts/docker.py compose up -d
```

Stopping containers preserves the volume. Do not remove volumes or reset normal data without separate authorization. Backup/reset/handoff procedures will be expanded in later phases. Test databases created by contract checks remain named lenny_contract_* inside this isolated PostgreSQL server; no existing databases are reused or dropped.

## Verification

```sh
python3 scripts/capture.py python3 scripts/docker.py compose exec -T api python -m backend.contract_check
python3 scripts/capture.py .venv-phase2/bin/python scripts/verify_phase2.py
python3 scripts/capture.py npm --prefix frontend run typecheck
python3 scripts/capture.py npm --prefix frontend run build
```

Run contract checks and restart/outage checks **sequentially**: restarting the API kills processes running inside it. contract_check creates/migrates a fresh database, runs actual PostgreSQL API tests plus focused adapter/config mocks, and retains it. The live verifier creates two synthetic sessions, saves/retries distinct messages, restarts the API and stops/starts only this project's DB, checks liveness/readiness and confirms recovery/persistence without resetting a volume. It restores a stopped DB in finally. These commands require the already prepared local Python/Node dependencies for the host-side checks; alternatively Docker builds run the frontend typecheck/build without host Node.

For the optional real fixture boundary proof, `python3 scripts/docker.py compose exec -T api python -m backend.agent_smoke` writes actual protocol stdout and separate diagnostics inside /app/evidence. Copy evidence out before recreating the API container; ordinary saved user messages are in PostgreSQL and do not depend on that ephemeral folder. Do not mistake the fixture smoke for real transcript answers.

## Diagnostics and current limits

Request/dependency/database events use JSON with request/session IDs, UTC time, phase, status and duration. Messages/prompts, database URLs, raw exception text and credentials are excluded. Web access logs use safe structured metadata without query strings/content. Liveness is dependency-independent; foundation readiness checks DB migration/extension, installed Pi version and container-to-host Ollama/model metadata. Corpus state is separate.

Missing DB returns 503 readiness and structured retryable API errors; recovery uses new/pre-ping connections without an app restart. Missing Ollama/model or Pi makes foundation readiness fail, never enabling cloud. User input remains in the composer after a failed save; retries use a client message UUID. There is one fixed local evaluator and no authentication/SSO or production multi-tenant security claim.

Browser inspection was blocked by the installed browser runtime before connection. HTTP serving/proxy, TypeScript/build and actual APIs were verified; visual layout, keyboard flows and responsive browser behavior remain unverified. Transcript ingestion, conversational generation, writing, artifact viewing, live cloud integration and full handoff are later work.
