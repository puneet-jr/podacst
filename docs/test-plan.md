# Verification plan and actual status

## Phase 2 automated evidence

- Actual PostgreSQL migration/schema/pgvector/index checks, session/message API contracts, local user metadata, UTC timestamps, independent context storage, cross-user exclusion, unknown/invalid IDs and pagination, idempotent retry/conflict and structured log-content redaction: passed in the real isolated contract database. Five adapter/config/protocol checks use mocks; they are distinguished from seven PostgreSQL/API checks.
- Real TCP/Compose gate: two messages remain isolated after API restart and DB outage/recovery; liveness/readiness differ during outage, failed write rolls back, app resumes without reset, frontend HTTP/API proxy serve correctly. Exact requests/commands are in Phase 2 results.jsonl files.
- Frontend TypeScript and Vite production build: passed on host and in the Docker build.
- Real container Pi to host Ollama controlled fixture: passed; not real corpus, retrieval ranking or writing evidence.

## Manual browser plan (not executed)

Browser connection failed before navigation. Every item below remains unverified:

1. Create a session, save a note, refresh/reopen, switch to another session and confirm correct displayed messages.
2. Verify saved/error states and retained draft after a failed save; retry without duplicated message.
3. Use keyboard only to reach every control; inspect labels, focus, contrast and error announcements.
4. Inspect desktop and narrow mobile widths for readable text, usable composer and session/status navigation.
5. Inspect selected provider, unavailable model/database states and empty corpus; confirm nothing suggests grounded answers are available yet.

Later phases must add actual parser/embedding/retrieval tests, model routing and semantic grounding review, essay length/quality, hostile artifact browser checks, complete failure matrix and clean-checkout rehearsal. Do not count the fixture or mocked protocol checks as those integrations.


## Phase 3 actual evidence

- Parser: 13 tests for real observed structures, timestamp-only continuation, bracket/missing time, irregular metadata, YAML attacks/duplicate keys, sponsorship flags, exact offsets/Unicode/long turns and manifest safety. Initial boundary defect failed before correction.
- Embedding protocol: five mock tests cover array/model/dimension/count/vector rejection, prefix/no truncation, retry budget and deadline/input errors. No live-provider evidence is inferred from mocks.
- Final container suite: 30 tests passed on fresh migrated PostgreSQL (23 unit/parser/mock, seven DB/API). Starlette/httpx deprecation warning remains.
- Separate retained fixture DB + real Ollama: 12 integrity checks passed for unchanged/resume, spans/vectors/full-text, atomic change, injected failure rollback/recovery, incompatible model/identity, deletion, concurrency and interrupted-run status. Faults are labelled injection.
- Actual corpus DB/provider smoke: 3/303 episodes -> 114 vectors; repeat skipped all with same IDs, exact hashes/spans/full-text and unchanged saved conversations. Seven invariants passed. Full corpus indexing and retrieval metrics remain unverified.
- TypeScript/Vite build, pip check, readiness/status/proxy/HTTP serving passed. Browser visual/responsive/accessibility checks remain unrun. Status-panel counts have API evidence only.

[Phase 3 report](phase-03-report.md) links exact commands and both initial failures/corrections. The next test increment is reviewed retrieval evaluation; generated answer/essay/renderer checks remain dependent later phases.


## Phase 4 actual evidence

Final container suite49 passed:33 unit/parser/mock plus16 PostgreSQL/API checks. New cases cover deterministic RRF/ties/duplicate votes, dedup/overlap, budgets/diversity/scopes, local query prefix/identity bounds, actual sparse/dense/hybrid SQL, exact originals, neighbors, retirement, rare terms vs repeated headers, safe logs/typed errors and explicit default/failure behavior. Retrieval fixture embeddings are real local Ollama; injected outage is mocked and labelled. Three separate hand-calculated metric checks passed. Nine live HTTP/proxy/source/session proofs passed. No frontend changes/browser pass claimed.

