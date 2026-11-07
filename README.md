> Phase8 publication: workspace polish and sanitized checks are committed separately. The remote snapshot is intentionally incomplete: earlier Phase6/7 essay/artifact runtime prerequisites remain local at the user’s request. The live1208-word essay was a manually reviewed result after9 edits; autonomous essay quality remains unverified. See [Phase8 report](docs/phase-08-report.md). Stop before Prompt09.

# The Lenny Growth Assistant

A local research workspace with PostgreSQL sessions, hybrid retrieval, Pi-controlled tools and local Ollama. **Phase6 is work in progress: the local essay gate is blocked by an Ollama structured-output grammar error.** Phase5 demonstrates cited extractive conversation/recovery through the API; browser acceptance remains blocked. Answers quote a model-selected source excerpt; autonomous routing, general answer quality and essays remain unverified.

```sh
python3 scripts/bootstrap.py
```

Requires Docker/Compose and Mac Ollama with `qwen3:0.6b` and `nomic-embed-text:latest`. Open **http://localhost:8080/**; API docs **http://localhost:8000/docs**. Startup preserves credentials, databases and volumes. Isolated DB: **127.0.0.1:55432**; existing host5432 is untouched. Keep Ollama on the Mac. No cloud fallback or Phase5 model download.

[Setup](docs/phase-02-operations.md) · [Ingestion](docs/phase-03-operations.md) · [Retrieval](docs/phase-04-operations.md) · [Chat/API/recovery](docs/phase-05-operations.md) · [Phase5 results](docs/phase-05-report.md) · [Phase6 WIP](docs/phase-06-report.md) · [Progress](docs/progress.md)

Create a session, ask a focused question, inspect its source, then follow up. Questions are saved before inference. Progress, cancel, retry and reopen use real server state. Citation buttons open immutable evidence with exact spans and attribution. The UI compiles and is served; visual, keyboard and interaction checks are unverified because Browser fails before connection.

The requested live hybrid cases succeed: a Sean Ellis question, a follow-up with new evidence, and an unsupported private-data request. The last needs an explicit server policy because the tiny model selected unrelated evidence. Pi executes the real registered retrieval tool after a strict adapter converts its exact textual function request into a framework call. Native/autonomous calling is unproved. The report records outputs, IDs, latency, failures and manual support reviews.

Index: **9/303 episodes, 373 passages; 294 unindexed**. Phase4 historical results/default remain unchanged: selected sparse held-out Recall@8 **62.5%**, dense **87.5%**, hybrid **93.75%**, only eight held-out questions. The broader quality target is unmet. Phase5 chat explicitly uses hybrid; standalone retrieval defaults to sparse. `product_ready=false` remains honest.

[Architecture](docs/architecture.md), [requirements](docs/requirements.md), [PRD](docs/PRD.md), [decisions](docs/decisions.md), [risks](docs/risks.md) and [actual evidence](docs/agent-transcripts/phase-05/README.md) distinguish measurements and limits. Original [Phase1 spike](spike/README.md) and Phase1–4 evidence are unchanged.

Phase6 implemented a dedicated cited-outline/section-drafting workflow, but the corrected local run produced0 essay words/0 sections in20.47s before Ollama rejected its response grammar. No essay-quality pass. Stop before Phase7. Cloud, artifacts, full-corpus quality, clean evaluator rehearsal and demo remain pending. Repository publication is explicitly authorized; video/form submission remains separate. Credentials, weights, full corpus and private RPC stay outside shareable source; rights and complete coding-conversation export remain open.
