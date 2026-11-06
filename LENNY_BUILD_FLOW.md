# The Lenny Growth Assistant - Build Flow and Acceptance Plan

Planning baseline: 5 November 2026. Discovery emphasis updated: 6 November 2026. Submission deadline supplied by Vivek: **9 November 2026, India time**; exact submission time must be verified. The assignment PDF prints an older deadline (15 September 2026). Use the user's current deadline for planning, not the stale date.

Companion: [LENNY_CODEX_PROMPTS.md](LENNY_CODEX_PROMPTS.md). This is a proposed implementation plan, not evidence that software has been built or tests have passed.

## 1. Product goal and scope

Build a reliable internal workspace for product managers and growth practitioners to research Lenny's Podcast, inspect evidence, and turn the conversation into a finished essay or rendered document.

Primary journey: ask a question -> inspect supporting passages -> ask a follow-up -> generate a Ship 30 for 30 essay -> revise the artifact -> reopen the saved session.

Primary user: a product/growth practitioner who needs useful advice and reusable writing without understanding retrieval, prompts, or infrastructure.

Supporting success measures, to be measured rather than claimed (the primary product metric is defined below):

- Complete the primary journey locally without a critical failure.
- All displayed citations resolve to the exact stored evidence used for that answer.
- At least 85% passage Recall@8 on a manually reviewed set of at least 20 answerable questions; maintain separate unanswerable examples. Treat this as a target, not a fabricated result.
- Review factual support on at least 10 generated answers, including synthesis and follow-ups. Record unsupported claims and fix systematic causes.
- A new evaluator can run the documented setup without undocumented edits. Separate cold-start/model download/ingestion times from warm-response latency.
- Zero known critical defects at release; record lesser limitations honestly.

Required scope: all assignment requirements and eight deliverables. Optional polish: artifact revision history, download controls, simple topic browsing. Defer optional work until required flows pass.

Excluded for this deadline: voice, arbitrary web search, external user uploads, knowledge graph visualization, complex multi-agent architecture, collaboration, billing, and production SSO. Assume a local single-evaluator deployment; still provide isolated sessions and minimal user metadata. Explain that this is not production multi-tenant authentication.

Use the friend's README as a reference, not proof of implementation. Record provenance and license checks for any reused code. Do not rebrand another submission as entirely original work.

### 1.1 Required discovery brief: the opening of the PRD

Put these five elements at the beginning of `docs/PRD.md` BEFORE implementation. They are a client-engagement deliverable, not a retrospective justification for chosen technology. Revisit them at the quality and handoff gates.

| Discovery element | Project-specific framing | Evidence / implementation consequence |
| --- | --- | --- |
| User and problem | Primary user: a product manager or growth practitioner researching a decision and preparing reusable writing. Manually searching long interviews is slow; generic AI advice is difficult to verify. The job is to go from a product/growth question to an inspectable, usable written output. | One continuous research-to-artifact journey; source inspection and saved work take priority over extra features. This is a working assumption, not a claim that client interviews occurred. |
| Success metric | Proposed primary product target: at least 4 of 5 predefined end-to-end scenarios complete without manual recovery. Define cases and pass criteria before testing; report actual numerator/denominator and failures. | See scenario protocol below. Supporting retrieval, grounding, latency and setup measures diagnose why a scenario succeeds or fails. |
| Assumptions | Local single-evaluator deployment; English corpus/output; transcript repository is the sole factual source; suitable host hardware can run Ollama; first setup can download models/corpus; cloud credentials are separately supplied; no production SSO required. | Record each assumption's reason, impact, verification method and status. Verify hardware/model/tool capability early. Surface uncertainty rather than claiming client approval. |
| Scope choices | Include all required chat, follow-up, persistence, writing, artifact, model, security and operational workflows. Exclude voice, external web research/uploads, collaboration, billing, production SSO and graph infrastructure for this deadline. | Explain each exclusion through user value, delivery risk or operating complexity. Optional polish cannot displace required functionality. |
| Risks and trade-offs | Hallucination, latency, cost, local-model capability, data leakage and unsafe rendering each require a mitigation, verification and residual limitation. | Maintain the risk register below and link decisions to user impact and tests. |

### 1.2 Primary metric: scenario completion protocol

Target **SC-01: at least 4/5 scenarios (80%) pass without manual recovery**, proposed by us; the company asks for a measurable metric but sets no numerical threshold. This is a small acceptance exercise, not a statistically robust usability study. All mandatory requirement gates remain separate: reaching 80% never excuses a missing feature or critical defect.

