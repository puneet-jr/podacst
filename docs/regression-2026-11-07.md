# Current working-tree regression — 7 November 2026

Verdict: local regression passed after correcting one stale browser-test assertion and refreshing a stale running API image. Ready to **start Prompt 10 locally**; Phase10 itself was not executed. Uncommitted UI source files are byte-for-byte unchanged from this regression's initial snapshot (ignored Finder .DS_Store metadata is excluded). No commits, pushes, database resets, corpus ingestion, model downloads or cloud inference.

## Results

- Frontend typecheck and production build: pass; source-span tests **2 passed/0 failed/0 skipped**.
- Agent policy tests: **10 passed/0 failed/0 skipped** (local/cloud policies use mocks, no cloud inference).
- Documented contract suite: **115 passed/0 failed/0 skipped**,20.748s test execution, on new retained `lenny_contract_397a7b56093b`, migration0005. Includes real PostgreSQL/API and local synthetic embedding checks plus deliberately mocked selection/lifecycle checks. A nonfatal psycopg connection ResourceWarning remains; it was not suppressed. Bounded command capture truncates earlier stderr while retaining the final115-test OK summary; do not claim every individual test line is retained.
- Standard browser fixtures: **16 cases +4 Anthropic display assertions passed**. OpenRouter fixture: **4 assertions passed after correction**. These provider checks do not call cloud models.
- Resize suite: **5 groups passed** (4 intercepted fixture groups,1 real saved-content group); brand/provider suite: **3 groups passed** (2 real homepage groups,1 intercepted OpenRouter disclosure/navigation group). Live UI adds **3 groups passed**. These are named groups, not an assertion-coverage score.
- No unresolved test failure; **0 required checks skipped**. Two initial verification failures are retained in private command capture.

## Actual browser and local smoke

Isolated Chrome157.0.8103.38, fresh profiles. The in-app connector remains a previously documented bootstrap limitation; Chrome provides the actual browser evidence. Homepage/workspace checked at1440px and390px; layout/reader/draft checks also1024px and768px. Verified shared waveform/home link, interactive example, new session and input focus, composer visibility/reachability, Models disclosure, citation focus/return, no page or console errors or horizontal overflow. A fresh dedicated regression session was created; existing sessions were not edited. Width persistence, mouse/keyboard resize, resets, clamps, collapse/expand, mounted reader preservation, tablet and phone navigation passed. Real phone keyboards and other browser engines remain unverified.

Exactly two new local requests, FastAPI/Pi1.5.0 → Mac Ollama0.30.11 / qwen3:0.6b, hybrid retrieval. Readiness200; database schema0005, pgvector0.8.7; index9/303 episodes and373 passages.

| Request | Stream/UI elapsed | Backend operation | Citation / passage | Support review |
| --- | --- | --- | --- | --- |
| Sean Ellis must-have survey question | 6.817s | 6.640s | S1 / c0aa1ec1-9da2-5bc9-a1ed-550df1f12411 | Exact survey wording is present in opened original passage; supports answer. |
| Lookout onboarding follow-up | 4.820s | 4.640s | S1 / 53054eb0-beee-5be4-b2f1-99ca9b2eac2d | Source explicitly describes antivirus setup first and protected message; supports quoted change. No engagement/conversion improvement inferred. |

The first request had no prior context. The follow-up included the same session's first user message and retrieved a different passage. Both exact spans and source ownership resolve; both Pi processes reaped and tool bridges closed. This is bounded extractive smoke evidence, not autonomous routing/quality validation.

Existing reviewed1208-word essay reopened, including saved Markdown and HTML previews on desktop and phone. This remains the earlier manually reviewed/edited result; no essay was generated or regraded as autonomous output.

## Initial failures and small correction

1. Running API freshness check found only `agent/provider_policy.ts` differed from the working tree. After the isolated contract suite had exited, refreshed API/web from already-built current images. Rerun compared26 runtime files and passed. No outage/restart was run concurrently with the suite; no normal dependency outage was induced.
2. Existing `scripts/browser_openrouter.py` expected the former always-visible `Chat google/...` label. Current UI intentionally places `Chat: google/...` inside Models. Updated only the test to open/close that disclosure and assert the current label. Added injectable report/screenshot roots so this rerun preserves historical Phase9 evidence. Rerun passed; no product code changed.

## Exact commands and actual exit results

The command runner prefix was `python3 .cache/regression-current/capture.py`; it captured actual bounded stdout/stderr, UTC times and exit codes to ignored private `commands.jsonl`. Helper browser wrappers redirect existing runners to this regression's private evidence rather than overwriting historical reports. No command contains credentials.

| Command after capture prefix | Result |
| --- | --- |
| `npm --prefix frontend run typecheck` | PASS; exit 0; 1.816s |
| `npm --prefix frontend run build` | PASS; exit 0; 2.602s |
| `node --test frontend/test-source-span.mjs` | PASS; exit 0; 0.183s |
| `node --test agent/test_provider_policy.ts agent/test_conversation_policy.ts agent/test_essay_format.ts` | PASS; exit 0; 0.524s |
| `python3 scripts/docker.py compose build api web` | PASS; exit 0; 2.939s |
| `python3 scripts/docker.py compose run --rm --no-deps -e DEFAULT_PROVIDER=ollama -e OPENROUTER_API_KEY= -e ANTHROPIC_API_KEY= api python -m backend.contract_check` | PASS; exit 0; 29.904s |
| `python3 .cache/regression-current/runtime-check.py` | INITIAL FAILURE (corrected later); exit 1; 0.712s |
| `python3 scripts/docker.py compose up -d --no-deps api web` | PASS; exit 0; 3.175s |
| `python3 .cache/regression-current/runtime-check.py` | PASS; exit 0; 0.816s |
| `.venv-phase2/bin/python scripts/browser_openrouter.py` | INITIAL FAILURE (corrected later); exit 1; 8.914s |
| `.venv-phase2/bin/python .cache/regression-current/browser-checks.py` | PASS; exit 0; 28.086s |
| `.venv-phase2/bin/python .cache/regression-current/home-check.py` | PASS; exit 0; 5.167s |
| `.venv-phase2/bin/python .cache/regression-current/openrouter-check.py` | PASS; exit 0; 3.809s |
| `.venv-phase2/bin/python .cache/regression-current/live-local.py` | PASS; exit 0; 21.821s |

## Remaining work / next gate

Prompt10 must still perform the explicitly authorized full-corpus work, frozen scenarios and broader grounded quality/evaluation gate. This regression did not ingest data or download models. The existing published origin/main snapshot remains incomplete by the user's earlier choice; fresh remote-checkout reproducibility is not established. Autonomous essay quality, broad retrieval/answer quality, cold setup and device-keyboard validation remain unverified. No new critical regression was found in this pass.

Private evidence: `.cache/regression-current/summary.json`, `commands.jsonl`, browser fixture reports/screenshots and `live/report.json` with raw outputs/source review. Private payloads and logs were not staged or published.

Final hygiene: exact configured secret-value scan covered33 new evidence/report/test files and found0 matching files; scope is bounded, not universal assurance. `git diff --check` passed; index empty. The Models disclosure was tested; there is no interactive frontend provider/model picker in this checkout (selection remains server configuration). Normal readiness and corpus count were checked again after the smoke.
