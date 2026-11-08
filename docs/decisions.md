# Decision record

6 November 2026 baseline. All technology selections remain proposals until their integration gate succeeds.

| ID | User need and alternatives | Selected direction / expected benefit | Downside / evidence and status |
| --- | --- | --- | --- |
| D-01 | One evaluator needs saved independent research; production identity vs minimal local user. | Propose minimal local user + scoped PostgreSQL sessions; focus on reliable saved work. Include all mandatory flows, defer voice/uploads/collaboration/SSO/billing/graphs with reasons in PRD. | Not production tenancy. AS-01/02/07 unverified; no client interviews. Database readiness observed, schema/isolation untested. |
| D-02 | Verifiable advice; model-memory answers vs long-context vs retrieval. | Transcript-only evidence; propose PostgreSQL full-text + pgvector with measured hybrid/sparse/dense comparison and exact citations. | Retrieval may miss context; valid citation IDs do not establish support. AS-03 confirmed by assessment, implementation pending. Hybrid is not a company mandate. |
| D-03 | Real local demo on actual machine; Pi RPC vs SDK bridge vs Claude Agent SDK; small local model vs larger model. | Investigate FastAPI -> Pi JSONL subprocess -> Ollama compatible endpoint with one controlled extension tool. Prefer one active generation request and bounded context on 8 GiB. Do not select a model before fit/tool tests. | Pi missing, Ollama stopped, no installed-model inventory or inference evidence. Current official docs support RPC, custom tools and compatible endpoints; package candidate is @earendil-works/pi-coding-agent 1.5.0, Node >=22.19.0; installed Node 24.9.0 meets declared range. Publication/install compatibility not yet proved. AS-04/05; RK-02/04. |
| D-04 | Evaluator can switch provider; Anthropic vs Gemini vs OpenAI/other Pi providers. | Defer cloud provider/model choice until actual credentials are available; Anthropic and Gemini are documented options. Explicit selection, no silent local-to-cloud fallback; server-side credentials only. | None of four checked environment keys present; no live cloud validation. Cloud mode sends selected evidence, relevant conversation and instructions; separately billed use. AS-06; RK-03/05. |
| D-05 | Useful HTML/CSS preview while containing generated code; raw DOM vs sanitizer vs iframe. | Propose safe Markdown + sanitization/allowlist and opaque-origin script-disabled iframe/CSP for HTML, blocked external networking. | Some content intentionally unsupported. Policy efficacy needs actual browser hostile fixtures; no renderer exists. RK-06. |
| D-06 | Reproducible and honestly attributed source; copy friend/corpus vs original app and external corpus. | Original documentation/app baseline; no friend's work supplied/reused. Keep corpus external/pinned at ingestion, record rights and attribution. Keep assessment private. | Corpus root has no LICENSE in observed listing; redistribution permission unconfirmed. Pi source declares MIT; preserve notices if copying substantial code. AS-09; RK-07. |
| D-07 | Reviewable increments before deadline; build all at once vs gated prompts. | Run Prompt 00 only, stop/report, then sequential authorized prompts. Use plan's 9 November India-time date provisionally, exact deadline verification candidate-owned. | Schedule tight, runtime blockers unresolved. Do not sacrifice mandatory gates or invent evidence; PDF date is older. AS-08; RK-08. |

Official documentation references and source revision are in [environment.md](environment.md). Update each decision with measured benefit, rejected alternatives and user impact after the relevant spike. The Phase 0 baseline had no lock/model selection; Phase 1 tested locks and fixture-only model identity now exist as documented below.


## D-03 update: proved explicit local fixture boundary (Phase 1)

Actual choice: Python/FastAPI manages a fresh Pi 1.5.0 JSONL subprocess with temporary configuration/history per request, one reviewed schema-based fixture tool, local Ollama 0.30.11 and qwen3:0.6b Q4_K_M at 4,096 context / 256 output tokens. Pin the tested npm lock and Python environment for this spike only. Pi drives both generation turns and validates/executes the real tool; no direct-model bypass.