Freeze scenario inputs and reviewed source expectations after initial corpus inspection, before quality tuning. Do not pick only easy demo questions or silently replace failed cases. Run on the release candidate with actual local Ollama and PostgreSQL. Record release revision, corpus/model configuration, hardware, start/end time, outcome, evidence and failures. A pass means correct supported behavior, valid source inspection, successful relevant artifact rendering/save, and a reopened session with the correct content. No database edits, provider swaps, reruns or developer intervention during a scenario. A failed attempt remains in the report; record post-fix reruns separately.

| Scenario | Predefined journey | Additional pass condition |
| --- | --- | --- |
| SC-01-A | Product/growth question -> cited answer -> inspect evidence -> save Markdown artifact -> reopen | Relevant evidence supports reviewed factual claims; artifact matches the discussion. |
| SC-01-B | Question -> follow-up with changed audience/context -> inspect new evidence -> generate complete HTML/CSS artifact -> reopen | Follow-up uses the correct session context; HTML renders safely beside chat. |
| SC-01-C | Grounded research -> dedicated approximately 1,250-word essay -> inspect sources -> reopen | Essay meets the documented count/structure rubric and manual factual-support review. |
| SC-01-D | Research in one session -> new independent session -> separate question/artifact -> reopen both | No context/source/artifact crossover; both conversations persist correctly. |
| SC-01-E | Unsupported request -> clear evidence limitation -> supported reformulation -> cited answer and saved artifact -> reopen | Initial unsupported facts are not fabricated; the user can continue through normal UI actions. |

Define per-scenario duration caps before the final run using measured hardware baselines; do not retroactively increase caps to label failures successful. Report total task time and warm-answer latency separately, including sample sizes. Do not claim human usability validation unless real participants performed it.

### 1.3 Assumption and risk registers

Maintain `docs/assumptions.md`: ID, assumption, why the brief leaves it open, impact if false, validation, status (unverified/verified/rejected), and resulting decision. English/local deployment are scope assumptions; actual RAM, model fit and tool reliability require empirical validation. Link assumptions to relevant requirements and decision records.

Maintain `docs/risks.md` with these minimum entries. Add likelihood/impact, owner, implementation/test links, actual outcome and residual risk as work proceeds. Do not label a mitigation complete from a plan alone.

| Risk / trade-off | Mitigation and check | Residual limitation to disclose |
| --- | --- | --- |
| Hallucination | Retrieve source evidence, validate reference IDs, manually review claim support, and acknowledge insufficient evidence. | Valid IDs do not establish entailment; sampled review does not guarantee every future answer. |
| Latency | Bound evidence/context/tool iterations and retries; stream understandable progress; measure actual local timings. | Longer essays may remain slow on limited hardware; report observed behavior. |
| Cost | Default demo to local inference; bound cloud calls and expose provider selection; document separately billed API use. | Local compute uses hardware/electricity; cloud pricing and limits are external. |
| Local-model quality | Prove tool calls, supported answers and essay generation early; choose a model that actually fits the machine. | Smaller models may be weaker at synthesis, instructions and long-form writing; disclose measured gaps. |
| Data leakage | Server-side secrets, scoped session context, redacted logs, narrow tools and explicit cloud switching. Explain what leaves the device: selected transcript passages, relevant conversation and generation instructions. | Local-only mode differs from cloud mode; no production multi-tenant security claim. |
| Unsafe artifact rendering | Isolated script-disabled iframe, restrictive CSP, safe Markdown and hostile browser fixtures including external-resource checks. | Only tested HTML/CSS capabilities are supported; document restrictions and remaining uncertainty. |

For each major choice in `docs/decisions.md`, record the user need, alternatives considered, selected option, expected benefit, downside and verification evidence. In particular, hybrid retrieval is a hypothesis to compare with sparse/dense baselines, not a mandatory company requirement.

## 2. Decisions and early risk gate

