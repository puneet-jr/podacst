# Phase 12 bounded candidate repair — 8 November 2026

**NO-GO for submission. Retain the two narrow fixes; do not claim general quality acceptance.** Started from private `f89807d8db16c20e652590a6470810e5eb60b078` in isolated `/private/tmp/lenny-repair-f89807d-20261108`. Tested runtime commit **`3dc814552104edc83072503811c56dbe452e9552`** contains only two backend files and their focused tests. A later documentation-only seal is identified by the external `release-revision.json` receipt and the publication manifest. No normal-checkout code replacement, push, deployment, upload or submission.

## Diagnosis, red tests and retained changes

**Follow-up:** Replayed the actual saved failed S1 snapshot (`53054eb0-beee-5be4-b2f1-99ca9b2eac2d`, text SHA `bbca0600f25b06c3861b687b42517e587ba3bab30ec044c7ca10b300faeec38f`) offline. This reproduces the per-passage loss; other retrieved passages/rankings were not invented. The answer-bearing next-cohort sentence existed in the passage. Matches on “for” and “they” gave earlier irrelevant spans equal scores, with earlier offsets breaking ties. Overlapping sentence pairs also consumed both slots.

Removed only those two function-word matches and select non-overlapping spans. No named-entity, numeric-result or scenario-specific rule. Limits remain **two excerpts/passage,500 characters/excerpt,6,000 UTF-8 bytes/packet**; original IDs, absolute source offsets and the single-ID model contract remain. Retrieval ranking, source/vector data,4,096 model context,128 chat output,model/provider and timeout settings are unchanged. Replay now contains the answer,**408 bytes versus659**,all offsets exact. This narrow correction does not solve every multi-part answer or abstention failure.

**Essay:** The failed Phase 11 raw review showed a selected prefix ending inside a direct quoted question. Sentence-final punctuation alone was not a complete quotation boundary. Added a balanced straight/curly double-quotation guard when choosing the existing20–130-word source prefix. It backs off to a complete verbatim prefix; no source words or citation mappings are rewritten. Apostrophes remain contractions. Fact/section/advice budgets remain unchanged.

The same saved essay sources replayed offline: **one open factual quotation → zero**,six sections,ten exact facts. This is a syntax guard,not grammar,entailment or relevance certification. The incomplete95% transcription still passes punctuation/quote syntax and remains a known unresolved defect; no special LogMeIn rule was added.

Three new assertions failed on baseline (outcome missing,overlapping slots,open quotation); the other two new preservation tests passed. A loopback socket test also initially hit sandbox permission; corrected execution scope,not app logic. Final focused **18/18** pass. [Before/after replay and real tests](agent-transcripts/phase-12-repair/command-ledger.md).

## Isolated full-index preparation

New project `lenny_phase12_repair`,fresh retained `pgdata`/`chat_traces` volumes; web **18081**,API **18001**,PostgreSQL **55434**,database `lenny_repair_phase12`. Bootstrap11.113s. No original service stopped/restarted; no old volume/database reset.

A consistent read-only `pg_dump` copied only knowledge tables into the empty migrated repair DB: episodes,episode_versions,chunks,knowledge_config,ingestion_runs,ingestion_items. **303 episodes/12,770 passages;zero saved sessions copied**. Private dump210,904,287 bytes,operation33.191s. Refreshed statistics only in the new DB using `ANALYZE` (2.276s); no ranking/deadline/source changes. Full row/vector integrity comparison and normal preservation receipts are separate. Raw SQL/source payload stays ignored,never in the publication tree.

Apple M2/8GiB;free disk103,082,541,056 bytes and swap13,220MiB in use at preflight. Existing Ollama0.30.11,Pi1.5.0,qwen3:0.6b/qwen3:1.7b,Nomic768 reused. API confirms host Ollama reachable,index identity compatible. No model downloads;high swap and the additional isolated stack limit latency comparisons. Readiness establishes dependencies,not product quality (`product_ready=false` remains honest).

## Exactly one real demo pair

Fresh UI session,Sean Ellis scope,**hybrid**,full copied index. Browser/API/run traces agree on **Pi → local Ollama,qwen3:0.6b**. No retries/cloud fallback.

| Exact prompt | Result | UI elapsed | Evidence |
| --- | --- | --- | --- |
| How did Sean Ellis change onboarding at Lookout? | **PASS:** antivirus-first setup and protected confirmation directly answer the question. | **6.422s** | S1 →53054eb0-beee-5be4-b2f1-99ca9b2eac2d,exact supported source quote. |
| What did they report for the next cohort in the must-have survey? | **PASS:** next cohort40% “very disappointed” wording preserved. | **5.185s** | Same S1 passage;answer-bearing sentence included in packet and selected as E1. |

Both citations opened their actual stored passages;heading focus and return passed. Follow-up retains the first user message and performs fresh retrieval;Pi sessions differ,processes reaped/bridges closed. No measured Lookout engagement/conversion improvement is claimed. This is **two narrow chat checks**,not a new five-scenario score. [Actual support/trace review](agent-transcripts/phase-12-repair/local-live-review.json).

## Exactly one fresh essay, scored as generated

Standard endpoint,Pi → **local qwen3:1.7b**;original Phase 11 topic,audience,constraints,source scope and limits. Fresh essay-only session avoids prior chat history;the earlier Phase 11 essay had preceding chat context,and its index had3 episodes. Those differences are disclosed;offline source replay provides the controlled quotation-defect comparison.

Topic: **Use must-have customer feedback to improve onboarding and speed to value for a new growth PM.**

