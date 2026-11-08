# Phase10 — full corpus, quality and release regression

**Verdict: full-corpus ingestion PASSED; Phase10 release/quality gate FAILED and remains open.** Five frozen first-attempt scenarios scored **0/5** against the proposed **4/5** target. Separate post-fix C/E reruns both still fail the full requested meaning/rubric. No Prompt11 work, commits or pushes. No cloud inference, model downloads, database resets or normal database/dependency outage.

This is direct engineering verification by Codex, not a user study or independent review. Baseline: [7 November regression](regression-2026-11-07.md). Work ran in the existing dirty checkout at Git HEAD `363025918b9ab53db6295b8d190ed23c58d1eaea`; the dirty working tree, not origin/main, is the tested candidate. [Latest source hashes](agent-transcripts/phase-10/release-state-latest.json) and a final running-API comparison cover27 backend/agent files with zero mismatches. The first source-hash manifest was overwritten by a later readiness helper; the misleading filename was corrected to `release-after-query-fix.json`. Do not treat it as a retained pre-scenario source snapshot. Commands/image identities and original UI/frozen-input hashes remain recorded.

## Corpus and preservation

Pinned source checkout and all303 manifest byte hashes match revision `be8ab89a890a833cbba2c892178f823fff178c65`. Before ingesting, parsed every episode:0 parse failures,12770 expected passages, maximum78 passages/episode. Existing index9 episodes/373 passages. Existing Nomic embedding identity/digest,768 dimensions and document prefix were verified compatible before writing.

One resumable writer, batch4, one embedding request in flight;20s/call, at most3 finite attempts,180s/episode,3600s/run. No source was re-fetched. Commands include the capture prefix:

```sh
python3 scripts/capture_phase10.py python3 scripts/docker.py compose exec -T api python -m backend.ingest --root /corpus/be8ab89a890a833cbba2c892178f823fff178c65 --batch-size 4 --deadline-seconds 3600
```

| Actual run | Discovered / selected | Loaded | Skipped | Failed / deleted / unattempted | Operation / full command |
| --- | --- | ---: | ---: | --- | --- |
| First, `55813c77-9bc4-4c7d-8c3f-17a52b5ce196` | 303 /303 | 294 | 9 | 0 /0 /0 | 2635.389s /2640.056s |
| Identical repeat, `9d07a94a-19b5-49f8-a07c-fd4bc1a46f44` | 303 /303 | 0 | 303 | 0 /0 /0 | 1.626s /3.506s |

Final **303/303 active episodes,12770 active/total passages,303 episode versions,0 duplicate active ordinals**. All12770 active passages were checked against original character spans, current versions, source/manifest hashes, embedding digest/model/dimensions and revision, with0 failures. Source timestamp warnings were retained rather than invented/corrected timestamps. Both after-ingestion and repeat audits preserve the original9 episodes and373 complete chunk/vector hashes.

Original saved records remain present and byte-equivalent by per-row hashes:1 user,42 sessions,108 messages,49 answer sources,11 essay runs,68 essay sources,6 artifacts and48 answer runs. Dedicated Phase10 sessions increased totals to67 sessions,165 messages,13 essays,12 artifacts and76 answer runs; no old records were edited. Aggregate table hashes therefore differ after live tests, while the original-row subset proof passes. Host PostgreSQL5432 was untouched; Compose database55432 and existing volumes remain intact.

[Actual ingestion results](agent-transcripts/phase-10/ingestion-results.json) · [Preservation audit](agent-transcripts/phase-10/preservation.json). Ingestion is complete. If a later refresh stops, the exact same command above is the resume command: committed unchanged episodes skip; incomplete episodes retry transactionally. Do not reset the database.

## Actual hardware, versions and bounded local inference

Apple M2,8589934592 bytes RAM (8GiB). Free disk106380193792 bytes before versus104101183488 after (~99.07→96.95GiB). Swap already heavily used before:11690.56MiB of12288MiB; after13118.88MiB of14336MiB. These are host observations, not an isolated model memory benchmark. Serial service/model operation fits sufficiently for these tests, but memory pressure remains a latency/reliability risk. No larger model was downloaded.