Alternatives tried: optional autonomous tools; tool_choice alone; rigid answer formatting; enum input; bounded natural search query; generic description. Failed development batches were 0/5, 0/5, 3/5, 4/5 and 0/5. Selected simplification: explicitly identify one fixture topic in the Pi extension, anchor its query, request the tool first and generate from its evidence. Final batch 5/5 plus real API/lifecycle checks passed. This is the plan's permitted explicit retrieval flow, not proof of broad intent routing.

User benefit: a real local framework boundary with finite failure behavior rather than unreliable looped attempts. Downside: the tiny model is highly prompt/schema-sensitive and guided topic routing is fixture-specific; the real transcript/writing system still needs quality validation. A larger local model was deferred because memory/swap already constrained this 8 GiB host; no cloud substitute was allowed. In-process SDK/Node bridge would add a service boundary and did not address this observed model failure, so the validated language-independent RPC boundary was retained.

Evidence: docs/phase-01-report.md and final batch 20261106T042120-59b3c6. Warm small-fixture latency n=5: 1.205-2.248 s, median 1.729 s. Actual source labels are attached from executed tool evidence; model_text preserves original wording. Server labels establish traceability, not general claim entailment. D-07 phase boundary advances to Prompt 01 complete and stops; no Phase 2 authorization inferred.


## D-08: isolated Phase 2 data and operating boundary

Need: evaluator startup and durable independent sessions without disturbing pre-existing data. Host 5432 was occupied; chose dedicated lenny-phase2 Compose PostgreSQL/pgvector with loopback host 55432 and its own named volume, rather than reusing the user's host server. Immutable Alembic revision applies on startup; exact transactions/constraints and client retry IDs protect saved messages. The local fixed evaluator metadata is explicit, with scoped queries and no production SSO claim.

Evidence: real PostgreSQL 16.15/pgvector 0.8.7 migrations, 12 backend checks, exact saved state after API restart, readiness 503/live 200 under DB stop, rollback and recovery without app restart. The host instance stayed available and volumes/test databases were retained. Downside: another DB consumes local RAM; Compose service limits bound usage, not whole-product model quality.

## D-09: packaging and verified host inference

Need: reproducible stack and honest availability. Chose Python+Node/Pi in one API container plus a static React/Vite/Nginx frontend; avoided a separate agent microservice. Public base images are digest-pinned; JS/Python dependencies locked after actual builds/tests. An isolated credential-free Docker CLI config fixed hung public pulls without changing user credentials; private registries are outside this helper's scope. Bootstrap creates a random ignored credential only if absent.

Retained host Ollama and verified host.docker.internal from actual containers, including a 3.945 s guided Pi fixture call. Foundation readiness checks transport/model metadata and reports empty corpus/product_ready=false separately. Linux host networking and broad model/writing quality remain unverified. Native Ollama on Mac avoids a GPU-less container model runtime; the downside is an explicit host prerequisite and platform networking difference.

UI saves notes only at this phase; claiming generated research before real ingestion/grounding would mislead the evaluator. Browser tooling failed before connection, so current UI quality evidence is typecheck/build/HTTP, not visual or accessibility verification. Next dependent gate is Phase 3, not a claim that the product metric or complete application is ready.


## D-10: exact local evidence and episode-atomic refresh (Phase 3)

Need: trustworthy citations and interruption-safe updates. Selected a pinned 303-file source manifest, safe YAML plus exact original character spans, sentence/turn chunking and immutable source versions. Alternatives: normalize/replace originals (loses evidence), turn-only chunks (oversized inputs), destructive replacement (breaks saved evidence), whole-corpus atomic refresh (larger staging/memory cost). Retaining historical versions costs disk but lets saved work survive refresh. A complete manifest controls deletion retirement; `--limit` is never the deletion list. One advisory-locked writer avoids conflicting publication and needs no queue service at this scale.

