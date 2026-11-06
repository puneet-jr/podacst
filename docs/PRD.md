# The Lenny Growth Assistant: product requirements

## Discovery brief (before implementation)

Created 6 November 2026, India time, in an empty project workspace. This is a proposed product contract, not shipped behavior. The persona and deployment assumptions have not been confirmed by client interviews.

1. **User, job and pain.** A product manager or growth practitioner needs to research a product decision and prepare reusable writing. Searching hours of interviews is slow, while generic AI advice is hard to verify. The job is to turn a product/growth question into an inspectable answer and usable written output in one saved workspace.
2. **Measurable success.** Proposed primary target SC-01: at least **4 of 5 predefined end-to-end scenarios (80%)** complete without manual recovery. This is our target, not a company benchmark or permission to omit mandatory requirements. The denominator, scenarios and pass protocol are in [scenarios.md](scenarios.md). No scenarios have run; actual result is **not measured**, not 0/5. Supporting retrieval, grounding, latency and setup measures remain separate.
3. **Assumptions.** We assume one local evaluator, English output, transcripts as the sole factual source, sufficient model hardware, first-run network access, separately supplied cloud credentials and no production SSO. [assumptions.md](assumptions.md) records why, impact, validation and decisions. Actual hardware is Apple M2 / 8 GiB RAM; model fit and quality remain unverified. No client interview or approval is claimed.
4. **Reasoned scope.** Include independent grounded chats, evidence inspection, PostgreSQL persistence, dedicated Ship 30 writing, Markdown and HTML/CSS artifacts beside chat, explicit local/cloud configuration and practical operational handoff. Each supports research -> evidence -> essay/artifact -> revision/reopen. Exclude voice, arbitrary web research, uploads, collaboration, billing, production SSO and graph infrastructure to protect the required journey and deadline. Detailed scope below explains each choice.
5. **Risks and trade-offs.** Hallucination, latency, cost, small local-model quality, data leakage and hostile artifacts need specific mitigations and observed checks; [risks.md](risks.md) records residual limitations. Local inference supports privacy and avoids per-call cloud billing but competes with Docker and the OS for 8 GiB RAM. PostgreSQL consolidation reduces operating burden; hybrid retrieval is a hypothesis to evaluate, not an assessment mandate. No planned mitigation is claimed verified.

## Authority and delivery context

The privately supplied four-page assessment defines mandatory requirements. [requirements.md](requirements.md) paraphrases Sections 2-8 and maps every build-plan ID. The planning documents provide execution order and proposed technology choices, not proof of completed work. The plan conveys 9 November 2026 India time as the current deadline; the PDF prints 15 September 2026 EOD. The newer deadline and exact time/form availability still require candidate confirmation before submission. Do not upload or republish the assessment.

## Product scope

| Included | Reason and acceptance boundary |
| --- | --- |
| FastAPI contracts, validation, errors and health | Required API and evaluator diagnostics; distinguish process liveness from dependency readiness. |
| Pi-controlled agent with narrow tools | Required framework must meaningfully drive retrieval/writing/artifact routes; prove local integration first. Claude Agent SDK remains an allowed alternative requiring a documented decision. |
| New independent chats and follow-ups | Research changes direction; maintain context within each session, never use prior assistant text as factual evidence. |
| PostgreSQL state | Conversations, IDs, UTC timestamps, minimal user metadata, evidence associations and artifacts must survive restart. |
| Transcript ingestion and inspectable citations | Preserve original evidence, source path/hash and available timestamps; explain refresh and malformed input behavior. |
| Grounded answers and unsupported behavior | Factual claims come only from selected transcripts; preserve qualifications and distinguish application suggestions. |
| Dedicated Ship 30 workflow | Read assigned guide in Phase 6; encode mapped principles and produce approximately 1,250 grounded words. Proposed acceptance band 1,125-1,375 excluding reference metadata. |
| Markdown and complete HTML/CSS artifacts beside chat | Turn research into usable content; safe rendering, current-session save, clear generation/error states. |
| Revise and reopen | Support a basic current artifact update and retrieve fresh evidence for new claims; historical version UI is optional. Reopened work must retain source associations. |
| Local Ollama and one cloud provider | Real local demo mandatory; explicit switch without source edits, selected provider visible, documented behavior without automatic cloud fallback. |
| Setup, logs, recovery, tests and handoff | An evaluator must run, diagnose and extend the system from documented prerequisites. All eight deliverables remain required. |

| Excluded or deferred | Reason |
| --- | --- |
| Voice | Does not improve the required written research journey enough to justify new latency and failure modes. |
| Arbitrary web research | Conflicts with transcript-only factual grounding and adds trust/network scope. |
| External uploads | Adds parsing, privacy and security work outside the assigned source. |
| Multi-user collaboration | Local single evaluator is the working deployment assumption; shared editing and permissions are out of scope. |
| Billing | No paid-service business workflow was requested. |
| Production SSO/multi-tenant authentication | Not required by the stated brief; still scope sessions to a minimal local user and avoid claiming production security. |
| Knowledge graphs/complex multi-agent architecture | More services and failure boundaries without demonstrated user benefit; start with simpler measured retrieval. |
| Revision history, exports/downloads, topic browsing | Optional polish only after all mandatory flows pass; basic artifact revision/save remains in the journey. |