**47.755s,1,145 words,six sections,five bullets,one bold span,six cited IDs/ten directly attached exact source blocks.** Six fresh Pi advice stages,zero initial messages,all reaped;**zero automatic length repairs,zero manual edits,not accepted**. The historical **1,208-word essay remains a separate reviewed result with nine manual edits**,unchanged.

| Original rubric area | Actual generated result |
| --- | --- |
| Approximately1,250 words | PASS under our operational1,125–1,375 range;1,145. The numerical band is our interpretation,not a company-set threshold. |
| Headings,bullets,selective bold | Present:6/5/1. |
| Useful topic hook | FAIL:feature-request/innovation opening drifts from must-have feedback;asserts an invented finding. |
| Logical progression/readability | FAIL:repeats real-time-feedback experiments across sections;labels/headings do not create a coherent feedback-to-onboarding argument. |
| Complete supported factual claims | FAIL:unfinished LogMeIn95% statistic survives;“we find a correlation” invents a reviewed-data finding. |
| Applications and sound interpretation | FAIL:DAU increases are treated as proof of effectiveness/retention;proxy thresholds are said to validate engagement and suggest churn improvement without sufficient support. |
| Useful final takeaway | FAIL:repeats earlier advice and recommends implementation from proxy thresholds. |
| Citation identity/placement | PASS all6 IDs resolve;10/10 spans/hashes/attachments exact. This does not repair incomplete meaning. |
| Overall | **FAIL as generated.** No editorial rescue or second draft. |

Proposed15%/20% thresholds and explicit hypotheses are **not historical measured claims**. There is no invented historical Lookout engagement/conversion improvement. The unsupported observational statement and invalid proxy conclusions are separately recorded. Ten factual blocks and each advice sentence were reviewed;[claim-by-claim rubric review](agent-transcripts/phase-12-repair/essay-review.json).

Raw output preserved at `.cache/phase12-repair/essay/raw.md` and `raw.json`,sources separately private. Markdown SHA `67b7b01f3c3baeb484c2667aeb4d791faca4b794b51b514811637558a7242f14`. UI opens all six source groups at1440/390,focus/return works,no horizontal overflow or console/page errors;Accept remains disabled. No fresh essay artifact was presented as an accepted/reviewed result.

## Affected verification and preservation

- Backend **125/125** pass,33.660s suite/40.803s command,retained isolated `lenny_contract_60ff34975175`. Real PostgreSQL and local synthetic embeddings;generation/process mocks explicitly separate. Initial red tests preserved.
- Focused **18/18** pass;Node Pi/provider/Markdown policies **10/10** pass. No frontend source changes;production web build reused unchanged verified cache during bootstrap. This is not a new standalone frontend regression claim.
- Live UI2/2 chat support checks and raw-essay/source viewer checks pass in their stated scopes. Fresh essay **fails semantic rubric**,not hidden by deterministic success.
- Original normal database full-row audit passes:all **73 sessions,181 messages,14 essays,17 artifacts**,associations and **303/12,770** index/vector rows unchanged. Original `f89807d` checkout remains clean;root Git index remains empty.
- All **723 prior publication files** and archive checksum unchanged;both0/5 results,raw essay and retrieval-timeout trace retain prior hashes. New publication uses a distinct directory/archive.
- Initial copied-index integrity helper hit the unchanged3s statement timeout serializing all full episode versions in one query. Corrected only that diagnostic to paginate10 versions;application deadlines unchanged. First failure preserved. Corrected audit passed in11.576s:all12,770 complete chunk/vector rows,303 episode/version rows and knowledge/ingestion identities match original full-row hashes. [Integrity receipt](agent-transcripts/phase-12-repair/index-copy-verification.json).

[Exact command ledger](agent-transcripts/phase-12-repair/command-ledger.md) retains actual UTC,cwd,exit,durations. Full protocol/source/model payloads remain private;safe IDs/hash/timing/claim reviews publish separately. Historical Phase 12 report/checklist remain unchanged as historical evidence.

## Assignment requirements and proposed targets

**Passed in this bounded rerun:** actual FastAPI/Pi/local Ollama operation;the exact grounded question and useful follow-up with retained context and fresh retrieval;citation mapping and source inspection;bounded cleanup;fixed open-quotation selection;isolated PostgreSQL regression and preserved source/index identity.

**Still blocked explicit requirements:** useful grounded essay as generated (this actual draft fails);general useful answers/unsupported behavior are not established by a two-question pass;complete public source/coding-conversation export/camera-enabled video and submission/access deliverables remain incomplete. Reviewed/editable essay capability is distinct from autonomous quality. Current-candidate cloud walkthrough remains **blocked by unavailable credits**;zero cloud requests/keys copied. Historical verified OpenRouter integration remains preserved,not re-proved.

**Proposed target,not a company threshold:** original frozen scenarios **0/5**,bounded rerun **0/5**,proposed **4/5**. No new frozen five-case batch or score in this task. Recall tuning56.25%/observed held-out81.25% versus proposed85% remains historical;retrieval ranking unchanged,so no new tuning/hold-out claim.

Retain the two narrow fixes and regenerate a sanitized tree from the final private candidate. Next required work is evidence-unit completeness and factual/advice support,then a fresh raw-essay rubric gate and independent broader answer/abstention acceptance. Do not use the reviewed nine-edit essay or this successful pair to declare those gates passed. **Stop with NO-GO for the exact sealed candidate.** No further generation attempt,cloud request or publication in this task.
