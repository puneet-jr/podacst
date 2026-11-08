# Lenny Growth Assistant

> **Bounded repair review, not a submission pass.** Runtime `3dc814552104edc83072503811c56dbe452e9552` fixes follow-up sentence coverage and open factual quotations. The exact local demo pair passed on303 episodes/12,770 passages. The fresh unedited1,145-word essay still fails semantic/readability review. Historical1,208-word essay is **reviewed with9 manual edits**. Both historical0/5 scores remain;no new five-case score. The verified OpenRouter GPT-OSS120B final-answer token-cap patch is included;this publication rehearsal uses Ollama only. Cloud credits/availability are not revalidated. [Repair report](docs/phase-12-repair-report.md) · [Current checklist](docs/submission-checklist-repair.md).


Research Lenny’s Podcast, inspect the transcript evidence, and save reviewed Markdown or HTML documents. React/Vite → FastAPI → PostgreSQL/pgvector; Pi controls a narrow read-only retrieval tool and bounded local Ollama calls. Sources are the sole factual evidence. This is a local single-evaluator app, not production authentication.

**Current acceptance:** the main index contains303 episodes/12770 passages at pinned revision `be8ab89a890a833cbba2c892178f823fff178c65`. Original Phase10 scenarios **0/5**, bounded experiment **0/5**, proposed target **4/5**. Quality gate is open. A reviewed1208-word essay required9 edits; raw1216-word generated drafts fail the full rubric. Citation existence is not factual support. [Results](docs/phase-10-report.md) · [Known issues](docs/known-issues.md).

The bounded multi-excerpt experiment is quarantined from the selected candidate. The normal development checkout still preserves it. This complete Chat publication candidate is based on `bffcace365fe97e538599d12acb6989c9e0beab7` plus the narrowly verified OpenRouter cap patch and labelled reviewed-essay setup fixture. The publication commit is built on `origin/main` and is pushed only after its release rehearsal passes. Voice Mode and experimental multi-part shortlists are excluded. See [publication scope and remaining limitations](docs/chat-publication.md).

## Prerequisites and clean checkout

Mac with Python3.11+,Git,Docker Desktop/Compose v2 running,and host Ollama. Development checks use Node24.9.0/npm;the application build installs pinned frontend/agent dependencies inside Docker. Pi1.5.0 is pinned in `agent/package-lock.json` and installed inside the API image. Never copy a real `.env` or credential file between checkouts.

After publication,clone the complete tree from GitHub:

```sh
git clone https://github.com/vivekvattem/lenny.git
cd lenny
git rev-parse HEAD
git status --porcelain
```

For the pre-publication rehearsal,clone the maintainer's complete publication candidate instead of the still-old remote:

```sh
git clone --no-hardlinks /path/to/publication-candidate /private/tmp/lenny-release-evaluator
cd /private/tmp/lenny-release-evaluator
git rev-parse HEAD
git status --porcelain
```

The exact tested commit/tree and final public HEAD are recorded in the publication verification receipt. Do not substitute a dirty development checkout or the Voice Mode branch.

Start/check host Ollama. Inspect memory,disk and installed models before downloading:

```sh
open -a Ollama
ollama --version
ollama list
sysctl hw.memsize vm.swapusage
df -h .
```

Required installed tags: `qwen3:0.6b` chat,`qwen3:1.7b` essay,and `nomic-embed-text:latest`768-dimensional embeddings. If a tag is missing,only then download that tag with `ollama pull <tag>`. The8GiB M2 has substantial memory pressure;use one generation at a time. Phase11 reuses installed models and does not measure cold downloads. Model digests from Phase10 are in [models.json](docs/agent-transcripts/phase-10/models.json). A tag name alone does not establish compatibility or quality.

## Safe isolated startup

If reusing an existing pinned corpus cache,perform the read-only cache-link steps in the Corpus section **before bootstrap**;Compose otherwise creates an empty cache directory. For an isolated evaluator run,choose unused ports and a unique Compose project. The following example preserves the normal8080/8000/55432 stack and all its volumes:

