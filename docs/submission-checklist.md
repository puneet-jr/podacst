# Prompt 12 review checklist — 8 November 2026

**NO-GO for submission. Preparation only; no push, deployment, recording upload or submission authorized.** Base release candidate: `f89807d8db16c20e652590a6470810e5eb60b078`. Reviewable export: `/private/tmp/lenny-publication-f89807d`, without Git history. Documentation/evidence projections are additions to that base, not a newly tested Git revision. All 41 selected runtime hashes must remain identical. The normal dirty checkout and both failed Phase 10 runs remain separate.

## Eight deliverables

| # | Required deliverable | Location in publication tree | Actual status / remaining action |
| --- | --- | --- | --- |
| 1 | Complete public source repository | `backend/`, `agent/`, `frontend/`, `spike/`, `scripts/`, `eval/`, `compose.yaml`, lockfiles, `.env.example` | Complete local source export prepared. Existing remote is incomplete. Public repository, access and complete published revision still pending separate authorization. |
| 2 | Runnable README | `README.md`, `docs/troubleshooting.md`, `docs/handoff.md` | Fresh-volume cached setup rehearsed on this candidate. Three-episode smoke is explicit; full ingestion separate. Cold-machine downloads not timed. |
| 3 | PRD | `docs/PRD.md`, `docs/scenarios.md`, `docs/assumptions.md`, `docs/risks.md`, `docs/decisions.md` | Discovery and actual failed targets documented. No customer approval or user-study claim. |
| 4 | Design | `docs/design.md` | Editorial home/workspace, responsive panels, focus, citations and reader documented. No interactive provider picker in this revision. |
| 5 | Architecture | `docs/architecture.md` | FastAPI → controlled Pi tools → Ollama/OpenRouter, PostgreSQL, ingestion, reviewed essay and isolated artifacts documented. Bounded experiment excluded. |
| 6 | Sanitized coding-agent transcripts | `docs/agent-transcripts/`, `docs/phase-01-report.md` through `docs/phase-12-report.md` | Genuine command metadata, failure/correction reports and redaction hashes retained. **Partial:** no complete sanitized conversation export. Projections/narrative summaries are not a conversation transcript. Obtain and sanitize a real export; do not reconstruct dialogue. |
| 7 | Automated tests and manual UI plan | `backend/tests/`, `agent/test_*.ts`, `frontend/test-*.mjs`, `spike/`, `docs/test-plan.md` | Baseline 120 contracts plus frontend/Node/browser checks recorded. Prompt 12 separately verifies retained fixture compatibility and source integrity. Quality acceptance remains failed. |
| 8 | 2–3 minute camera-enabled YouTube demo | `docs/demo-script.md`, `docs/agent-transcripts/phase-12/demo-rehearsal.json` | Timed screen rehearsal and fresh local UI preflight; **no camera/audio recording or uploaded video**. Record with camera, disclose limitations, upload only with authorization, then verify evaluator access. |

## Required behavior versus our proposed targets

