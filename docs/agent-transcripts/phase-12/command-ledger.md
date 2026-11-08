# Phase 12 exact command ledger

Actual child commands captured at execution time with UTC, cwd, exit and duration; invoked through `python3 scripts/capture_phase12.py`. Actual stdout/diagnostics remain separate private streams. Private helper paths are ad hoc checks, not hidden README prerequisites. No credentials or full upstream payloads.

| Started UTC | Cwd | Exact child command | Exit | Seconds |
| --- | --- | --- | --- | --- |
| 2026-11-08T04:38:29.276296+00:00 | `/Users/vivekvattem/Desktop/lenny` | `python3 .cache/phase12/credit-check.py` | 0 | 0.624 |
| 2026-11-08T04:41:51.869670+00:00 | `/private/tmp/lenny-evaluator` | `env COMPOSE_PROJECT_NAME=lenny_phase11_eval WEB_HOST_PORT=18080 API_HOST_PORT=18000 DB_HOST_PORT=55433 POSTGRES_DB=lenny_rehearsal_phase11 DEFAULT_PROVIDER=ollama OPENROUTER_API_KEY= ANTHROPIC_API_KEY= python3 scripts/bootstrap.py` | 0 | 7.206 |
| 2026-11-08T04:42:30.137830+00:00 | `/Users/vivekvattem/Desktop/lenny` | `.venv-phase2/bin/python .cache/phase12/local_ui.py` | 1 | 37.4 |
| 2026-11-08T04:43:15.487462+00:00 | `/Users/vivekvattem/Desktop/lenny` | `python3 .cache/phase12/import_reviewed.py` | 0 | 2.512 |
| 2026-11-08T04:43:37.725861+00:00 | `/Users/vivekvattem/Desktop/lenny` | `.venv-phase2/bin/python .cache/phase12/local_ui.py` | 0 | 19.208 |
| 2026-11-08T04:45:09.054404+00:00 | `/Users/vivekvattem/Desktop/lenny` | `python3 scripts/prepare_publication.py --source /private/tmp/lenny-evaluator --revision f89807d8db16c20e652590a6470810e5eb60b078 --output /private/tmp/lenny-publication-f89807d` | 0 | 32.149 |
| 2026-11-08T04:48:13.304424+00:00 | `/private/tmp/lenny-publication-f89807d` | `/Users/vivekvattem/Desktop/lenny/.venv-phase2/bin/python /Users/vivekvattem/Desktop/lenny/.cache/phase12/sanitized_fixture_browser.py` | 0 | 11.97 |
| 2026-11-08T04:46:26.044344+00:00 | `/Users/vivekvattem/Desktop/lenny` | `.venv-phase2/bin/python .cache/phase12/artifact_walkthrough.py` | 0 | 145.806 |
| 2026-11-08T04:49:56.895272+00:00 | `/Users/vivekvattem/Desktop/lenny` | `python3 scripts/verify_publication.py --tree /private/tmp/lenny-publication-f89807d --baseline docs/agent-transcripts/phase-10/release-state-latest.json --output docs/agent-transcripts/phase-12/publication-audit.json` | 1 | 0.976 |
| 2026-11-08T04:50:23.423185+00:00 | `/private/tmp/lenny-evaluator` | `npm --prefix frontend run typecheck` | 0 | 1.67 |
| 2026-11-08T04:50:32.697739+00:00 | `/private/tmp/lenny-evaluator` | `npm --prefix frontend run build` | 0 | 3.03 |
| 2026-11-08T04:50:45.133369+00:00 | `/Users/vivekvattem/Desktop/lenny` | `python3 scripts/docker.py compose exec -T api python /app/evidence/phase11-preservation/audit.py after` | 1 | 1.241 |
| 2026-11-08T04:50:46.309590+00:00 | `/private/tmp/lenny-evaluator` | `node --test frontend/test-source-span.mjs` | 0 | 0.612 |
| 2026-11-08T04:50:46.309376+00:00 | `/private/tmp/lenny-evaluator` | `node --test agent/test_provider_policy.ts agent/test_conversation_policy.ts agent/test_essay_format.ts` | 0 | 0.623 |
| 2026-11-08T04:51:05.690615+00:00 | `/Users/vivekvattem/Desktop/lenny` | `python3 scripts/verify_publication.py --tree /private/tmp/lenny-publication-f89807d --baseline docs/agent-transcripts/phase-10/release-state-latest.json --output docs/agent-transcripts/phase-12/publication-audit.json` | 0 | 1.032 |
| 2026-11-08T04:51:04.493098+00:00 | `/Users/vivekvattem/Desktop/lenny` | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase11-preservation/audit.py after` | 0 | 12.114 |
| 2026-11-08T04:51:58.108759+00:00 | `/private/tmp/lenny-evaluator` | `env COMPOSE_PROJECT_NAME=lenny_phase11_eval WEB_HOST_PORT=18080 API_HOST_PORT=18000 DB_HOST_PORT=55433 POSTGRES_DB=lenny_rehearsal_phase11 DEFAULT_PROVIDER=ollama OPENROUTER_API_KEY= ANTHROPIC_API_KEY= python3 scripts/docker.py compose restart api web` | 0 | 1.5 |
| 2026-11-08T04:52:23.839890+00:00 | `/Users/vivekvattem/Desktop/lenny` | `.venv-phase2/bin/python .cache/phase12/verify_reopen.py` | 0 | 4.917 |
| 2026-11-08T04:55:48.622025+00:00 | `/Users/vivekvattem/Desktop/lenny` | `python3 .cache/phase12/finalize_tree.py` | 0 | 0.277 |
| 2026-11-08T04:56:26.963196+00:00 | `/Users/vivekvattem/Desktop/lenny` | `python3 scripts/verify_publication.py --tree /private/tmp/lenny-publication-f89807d --baseline docs/agent-transcripts/phase-10/release-state-latest.json --output docs/agent-transcripts/phase-12/publication-audit.json` | 0 | 0.978 |

Failures preserved: scope-label helper before inference; missing PYTHONPATH on read-only audit; generated Python caches in initial export scan. Corrected only helpers/export caches, no runtime change or extra inference. Final seal rechecks the source tree and records the archive/tree hash receipt; no push/upload.