| Component | Proposed choice | Reason / condition |
| --- | --- | --- |
| Frontend | React + TypeScript + Vite | Focused interactive workspace; type-checked UI |
| API | FastAPI + Pydantic | Explicit assignment requirement and validated contracts |
| Persistence | PostgreSQL + pgvector + migrations | Sessions, artifacts, metadata, full-text and vector retrieval in one service |
| Agent | Pi Coding Agent, version pinned after spike | Allowed by brief; prove meaningful retrieval/tool integration with local model |
| Integration boundary | FastAPI manages a Pi RPC adapter | Validate protocol, lifecycle, streaming, and isolation before committing; document any justified alternative |
| Local generation | Ollama on the host | Mandatory real local demo; select model based on actual machine |
| Embeddings | Ollama embedding model, pinned/configured | Local ingestion and query embedding; fixed dimension checked against DB |
| Cloud generation | One supported provider | Required cloud integration, configurable without code changes; test live with an available key |
| Transport | SSE if validated in spike | Status and response events; cancellation and disconnect behavior required |
| Packaging | Docker Compose for app stack | Host Ollama prerequisite explicit; tested macOS and documented Linux networking |

Do not assume a small model supports reliable tools or long essays. First prove Pi + Ollama + one controlled retrieval tool + persisted session. Test the chosen model's context budget, structured output/tool behavior, and end-to-end latency on the user's actual machine.

If tool calling is unreliable, first simplify tool schemas, reduce evidence/context, and test an appropriate model that fits hardware. A documented explicit retrieval workflow driven through Pi may be considered, but do not replace the required framework with a decorative import or a separate direct-model path. Record the actual architecture and limitations.

Pi is the application runtime; Codex is the development assistant. Keep framework and provider dependencies pinned after validating their current official APIs. Do not grant the application agent shell, unrestricted filesystem, or arbitrary web access.

## 3. Requirement register

Create `docs/requirements.md` from this table before feature development. Columns: ID, acceptance criterion, implementation path, verification command/manual evidence, actual status, blocker. Statuses: pending / implemented / verified / blocked. No row becomes verified without evidence.

| ID | Mandatory acceptance criterion | Primary evidence |
| --- | --- | --- |
| FD-01 | Opening PRD discovery before implementation: user/job/pain, predefined measurable metric, assumption register, reasoned scope and verified risk/trade-off register | docs/PRD.md and initial build log |
| API-01 | FastAPI backend; validated requests/responses, structured errors, health endpoints | OpenAPI + API tests |
| AG-01 | Meaningful use of Claude Agent SDK or Pi Coding Agent | Adapter, routing/tool implementation, real local trace |
| SES-01 | New independent chats with follow-up context | API + browser isolation tests |
| DB-01 | PostgreSQL conversations, IDs, timestamps and user metadata | Migration + real PostgreSQL persistence/restart test |
| MOD-01 | At least one cloud provider integrated | Configuration, adapter, real keyed smoke test when available |
| MOD-02 | Actual demo runs with Ollama on a suitable local model | Local end-to-end evidence and demo |
| MOD-03 | Provider switch without source edits; selection visible; fallback documented | UI/config checks; provider failure tests |
| KB-01 | Load source transcripts; document parsing, chunking, indexing and refresh | Ingestion CLI, manifest, parser tests, architecture |
| KB-02 | Trace relevant evidence to original transcripts | Stored source paths, timestamps, hashes, citation inspector |
| RAG-01 | Product/growth answers strictly grounded in transcripts; useful follow-ups; unsupported requests acknowledged | Golden set, support review, local smoke |
| ESS-01 | Dedicated Ship 30 skill/tool grounded in the linked writing guide | Skill definition + source/principle mapping + routing test |
| ESS-02 | Approximately 1,250 words; hook, progression, headings/bullets/selective bold, useful takeaway, grounded claims | Automated structure/count checks and manual quality review |
| ART-01 | Generate Markdown and complete HTML/CSS artifacts from current conversation | Integration cases for both formats |
| ART-02 | Render beside chat within the app | Real browser evidence and responsive manual plan |
| ART-03 | Untrusted HTML isolation/sanitization with explained permissions | Renderer implementation + hostile artifact checks |
| OPS-01 | Reproducible practical startup, preferably one command after documented prerequisites | Clean checkout rehearsal |
| OPS-02 | Safe .env.example; required and optional variables; no committed secrets | Config validation + tracked-content/history secret review |
| OPS-03 | Structured logs diagnose retrieval/model/DB/rendering failures | Correlated successful and failed traces |
| OPS-04 | Missing keys, missing Ollama, timeout, empty retrieval, DB outage handled gracefully | Failure matrix and recovery evidence |
| OPS-05 | Run/test/troubleshoot/extend handoff | docs/handoff.md + evaluator rehearsal |
| DEL-01 | Public repository with complete source and sensible structure | Candidate creates/publishes approved submission repository |
| DEL-02 | Complete README | README checklist and clean setup test |
| DEL-03 | Complete PRD | Product/acceptance review |
| DEL-04 | design.md with principles, IA, states, responsive/accessibility decisions | Design review + browser checks |
| DEL-05 | architecture.md with schema/API/boundaries/ingestion/routing/models/security/topology | Documentation vs code review |
| DEL-06 | Dedicated sanitized agent transcripts, including genuine failed attempts and corrections | docs/agent-transcripts/ |
| DEL-07 | Meaningful API/retrieval/routing/persistence tests and manual UI plan | Test reports + docs/test-plan.md |
| DEL-08 | 2-3 minute camera-enabled YouTube demo: problem, product, actual local Ollama, one trade-off | Candidate-recorded final video and URL |