## User flows and acceptance

**Research and evidence:** ready corpus -> new chat -> question -> retrieval/model progress -> grounded answer -> inspect exact passage and attribution -> follow-up with new retrieval. Empty or weak evidence produces a useful limitation, never unsupported facts. Unknown citations never become links.

**Write and reuse:** choose audience/topic from the current discussion -> dedicated evidence/outline/draft/validate/finite repair workflow -> approximately 1,250-word essay -> inspect sources -> request Markdown or a complete HTML document -> preview beside chat -> revise -> save. Formatting must serve the narrative; invented statistics, quotes or stories cannot fill word count.

**Return and recover:** reopen session after restart -> recover messages, correct provider metadata and artifacts -> continue. A failure retains the user's prompt and offers an ordinary retry without duplicated saved output. New chats remain isolated.

**Provider and setup:** after documented prerequisites, one startup command runs the app stack and migrations. Show dependency readiness and corpus status. Default generation stays local. Missing cloud keys disable that choice; explicit cloud use may send selected passages, relevant conversation and generation instructions off device. Store keys server-side and redact diagnostics.

**Safe artifacts:** Markdown disables or sanitizes raw HTML and unsafe URLs. HTML/CSS uses allowlisting/sanitization plus an isolated script-disabled iframe without same-origin privilege, restrictive CSP and blocked external networking. Test scripts, handlers, SVG, CSS URLs, links/images, forms, nested frames and malformed input. Explain supported behavior to users without exposing infrastructure controls.

Features are implemented by phase. Phase5 connects retrieval to bounded local extractive chat/source inspection; broader research and writing remain unverified. Requirement IDs and evidence paths are authoritative in the register; plans and mock tests do not establish live integration.

## Measurement plan

| Measure | Proposed target or protocol | Evidence, sample and current outcome |
| --- | --- | --- |
| Primary scenario completion | >=4/5 without developer/manual recovery | Five fixed journeys on release candidate with actual local Ollama/PostgreSQL; record failures and reruns separately. Not measured. |
| Retrieval | >=85% passage Recall@8 | Phase 4: 24 reviewed questions (16 tuning/eight held out), four unsupported; actual three-mode baseline on nine episodes. Selected sparse 68.75% tuning/62.5% held-out, 66.67% all-case descriptive recall; proposed target not met. See phase-04-report.md. |
| Citation traceability | Every displayed citation resolves to the exact answer evidence | Final Phase5 citations opened and exact originals manually reviewed. Supported question/follow-up pass; independent Shreyas answer is incomplete despite a valid source. Browser inspection blocked. |
| Grounding | Review >=10 actual answers including synthesis and follow-ups | Phase5 reviews two supported outputs, one policy-corrected private-data gap and one incomplete independent answer. The >=10 unique-answer/broad synthesis target is not met; repeats are not independent quality cases. |
| Latency | Establish hardware baseline before fixing scenario caps | Record warm-answer and total-task times, sample sizes and model/context; separate cold downloads and ingestion. No complete-journey cap yet; final Phase5 requested API checks took8.96/7.05/5.26s on M2/8GiB. These are extractive answers, not essay/full-journey timings. |
| Setup | Fresh evaluator completes README without undocumented changes | Isolated clean-checkout rehearsal, fresh test volumes, measured first run and restart persistence. Not run. |
| Defects | Zero known critical defects at release | Mandatory gate/failure checklist and open issue register; discovery-only state cannot establish product reliability. |

## Phased implementation

| Prompt | Intended increment and gate |
| --- | --- |
| 00 | Discovery before code, complete matrix/rules, provenance and environment evidence. |
| 01 | Real Pi + local Ollama controlled tool; bounded lifecycle, protocol and session isolation. |
| 02 | Stack, migrations, independent persisted sessions, API contracts and readiness. |
| 03 | Real corpus parser/chunks/embeddings, resumable and atomic refresh. |
| 04 | Retrieval integrity, reviewed baseline questions and actual evaluation. |
| 05 | Local cited chat/follow-ups, source UI, unsupported and failure recovery. |
| 06 | Dedicated guide-grounded essay with local count/structure/support review. |
| 07 | Both artifact formats and hostile-input containment in browser. |
| 08 | Responsive/accessibility polish and complete primary journey checks. |
| 09 | Live cloud configuration and operational failure matrix. |
| 10 | Full corpus, regression, measured quality and scenario outcomes. |
| 11 | Reconciled documents and clean evaluator setup rehearsal. |
| 12 | Release audit, demo preparation and candidate publication/video/submission handoff. |

Prompt 00 discovery preceded implementation. Prompt 01 completed the explicit fixture spike. Prompt 02 completed the persisted session/API foundation. Prompt 03 completed ingestion. Prompt 04 is now complete for tested retrieval and a reviewed actual baseline; the proposed quality target remains unmet. Prompt05 now demonstrates the local/API cited-conversation and recovery gate with explicit model limits; browser acceptance is blocked. Phase6 has since been authorized and attempted; its actual local essay gate is blocked by a structured-output grammar failure before section1. Stop before Phase7. Missing a dependent gate requires repair before further dependent implementation. The original schedule is a target, not a delivery guarantee; preserve mandatory work and drop optional polish first.
