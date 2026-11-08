# Requirement and deliverable register —8 November2026

This register reconciles implementation with the private-assignment audit in [assessment-audit.md](assessment-audit.md). Proposed4/5/85% targets are ours;mandatory requirements are not waived. Setup rehearsal does not turn failed quality into acceptance. Selected candidate matches41 pre-experiment source hashes and preserves the OpenRouter fix;bounded changes remain separate.

| ID | Acceptance criterion | Current status | Actual evidence / limitation |
| --- | --- | --- | --- |
| FD-01 | Opening PRD discovery before implementation: user/job/pain, predefined measurable metric, assumption register, reasoned scope and verified risk/trade-off register | implemented;discovery reconciled | PRD retains user/job/pain,proposed4/5,assumptions,scope and trade-offs;actual0/5 twice;not client interviews. |
| API-01 | FastAPI backend; validated requests/responses, structured errors, health endpoints | verified within contract scope | 120 baseline contracts plus typed endpoints;fresh README rehearsal separately recorded. |
| AG-01 | Meaningful use of Claude Agent SDK or Pi Coding Agent | verified bounded integration | Pi actually executes controlled retrieval;guided textual-call normalization still sometimes required;autonomous routing unproved. |
| SES-01 | New independent chats with follow-up context | verified storage/context scopes | Same-session prior-user context,fresh retrieval,independent histories/restart;semantic usefulness still fails broad tasks. |
| DB-01 | PostgreSQL conversations, IDs, timestamps and user metadata | verified | Real PostgreSQL,migrations0005,UTC/user metadata/atomic retry/citation persistence;not production auth. |
| MOD-01 | At least one cloud provider integrated | verified one OpenRouter chat case | Pi/OpenRouter google/gemini-2.5-flash-lite cited smoke6.513s;source support reviewed. Anthropic config/mocks only. |
| MOD-02 | Actual demo runs with Ollama on a suitable local model | implemented;recorded demo pending | Actual local questions/essay attempts use Ollama;quality failures retained. No recorded demo/YouTube proof. |
| MOD-03 | Config-based provider switch, visible selection and no implicit fallback | verified configuration/UI disclosure | Explicit server config/recreate,selected model/privacy,no automatic fallback;no interactive picker. |
| KB-01 | Load source transcripts; document parsing, chunking, indexing and refresh | verified full pinned index | 303/303 episodes,12770 passages,source/model identity/idempotency/preservation;normal index untouched by rehearsal. |
| KB-02 | Trace relevant evidence to original transcripts | verified traceability;meaning limited | Owned immutable original passages/exact spans,source links/browser inspection;valid IDs do not guarantee entailment/completeness. |
| RAG-01 | Product/growth answers strictly grounded in transcripts; useful follow-ups; unsupported requests acknowledged | blocked quality acceptance | Original0/5,bounded0/5;13 answerable reviews4 adequate,unsupported1/4 via policy. Hybrid56.25% tuning/81.25% observed holdout below85%. |
| ESS-01 | Dedicated guide-grounded Ship30 workflow | implemented | Dedicated evidence-first/Ship30 workflow,review/edit gates,bounded local advice;automatic narrative/source judgment weak. |
| ESS-02 | Approximately1250 words, useful structure, grounded claims and takeaway | verified assisted only;raw quality blocked | Historical1208-word essay required9 edits. Raw1216-word drafts fail full rubric despite1125–1375 length/citation checks. |
| ART-01 | Markdown and complete HTML/CSS artifacts from current conversation | verified static export scope | Owned accepted reply→Markdown and complete static HTML/CSS with sources;no inference during formatting. |
| ART-02 | Render beside chat within app | verified stated browser scope | Actual Chrome desktop/mobile viewer and restart/reopen;fixtures separate from live. |
| ART-03 | Untrusted HTML isolation/sanitization and permissions | verified stated security scope | Sanitizer/CSP/opaque iframe hostile fixtures;not universal browser/security certification. |
| OPS-01 | Practical one-command startup | implemented;Phase11 rehearsal recorded separately | README complete-candidate clean checkout/fresh volumes;normal data preserved;cold model/image download not benchmarked. |
| OPS-02 | Safe configuration and secrets | verified within bounded scans | Server-only keys,ignored.env/private traces,no secret publication;exact/pattern scans not universal assurance. |
| OPS-03 | Safe structured diagnostics | verified baseline safe-event scope | Correlation/codes/durations/source IDs;baseline may collapse tool failures into RPC error. Experimental richer typing quarantined. |
| OPS-04 | Failure and recovery | verified isolated test scopes | Real DB/refused endpoints and real mock-process cancel/timeout/disconnect;restart separately;no normal outage. |
| OPS-05 | Run/test/troubleshoot/extend handoff | implemented/reconciled | README/handoff explain setup,refresh,diagnostics/extensions/provider/migrations;Phase11 lists exact setup gaps. |
| DEL-01 | Source repository with complete current project structure | incomplete publication | Local complete candidate snapshot exact revision in Phase11;previous public snapshot omits prerequisites. No new push. |
| DEL-02 | Complete README | reconciled;rehearsal scoped | README is executable contract;Phase11 reports actual pass/fail and fresh-source limitations. |
| DEL-03 | Complete PRD | reconciled | Opening five-part discovery retained;measured metric failures and user-impact trade-offs explicit. |
| DEL-04 | design.md with principles, IA, states, responsive/accessibility decisions | reconciled | Current editorial layouts/focus/resizing/mobile/renderer boundaries and actual verification limits. |
| DEL-05 | architecture.md with schema/API/boundaries/ingestion/routing/models/security/topology | reconciled | Current0005 schema,APIs,Pi/provider/security/index/essay/artifact topology;experiment excluded. |
| DEL-06 | Dedicated sanitized agent transcripts, including genuine failed attempts and corrections | partial | Genuine sanitized command metadata/reports/failures retained;complete sanitized coding conversation export unavailable. |
| DEL-07 | Meaningful API/retrieval/routing/persistence tests and manual UI plan | verified stated scopes;quality blocked | 120 baseline contracts,frontend/Node/metric/browser checks plus actual local evidence;not all tests are inference. |
| DEL-08 | 2-3 minute camera-enabled YouTube demo: problem, product, actual local Ollama, one trade-off | pending | No2–3minute camera-enabled YouTube recording/access verification;separate candidate action. |

Section5 engineering concerns map to OPS01–05 and API/AG/SES/DB/KB/RAG/ESS/ART/MOD rows:practical setup/config,framework integration,source integrity,history/recovery,controlled tools,secrets,unsafe rendering,diagnostics,tests and extension handoff. Exact environment/revision/commands are in [Phase11 report](phase-11-report.md). The original and bounded five-case scores are both0/5;release quality is blocked. Public repo completeness,rights,full coding export,camera video/upload/evaluator access,deadline/form confirmation and submission receipt remain candidate actions. No confidential PDF is included in source.


## Phase12 bounded repair verification

RAG01/SES01/KB02:exact narrow live pair now passes with fresh retrieval/context and supported citations;general/multi-part/unsupported acceptance remains blocked. ESS02:open-quote selection fixed,but fresh1145-word/zero-edit essay fails full semantic/readability rubric. MOD01 current-candidate walkthrough remains credit-blocked;historical OpenRouter smoke separate. Both0/5 scores versus proposed4/5 remain historical,not rerun. Normal303/12770/saved work and old publication package unchanged. See [repair report](phase-12-repair-report.md),[current checklist](submission-checklist-repair.md).