Public repository, recording, YouTube upload and final form submission are explicit candidate handoff actions unless separately authorized and technically available. Do not mark these complete from a prepared script alone. Do not republish the confidential assessment PDF in the public repository; use a paraphrased requirement register.

## 4. RAG implementation flow

### 4.1 Ingest and refresh

Source: https://github.com/ChatPRD/lennys-podcast-transcripts

1. Fetch a pinned snapshot; record commit SHA, source URL, ingestion version and actual discovered file count. A prior inspection found 303 transcript files while README/index metadata said 269; never hardcode either count.
2. Parse YAML frontmatter and transcript body robustly. Preserve original evidence text separately from any search normalization.
3. Parse speaker/time markers, carry speaker forward on timestamp-only turns, tolerate missing/irregular metadata and report malformed records.
4. Flag sponsor passages with documented heuristics and review representative cases; don't silently remove useful discussion merely because a product name occurs.
5. Group turns into sentence-aware passages, initially 400-700 tokens with modest overlap; bound unusually long turns. Track token estimates honestly.
6. Preserve episode ID, source path, source hash, title, guest, date, video URL, speakers, start/end timestamps, and chunk ordinal/version.
7. Embed in batches with bounded retries, resumability and progress. Validate dimension/model compatibility before writes.
8. Publish an episode's updated chunks atomically. Skip unchanged files; explicitly handle changed/deleted files and partial failures. Query only a consistent active version.
9. Offer smoke ingestion (`--limit`) and full ingestion; show discovered/loaded/failed counts and indexing status in the app. Do not commit the whole corpus or private data into the submission.

### 4.2 Retrieve and generate

1. Resolve follow-ups from bounded session context; preserve names, constraints and requested scope. Do not use prior assistant text as factual evidence.
2. Apply explicit guest/episode filters if requested. Avoid overrestricting based solely on stale AI-generated topic tags.
3. Embed query and run vector search plus PostgreSQL full-text search. Starting defaults: 20 candidates each.
4. Fuse with reciprocal rank fusion, deduplicate overlap and diversify episodes. Use deterministic ordering and retrieve neighbours when context is needed.
5. Select initially 6-10 passages within the local model's token budget; calibrate using evaluation. Do not treat rank-fusion scores as probabilities or use an uncalibrated similarity threshold as proof of support.
6. Assign evidence IDs server-side; pass source passages as untrusted data. Generate only against the supplied evidence.
7. Output source-backed findings, explicitly labelled application suggestions when requested, and evidence gaps. Preserve disagreement when supported.
8. Reject unknown/malformed citation IDs, store exact answer-evidence associations, and render source references. This proves traceability, not semantic entailment.
9. For weak or absent evidence, refine retrieval within a bounded budget or acknowledge insufficient support. Do not silently answer from model memory or the web.
10. Persist completed and failed/cancelled outcomes consistently; make partial output status explicit.

### 4.3 Evaluate

Maintain versioned question IDs with expected passage evidence, not just expected guests. Include direct lookup, paraphrase, named entities, synthesis across episodes, multi-turn follow-ups, sponsor traps, and unanswerable questions. Separate development/tuning examples from a small held-out set.

Report Recall@k and an appropriate ranking measure, manually reviewed claim support/citation correctness, unsupported-question handling, routing correctness, and measured latency. Record model, corpus revision, sample size and hardware. Do not invent scores or use an LLM judge as the sole truth source.

## 5. Agent, writing and artifact workflows

Expose only controlled tools such as `search_transcripts`, `get_passages`, `create_essay`, `create_artifact`, `revise_artifact`. Validate all arguments and bound iterations/tool budgets. Grounded Q&A, essay and artifact intents must have explicit tested routes. Avoid repeated retrieval/tool loops on weak local models.