Pi1.5.0, Ollama0.30.11, PostgreSQL16.15, pgvector0.8.7, migration0005. [Installed model identities](agent-transcripts/phase-10/models.json):

- Chat: `qwen3:0.6b`, digest `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435`,522653767bytes,Q4_K_M; installed metadata reports751.63M parameters.
- Essay advice: `qwen3:1.7b`, digest `8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7`,1359293444bytes,Q4_K_M; metadata reports2.0B parameters. Model tag and metadata are reported separately.
- Embedding: `nomic-embed-text:latest`, digest `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`,274302450bytes,F16,768dimensions.

FastAPI→fresh Pi→host Ollama; local provider explicitly verified, no automatic fallback. Chat:4096 context,128 output tokens, at most2 provider turns/one narrow read-only retrieval operation,90s request bound in this run. Advice:4000-byte prompt bound,384 output tokens,one provider request per fresh session,90s/stage,600s essay maximum,one bounded length repair. Server owns factual text/citations. No default shell, filesystem or web tools. Safe tool trace and usage/lifecycle metadata are in [answer review](agent-transcripts/phase-10/answer-review.json); raw protocol/diagnostics remain private and separate.

The17-answer sample measured5.304–15.442s HTTP requests,median6.827s,p95 nearest-rank15.442s. Retrieval timing is separately recorded per request; remaining lifecycle time includes Pi startup, selection and cleanup and is **not** a pure model-generation benchmark. Both essays below include individual advice-stage timings and retrieval receipts privately. Full ingestion is measured separately; cold setup was not rerun.

## Retrieval evaluation

Exact frozen `eval/retrieval-cases.json` and `eval/retrieval-local-v3.json` hashes unchanged.16 tuning,8 previously observed held-out,4 unsupported questions ×3 modes =**84 successful retrieval requests** on actual PostgreSQL/local Nomic, all source-integrity checks passed. Limits unchanged:20 candidates,limit8,3200tokens,6/episode,1-hop neighbors (max2),RRF60,sponsors retained with warnings. Actual returned counts usually5–6 because of budgets.

Gold judgments were authored on nine source episodes; the retrieval index for every Phase10 measurement is303 episodes/12770 passages. The evaluator retains that historical scope annotation; it does not mean current retrieval is limited to nine episodes. Observed holdout is a rerun, not an unseen benchmark or random full-corpus quality sample. `report.passed=true` means evaluation execution/source integrity, not the85% relevance target.

| Split / mode | Recall@8 | MRR@8 | nDCG@8 | Median / p95 ms |
| --- | ---: | ---: | ---: | --- |
| Tuning16 / sparse | 53.125% | .3896 | .4074 | 307.8 /3095.2 |
| Tuning16 / dense | 43.75% | .2469 | .2924 | 290.1 /1768.8 |
| Tuning16 / hybrid | 56.25% | .3198 | .3800 | 707.3 /2352.0 |
| Held-out8 / sparse | 62.5% | .5625 | .5789 | 233.9 /1180.0 |
| Held-out8 / dense | 68.75% | .6500 | .6250 | 230.5 /792.9 |
| Held-out8 / hybrid | 81.25% | .6500 | .6577 | 529.9 /1575.8 |

**85% Recall@8 target missed in every split/mode.** Anchor recall happens to equal passage recall here; it is not substituted for it. Hybrid scoped recall83.33% tuning/100% held-out versus unscoped40%/62.5%; performance degrades on broad queries as the corpus expands. No post-holdout label/config tuning. Unsupported retrieval returns5 loosely related passages/case in all modes; nonempty search is not evidence of support. [Measured summaries](agent-transcripts/phase-10/retrieval-evaluation-summary.json).

