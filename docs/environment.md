# Environment and integration feasibility audit

Phase 0 observations, 6 November 2026 India time (historical; see Phase 1 update below). Exact read-only commands/results are preserved in [agent-transcripts](agent-transcripts/README.md). No dependencies installed, models downloaded, services started, database schemas inspected or data changed during discovery.

| Capability | Actual observation | Limit of evidence |
| --- | --- | --- |
| OS/CPU | macOS 26.5.2, Darwin arm64, Apple M2, 8 physical cores | Host facts, not inference performance. |
| RAM | 8,589,934,592 bytes = 8 GiB physical memory | Available memory/load and full-stack model fit not measured. |
| Disk | df reports ~100 GiB available on workspace volume | Shared disk; not a commitment to download large models. |
| Python | 3.13.5 | FastAPI/dependency compatibility not yet exercised; may choose a separately proven version later. |
| Node / npm | Node v24.9.0, npm 11.6.0 | Node meets candidate Pi declared >=22.19.0; package installation not proved. |
| Other package managers | pnpm, yarn, uv not found on PATH | npm available; no need to install extras for discovery. |
| Docker / Compose | CLI 28.4.0, Compose v2.39.2-desktop.1; daemon responds with 28.4.0 | No app image built or stack started. Docker memory allocation not inspected. |
| Ollama | Client 0.30.11; localhost:11434 connection refused outside sandbox | Installed, not serving. Inventory unknown, not 'zero models installed'. No inference/embedding run. |
| PostgreSQL | psql 15.14; localhost:5432 accepting connections | pg_isready is not authenticated query, pgvector, migration or persistence evidence. Never repurpose/reset existing database. |
| Pi | No pi executable found on PATH | Highest-risk spike prerequisite missing. No framework/tool/local-model success. |
| Cloud credentials | ANTHROPIC_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY, OPENROUTER_API_KEY absent in inherited environment | Presence-only check; no values printed, credential files not read. Keys elsewhere/account access not inferred. |
| Private assignment | Four pages readable with pypdf; links inspected | Kept external; no rendered-layout assertion. |

## Sandbox failures and corrected observations

Initial sysctl, Docker-socket and localhost probes were blocked by the execution sandbox. These were not proof that Docker/PostgreSQL were down. Read-only checks retried outside the sandbox succeeded for hardware, Docker and PostgreSQL. Ollama then failed with actual connection refused. Both failure and correction are recorded; only the unrestricted probes support current service statements.

## Current official Pi documentation checked

The old badlogic/pi-mono links redirect to earendil-works/pi. Observed source revision: `2a32a605a9f18a5f0191f65358a2e764b2f69fc7`. Package metadata fetched at that exact revision declares `@earendil-works/pi-coding-agent` version `1.5.0`, Node `>=22.19.0`, MIT. This is an upstream candidate, **not an installed or compatibility-proven pin**. Verify npm availability and installed CLI help in Prompt 01.