Measured: full audit parsed 303/303, 12,770 candidate chunks, median 563 estimated tokens, 58–700 range. Initial regex boundary defect was caught/fixed; anchors corrected before tuning. Missing/irregular metadata and sponsor warnings remain visible rather than guessed. Ryan Hoover's title/guest/video conflict remains a source warning. Phrase-based sponsor flags are imperfect; future review/search must account for that. Full source stays ignored/read-only and root license absence does not establish redistribution permission.

Actual real-model/DB checks prove complete episode replacement, unchanged resume/no duplicates, prior active state on injected failure, retirement with old originals retained, writer exclusion and stale-run recovery. They do not prove corpus-wide transactional rollout or within-episode checkpoint resume. User impact: failure preserves prior evidence and accurate partial coverage; a failed episode must be embedded again on resume.

## D-11: existing Nomic local embedding profile and bounded smoke

Need: real local ingestion on 8 GiB M2 without another model download. Selected the already installed `nomic-embed-text:latest`, native 768 dimensions, digest `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`. Actual `/api/embed` batches use `search_document: `, 2048 context and `truncate=false`; future queries need `search_query: `. Model/digest/prefix are pinned in the index, with real probe and capability/dimension checks. A smaller/different embedding model would require measured quality and a new index; cloud embeddings would send source text off-device and were not allowed for this local check. Tag-only compatibility and silent truncation were rejected because they can corrupt retrieval semantics or lose evidence.

Three real episodes/114 vectors loaded in 24.078 s; repeat skipped in 0.247 s, with exact source/DB integrity. Actual qwen3:0.6b embedding attempt was clearly rejected; injected different digest was rejected even with matching dimension. Three-file timing is not full-corpus throughput or answer quality. Batches four, calls 20 s/three attempts, episodes 180 s and run 600 s (max 3600) keep work finite. Full corpus is parsed, only 3/303 indexed; UI/readiness expose partial status and product_ready=false. Full ingest is available but not rehearsed.

Post-smoke host snapshot: 8 GiB, swap 8194.56 MiB, memory-pressure free percentage 28%, disk 105 GiB available; API/DB/web approximately 65.56/53.78/8.348 MiB then. This is not peak telemetry and host-wide swap cannot be attributed to this task. Downside: model switching can load/evict generation weights and cause latency; retain one ingest writer, avoid concurrent generation, and defer any larger local-model decision until measured. Real RAG/essay quality remains open. See phase-03-report.md for exact commands, failures and alternatives.


## D-12: bounded PostgreSQL retrieval and source-preserving selection (Phase 4)

Need: precise evidence lookup with inspectable originals. Implemented native exact pgvector cosine search plus English full-text retrieval, RRF and deterministic source IDs, deduplication, episode caps and radius-one neighbor expansion. Alternatives: a separate vector service/approximate index/reranker add operating cost and unmeasured recall trade-offs; exact scanning is sufficient for the current 373-chunk baseline, with full-corpus latency still open. No arbitrary cosine cutoff or RRF probability claim. Fresh lexical term-coverage frequency weights reduce repeated speaker-header dominance; this is not a BM25 claim. Explicit exact scopes intersect; they never silently broaden or rely on AI topic tags.

Initial tuning exposed mixed sponsor chunks being excluded, an overly small episode cap and token-starved neighbors. Chose to retain/flag sponsored chunks by default, with explicit exclusion available; preserves useful mixed evidence but permits advertisements in candidate packets. Promotions are not substantive claim support and the downstream agent must enforce that distinction. Reserved both slots and tokens for neighbors, capped output at eight/3200 estimated source tokens and kept exact text rather than clipping evidence. Context can displace ranked hits; this trade-off is measured, not universally optimal. Original v1/v2 attempts retained.

