# Phase 8: interface and main journey

**Gate passed for the manually reviewed local workflow. Stop before Prompt09.**

## Publication scope: incomplete remote snapshot

The user explicitly selected a Phase8-only commit. Earlier Phase6/7 runtime prerequisites remain local and uncommitted: evidence-first essay/artifact services and routes, essay model configuration/adapter, dependency pins and supporting container configuration. The Phase8 UI calls those services. Therefore this commit on origin/main is intentionally an incomplete application snapshot and cannot reproduce the verified end-to-end journey by itself. Browser tests also require the local Phase7 backend helper and labelled fixture. Reported live results describe the full local working tree, not this standalone commit. No autonomous essay-quality claim is made.

Raw API responses, transcript payloads, command stdout/stderr, model output drafts and private screenshots are excluded from this commit. Sanitized command metadata, checks, IDs/counts/hashes and manual-review evidence are included; originals remain local. The 1,208-word essay is a **manually reviewed result**, with six advice and three source-selection edits; autonomous essay quality remains **unverified**. The interface opens directly into the workspace, supports research and evidence-led essays, and exposes source inspection, explicit review and saved documents. This is not autonomous essay acceptance or the frozen five-scenario release metric.

## Changes and purpose

The frontend now has an editorial reading layout, real model/corpus status, interview scope, examples, draft recovery and contextual documents. Mobile tabs replace compressed columns. Keyboard source focus/return, stale-response protection, retained per-session input, retry identity, visible failures and dirty-review protection address loss of work and navigation errors. Source span selection handles Unicode correctly. Artifact sandbox/CSP and local inference boundaries remain intact.

Small backend additions expose owned saved essays, actual indexed interview scopes and the separate essay model. An ordinary one-query essay initially found only five usable guest selections and stopped with `insufficient_evidence`, without Pi drafting calls. The candidate buffer now requests up to eight passages/5600 estimated source tokens instead of six/4200 (and the earlier four/2400 baseline). The server still writes six sections and passes advice-only inputs to bounded4096-context/384-output generation. Same topic and interview scope were retained; no hidden fixture queries or lowered evidence gate. The read-only preflight found eight candidates/4711 estimated source tokens. Phase4 defaults/evaluation are unchanged.

## Verification, separated by evidence type

All exact executed commands, timestamps, exit codes and bounded stdout/stderr: [command index](agent-transcripts/phase-08/command-index.json), private local capture log (excluded from Git). Relevant final checks:

| Command | Actual result |
| --- | --- |
| `npm --prefix frontend run build` | TypeScript and Vite pass; final build2026-11-07T02:59:28Z |
| `python3 scripts/docker.py compose run --rm --no-deps api python -m backend.contract_check` |99 tests pass,7.775s, fresh retained isolated PostgreSQL DB; model selections mocked where specified |
| `node --test frontend/test-source-span.mjs` |2 tests pass: Unicode offsets and invalid selection rejection |
| `.venv-phase2/bin/python scripts/browser_phase8.py` |16 deterministic browser checks pass; no model calls/database writes |
| `.venv-phase2/bin/python scripts/live_ui_phase8.py` |Real app/Pi/Ollama main journey; initial evidence gap retained, then full draft after bounded candidate correction |
| `.venv-phase2/bin/python scripts/prepare_review_phase8.py` |Explicit source/advice edit plan from actual retrieved evidence |
| `.venv-phase2/bin/python scripts/review_ui_phase8.py` |Normal UI review/save/accept, both artifacts, reload/reopen and mobile source focus/return pass; no browser API interception |

The [fixture browser report](agent-transcripts/phase-08/browser-fixture.json) covers new session, supported/follow-up rendering, source focus, unsaved review, review gate, artifact save failure/retry, both formats, reload/reopen, long scrolling, contrast samples, session draft isolation, late source results, timeout/retry identity, missing-model recovery, unsupported results, pre-start cancel and mobile keyboard/layout. Mock cancel is not model-process cleanup proof. Real lifecycle cleanup evidence remains separately recorded in Phase5.