- [RPC documentation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md): subprocess JSONL suits Python; LF framing, unique command IDs, async response correlation and separate event records need an adapter.
- [Model configuration](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md): Ollama connects as a configured compatible endpoint in models.json. Validate actual model ID, tool behavior and endpoint locally.
- [Extension documentation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md): registered schema-based custom tools can expose a narrow fixture retrieval operation. Extensions execute with process permissions, so load only reviewed project code and disable unrelated/default tools.
- [CLI reference](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/cli.md): consult installed help before constructing process flags; stdout is protocol output in RPC mode.
- [Provider documentation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/providers.md): Anthropic and Google Gemini are supported key-based options. No provider selected until credentials/access are checked; no cloud smoke run.
- [Exact package metadata](https://github.com/earendil-works/pi/blob/2a32a605a9f18a5f0191f65358a2e764b2f69fc7/packages/coding-agent/package.json) and [license](https://github.com/earendil-works/pi/blob/main/LICENSE).

No broader API/product claims are inferred from documentation alone. No generated application is using these APIs yet.

## Prompt 01 feasibility and exact blockers

1. Install a project-local, version-checked Pi candidate with npm after proving package identity/availability; no global configuration edits needed. Blocker B-01.
2. Start host Ollama, list actual installed models and measure memory headroom with app/DB overhead. No large model pull until this check. Blocker B-02. A small quantized tool-capable candidate is a hypothesis, not a chosen model.
3. Prove Python/FastAPI -> Pi -> local model -> controlled deterministic retrieval fixture -> final response. Bound context, iterations, output and deadline; isolate sessions and clean up cancellation/disconnect.
4. Capture actual protocol and diagnostic evidence, focused mock protocol checks and separate real-local smoke results; pin only the proven working versions.

Python/Node/npm and disk prerequisites are present; the next spike is feasible to attempt after B-01/B-02, but reliability and latency on 8 GiB remain unknown. Cloud credentials do not block the local spike. Existing PostgreSQL readiness supports a later isolated test database attempt, not product database success.


## Phase 1 superseding runtime observations

Ollama 0.30.11 is now started on localhost with cloud disabled. Only nomic-embed-text was preinstalled (embedding-only). Downloaded qwen3:0.6b, 522,653,767 bytes, Q4_K_M; digest and observed ~1.02 GB loaded footprint are in phase-01-report.md. Pi 1.5.0 installed and version/help/runtime validated in isolated configuration. Python 3.13.5 / Node 24.9.0 / npm 11.6.0 exercised; tested Python versions frozen in spike/requirements.lock and npm dependency tree in spike/package-lock.json.

Final 5/5 guided fixture calls and real API/lifecycle checks passed. Model context observed 4096, output capped at 256, one concurrent request. The model was not reliable with autonomous/ambiguous tool selection; general research/writing and full-stack memory fit remain unverified. No larger model or cloud inference was used. Phase 0's 'Pi absent/Ollama stopped' observations no longer describe the current runtime. PostgreSQL product access was not tested in Phase 1.


## Phase 2 current environment

Existing host PostgreSQL on 5432 was occupied and remains accepting connections; new isolated Compose DB is PostgreSQL 16.15/pgvector 0.8.7 at host 55432. API/web run at loopback 8000/8080. Python 3.13.5, Pi 1.5.0/Node 24.9.0, SQLAlchemy 2.0.57, Alembic 1.20.1 and psycopg 3.2.12 were exercised in Linux aarch64 containers with pinned dependencies/bases. Docker Desktop 28.4.0/Compose 2.39.2 responded; stalled credential helpers were isolated for public pulls.

Actual API-container Ollama readiness and a controlled local tool run to the Mac passed. Ollama 0.30.11 stays on the host, models preserved, no cloud fallback. No new model was downloaded. Embedding metadata dimension 768 matches schema; actual embedding/ingest remains untested. Browser runtime failed before connection; no UI inspection. Phase 1 spike files/evidence preserved; see phase-02 report for current checks and exceptions.


## Phase 3 superseding observations

Migration 0002_ingestion applied to actual app PostgreSQL plus fresh retained contract/integrity databases. PyYAML 6.0.3 was installed/pinned after tests and container build; other tested Phase 2 dependency pins remain. Final 30-test suite passed, separately 12 real local ingestion integrity checks and seven real-corpus smoke invariants passed; pip check found no broken requirements.

Actual Ollama 0.30.11 `/api/embed` returned/stored 768-dimensional Nomic vectors. Existing `nomic-embed-text:latest` digest `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`; model native context 2048, no new model downloaded. Three real files/114 chunks loaded in 24.078 s, repeat 0.247 s. Container-to-host reachability and pinned index identity passed. qwen3 remains fixture-generation only; no corpus generation/essay quality claim.

Post-smoke snapshot (not peak): Mac14,7/M2, 8 cores/8589934592 bytes, swap used 8194.56 MiB, memory-pressure free percentage 28%, workspace volume 105 GiB available. Container usage then API 65.56 MiB/768 MiB limit, DB 53.78/512, web 8.348/64. Host-wide swap reflects other workloads too; do not attribute its change to ingestion or infer free RAM from a percentage alone. Actual commands/results are in phase-03/commands.jsonl. Browser still unverified; no clean evaluator or Linux host Ollama-network rehearsal.


## Phase 4 current measurements

No dependency pin/schema/model download changed. Same PostgreSQL16.15/pgvector0.8.7, Ollama0.30.11 and existing Nomic768-dimensional digest were actually exercised for corpus/query vectors. Six selected corpus sources added259 chunks in43.533s; total9/303 episodes/373 chunks. Final49 tests passed in6.292s on retained lenny_contract_38c907210618; three separate hand-calculated metrics and nine live API/DB proofs passed. Evaluation is real local DB/model search, not generation.

Final API image manifest sha256:ae095a6aed7bda686cfc920e3b4bf946d1ec11f457d86a96c3ac8f4b0da63634 (Linux arm64). Readiness scope phase_4_retrieval, partial corpus/product_ready=false. Post-evaluation snapshot: Mac14,7/M2 eight cores/8GiB, swap8520.81MiB, free percentage29%, disk105GiB; API77.83/768MiB, DB87.31/512MiB, web8.387/64MiB. This is not peak telemetry and does not attribute host workload/swap to retrieval. No cloud inference or browser/clean-evaluator verification. Exact commands/results in phase-04 evidence.


## Phase 5 current environment and interruption audit

Migration0003_conversation is applied to real isolated PostgreSQL. Existing locks/models are unchanged: Python3.13.5, Pi1.5.0/Node24.9.0, FastAPI0.138.1, Pydantic2.14.3, SQLAlchemy2.0.57, Alembic1.20.1, psycopg3.2.12, pgvector Python0.4.1/server0.8.7, HTTPX0.28.1, Starlette1.10.0, PyYAML6.0.3. The retained test-client deprecation is documented; no unproved version upgrade was introduced.

Real generation uses local qwen3:0.6b, digest7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435, Q4_K_M, downloaded size522653767 bytes; earlier observed loaded size1022309171 bytes/context4096. Local Nomic digest/profile remains unchanged. No Phase5 model download or cloud inference. Final runtime/source identities are in phase-05/runtime-review.json and source-manifest.json.

Final66-test suite completed exit0 in6.668s. The final actual proxy/API live batch081843 also completed exit0; resuming found no active verification process and reran no model tests. Only read-only preservation/runtime/source review and documentation were completed. Post-check Mac14,7/M2/eight cores/8GiB snapshot: swap9584.31MiB,24% memory-pressure free percentage,109921341440 bytes disk free. API66.3/768MiB, DB126.8/512MiB, web7.422/64MiB then; snapshots, not peak/causal attribution.

All221 protected prior files and original six saved messages/session hashes are unchanged. Nine episodes/373 active chunks remain. Browser again blocked before connection; no visual/accessibility claim. Prompt06 not started.
