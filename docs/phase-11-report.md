# Phase11 — isolated README rehearsal,8 November2026

**Clean local setup,persistence and rendering passed after one helper correction. Complete product acceptance remains blocked.** Original Phase10 **0/5**,bounded pass **0/5**,proposed target **4/5**. A setup rehearsal is not a new scenario score or an autonomous essay pass. No public push,video,upload or submission.

## Selected source and experiment separation

The normal checkout remains dirty at HEAD `363025918b9ab53db6295b8d190ed23c58d1eaea`;its bounded experiment and all previous work remain intact. Candidate preparation reversed only recorded bounded changes **in an isolated copy**. All41 saved pre-experiment Phase10 source hashes match exactly,including UI polish,full-index support and verified OpenRouter payload fix. The old image was unavailable;the hash comparison,not an invented image recovery,is the proof.

[Selection receipt](agent-transcripts/phase-11/baseline-selection.json) identifies restored files/exclusions. Experiment archive `.cache/phase11/bounded-pass` and hashed `.cache/phase11/bounded-pass.patch` retain the changed code/tests. Bounded raw1216-word essay and retrieval-timeout trace remain at their original paths;both0/5 result files remain unchanged. Experimental multi-excerpt selection,typed-error code and timeout-copy regression were excluded from the candidate. No blanket reset,root product-file restore,root commit or normal-service restart.

A complete **private local Git snapshot** was cloned with `--no-hardlinks` to `/private/tmp/lenny-evaluator`;this is not a claim that the incomplete public repository already builds. Initial source/docs revision `26a5e1e67616f4c8a92f7186a33e93a50a2dec9d` ran startup/build/tests/generation. Exact corrected helper/reopen revision **`9c8c903a8e70336885660683dfa8b9c37cc5e1d8`** changes only the new smoke helper’s readiness polling. All41 baseline runtime hashes remain unchanged. A later documentation-only seal,if present,is identified in the external release-revision receipt;no later runtime/inference result is implied.

## README-only execution and resources

Commands were executed from the clean clone using the README,with capture wrappers recording actual command/cwd/UTC/exit/duration. [Exact ledger](agent-transcripts/phase-11/command-ledger.md). Browser automation performs the documented UI actions;preservation audits are separate read-only engineering checks,not hidden setup workarounds.

- Project `lenny_phase11_eval`;fresh `lenny_phase11_eval_pgdata` and `lenny_phase11_eval_chat_traces` volumes. Availability checked before creation.
- Loopback web18080/API18000/DB55433;database `lenny_rehearsal_phase11`. Normal8080/8000/55432 and existing host5432 untouched.
- New ignored mode0600.env generated locally;no normal credential copied. Explicit Ollama/default and empty cloud-key overrides. No cloud requests or model downloads.
- Existing Mac models reused:Ollama0.30.11,qwen3:0.6b chat/qwen3:1.7b advice,Nomic768. Pi1.5.0 installed from the lockfile inside API. Source cache linked before bootstrap and mounted read-only;all303 pinned source hashes verified.
- Apple M2/8GiB,free disk103901798400 bytes,swap13093.31MiB in use at preflight. Base images/dependencies/models/cache already present:these are **fresh-volume cached setup measurements,not cold-machine/download timings**.

| Command/result | Actual evidence |
| --- | --- |
| `python3 scripts/bootstrap.py` with README isolation environment | PASS9.738s;new project/network/volumes;no normal data copied/reset |
| Explicit `python -m backend.migrate` | PASS1.835s,idempotent0005;entrypoint also migrates |
| Readiness before ingestion |200 foundation ready,corpus empty0/0,product_ready=false;not falsely called grounded readiness |
| README pinned-cache verifier |303 source hashes/Git revision match;no fetch/download |
| Three-source ingestion,sean-ellis/shreyas-doshi/shreyas-doshi-live,batch4/deadline900 |3 loaded,0 skipped,0 failed;**3/303 episodes,112 passages**,25.601s operation/27.488s command |
| `npm ci --prefix frontend --ignore-scripts --no-audit --no-fund` | PASS71 packages,2.216s |
| Frontend typecheck/build | PASS5.124s/7.969s;Docker production build also succeeds |
| Frontend source-span tests /Node provider/conversation/Markdown policies |2/2 and10/10 pass,0 fail/skip;provider tests are mocks |
| README contract suite |**120/120 pass**,19.733s suite/25.477s command;fresh retained isolated contract DB;real PG/synthetic Nomic plus explicit model/process mocks |
| README local smoke |2 chat operations+one raw essay workflow,59.473s total;raw/private outputs preserved |
| README API/web restart and `--reopen` | Initial helper failure preserved;corrected rerun PASS7 exact saved API objects,4.100s reopen |
| Actual Chrome157 at1440/390 | Homepage/example/home route,session-field focus,composer/model disclosure,2 citation focus/returns,both previews,raw essay visibility,no horizontal overflow/page/console errors;no browser inference |

The small rehearsal index is deliberate setup coverage. It is not the normal303-episode database,a full-corpus ingestion rerun,retrieval benchmark or new5-case exercise. Full-index hybrid historical Recall@8 remains56.25% tuning16/81.25% observed holdout8 versus85% target;no retuning or misleading small-index metric comparison.

## Actual local answer and essay review

[Detailed source/claim review](agent-transcripts/phase-11/live-review.json),[safe IDs/timings/reopen/browser results](agent-transcripts/phase-11/rehearsal-results.json).