A read-only repeatable-read snapshot protects consistent active versions across both lists/neighbors. Actual DB/source tests and every evaluated result preserve exact source spans/hashes. Query embeddings use the existing local Nomic digest and search_query prefix; sparse is explicit and needs no model call. No cloud fallback, new model/download/dependency, generated answers or new app-agent tools. See phase-04-report.md and phase-04-operations.md.

## D-13: frozen reviewed evaluation and provisional sparse default

Need: measure methods without inventing ground truth or tuning on the test set. Froze 24 source-grounded questions/32 exact spans before scores (16 tuning/eight held out), plus four unsupported diagnostics; nine deliberately selected episodes, not random/full coverage. Codex directly read real source text; this is not independent expert review. Exact span-to-active-chunk mapping precedes retrieval and credits IDs, not guest matches. Incomplete gold means valid alternative passages can receive no credit; support review remains distinct from recall.

Tuning-selected sparse default: 68.75% recall, MRR0.5458, median41.71 ms vs dense62.5%/79.50 ms and hybrid65.63%/116.06 ms. Kept the simpler measured method and froze source/config before holdout. The first holdout reversed the ranking: sparse62.5%, dense87.5%, hybrid93.75% (n=8). Did not covertly reselect/relabel or rerun the holdout. This exposes instability: default is provisional, not established as the best general product method. All-24 descriptive recall66.67/70.83/75%; proposed overall/default85% target unmet. Future mode-policy changes need fresh independent evaluation and full-corpus distractors; explicit dense/hybrid are available meanwhile.

Downside/user impact: unscoped and cross-episode requests can miss necessary evidence; nearest-neighbor output remains related even for unsupported/private/future facts. All twelve unsupported diagnostics returned candidates, not certified facts or generated abstentions. The API reports review_required/support_verified=false and finite limitations for empty scope. Phase 5 must review/abstain and preserve user scope. Nine live API/source/session proofs, 49 tests and three independent metric checks passed; engineering success is not semantic quality. Browser, product scenarios, essay quality and full corpus remain later gates.


## D-14: meaningful Pi retrieval with a bounded serialization adapter (Phase 5)