Read the assigned guide before encoding principles: https://www.ship30for30.com/post/how-to-start-writing-online-the-ship-30-for-30-ultimate-guide

Essay flow: understand audience/topic -> select evidence -> grounded outline -> draft -> validate -> at most a bounded repair -> save. Document a proposed 1,125-1,375-word acceptance range around 1,250, excluding reference metadata; explain the range as our interpretation. Verify hook, narrative progression, skimmable headings/bullets/selective bold and actionable takeaway. Never fabricate stories, guest quotes, case-study numbers or source claims to meet length. If evidence is too thin, retrieve more or explain the limitation.

Artifacts: structured type/title/content/source metadata; save in the current session. Markdown uses safe rendering with raw HTML disabled or sanitized. HTML is a complete document with inline CSS rendered in an isolated iframe with scripts and same-origin privileges disabled, restrictive CSP, external networking blocked, and forms/popups/downloads/navigation controlled. Explain permitted HTML/CSS and blocked behavior. Prevent CSS leaking into the app. Test links, images, CSS URLs, event handlers, SVG, scripts and malformed markup; do not rely on regex sanitization. Revision history is optional until core flows pass.

## 6. API, data and UI boundaries

Proposed entities: users (minimal local identifier/metadata), sessions, messages, episodes, chunks, answer_sources, artifacts, artifact_versions if implemented, ingestion_runs. Use UTC timestamps internally. Use foreign keys, migrations, deletion semantics and indexes. PostgreSQL is authoritative for product state; do not rely only on Pi history files or browser storage.

Proposed API groups (final contract documented in OpenAPI): sessions list/create/read; messages/stream; source passage read; artifacts get/revise; provider capabilities; ingestion status; liveness/readiness. Validate pagination, IDs, limits and provider settings. Return an error envelope with stable code, safe message, request ID and retryability. Document local user scope and avoid leaking one session's data into another.

UI: sessions sidebar, conversation, contextual source/artifact panel. Show provider/model, corpus readiness, progress, empty results, recoverable errors and save status. Keep user prompts after failure. Use readable typography, one restrained accent, keyboard navigation, labelled controls, focus management and responsive chat/artifact tabs. Do not expose internal infrastructure controls unless needed for an evaluator's model choice.

## 7. Section 5 operational contract

| Concern | Implementation and evidence |
| --- | --- |
| Startup | One documented command starts DB, migrations, API, agent boundary and UI after prerequisites. A documented bootstrap wrapper may orchestrate smoke ingestion; full ingestion progress is explicit. No hidden manual SQL or dependency installs. |
| Host Ollama | Document model download, memory requirements, health check, Docker-to-host connection and Linux alternative. Model download and full indexing may require first-run network; warm local generation must not secretly call cloud. |
| Configuration | .env.example, validated settings, provider capabilities, required/optional variable table and pinned dependencies. Keys server-side only, excluded from logs/artifacts. |
| Fallback | Default local demo stays local. No automatic local-to-cloud fallback. Missing cloud credentials disable that choice clearly; switching/fallback is explicit and logged. |
| Logs | JSON events with request/session/run IDs, phase, duration, outcome and safe error code. Log retrieved source IDs and counts instead of full prompts/transcripts by default; redact secrets. |
| Health | Separate process liveness and dependency readiness. Report DB, agent, Ollama/model availability, embedding/index compatibility and corpus state without exposing credentials. |
| Failure recovery | Bounded model/retrieval deadlines, finite retries only for safe transient work, rollback on failed writes, cancellation/disconnect cleanup, no duplicate messages/artifacts on retry. |
| Rendering diagnostics | Safe client error state and server-correlated error event where applicable; never log raw potentially sensitive artifact content. |
| Handoff | Setup, tests, ingest/refresh, troubleshooting, provider changes, skill/tool extension, schema changes, limitations, backup/reset warnings. Never run destructive reset without authorization. |

## 8. Build phases and gates

