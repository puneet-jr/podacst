# Independent assessment audit

6 November 2026. Read all four pages of the privately supplied assessment using pypdf; inspected link annotations to identify the corpus and writing guide. This document paraphrases requirements; it is not a copy of the confidential assessment. Text extraction was sufficient for the requirement audit; no PDF layout/rendering claim is made. The original PDF stays outside the project.

## Sections 2-8 cross-check

| PDF section | Requirement/evaluation coverage | Register and planned evidence |
| --- | --- | --- |
| 2 Forward deployment brief | Before code: concrete user/job/pain, measurable metric, assumptions, reasons for scope, risks/trade-offs. | FD-01; PRD opening, assumption/risk/scenario/decision registers and creation evidence. |
| 3.1 API/sessions/persistence | FastAPI; Pi or Claude Agent SDK; independent new chats; PostgreSQL conversations/IDs/timestamps/user metadata; validated contracts/errors/health. | API-01, AG-01, SES-01, DB-01; real framework trace, database and API/browser checks. |
| 3.2 Model flexibility | At least one cloud provider; actual local Ollama demo on a comfortable model; no source edits to switch; selection visible and fallback documented. | MOD-01/02/03; local and live keyed cloud runs distinguished. |
| 3.3 Knowledge base | Assigned transcripts; explain loading/chunking-or-selection/index/refresh and source traceability. | KB-01/02; corpus manifest, ingestion/refresh tests, exact citation inspector. |
| 4.1 Grounded conversation | Product/growth questions strictly from transcripts, useful follow-ups, preserved context, explicit unsupported behavior. | RAG-01, SES-01, KB-02; reviewed support and unsupported fixtures plus actual local questions. |
| 4.2 Dedicated content skill | Read assigned guide; encode writing principles in a distinct skill/tool; approximately 1,250 words, hook, progression, headings/bullets/selective bold, useful takeaway, grounded claims. | ESS-01/02; actual guide mapping in Phase 6, routing/structure/count tests and manual writing/support review. |
| 4.3 Artifacts/security | Conversation-based Markdown and complete HTML/CSS, rendered inside product beside chat; explain/implement untrusted-content containment and permissions. | ART-01/02/03; both local outputs, browser preview and hostile-input checks. |
| 5 Operations | Practical one-command setup, safe config, structured logs, five failure classes, run/test/troubleshoot/extend handoff. | OPS-01 through OPS-05, detailed table below. |
| 6 Deliverables | All eight deliverables explicitly tracked, including real sanitized failures/corrections and manual UI plan. | DEL-01 through DEL-08; table below. |
| 7 Submission | Candidate verifies fresh-evaluator setup, current repository/video/form/deadline and submission. | OPS-01/05, DEL-01/02/08; no publication, recording, upload or submission performed. Plan's newer date is provisional; exact time not confirmed. |
| 8 Evaluation | Product judgment; execution; agent architecture/grounding; deployment; code quality; UI/accessibility; communication. | See evidence mapping below; these are review dimensions, not extra shipped features. |

## Every Section 5 bullet

| Obligation | Register | Acceptance evidence still required |
| --- | --- | --- |
| Practical one-command startup | OPS-01 | Clean checkout using README-only steps after stated prerequisites; migrations included, smoke/full ingestion explicit. |
| .env.example and clear required/optional defaults, no committed secrets | OPS-02 | Validated settings table, server-only keys, secret/history review. .gitignore exists but config does not. |
| Structured diagnostics for model/retrieval/DB/rendering | OPS-03 | Correlated safe successful and failed events with IDs, phase, outcome and durations; no full sensitive content by default. |
| Missing key | OPS-04, MOD-03 | Missing cloud choice unavailable with safe actionable message, no fake success. |
| Unavailable Ollama | OPS-04, MOD-02 | Local dependency error and recovery, no implicit cloud switch. |
| Model timeout | OPS-04 | Bounded deadline/cancel/disconnect cleanup, clear failed state and safe retry. |
| Empty retrieval | OPS-04, RAG-01 | Acknowledge evidence gap and allow supported continuation without fabrication. |
| Database connection failure | OPS-04, DB-01 | Readiness fails safely, writes not falsely reported saved, recovery without reset. |
| Operational handoff | OPS-05 | Another engineer can run, test, troubleshoot and extend models/tools/skills/schema/ingestion. |

The build flow additionally elaborates host Ollama networking/downloads, explicit fallback, dependency readiness, retry/write rollback and rendering diagnostics. These are preserved in OPS evidence plans and must not be lost by implementing only the five high-level bullets.

## All eight deliverables

| Deliverable | Register | Actual Phase 0 output |
| --- | --- | --- |
| Public source repository | DEL-01 | Empty workspace audited; no repository initialized or published. |
| README | DEL-02 | Honest discovery-only README, not a runnable setup guide. |
| PRD | DEL-03 | Initial discovery, scope, flows, acceptance and phase plan; final reconciliation pending. |
| design.md | DEL-04 | Future deliverable; not created as a misleading finished design. |
| architecture.md | DEL-05 | Future deliverable; proposed boundaries in PRD/decisions, no code-backed architecture yet. |
| Sanitized coding-agent transcripts | DEL-06 | Actual command audit logs and clearly labelled session summary; full conversation export gap disclosed. |
| Critical-path automated tests plus manual UI plan | DEL-07 | None yet; documentation integrity checks do not substitute for app tests. |
| 2-3 minute camera-enabled YouTube demo | DEL-08 | Not recorded/uploaded; candidate action after real local demonstration. |

## Evaluation evidence plan

| Dimension | Intended proof |
| --- | --- |
| Customer/product judgment | Five-part brief, proposed vs measured metric, narrow journey, reasoned exclusions, validated assumptions and user-facing trade-offs. |
| Technical execution | Actual UI/FastAPI/Pi/PostgreSQL/Ollama path, cloud configuration and both artifacts. |
| Agent architecture/grounding | Narrow validated tools, tested Q&A/essay/artifact routes, fresh follow-up retrieval, exact evidence, unsupported responses. |
| Deployment/operability | Rehearsed startup, safe settings/logs/readiness, failure recovery and handoff. |
| Code quality | Separation of boundaries, migrations/contracts, pinned compatible dependencies and meaningful API/retrieval/routing/persistence checks. |
| UI/UX | Readable conversation/source/artifact workspace, understandable states, responsive layout, keyboard/focus/accessibility review. |
| Communication | Docs reconciled with code, actual failures/corrections, measured limitations and concise camera demo. |

Audit result: all mandatory assessment areas map to the 29 supplied plan IDs. No additional mandatory feature omitted was identified. The plan adds useful proposals (React/Vite, pgvector/hybrid, SSE, numerical quality targets and the essay count band); do not present them as company-specified technology or thresholds. No product requirement was verified by reading the PDF alone.