| Request | Measured result / support |
| --- | --- |
| What does Sean Ellis ask in the must-have survey? |6.837s;S1→9d370308-1dd5-5657-bdf5-f159a62ce159. Exact supported quote,but it is the **feature-level adaptation in the Nubank discussion**,not the requested general product wording. Partial relevance;not a complete-answer pass. |
| How did they change onboarding at Lookout? |5.033s;same session/prior-user context,fresh different S2→53054eb0-beee-5be4-b2f1-99ca9b2eac2d. Passage explicitly describes antivirus setup first and “protected” message. Supported;no measured engagement/conversion improvement inferred. |
| Raw evidence-first essay |qwen3:1.7b,46.650s,1098 words before one automatic length repair,**1157 final words**,6 sections,8 bullets,1 bold span,6 valid cited IDs/9 exact factual blocks. Seven fresh advice stages reaped;0 manual edits,not accepted. |

The raw1157-word essay **fails the full rubric** despite deterministic length/IDs passing:an unfinished LogMeIn95% statistic,open-ended quote,weak progression/repeated experiments,and claims that DAU/session proxies support/refute retention are not established causal/retention evidence. No invented measured Lookout engagement/conversion outcome appears,but that does not make the advice/readability acceptable. Raw output: `/private/tmp/lenny-evaluator/.cache/readme-smoke/essay-raw.md`. No second essay or claim-hiding edit was made.

Markdown/HTML exports in this rehearsal format the supported follow-up reply;they are **not exports of an accepted generated essay**. Both save/API reopen/browser previews and citation associations pass after restart. The raw essay/sections/sources also reopen,without being autoapproved.

Separately,the normal stack’s historical **reviewed1208-word essay after9 edits** reopened read-only in both formats;[receipt](agent-transcripts/phase-11/reviewed-essay-reopen.json). It was not imported into the fresh DB or mislabelled new generation. This preserves the distinction between reviewed results and raw drafts.

## Setup gaps and corrections

1. Known public-source gap:the last published snapshot omits runtime prerequisites. Rehearsed a complete private candidate revision;public checkout reproducibility remains blocked until a separately authorized complete publication.
2. Before launch,README review identified cache-ordering and startup-readiness gaps. Documented cache link before bootstrap and bounded curl polling. Bootstrap’s fixed8080 banner does not reflect custom ports;README explicitly says18080. No hidden manual code patch in the evaluator clone.
3. Actual first restart helper failed on `http.client.RemoteDisconnected` while the API was coming up. Raw failure retained. Added that transient class/connection errors to bounded30s polling,then committed only the helper in the private source and fast-forwarded the clean clone. Repeated idle restart/reopen passed;no model call repeated or data replaced.
4. Starlette/httpx deprecation and psycopg ResourceWarning remain nonfatal;not suppressed or fixed by dependency churn.

## Documentation and deliverable audit

README,PRD,assumptions/risks,scenarios,design,architecture,handoff,test plan and29-ID requirement register now describe the selected candidate and actual limits. The original frozen scenario definition is retained verbatim beneath added results;original freeze hashes remain recorded. The opening discovery brief explicitly connects practitioner pain to evidence inspection/local trade-offs,reasoned exclusions and proposed versus measured targets. No external-client approval or user-study claim.

All assessment Section5 concerns map to OPS/API/DB/agent/model/source/rendering requirements:practical startup/config,safe keys/logs,missing key/Ollama/model timeout/empty retrieval/database failure,recovery and extension handoff. Existing isolated contract cases exercise those failure categories;native real-model cancel behavior is not inferred from mock processes.

Eight deliverables:complete local source snapshot exists but public repo is incomplete;README/PRD/design/architecture/manual test plan are reconciled;genuine command logs include failures/corrections but complete sanitized conversation export remains unavailable;camera-enabled2–3minute YouTube demo is unrecorded/unuploaded. Source rights,current deadline/form confirmation,evaluator access and submission receipt remain candidate actions.

## Preservation and next boundary

Read-only row-hash audits before/after pass:all normal **73 sessions,181 messages,14 essays,17 artifacts**,source associations,runs and all303 episodes/12770 complete chunk/vector rows unchanged. [Preservation receipt](agent-transcripts/phase-11/normal-preservation.json). Normal product files,UI styles/brand/resizer,OpenRouter integration,.env and both0/5 raw runs remain preserved. Only docs/new README helpers were added in the normal checkout;no root staging/commit or public push.

Review the isolated candidate at **http://localhost:18080/** and **/workspace**. Its source checkout is `/private/tmp/lenny-evaluator`;the normal8080 stack still contains the quarantined experiment. Volumes are retained,not removed.

**Stop after rehearsal.** Before Prompt12 release work:resolve mandatory answer/abstention/essay-quality blockers and full-index timeout risk;choose the complete reviewed publication tree while keeping experiment separate;retain both0/5 scores and manual-edit disclosures. Then prepare the real local camera demo/trade-off narrative and verify repository/video/form/deadline/access/receipt with separate authorization for publication/submission. Setup success alone is not a release recommendation.

Final hygiene before documentation seal:821 candidate/new evidence/stream files checked against4 configured secret values and common credential patterns,0 findings;14 archived experiment files and170 original raw-evidence files unchanged. Both0/5 score receipts,bounded raw essay and timeout trace separately hashed. Frozen scenario definition retained verbatim;root index empty and diff check passes. [Scope/result](agent-transcripts/phase-11/hygiene.json).