The initial full-index sparse T01 query exceeded the existing3s PostgreSQL statement timeout and produced no valid metric batch. A first materialization-only probe also failed. The focused fix precomputes each term’s tsquery, corpus count and document frequency once per statement; rank formula/filter/tiebreak/budgets remain unchanged. Read-only T01 probe then completed1.363s; a separate diagnostic JIT-off probe0.811s was **not** applied to product settings. A real PostgreSQL regression compares old/new rankings and exact scores over four synthetic queries. Explicit materialization is consistent with [PostgreSQL16 CTE documentation](https://www.postgresql.org/docs/16/queries-with.html#QUERIES-WITH-CTE-MATERIALIZATION). No universal latency guarantee or historical SC-E root-cause proof follows from this improvement.

## Frozen scenarios

Inputs and caps frozen before generation; hash `40f37d0690c4e6d7963c27343c1b31293aa47c71f8936b058b646ac32d5511ce`. Durations below include operator evidence/browser review, distinct from request latency. Full requested meaning, factual support, relevant artifact save/render/reopen and duration must all pass. Partial quotes do not pass. No actual external participants.

| First attempt | Requests / essay | Task / cap seconds | Actual result |
| --- | --- | --- | --- |
| A | 7.595s | 159.841 /240 | FAIL: generic must-have advice; omits survey question and use of responses. Exact citation and Markdown save/render/reopen pass. |
| B | 17.174s +9.009s | 126.481 /360 | FAIL: leverage-only initial answer; unrelated procrastination follow-up rather than bug-triage advice/checklist. Correct same-session context and fresh passage. HTML renders/reopens but lacks requested content. |
| C | 6.520s +42.387s essay | 482.151 /900 | FAIL: raw1275 words/six sections/valid citations, but invented Lookout outcomes in advice, weak source selections and readability. No acceptance/artifact created from a failed essay. |
| D | 9.004s +7.156s | 147.330 /360 | FAIL: incomplete survey answer and omitted listening resources. Independent histories/marker exclusion and8 saved API objects after idle API restart pass; saved browser/artifacts later pass. |
| E | failed8.940s +8.372s | 1391.918 /240 | FAIL: initial `rpc_rejected` gives no gap response; reformulation omits survey question. Saved supported artifact later renders/reopens. Operator task cap exceeded. |

**First-attempt numerator0/denominator5; target4/5 missed.** D/E browser results arrived after their first timed review and do not retroactively convert the score. One early D review note claimed browser completion prematurely; its correction is explicitly appended in the original review JSONL. A corrected helper awaited completed session selection before source focus checks. A full-text locator failed on A’s rendered Markdown; helper now identifies the correct assistant row.

One E browser launch had378.7s UTC interval versus9.483s monotonic command duration and a launch timeout. This clock gap/host suspension anomaly is observed, not diagnosed. The long E operator task is not app latency. Subsequent bounded launches and saved-output browser checks recovered without new inference; no claim about a physical phone keyboard.

Separate post-fix reruns:

- **C:**36.386s request,**1216 words**,6 sections,8 bullets,1 bold span,all9 factual blocks exact with directly attached6 citation labels. Six fresh advice sessions had0 initial messages and were reaped. Removing topic/history/constraints from the advice prompt eliminated new historical Lookout engagement/conversion claims in this one rerun. Still **FAIL**: irrelevant Airbnb/Facebook case context, incomplete LogMeIn95% predicate, missing survey question/initial7%/six-month60% and qualifications, repeated real-time-feedback advice, poor experiment decisions/weak opening and close.0 manual edits,not accepted. Browser renders draft and all6 source groups at1440/390. [Claim review](agent-transcripts/phase-10/essay-post-fix-review.json); actual raw draft: `.cache/phase10/live/post-fix/SC-01-C/essay-raw.md`.
- **E:**13.079s unsupported +5.329s reformulation,62.613s task<240. Existing private-fact guard produces explicit gap after model chose unrelated evidence. Correct survey question appears in reformulation, but the response-investigation part is absent: **FAIL**. Citation/artifact/browser reopen pass. Earlier RPC failure did not recur; its missing captured bridge exception prevents a definitive historical cause attribution.

Post-fix C/E score0/2; no new complete five-scenario score is claimed. [Detailed scenario results](agent-transcripts/phase-10/scenario-summary.json). Old manually reviewed1208-word essay still opens with Markdown/HTML; it remains manually edited historical evidence, not an autonomous Phase10 pass.

## Direct answer/citation review

**13 completed answerable outputs** reviewed against the actual saved original passages: ten preregistered development/observed-holdout questions plus three convenience new-source cases. This meets the minimum10 direct reviews, not statistical full-corpus representation. No cloud/model reviewer was used as authority.

- **4/13** adequate requested-meaning answers: T01 survey question,T15 pre-mortem psychological safety,N02 frameworks as learning rather than process,N03 arrogant-doctor pitch.
- **9/13** incomplete/irrelevant: T04 LNO definition,T07 four stages,T09 decision-confidence explanation,T11 management answer,T13 two-guest comparison,H17 bug-report contrast,H21 specific-platform qualification,H24 full Lookout survey context,N01 generative-era uncertainty. T11 quotes the host’s question; N01 stops immediately before the answer; H24 preserves60% but loses next-cohort40% and qualifiers.
- Across13 answerable +4 unsupported,**16 quoted outputs have valid IDs, exact stored spans and supported quoted text**. That does not establish relevance/completeness or the user’s unsupported premise.
- Unsupported: **1/4** correct gap (private churn/dashboard), via existing server policy. Native tiny-model abstention **0/4**: it selected unrelated quotes for future December2026 API features,fictional Zyphor-17 formula,and a Gamma sponsorship100%-PMF guarantee. Those passages establish none of the requested facts. No fabricated formula/date/guarantee was written, but failure to acknowledge the gap still fails RAG-01.
- B’s follow-up included the correct original user question, inherited the intended Shreyas scope and retrieved a different passage. Semantic usefulness still failed. D’s sessions remained independent before/after restart.

[Per-answer support, IDs, traces and timings](agent-transcripts/phase-10/answer-review.json). Raw replies/passages remain ignored under `.cache/phase10/live/first/quality-*`. The first sampler finished T01, then readiness503 interrupted before T04 session creation; historical response body was not saved, so exact failing readiness component is unknown. Subsequent probe200. Empty failed preflight retained; resumed only16 ungenerated cases. No completed model call was repeated. Helper now saves readiness bodies and supports selecting ungenerated cases.

## Fixes and regression

Focused fixes only; original UI design/provider/essay/export changes preserved:

1. Shared source-path validation covers all303 canonical paths, including four previously rejected Unicode/underscore names, while rejecting traversal/URLs/extra separators. Three new boundary tests and real API requests to allfour paths pass.
2. Older-session pagination fixes only25 visible despite42 saved; keeps selection/drafts and loaded page depth across refresh. Actual saved-session and42-row fixture checks pass.
3. Corpus label reflects303/303 rather than hardcoded partial; partial/full fixtures pass.
4. Full-index SQL repeated work reduced as described above; numeric ranking equivalence and all84 retrieval operations pass with original deadlines.
5. Advice-only prompt no longer receives historical topic/factual constraints. Focused mock boundary test plus one real rerun prove the narrow change; full essay rubric still fails.

Protected22-file baseline check: only `frontend/src/main.tsx` changed for pagination/status; other original UI files/config and frozen scenarios/evaluation inputs unchanged. No new UI library, dependency pin, migration, provider/model selection change or citation/source editing bypass. [Boundary/code review](phase-10-code-review.md).

| Release check | Actual result |
| --- | --- |
| `npm --prefix frontend run typecheck` | PASS; final2.413s |
| `npm --prefix frontend run build` | PASS; final2.816s |
| `node --test frontend/test-source-span.mjs` | 2 pass /0 fail /0 skip |
| `node --test agent/test_provider_policy.ts agent/test_conversation_policy.ts agent/test_essay_format.ts` | 10 pass /0 fail /0 skip; provider tests are mocks,not cloud inference |
| `.venv-phase2/bin/python -m unittest discover -s eval -p test_metrics.py -v` | 3 pass /0 fail /0 skip |
| `python3 scripts/docker.py compose build api` | PASS; current post-fix image |
| `python3 scripts/docker.py compose run --rm --no-deps -e DEFAULT_PROVIDER=ollama -e OPENROUTER_API_KEY= -e ANTHROPIC_API_KEY= api python -m backend.contract_check` | **120 pass /0 fail /0 skip**,31.037s suite,42.779s full command; retained isolated `lenny_contract_47e5e4413915` |
| `.venv-phase2/bin/python .cache/phase10/release-regression.py` | PASS47.344s;16 standard fixture cases,4 Anthropic display assertions,4 OpenRouter assertions,4 resize fixture groups+1 actual saved-content group,2 pagination fixture groups |
| `.venv-phase2/bin/python .cache/phase10/home-check.py` | PASS after helper correction;2 actual homepage groups1440/390 plus1 provider/navigation fixture1024 |
| `.venv-phase2/bin/python scripts/browser_phase10.py --run <saved-run-dir>` | A–E saved output browser checks pass after preserved helper/launch failures; C/E post-fix checks pass, separate from semantic score |
| Runtime/source/saved-row audit + readiness | PASS;27 runtime files match,all12770 spans pass,all original records retained,readyHTTP200 |

Every command above was run through `python3 scripts/capture_phase10.py`. [Exact command ledger with UTC, exits, durations and private stream paths](agent-transcripts/phase-10/command-ledger.md) includes failed attempts and full evaluation commands. Retrieval commands use `python -m backend.evaluate_retrieval --split tuning|held_out|unsupported --config eval/retrieval-local-v3.json --output /app/evidence/phase10/<separate-attempt>` inside `compose exec -T api`; raw reports were copied before container replacement.

Contract suite mixes unit/mocks,real PostgreSQL/API and local synthetic Nomic embeddings; source/atomic refresh/deletion operations are isolated fixtures,not corpus measurements. Failure injection uses refused endpoints in the isolated test DB; actual normal PostgreSQL/Ollama were never stopped. Timeout/cancel/disconnect tests use real stubborn Python mock processes and bridges/DB,not real model cancellation. SC-D’s API restart ran idle, separately from suites/generation.

Actual isolated Chrome157.0.8103.38 checks cover1440/1024/768/390 layouts,mouse/keyboard resizing,storage persistence/reset/clamps,collapse/expand,reader preservation,Ask/Essay composer reachability,Models disclosure,source focus/return,no horizontal overflow. New-session UI focus/creation/retry/hostile-artifact interactions use labelled API fixtures; Phase10 live sessions/generation are actual API runs,then actual saved-content browser reads. Both routes and shared logo/home links were checked live. Latest homepage and live scenario browsers have0 page/console errors. No interactive provider picker exists in this checkout; server-selected model disclosure remains intact. Physical keyboard behavior/other engines remain unverified; in-app connector still has the baseline bootstrap limitation,isolated Chrome provides browser evidence.

Nonfatal Starlette/httpx deprecation and psycopg connection ResourceWarning remain. Initial audit lacked PYTHONPATH; initial unit setup lacked a required placeholder DB password (two attempts); corrected helper invocations then passed. Initial pagination/partial-label failures were product defects,others include stale/racing browser helpers as described. All12 captured nonzero command attempts are retained; they are not twelve unresolved product defects. No meaningful required regression check was skipped; failed semantic gates remain failed.

## Remaining gate and scope

Full-corpus gate is closed successfully; **quality/release gate remains open**. Next blockers: reliable explicit abstention when retrieval is merely related; complete multi-part/follow-up/two-source answers; relevant whole factual selections and readable as-generated essay advice; Recall@8 below85%. These are material user-facing defects,not hidden by passing tests,citation existence,manual historical essays or corpus completeness. No known critical source-security/data-loss defect was found within this bounded review,which is not a universal security assurance. A small speculative name/keyword filter was not added to overfit the four unsupported prompts.

Cloud behavior was not revalidated; remote snapshot remains intentionally incomplete from prior publication choice. Cold/clean-checkout rehearsal,external users,physical device keyboards,rights review and complete coding conversation export remain separate limitations. No changes staged/committed/pushed; original sessions/artifacts/index retained. Stop before Prompt11.

Final hygiene:464 new evidence/changed text files scanned against3 exact configured secret values plus common credential patterns;0 findings. Values were never printed. `git diff --check` passes,index empty,all changes uncommitted. Scan is bounded and excludes pre-existing private traces/history/models/corpus;see [scope/result](agent-transcripts/phase-10/hygiene.json).


## Bounded quality pass — completed8 November2026

**Original0/5;bounded rerun0/5;proposed target4/5.Quality gate remains FAILED.** Original raw runs/score preserved;one new A–E batch only,8 local chat operations(7 complete,1 failed),one fresh1216-word essay,no model retry/manual essay edits. Chat qwen3:0.6b,essay qwen3:1.7b,Pi/Ollama only;303/12770 index unchanged. [Diagnosis before editing](agent-transcripts/phase-10/quality-pass/diagnosis.md),[results](agent-transcripts/phase-10/quality-pass/results.json),[exact command ledger](agent-transcripts/phase-10/quality-pass/command-ledger.md).

Two shared changes were tested:(1) exact same-speaker context excerpts,7200-byte packet/1600-byte excerpt/10 candidate bounds,and at most6 validated evidence IDs with answered/partial/insufficient_evidence; (2) preserve typed retrieval failures separately from semantic gaps and generic RPC failure,in metadata/safe logs/live UI error copy. Retrieval ranking/config,models and essay implementation unchanged. Full corpus evidence in D includes the entire listening/resource answer,so new abstention is a model selection failure,not missing source text. More context/complex schema did not establish better quality;why the tiny model over-abstains is not proven by this single batch.

| Case | New result | Request seconds |
| --- | --- | --- |
| A | FAIL:false abstention despite survey wording/respondent evidence;gap-message artifact persists but is irrelevant. |8.744 |
| B | FAIL:complete LNO contrast now quoted,but six noisy excerpts/partial status;follow-up abstains and does not make bug-triage checklist. Correct context/fresh retrieval. |9.480 +7.249 |
| C | FAIL:1216 words,6 sections,9 exact factual blocks/6 citation labels;53.522s essay. Byte-identical to prior post-fix draft. Irrelevant/truncated facts,missing qualifications,repetition and unsupported advice inferences remain. No invented historical Lookout engagement/conversion outcome. |11.557 research +53.522 essay |
| D | FAIL:both answers falsely abstain;listening rationale and Rick Rubin/[inaudible]/Drucker are in E1. Isolation,marker exclusion and6 resources after idle API restart pass. |7.061 +6.864 |
| E | FAIL:initial retrieval_timeout,then false abstention despite survey/benefit follow-ups in packet. No completed evidence-gap response to initial request. |5.558 failed +5.976 |

Completed chat statuses:1 partial/6 insufficient_evidence/0 answered;median7.155s. C’s operator-review clock includes the reconnect interruption(17426.959s versus900 cap);actual request was53.522s. Other task clocks remain within original caps. No retroactive cap adjustment. Raw essay remains `.cache/phase10-quality/live/SC-01-C/essay-raw.md`. [Direct essay review](agent-transcripts/phase-10/quality-pass/essay-review.json).

E now records retrieval-stage OperationalError classified retrieval_timeout,upstream rpc_rejected retained,process/bridge reaped. [Safe runtime trace](agent-transcripts/phase-10/quality-pass/safe-runtime-events.json) confirms this new failure;it does not prove the historical failure’s cause. Browser reopening exposes another limitation:failed/Retry state does not show the detailed reason after reload. Friendly typed copy is wired only to the live alert. A separate diagnostic finds model_timeout misclassified as validation failure by the new copy ordering. Both failures are preserved;no post-rerun product fix or model retry.

Focused14 tests,12 Node policy/schema tests,3 frontend tests,typecheck/build passed. Initial full suite126/127 plus one test-import error(spike module absent from image);corrected to app RemoteError and included new runtime helper in Docker. Final **127/127** contracts,19.156s,on retained isolated lenny_contract_3b402853c986. Browser A–D saved-content checks pass;E’s two detailed-error assertions fail. Timeout-copy diagnostic fails. Read-only preservation audit initially timed out while serializing/sorting full vectors;primary-key pagination then passed unchanged3s per-query deadline. Snapshot filters pre-pass sessions;all67 prior sessions/165 messages/13 essays/12 artifacts and all303 episodes/12770 complete chunk/vector rows remain unchanged. All original UI/frozen-input/raw-result hashes preserved except intentional lib.ts error copy. [Preservation](agent-transcripts/phase-10/quality-pass/preservation.json).

No retrieval metrics rerun because no ranking/index/config changed. Previous full-index tuning/observed-holdout metrics remain separate historical measurements,not new quality scores. **Do not promote the bounded experiment as a verified improvement.** Before a release rehearsal,keep it separate from the last verified120-contract baseline. Carry forward false abstention,missing checklist synthesis,intermittent full-index timeout,raw essay failure,saved error visibility and the experimental timeout-copy regression. Publication/submission remain separate.