Actual evaluation:24 frozen reviewed questions (16 tuning/eight held-out), four unsupported, three methods, current9/303 corpus scope. Every returned source passed DB original/hash/span/current-version proof. First low baseline and corrections retained. Selected default recall62.5% held-out/66.67% all-case descriptive, target unmet; method selection unstable. All12 unsupported diagnostics returned candidates, not answers. Manual support rubric/selected excerpt notes exist, but generated claim-support/abstention/routing/essay/SC-01 outcomes remain unrun. Never promote integration runner passed=true to a quality pass. See phase-04-report.md and eval/README.md for exact methods/counts/latencies/limits.


## Phase 5 actual evidence and remaining checks

Final66 backend checks passed on a fresh retained PostgreSQL database:42 unit/parser/mock and24 DB/API checks. New conversation DB cases deliberately mock Pi selections/timeout and must not be called real model proof. Actual local Nomic embeddings/SQL remain used by retrieval fixture tests. Separate four Node tests cover strict textual tool-call adaptation and rejection of unapproved/source/later-turn requests. Host and Docker TypeScript/Vite builds pass.

Real-model evidence is separate: final live-20261106T081843 through Nginx/FastAPI/Pi/Mac Ollama passes the requested supported/follow-up/private-gap contracts. Every displayed citation is opened; manual support-review.json distinguishes correct two answers from the incomplete isolated Shreyas answer. Unsupported response is a server-policy correction, not model abstention. Earlier automatic pass flags are corrected by a separate manual failure review, without rewriting original logs.

Real lifecycle evidence: timeout, explicit cancel, stream disconnect, same-ID retry, completed replay without inference, empty retrieval, six expected messages, restart-identical messages/source snapshot, unknown/cross-session404. Separate actual local hostile-source fixture succeeds with17-day evidence; this is synthetic and isolated from nine podcast episodes. Final source/runtime audits preserve earlier spike/evidence/data. The final live command and suite completed despite turn interruption; no needless model rerun on resume.

Browser plan remains unexecuted: create/ask/follow-up/open source, cancel/retry, reopen/switch and stale-response behavior, keyboard/focus/error announcements, desktop/mobile layout, observed timestamp/links and unavailable dependency states. Browser bootstrap fails before navigation. No build or API result substitutes for this. General context/abstention/synthesis quality, >=10 unique-answer review, essays/artifact hostile rendering, cloud and full-corpus/scenario gates remain pending.


## Phase6 evidence status at publication

81 backend contracts passed in6.790s on fresh retained PostgreSQL:51 unit/parser/mock and30 DB/API checks. Essay generation in DB tests is deliberately mocked. The corrected real local essay run is separate and FAILED before section1 with Ollama grammar initializationHTTP400;0 essay words/0 completed sections. Earlier actual outline and unsupported rejected prose are preserved. No Phase7 or essay-quality success is inferred. Publication changes are documentation/evidence sanitation and Git organization; app runtime is the snapshot tested before that failure. No new model test was run during publication.


## Phase8 executed UI checks

See [report](phase-08-report.md) and actual command capture for99 passing backend contracts on fresh retained PostgreSQL,2 Node Unicode-source tests and frontend typecheck/build. `scripts/browser_phase8.py` runs16 deterministic browser cases with intercepted fixture APIs and no model/DB side effects. `scripts/live_ui_phase8.py` and `scripts/review_ui_phase8.py` operate the actual UI/Pi/Ollama separately: supported/follow-up/source, draft, explicit corrections/review, both artifacts and reload/reopen. Preserve initial insufficient-evidence stop and raw1224-word rejection; final1208 words passed after9 logged edits. Private desktop/mobile screenshots visually inspected; hashes only in publishable evidence. One Chrome version, no screen-reader study; actual restart proof remains Phase7. Mock pre-start cancel is not model cleanup. No SC-01 completion rate inferred; stop before09.