| Gap | Requirement or proposed target? | Release implication / smallest next change and verification |
| --- | --- | --- |
| Grounded useful answers and follow-ups | Explicit requirement. Original **0/5**, bounded **0/5** against proposed **4/5** is a measurement, not a company-set threshold. | **Required quality blocker.** Prompt 12 follow-up retrieves the right passage but the top-two sentence packing drops the 40% next-cohort sentence. Smallest supported fix: preserve query-relevant outcome sentences in `sentence_items` under existing budgets, with general tests rather than a Lookout rule. Verify the saved failing packet includes that sentence, then rerun the same pair on the full 303-episode index and review completeness/unsupported behavior. This candidate is frozen; no fix applied here. Multi-part answers also need a bounded multi-evidence contract and independent acceptance, not wholesale reuse of the failed experiment. |
| Evidence gaps and operational failures | Explicit grounding/operations requirement | **Required quality blocker.** Historical unsupported success only 1/4; related quotes can be mistaken for answers. Separately test answerable/unsupported cases and provider/RPC/timeout failures. Require explicit insufficient-evidence behavior without mislabelling infrastructure errors. Baseline error typing limits are disclosed; no cloud fallback. |
| Useful approximately 1,250-word grounded essay | Explicit content workflow/quality requirement; **1,125–1,375** is our operational band. | **Required unassisted-quality blocker.** Reviewed 1,208-word essay passes with nine edits; raw Phase 11 1,157-word draft fails despite length/IDs. Smallest evidenced fixes: reject dangling/truncated factual units and complete quotes; tighten advice validation against unwarranted metric/retention conclusions. Verify exact approved spans and one fresh full standard-endpoint draft, with claim-by-claim and readability review. Manual editing is a supported workflow but cannot establish autonomous quality. |
| Recall@8 below 85% | Proposed retrieval target, not explicit company threshold | Tuning 56.25% (16 cases), previously observed held-out 81.25% (8). Keep separate; hold-out is no longer unseen. No tuning in Prompt 12. Relevance failures and full-index timeout risk still affect required workflows. |
| Local and cloud paths | Both are explicit integration/demo requirements | Local fresh UI question succeeds; follow-up incomplete. Historical OpenRouter single chat succeeded, **same-candidate pair pending** because read-only credit checks show exhausted key limit/non-positive account balance. Credits and server configuration/recreate are needed, then one public question + follow-up, actual provider/model trace and passage review. No inference made while credits unavailable. |
| Interactive provider picker | User-requested cloud demo action, not explicit assignment requirement | User approved README configuration plus UI disclosure for this candidate. No new picker required or claimed. |
| Complete public repo, full sanitized coding export, camera video | Explicit deliverables | Export/scripts/checklist ready for review; publication, real export, recording/upload/access proof remain incomplete. No fictitious completion. |

The two 0/5 results, Phase 11 partially relevant general-survey answer, failed raw essay, and Prompt 12 incomplete follow-up remain visible. Neither valid citations nor a successful setup replace semantic acceptance.

## Section 5 operations check

- [x] README startup/migrations rehearsed on fresh isolated volumes; local Ollama reachable from container. Cached dependencies/models reused; no cold-install performance claim.
- [x] Server-only empty example cloud keys; ignored `.env`, credentials, dependencies, raw corpus, private traces and Git history absent from export.
- [x] Safe structured IDs/codes/durations, bounded model/tools/context; no shell/arbitrary files/web tools exposed to the app agent.
- [x] Historical isolated tests for missing credentials, unavailable Ollama, timeout/cancel/disconnect, empty retrieval, database failure/recovery. Mocks and real database/model scopes explicitly labelled.
- [x] Reviewed artifacts and Markdown/HTML containment/browser checks; manuals explain run/test/refresh/extend.
- [ ] Correct semantic abstention/completeness and raw essay quality; full-index timeout resilience still limited.
- [ ] Current-candidate cloud pair with usable credits.

## Publication and handoff controls

- [x] Select exact private candidate, preserve normal 303 episodes/12,770 passages and saved work; exclude bounded-pass implementation.
- [x] Standalone sanitized source tree, manifest and runtime-hash comparison. Full source passages/protocol streams/raw drafts stay private. Minimal final reviewed essay fixture contains curated quotes for UI tests, not full transcript payloads.
- [ ] Review redistribution rights for source-derived excerpts and reviewed artifact before external publication. Raw corpus is excluded; exclusion alone does not grant rights.
- [ ] Resolve required quality blockers or obtain an explicit evaluator-approved reduced scope; do not convert target misses into passes.
- [ ] Obtain actual coding conversation export and verify redactions/failure/correction coverage.
- [ ] Confirm current deadline, timezone, application form and evaluator identity/access; older assignment date and provisional plan date are not verified submission instructions.
- [ ] Separately authorize and verify public repository revision/links.
- [ ] Record camera-enabled demo; verify timing and local live behavior, label reviewed essay and all nine edits. Cloud segment separate and conditional on credits.
- [ ] Separately authorize YouTube upload, check evaluator access, submit correct form and retain receipt.

**Review readiness: yes for this tree/script/checklist. Submission readiness: no.** See [Phase 12 evidence](phase-12-report.md), [Phase 11](phase-11-report.md) and [Phase 10](phase-10-report.md).