| Phase | Work | Exit gate | Prompt |
| --- | --- | --- | --- |
| 0 | Discovery, requirement mapping, repo rules and provenance | PRD created before implementation; matrix and build log exist | 00 |
| 1 | Pi + Ollama integration spike | Real local controlled tool call; isolation/lifecycle validated | 01 |
| 2 | Reproducible stack, schema, sessions, contracts | Clean DB migrate; independent persisted sessions; health/errors | 02 |
| 3 | Parser, chunker, embeddings, refresh | Smoke ingest, idempotent rerun, malformed/changed input cases | 03 |
| 4 | Hybrid retrieval and baseline evaluation | Reviewed evidence set; deterministic retrieval and measured report | 04 |
| 5 | Grounded chat and streaming/follow-ups | Real local cited answer and multi-turn flow; failures handled | 05 |
| 6 | Ship 30 dedicated skill | Local essay within documented range with reviewed grounding | 06 |
| 7 | Markdown/HTML generation and safe viewer | Both formats render; hostile fixtures contained | 07 |
| 8 | UI polish and end-to-end tests | Main journey, responsive/accessibility and failure states verified | 08 |
| 9 | Cloud toggle and operational readiness | Section 5 failure matrix and provider isolation verified | 09 |
| 10 | Full corpus, quality review and regression | Measured eval and real persistence/browser checks; known issues logged | 10 |
| 11 | Handoff and clean evaluator rehearsal | Required docs match actual implementation and clean setup works | 11 |
| 12 | Release audit and demo package | Required rows verified or explicitly blocked; video checklist prepared | 12 |

Cloud configuration interfaces and operational logging begin early; phase 9 audits and completes them rather than retrofitting everything late. Capture logs at every phase. Check relevant tests after each change; run the full suite at integration/release gates.

## 9. Schedule and scope protection

- 5-6 November: phases 0-5, prioritizing the real local vertical slice.
- 7 November: phases 6-8; mandatory essay and both artifact formats before extras.
- 8 November: phases 9-11, full corpus, failure testing, documentation and feature freeze.
- 9 November: phase 12, critical fixes, candidate recording/upload and submission buffer.

These are targets, not time guarantees. If a gate slips, drop optional features first. Do not cut required local demo, agent framework, PostgreSQL, security, meaningful tests, Section 5 or mandatory documents. Record remaining gaps honestly.

## 10. Evaluation criteria mapped to proof

| Evaluation criterion | Proof we intend to provide |
| --- | --- |
| Customer and product judgment | Discovery assumptions, narrow primary journey, measurable goals, explicit exclusions and trade-offs |
| Technical execution | Real end-to-end UI/FastAPI/PostgreSQL/Pi/Ollama flow; cloud integration; artifact generation |
| Agentic architecture and grounding | Controlled tools, tested routing, inspectable citations, follow-up retrieval and unsupported-answer handling |
| Deployment and operability | Clean setup rehearsal, health/readiness, correlated logs, bounded failures and operational handoff |
| Code quality | Clear boundaries, validation, migrations, focused critical-path tests, dependency pinning and clean builds |
| UI/UX quality | Useful artifact panel, readable sources, responsive layout, accessibility and complete error/loading states |
| Communication | Concise consistent docs, real build transcripts, measured results, limitations and a coherent short demo |

## 11. Release checklist

- [ ] Opening PRD brief covers all five discovery elements; assumptions/risks/decisions link to implementation and evidence.
- [ ] Five frozen scenarios have recorded actual outcomes; report the proposed 4/5 target separately from mandatory acceptance gates.
- [ ] Every mandatory requirement has implementation and real verification evidence, or an explicit unresolved blocker.
- [ ] All eight deliverables are present; candidate-owned publication/video/submission actions are distinguished from prepared material.
- [ ] Section 5 failure cases exercised, recovery demonstrated and diagnostics actionable.
- [ ] Real local Ollama answers, follow-ups and essay/artifact flow verified on actual demo hardware.
- [ ] Cloud integration verified live when credentials are available; otherwise report the exact verification gap.
- [ ] Real PostgreSQL integration tests run; persistence tests are not silently skipped.
- [ ] Frontend type checks, backend checks, build and browser flows pass on the release revision.
- [ ] Full corpus coverage/failed files reported; no fabricated completeness claims.
- [ ] Sanitized actual coding-agent logs include failures and corrections; no reconstructed fake transcripts.
- [ ] No secrets or confidential assessment file in public tracked content/history.
- [ ] README followed from a clean checkout; restart persistence works without deleting volumes.
- [ ] Demo is 2-3 minutes, camera enabled, proves local Ollama, explains one trade-off, and is uploaded by the candidate.
- [ ] Candidate verifies repository/video links, current form/deadline, and submission receipt.

No plan, skill, or passing suite guarantees zero errors. Release means the specified checks ran, critical defects are resolved, and remaining limitations are disclosed.