Actual browser: isolated fresh-profile Chrome157.0.8103.38 via pinned Playwright1.64.1. The in-app connector still fails during bootstrap (`node:process` unavailable); it was not used to claim browser success. Desktop/mobile screenshots were visually inspected. Images stay in ignored `.cache/phase8-browser`; [hash index](agent-transcripts/phase-08/screenshot-index.json) identifies private QA captures. No horizontal overflow or page errors in tested cases. Sampled contrasts12.4/8.72/4.94:1 are not complete WCAG or screen-reader verification. Backend suite emitted nonfatal psycopg shutdown ResourceWarnings in some runs; no failed assertions were suppressed.

## Real local journey

Session `6f882513-96b5-4fcc-88c2-1e1dc82d9585`, hybrid retrieval, Mac M2/8GiB, FastAPI/Pi/host Ollama, chat `qwen3:0.6b`, essay `qwen3:1.7b`. Existing models only, no cloud inference/downloads. Nine indexed episodes/373 passages out of303 total; no broader corpus-quality claim.

1. Sean Ellis must-have survey question:8.031s, run `96bcfc00-cf75-467e-9ad1-1ec7ad8bbecf`; citationS1 chunk `c0aa1ec1-9da2-5bc9-a1ed-550df1f12411`. Exact source supports the quoted survey wording.
2. Lookout follow-up:6.798s, run `0761f213-69c6-4049-8b70-dc287529ee65`; correct prior user context and freshS1 chunk `53054eb0-beee-5be4-b2f1-99ca9b2eac2d`. Quote supports antivirus-first onboarding/protection notice, without claiming measured engagement/conversion improvement. Labels are local to each answer.
3. Same-session topic: use must-have customer feedback for positioning/onboarding, actual Sean Ellis interview scope. Initial run `6d006bbb-fa3f-4431-8583-d53ead570604` stopped at insufficient evidence, zero writing calls. Preserved evidence-gap output. After candidate-buffer correction, one full essay run `b4309701-8122-4b16-b38b-ec7ee8a3fe21`,41.096s, six Pi drafting stages/no length repair. Raw1224 words failed `unattributed_paragraph` in section5; weak/repeated advice and clipped source selections also required review.
4. Through normal UI controls, six advice paragraphs and three source selections were explicitly edited. First application precedes evidence to provide a reader hook. Final **1208 words**, six complete sections, selective bold and actionable takeaway list. Ten quote blocks exactly match immutable original spans; six labelsS2–S7 resolve. SourceS3 was shortened to complete sentences, S5 uses the complete benefit-question sequence, S7 stops before its dangling95% fragment. No invented95% result or unsupported Lookout improvement. Guest quotations are attributed views/case statements, not independently proven universal outcomes. Application text proposes experiments, metrics and decisions as advice/hypotheses.
5. Five review assertions and a note were saved explicitly before acceptance. Both Markdown and static HTML saved and reopened after page reload; mobile source opening/return passed. Artifact IDs: HTML `0e785957-d644-4a93-8a0a-54c3a5c43c52`, Markdown `75299b3d-3732-4b92-89fa-668921e9d013`. NewPhase8 persistence proof is reload/reopen; actual service-restart proof remains Phase7, not rerun here.

[Sanitized live summary and output hashes](agent-transcripts/phase-08/publication-evidence.json) · [source/manual review](agent-transcripts/phase-08/live-20261107T024458/review-checks.json). Full reviewed output, raw draft and raw API snapshots remain local and are excluded from this commit.

An initial automation attempt checked an Ask button before it became enabled; existing successful chats were recovered rather than regenerated. Subsequent browser check durations are not inference latency. Failed attempts and actual generation times remain in the logs. Manual editing time and model startup are not included in41.096s. This single journey is not a benchmark or reliability rate.

## Remaining limits

Substantial manual editorial/source work remains necessary; raw output did not pass. The final essay is evidence-led and quote-heavy, not independently judged polished writing. General autonomous routing/synthesis, full corpus, retrieval quality target, ten-answer quality exercise and frozen five-scenario metric remain open. One Chrome version, no screen-reader/user study. Unsaved composer drafts survive session switching only within the current page. Single local evaluator; no production authentication. Prompt09 operations/cloud work has not started. No volume deletion, existing database reset or model switch for chat. Publication is scoped as described above.