```sh
export COMPOSE_PROJECT_NAME=lenny_release_20261109r3
export WEB_HOST_PORT=18086
export API_HOST_PORT=18006
export DB_HOST_PORT=55438
export POSTGRES_DB=lenny_release_20261109r3
export DEFAULT_PROVIDER=ollama
export OPENROUTER_API_KEY=
export ANTHROPIC_API_KEY=
python3 scripts/bootstrap.py
python3 scripts/wait_ready.py --url http://127.0.0.1:18006/api/health/ready --deadline-seconds 90 --attempt-timeout 3
```

Bootstrap creates an ignored mode0600 `.env` with a generated database password if absent;existing files/volumes are preserved. The API container entrypoint is the sole migration owner in this Compose flow: it runs `python -m backend.migrate` successfully before starting Uvicorn. Bootstrap and Compose do not launch a second migration job. The readiness poll retries connection refused,empty reply (curl52),timeouts and not-ready responses with a90-second total deadline and at most3 seconds per attempt. It succeeds only on HTTP200 with JSON status ready. On deadline it exits nonzero,prints the last safe probe summary and an API-log inspection command. Wait for the readiness command above before using the app;the endpoint is unavailable until migration completes and also verifies the current schema revision. Do not run a separate migration command concurrently with startup. Never use `down -v`,database resets or normal-service outages. With fresh volumes,foundation readiness may return200 while `checks.corpus.ready=false` and `product_ready=false`:ingest evidence before asking questions. Readiness proves transport/model availability,not answer quality. Open **http://localhost:18086/** and **/workspace**;API docs **http://localhost:18006/docs**. Without overrides the normal defaults are8080,8000,55432. Bootstrap’s printed default8080 URL does not reflect overrides;use the selected port.

| Setting in ignored `.env` or environment | Safe default / effect |
| --- | --- |
| POSTGRES_PASSWORD | Generated locally;required,never log/share |
| POSTGRES_USER / POSTGRES_DB | lenny /lenny |
| COMPOSE_PROJECT_NAME | Set uniquely for isolation;do not reuse the normal project |
| DB_HOST_PORT / API_HOST_PORT / WEB_HOST_PORT | 55432 /8000 /8080;override for isolated runs |
| OLLAMA_URL | http://host.docker.internal:11434;Ollama runs on the Mac |
| GENERATION_MODEL / ESSAY_MODEL | qwen3:0.6b /qwen3:1.7b |
| EMBEDDING_MODEL | nomic-embed-text:latest;index must match digest/dimensions/prefix |
| DEFAULT_PROVIDER | ollama;no automatic cloud fallback |
| OPENROUTER_API_KEY / OPENROUTER_MODEL | Empty key /google/gemini-2.5-flash-lite |
| ANTHROPIC_API_KEY / CLOUD_MODEL | Empty key /claude-haiku-4-5-20251001 |
| PRIVATE_RPC_TRACES | false;opt-in raw traces are sensitive and stay private |

Keys stay server-side. To explicitly use OpenRouter later,set its key in your own ignored `.env`,select `DEFAULT_PROVIDER=openrouter`,and recreate only that intended API service. The previous cited Pi/OpenRouter Gemini chat smoke passed6.513s after removing incompatible follow-up JSON mode. Preserve that integration;Phase11 local rehearsal does not make a cloud call. There is a selected-model disclosure,not an interactive provider picker. [Cloud evidence](docs/phase-09-openrouter-diagnosis.md).

For the separately verified GPT-OSS120B route,set `OPENROUTER_MODEL=openai/gpt-oss-120b` in your own server configuration. Only its final answer after linked retrieval gets1,024 output tokens;the tool-call turn and local models retain128. The current release rehearsal does not spend cloud credits.

## Corpus: pin,smoke and full ingestion

Fetch only the pinned public revision into ignored cache:

```sh
python3 scripts/fetch_corpus.py --revision be8ab89a890a833cbba2c892178f823fff178c65
```