Need: real source retrieval through the required framework on the existing8GiB Mac. Retained Pi1.5.0 RPC and qwen3:0.6b; the extension registers one read-only current-question search, Pi executes it, and Pi continues with its result. Python pins query/scope and a single-use capability. Official installed extension docs and implementation were inspected: message_end may replace a finalized message with the same role before tool execution. The exact installed documentation hash and actual stdout/stderr are recorded. References: [Pi extensions](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md), [Ollama compatibility](https://docs.ollama.com/api/openai-compatibility).

Observed failure: qwen sometimes emitted a JSON function request as plain text; named tool_choice alone did not establish native call reliability. Chose a strict first-turn adapter for exactly search_transcripts/current, preserving the original text and actual subsequent tool events. It never acts on source/tool-result text, unknown names, extra arguments or final answer examples. One final follow-up was native; other final calls needed the adapter. This is an explicit compatibility boundary, not proof of autonomous routing. An SDK/service rewrite would add integration cost without fixing this model's serialization; no such alternative was falsely marked tested.

Alternatives: fully automatic routing remains unreliable; deterministic server search would simplify orchestration but reduce Pi's meaningful role; a larger quantized local model or more RAM may improve instruction following but requires new fit/quality measurements. No larger model/download or cloud rescue was used. Keep one generation and a bounded evidence pack. Downside/user impact: guided research works for demonstrated cases, while arbitrary question quality and routing remain uncertain.

## D-15: model-selected exact excerpts and explicit private-fact policy

Need: inspectable supported answers with honest limits. Selected single-ID structured output instead of free prose/multi-claim arrays. The model chooses one excerpt from real retrieved evidence or NONE; the server validates IDs/character spans and renders only the exact selected text. Safe source links, immutable snapshots and separate metadata preserve original context. This reduces invented factual prose, but a true quote can still be irrelevant or incomplete. Two-sentence groups preserve local context without crossing speaker headers; sentence rankings/limits may omit necessary qualifications. Source inspection remains essential.

Measured failures included copied examples, host questions selected as answers, an incomplete independent Shreyas answer and poor general abstention. The final private churn/dashboard request selected unrelated evidence; a narrow server policy corrected it after actual search/model work. This proves the app response for that class, not model understanding or all unsupported cases. General advice is not automatically treated as private data. Free synthesis and a broad entailment/relevance verifier remain unproved; honest NONE/failure is preferable when validation cannot establish source identity. The current approach does not satisfy essay or broad research quality by itself.

Hybrid is explicit for Phase5 chat/live checks under the user's instruction. Phase4 standalone sparse default, frozen evaluation and nine-episode scope are unchanged. Removing guest framing worsened a measured query and was reverted. Broader query rewriting/method selection needs fresh independent evaluation, not retroactive relabeling of Phase4 results.

## D-16: durable answer operations, private traces and measured limits

Need: recover a saved question after timeout/disconnect without duplicate output or lost evidence. Additive0003 migration stores run/attempt/context/outcome plus immutable source metadata and quote spans. User save precedes inference; answer/source/run completion is atomic. One running run per session, explicit retry budget3, completed replay and orphan recovery avoid duplicated messages. Single-worker deployment avoids unimplemented distributed ownership. Read-only retrieval threads retain their own finite deadline after cancellation.

Actual local timeout/cancel/disconnect/retry/empty-evidence and restart/reopen passed; unknown/cross-session source404, transaction rollback/retired snapshot and orphan recovery have focused DB proof. A new private0700 trace volume preserves raw protocol/diagnostics across API recreation. Downside: source history and traces consume disk; deletion/retention and production authentication remain future work. No normal database/volume was removed.

Final requested checks took8.96s/7.05s/5.26s, with variability across earlier repeats. Post-check snapshot:8GiB M2,9584.31MiB host-wide swap,24% memory-pressure free percentage,109921341440 bytes disk free; this is not peak or causal attribution. The existing model's observed loaded footprint was about1.02GB with4096 context. Prefer bounded work now; larger local-model claims require measurements and possibly more memory. Browser bootstrap remains blocked before connection, so API/build success does not certify UI interaction/accessibility. See phase-05-report.md for the precise gate and unresolved limitations.


## D-17: Phase6 bounded essay workflow and failed local gate

Selected dedicated app skill, cited outline and six section drafts through the existing Pi/local Ollama adapter. The first per-stage-tool approach failed when the0.6B model wrote unsupported prose before executing its required section tool. Preserved that failure; corrected the boundary once to real Pi retrieval/outline followed by fresh no-tool Pi turns receiving immutable section evidence. Adapter defaults still require retrieval tools; writing explicitly rejects any tool execution. This avoids repeated routing while retaining meaningful Pi retrieval and generation, without cloud output or invented tool traces.

The single corrected run failed earlier than drafting quality could be measured: OllamaHTTP400 Failed to initialize samplers: failed to parse grammar.0 accepted words/0 of6 sections in20.466s.81 passing contracts and valid outline source IDs do not establish essay success. Potential next work is reduced provider-schema constraints with server-side bounds retained; no exact keyword cause, fix, larger-model remedy or successful essay is claimed. Stop before Phase7. Risk: grammar/API compatibility can block generation even when typed mocks and outline generation work. User impact: no approximately1250-word essay is available yet.

## D-18: honest ordered publication

The user explicitly authorized Git initialization and non-force push to vivekvattem/lenny/main. Remote was empty. Current timestamps and seven ordered phase commits organize the saved snapshot, not a fabricated development history. Prior versions of shared files are unavailable, so current shared integration is grouped with Phase6 WIP. Full runtime originals are retained privately before publishing sanitized copies; IDs/hashes/limited selected answer quotes and actual failed outcomes remain. Full corpus/PDF/model weights/dependencies/configured secrets are excluded. This publication is not a passed product/release gate, demo upload or form submission.


## D-19: plain-Markdown writing probe and semantic stop

The user requested a single saved-outline section with structured grammar omitted. Added an explicit plain Markdown payload transform that deletes response_format/grammar/format while retaining local-provider, output, context and tool restrictions. Outline planning remains structured; writing emits Markdown validated server-side. A Node test proves the omission and the actual local probe confirms successful generation with no sampler error.

The section failed the user's next gate:362 words/16.323s, zero citation markers, prompt-instruction leakage and a causal engagement/conversion claim beyond S2/S3. The core Lookout example is related and partly supported, but that does not certify the whole paragraph or cure missing citations. Preserved the unedited output and direct manual support review. Do not fill in labels after generation or represent a transport-only result as a verified essay fix. No full essay/retry or commit follows a failed section. The format experiment is left uncommitted; broader quality and the original essay rubric remain unmet. No Phase7.


## D-20: isolated essay-model comparison, blocked at download

Need: test whether1.7B improves the same failed Foundation section without changing chat or concealing failure with cloud. User authorized the local download after host/model preflight. Selected the unchanged saved-outline/S2/S3 Markdown path, with only a Docker exec child model override; comparison runner is prepared but not executed. Keeping0.6B avoids a download but retains measured grounding failure. A larger model remains a hardware/quality hypothesis; cloud is outside this test and sends evidence off-device. No alternative was falsely marked tested.

Ollama exhausted download retries with TLS handshake timeout, then connection reset during one explicit resume; final tags still lack1.7B. No section inference/full essay. Old baseline hashes match, chat remains0.6B. Partial download consumes disk; host-wide swap rose from9724.31 to10408.06MiB but cannot be attributed to model inference (none ran). User impact: no new draft or demonstrated improvement. Preserve partial files and evidence rather than change networking/daemon or fabricate comparison results. The Markdown transport fix is separately committed4323911 with failed grounding recorded. See phase-06 comparison report. Stop before Phase7.


## 7 November 2026: actual 1.7B section outcome

D-21: The authorized installed1.7B model-only comparison retained identical prompt, saved outline, S2/S3 and Markdown runtime; no app model/config change. Actual289 words/29.050s failed citations and manual factual support. Stop rather than generate a full essay from a failed section. A larger model did not solve demonstrated grounding in this single case; other models/prompts remain untested alternatives with download/memory/latency costs. User impact: no accepted section/essay, current chat preserved. Existing0.6B output unchanged. [Full measured comparison](agent-transcripts/phase-06/qwen17-section-20261106T185057/report.md).


## 7 November 2026: approved-fact section experiment

D-22: User requested immutable approved factual statements/citation mappings rather than another free-prose retry. Selected server-owned atomic fact+label blocks, model places IDs and writes labelled application prose. Exact original-source anchors/hashes guard drift; semantic approval/review remains manual. Alternative free paraphrasing failed twice; fully templated advice would reduce model freedom/readability and was not substituted after failure. Single1.7B local test failed marker placement and introduced unsupported general claims despite labels (360 raw words/27.678s). Reject whole draft instead of silently deleting or fixing it. Benefit: no malformed uncited section accepted; downside: strict contract is brittle on this tiny model and does not itself establish semantic safety. User impact: still no usable accepted essay. Product route unchanged; no cloud/full essay/retry/Phase7. [Evidence](agent-transcripts/phase-06/approved-section-20261106T193354/report.md).


## 7 November 2026: server-owned section and advice-only test

D-23: user requested removing all model responsibility for fact placement/citation IDs. Server now directly assembles approved factual blocks and labels, while a narrow Pi stage writes one action paragraph without factual input. This fixes observed token-compliance failure and keeps traceability exact; downside is a more templated evidence-summary style and manual approval burden. Single run failed because even advice-only generation added an outcome assertion (7.545s/175 assembled words). Lexical rejection plus manual review prevents accepting it; fixed factual/citation subchecks are not an overall pass. Fully hand-authored advice would avoid that model failure but was not substituted into actual output. Full essay and fresh topic evidence selection deferred because the authorized section gate failed. [Evidence](agent-transcripts/phase-06/server-section-20261106T203813/report.md).


## 7 November 2026: experiment paragraph length gate

User-authorized65–75-word experiment paragraph ran once via Pi/local1.7B:59 words/11.939s, assembled198 vs210. Fixed five approved facts/citations pass owned-source/hash review; experiment, metric, keep/revise decision and explicit Hypothesize framing present. Length FAILS (6 below minimum), with awkward prompt-caveat echo. Known lexical screen omits Hypothesize though manual review credits it; actual rejection is length. No padding/model retry/full essay/Phase7. One automatic approval timeout preceded process creation, then one actual model request.14 writing/unit tests pass separately. Chat0.6B/prior evidence unchanged. Lookout facts remain fixture data; full topic evidence/rubric untested. agent-transcripts/phase-06/experiment-section-20261106T210046/report.md


## 7 November 2026: reviewed complete essay gate

D-24: user made section lengths drafting targets and authorized full essay plus useful revision. Use fresh topic hybrid evidence, manually approved fixed facts/citations, Pi1.7B advice stages and server layout. One draft1325 words required editorial correction of benefit assertion, metric inference, instruction leakage and caveat; final1319 passes reviewed rubric. Manual approval/editing is an explicit operating cost, not autonomous generation proof. Alternative unconstrained prose/ID routing had measured failures; cloud substitution remains excluded. Real save exposed8k messages bound; migration0005 permits assistant32,768 while retaining user8,000, proved by83 contracts and actual final accepted save/reopen. Standard API essay generation still needs migration to this assisted workflow. [Evidence](agent-transcripts/phase-06/server-essay-20261106T210445/report.md).


## 7 November 2026: artifact and endpoint verification

D-25: selected evidence-first standard endpoint instead of the unreliable factual-prose/ID emission path. Facts are exact retrieved guest spans; model writes advice. Direct review still required: raw first endpoint essay failed and9 explicit source/advice edits produced1270 words. Traceability is automatic, semantic acceptance is not. D-26: selected deterministic Markdown/HTML formatting from owned accepted replies, parser-based nh3 sanitization plus restrictive iframe/CSP; avoids another factual rewrite and keeps IDs fixed, but limits creative HTML/styles/interactivity. Fixture and live provenance visible. Actual Chrome attack/network/parent-style checks passed; not a universal claim. Official bases: [nh3 API](https://nh3.readthedocs.io/en/latest/), [MDN srcdoc isolation](https://developer.mozilla.org/en-US/docs/Web/API/HTMLIFrameElement/srcdoc), [CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP). [Implementation/evidence](phase-07-report.md).


## D-27: direct workspace, explicit reviewed writing and mobile panels

Keep research, sources and documents in one workspace; use contextual desktop panels and keyboard-accessible mobile tabs rather than compressing columns. Actual model/corpus state and explicit manual-review provenance avoid unsupported readiness/quality claims. Owned essay-list and scope endpoints recover saved work. Server-only source spans plus dirty-review protection reduce accidental loss; unsent composers remain page-local. Alternative durable unsent drafts would require separate persistence/privacy semantics and is deferred. Downsides: quote-heavy output and substantial reviewer effort remain; single-browser checks do not certify general accessibility.

Ordinary topic retrieval initially returned only five usable guest selections, so the server stopped before drafting. Increase the essay candidate buffer to8/5600 estimated tokens while retaining six sections and bounded advice-only model context. No manual fixture focus queries or weaker evidence gate. Actual later draft1224 words still failed;6 advice and3 source edits yielded reviewed1208 words via normal UI. This is a reviewable local tool, not autonomous publication. [Phase8 evidence](phase-08-report.md).


## D-28: explicit native Anthropic boundary and safe diagnostics

Use the existing Pi RPC with a fresh custom native Anthropic provider, official fixed HTTPS endpoint and server-only environment key, selected only through explicit config/restart. Local children exclude ambient cloud credentials; neither provider falls back. Native tool-choice/payload policies differ from local OpenAI-compatible grammar, so test them separately rather than adding a parallel direct SDK route. Model choice stays configurable; legacy4.5 default resolves in installed Pi but has no live keyed validation. Alternatives include a newer provider model requiring compatibility/quality checks, or retaining local-only behavior; no unmeasured cloud-quality gain is claimed. Cost/privacy downside: selected evidence/context leave the device and requests may incur charges.

Default stdout logs retain protocol metadata and diagnostics retain byte counts, with raw private capture opt-in. Detect normalization from framework IDs rather than sensitive stderr. Safe request/session/run stage codes diagnose failures without prompts. DB failure during essay finalization always releases the generation lock; retained orphan state recovers at restart. Ten isolated failure cases and separate live local evidence document limits; absent cloud key blocks live validation. [Report](phase-09-report.md).


## D-29: OpenRouter is a distinct requested boundary

Inspection confirmed Phase9 used direct Anthropic. Add OpenRouter through the existing Pi OpenAI-compatible provider instead of relabelling that evidence. Each cloud provider has a separate server-side secret and exact endpoint/model selection. Default OpenRouter model google/gemini-2.5-flash-lite is listed in the current official catalog with required tool/JSON parameters. Pin allow_fallbacks=false and require_parameters=true; model lists/routes are removed, so failures remain visible. One-off cloud validation leaves the normal app on Ollama and is pending until an actual cited request succeeds and its passage supports the answer. Key presence, synthetic initialization and fixtures do not pass that gate. [Amendment](phase-09-openrouter-report.md).


## Phase10: full-index compatibility and bounded repair

Observed full303/12770 index exposed4 canonical Unicode/underscore scope failures and repeated lexical term/DF work beyond the unchanged3s statement bound. Use one shared canonical path pattern and materialized term-tsquery/corpus-count/DF CTEs;keep ranking formula,deadlines,labels and frozen v3 limits unchanged. Real old/new score/rank equivalence regression and84 successful retrieval operations support this narrow repair;small synthetic equivalence is not a universal ranking/performance proof. Downside:materialization allocates per-query intermediate state and still has long-tail latency; broad unscoped retrieval quality falls short. No reindex/dependency/JIT setting change.

Full local model measurements reject assuming a supported quote answers the request. Preserve the bounded extractive chat boundary and record its incomplete/abstention failures rather than add prompt-specific name filters or silently use cloud. This leaves a release blocker requiring a general support/completeness repair. Server-owned essay facts/citations remain;remove historical topic/constraints from the advice-only model context. Trade-off:reduces historical invention but makes advice generic/repetitive;one actual1216-word run still fails relevance/readability. Do not autoaccept it. No model/pin changes;no larger download on8GiB. [Measured report](phase-10-report.md).


## Bounded repair decision

Saved actual per-passage replay showed function-word ties and overlapping spans dropping the requested cohort sentence. Remove only for/they matches and choose non-overlapping spans under unchanged2/500/6000 limits;do not alter retrieval ranking. Exact live pair passes;broader quality is not inferred. Saved essay source replay showed an open quoted question selected as a complete factual unit. Filter candidate ends by balanced double quotes and retain exact source prefixes. Downside:conservative syntax may omit useful material and cannot certify grammar,statistical completeness or support. Fresh1145-word raw draft still fails semantic review. No scenario-specific rules,cloud fallback or manual raw-draft rescue. [Report](phase-12-repair-report.md).