If a verified snapshot already exists on this Mac,reuse it instead of downloading again. In a new checkout whose `.cache/corpus` does not exist:

```sh
mkdir -p .cache
ln -s /path/to/existing/lenny/.cache/corpus .cache/corpus
```

The cache includes the revision directory and sibling `.manifest.json`;Compose mounts it read-only. Do not overwrite an existing cache or run fetch against an existing snapshot. Verify the source checkout and all manifest byte hashes:

```sh
python3 scripts/verify_snapshot.py --root .cache/corpus/be8ab89a890a833cbba2c892178f823fff178c65
```

For a fresh rehearsal database,index the three relevant interviews only (this is a separate small test index,not a full-corpus quality claim):

```sh
python3 scripts/docker.py compose exec -T api python -m backend.ingest --root /corpus/be8ab89a890a833cbba2c892178f823fff178c65 --source-path episodes/sean-ellis/transcript.md --source-path episodes/shreyas-doshi/transcript.md --source-path episodes/shreyas-doshi-live/transcript.md --batch-size 4 --deadline-seconds 900
```

The normal303-episode database is never copied or reset. To index the full303-source corpus in an intended database,or resume an interrupted run,omit source filters:

```sh
python3 scripts/docker.py compose exec -T api python -m backend.ingest --root /corpus/be8ab89a890a833cbba2c892178f823fff178c65 --batch-size 4 --deadline-seconds 3600
```

One writer;committed unchanged episodes skip,failures retain progress. Actual Phase10 first run294 loaded/9 skipped/0 failed,2635.389s;repeat303 skipped/0 duplicates. Source versions and saved citation snapshots are immutable;do not mix embedding identities. [Ingestion operations](docs/phase-03-operations.md).

## Local workflow and repeatable smoke

1. At `/workspace`,choose **Start a session**,name it,and create it. Opening a saved session reveals the composer.
2. Ask **“How did Sean Ellis change onboarding at Lookout?”** scoped to Sean Ellis. Open the citation and read the exact passage;closing returns focus.
3. Follow up **“What happened with the next cohort?”** in that same session,keeping the Sean Ellis scope. Verify the same session is used and a fresh source passage supports the answer. These narrow checks do not establish multi-part answer quality.
4. Select Essay,enter a topic with sufficient indexed evidence,and draft. Inspect every factual quote and application. A1125–1375-word range and valid IDs are necessary,not sufficient. Do not accept unsupported/repetitive raw drafts. Explicit review is required;manual changes must be recorded.
5. For an accepted answer,use Documents to save both Markdown and complete static HTML. Reopen the session and both previews after an idle API/web restart. A short answer export verifies persistence/rendering,not full essay quality.

For a reproducible API equivalent with actual source checks and one raw essay,run:

```sh
python3 scripts/readme_smoke.py --base-url http://127.0.0.1:18006 --output .cache/readme-smoke
python3 scripts/docker.py compose restart api web
python3 scripts/wait_ready.py --url http://127.0.0.1:18006/api/health/ready --deadline-seconds 90 --attempt-timeout 3
python3 scripts/readme_smoke.py --base-url http://127.0.0.1:18006 --output .cache/readme-smoke --reopen
```

The helper saves raw output,requires explicit source-span resolution,reports semantic review as pending,and never autoapproves an essay. It creates isolated labelled sessions.

## Previously reviewed essay and exports (explicit fixture)

This optional demo fixture is separate from live essay generation. It is the historical **1,208-word reviewed essay with nine manual edits**:six application-paragraph rewrites and three evidence-span edits. Fresh generated drafts still fail the semantic rubric. The fixture contains only the approved final Markdown/HTML and source-span hashes,not raw transcript payloads. Its original passages must already be indexed by the three-source ingestion above.

On the explicitly isolated `lenny_release_*` database,import it once:

```sh
python3 scripts/docker.py compose exec -T api python -m backend.import_reviewed_fixture --expected-database lenny_release_20261109r3
```

The command validates all six indexed sources and quote hashes,creates a newly labelled fixture session and two unchanged exports,and refuses an existing fixture. It makes no model call and never updates an existing session. Open **“Reviewed essay fixture · 1,208 words · 9 manual edits · not fresh generation”**,expand the saved essay,and choose **Documents**. Open both **markdown** and **html** previews. Each must show **Reviewed essay fixture · rendering check only**. The sidebar label and artifact metadata disclose all nine edits. Source buttons open the original indexed passages.

With no operation running,restart only this isolated app and reopen the same sessions/documents:

```sh
python3 scripts/docker.py compose restart api web
python3 scripts/wait_ready.py --url http://127.0.0.1:18006/api/health/ready --deadline-seconds 90 --attempt-timeout 3
```

The messages,citations,review label and both exports must remain unchanged. This verifies persistence/rendering of a reviewed fixture,not autonomous writing quality. Raw model output,live generation and reviewed fixtures must remain distinct.

## Tests and evaluation

```sh
python3 -m unittest scripts.test_wait_ready -v
python3 scripts/docker.py compose run --rm --no-deps -e DEFAULT_PROVIDER=ollama -e OPENROUTER_API_KEY= -e ANTHROPIC_API_KEY= api python -m backend.contract_check
npm ci --prefix frontend --ignore-scripts --no-audit --no-fund
npm --prefix frontend run typecheck
npm --prefix frontend run build
node --test frontend/test-source-span.mjs
node --test agent/test_provider_policy.ts agent/test_conversation_policy.ts agent/test_essay_format.ts
python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval --split tuning --config eval/retrieval-local-v3.json --output /app/evidence/eval-tuning-new
python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval --split held_out --config eval/retrieval-local-v3.json --output /app/evidence/eval-held-out-new
```

The contract suite creates a fresh retained `lenny_contract_*` database on the isolated server;it never drops normal data. Baseline120 tests include real PostgreSQL/local synthetic embeddings plus explicit model/process mocks. Do not restart services during a suite. Evaluation holdout has already been observed;new executions are reruns. Full-index hybrid Recall@8 was56.25% tuning/81.25% held-out,below85%;small rehearsal-index scores are not comparable. [Test plan](docs/test-plan.md).

## Troubleshooting and limits

- Docker/port conflict:check `python3 scripts/docker.py compose ps`;choose new project/ports before first bootstrap. Do not stop unrelated services.
- Readiness503:inspect its `checks`,Ollama tags and container-to-Mac connection;model availability is not quality. Empty corpus can coexist with foundation readiness200.
- Ingestion interruption:use the exact same ingest command to resume. Identity mismatch requires investigating the configured embedding model,not overwriting the index.
- RPC/provider failure:request remains saved;it is not an evidence gap. Baseline diagnostics can collapse retrieval failures into rpc_rejected;bounded-pass detailed typing is experimental and excluded from this candidate. Saved failed-message detail is limited.
- Context and citation limits:chat uses one short validated excerpt,4096 context/128 output,one retrieval/two provider turns. Multi-part/synthesis and unsupported requests remain unreliable. No shell,arbitrary filesystem or web tools.
- Essay:server owns facts/citations;Pi drafts advice. Raw generated drafts have failed grounding/readability. A reviewed essay is a separately labelled assisted result;do not claim autonomous quality.
-8GiB host:serial generation,heavy swap;do not add models or concurrency without measurements. Physical phone keyboards/other browser engines remain unverified.
- Never commit `.env`,keys,the confidential PDF,downloaded corpus/models,dependencies or private traces. Corpus rights and complete sanitized coding-conversation export remain open. No recorded video/form submission is implied.

[PRD](docs/PRD.md) · [Design](docs/design.md) · [Architecture](docs/architecture.md) · [Requirements](docs/requirements.md) · [Decisions](docs/decisions.md) · [Handoff](docs/handoff.md) · [Progress](docs/progress.md).
