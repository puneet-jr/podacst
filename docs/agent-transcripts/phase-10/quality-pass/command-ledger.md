# Bounded Phase10 quality-pass command ledger

Actual UTC timestamps and monotonic durations; stream files are private. Capture prefix: `python3 scripts/capture_quality_phase10.py`. Exit0 for a scenario runner is transport completion,not semantic pass.

| Started UTC | Command after capture prefix | Exit | Seconds | Private streams |
| --- | --- | ---: | ---: | --- |
| 2026-11-07T14:36:50.571141+00:00 | `python3 scripts/docker.py compose exec -T api mkdir -p /app/evidence/phase10-quality` | 0 | 0.768 | .cache/phase10-quality/commands/20261107T143650-88fe99 |
| 2026-11-07T14:36:51.391305+00:00 | `python3 scripts/docker.py compose cp .cache/phase10-quality/diagnosis-input.json api:/app/evidence/phase10-quality/diagnosis-input.json` | 0 | 0.257 | .cache/phase10-quality/commands/20261107T143651-ce5deb |
| 2026-11-07T14:36:51.698450+00:00 | `python3 scripts/docker.py compose cp .cache/phase10-quality/read-saved-evidence.py api:/app/evidence/phase10-quality/read-saved-evidence.py` | 0 | 0.18 | .cache/phase10-quality/commands/20261107T143651-2a81c7 |
| 2026-11-07T14:36:51.924827+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase10-quality/read-saved-evidence.py` | 0 | 2.689 | .cache/phase10-quality/commands/20261107T143651-98ffe8 |
| 2026-11-07T14:36:54.663105+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10-quality/diagnosis-evidence.json .cache/phase10-quality/diagnosis-evidence.json` | 0 | 0.264 | .cache/phase10-quality/commands/20261107T143654-28f441 |
| 2026-11-07T14:42:25.741985+00:00 | `.venv-phase2/bin/python -m unittest backend.tests.test_conversation backend.tests.test_evidence_coverage -v` | 0 | 0.604 | .cache/phase10-quality/commands/20261107T144225-265348 |
| 2026-11-07T14:42:26.393376+00:00 | `node --test agent/test_evidence_selection.ts agent/test_provider_policy.ts agent/test_conversation_policy.ts agent/test_essay_format.ts` | 0 | 0.449 | .cache/phase10-quality/commands/20261107T144226-fd2651 |
| 2026-11-07T14:42:26.889195+00:00 | `npm --prefix frontend run typecheck` | 0 | 1.643 | .cache/phase10-quality/commands/20261107T144226-eaad2b |
| 2026-11-07T14:42:28.585273+00:00 | `npm --prefix frontend run build` | 0 | 2.54 | .cache/phase10-quality/commands/20261107T144228-287bb3 |
| 2026-11-07T14:42:52.589738+00:00 | `node --test frontend/test-source-span.mjs frontend/test-answer-errors.mjs` | 0 | 0.351 | .cache/phase10-quality/commands/20261107T144252-51848d |
| 2026-11-07T14:43:05.531372+00:00 | `python3 scripts/docker.py compose build api web` | 0 | 12.995 | .cache/phase10-quality/commands/20261107T144305-84e922 |
| 2026-11-07T14:43:18.606249+00:00 | `python3 scripts/docker.py compose run --rm --no-deps -e DEFAULT_PROVIDER=ollama -e OPENROUTER_API_KEY= -e ANTHROPIC_API_KEY= api python -m backend.contract_check` | 1 | 26.661 | .cache/phase10-quality/commands/20261107T144318-2cab4a |
| 2026-11-07T14:44:38.642025+00:00 | `python3 scripts/docker.py compose build api web` | 0 | 7.925 | .cache/phase10-quality/commands/20261107T144438-e30437 |
| 2026-11-07T14:44:46.621584+00:00 | `python3 scripts/docker.py compose run --rm --no-deps -e DEFAULT_PROVIDER=ollama -e OPENROUTER_API_KEY= -e ANTHROPIC_API_KEY= api python -m backend.contract_check` | 0 | 24.714 | .cache/phase10-quality/commands/20261107T144446-4d128f |
| 2026-11-07T14:45:12.804145+00:00 | `python3 scripts/docker.py compose cp .cache/phase10-quality/preservation.py api:/app/evidence/phase10-quality/preservation.py` | 0 | 0.604 | .cache/phase10-quality/commands/20261107T144512-c95d66 |
| 2026-11-07T14:45:13.457585+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase10-quality/preservation.py before` | 1 | 5.607 | .cache/phase10-quality/commands/20261107T144513-73bf09 |
| 2026-11-07T14:45:19.121600+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10-quality/saved-before.json .cache/phase10-quality/saved-before.json` | 1 | 0.186 | .cache/phase10-quality/commands/20261107T144519-cb9a01 |
| 2026-11-07T14:45:30.290533+00:00 | `python3 scripts/docker.py compose up -d --no-deps api web` | 0 | 3.818 | .cache/phase10-quality/commands/20261107T144530-388291 |
| 2026-11-07T14:45:34.194671+00:00 | `.venv-phase2/bin/python .cache/phase10-quality/ready.py` | 0 | 3.746 | .cache/phase10-quality/commands/20261107T144534-fb88f9 |
| 2026-11-07T14:45:37.990672+00:00 | `.venv-phase2/bin/python .cache/phase10-quality/run-scenario.py SC-01-A` | 0 | 10.033 | .cache/phase10-quality/commands/20261107T144537-7a13cd |
| 2026-11-07T14:46:38.785796+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10-quality/live/SC-01-A` | 0 | 6.878 | .cache/phase10-quality/commands/20261107T144638-127d39 |
| 2026-11-07T14:47:15.902737+00:00 | `python3 scripts/docker.py compose exec -T api mkdir -p /app/evidence/phase10-quality` | 0 | 0.741 | .cache/phase10-quality/commands/20261107T144715-1bf0fd |
| 2026-11-07T14:47:16.697805+00:00 | `python3 scripts/docker.py compose cp .cache/phase10-quality/preservation.py api:/app/evidence/phase10-quality/preservation.py` | 0 | 0.278 | .cache/phase10-quality/commands/20261107T144716-a6fe13 |
| 2026-11-07T14:47:17.062993+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase10-quality/preservation.py before` | 1 | 9.395 | .cache/phase10-quality/commands/20261107T144717-00332e |
| 2026-11-07T14:47:26.525491+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10-quality/saved-before.json .cache/phase10-quality/saved-before.json` | 1 | 0.443 | .cache/phase10-quality/commands/20261107T144726-05fcd2 |
| 2026-11-07T14:47:43.667955+00:00 | `.venv-phase2/bin/python .cache/phase10-quality/run-scenario.py SC-01-B` | 0 | 18.785 | .cache/phase10-quality/commands/20261107T144743-3595ae |
| 2026-11-07T14:48:37.334670+00:00 | `python3 scripts/docker.py compose cp .cache/phase10-quality/preservation.py api:/app/evidence/phase10-quality/preservation.py` | 0 | 1.271 | .cache/phase10-quality/commands/20261107T144837-45feef |
| 2026-11-07T14:48:33.141831+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10-quality/live/SC-01-B` | 0 | 7.37 | .cache/phase10-quality/commands/20261107T144833-ad00b1 |
| 2026-11-07T14:48:38.778417+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase10-quality/preservation.py before` | 0 | 13.682 | .cache/phase10-quality/commands/20261107T144838-b2cd2b |
| 2026-11-07T14:48:52.615650+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10-quality/saved-before.json .cache/phase10-quality/saved-before.json` | 0 | 0.824 | .cache/phase10-quality/commands/20261107T144852-b6a3bb |
| 2026-11-07T14:49:21.605154+00:00 | `node --test frontend/test-source-span.mjs frontend/test-answer-errors.mjs` | 0 | 0.643 | .cache/phase10-quality/commands/20261107T144921-40cd8d |
| 2026-11-07T14:49:22.358864+00:00 | `node --test agent/test_evidence_selection.ts agent/test_provider_policy.ts agent/test_conversation_policy.ts agent/test_essay_format.ts` | 0 | 0.475 | .cache/phase10-quality/commands/20261107T144922-ff15d6 |
| 2026-11-07T14:49:22.914844+00:00 | `npm --prefix frontend run typecheck` | 0 | 3.051 | .cache/phase10-quality/commands/20261107T144922-cfd6e7 |
| 2026-11-07T14:49:26.023414+00:00 | `npm --prefix frontend run build` | 0 | 3.191 | .cache/phase10-quality/commands/20261107T144926-212fc8 |
| 2026-11-07T14:49:20.500423+00:00 | `.venv-phase2/bin/python .cache/phase10-quality/run-scenario.py SC-01-C` | 0 | 66.469 | .cache/phase10-quality/commands/20261107T144920-2ba0df |
| 2026-11-07T19:39:24.409490+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10-quality/live/SC-01-C` | 0 | 7.888 | .cache/phase10-quality/commands/20261107T193924-08dace |
| 2026-11-07T19:39:47.639374+00:00 | `python3 .cache/phase10-quality/review-essay.py` | 0 | 0.075 | .cache/phase10-quality/commands/20261107T193947-657f9f |
| 2026-11-07T19:39:47.759983+00:00 | `.venv-phase2/bin/python .cache/phase10-quality/run-scenario.py SC-01-D` | 0 | 14.964 | .cache/phase10-quality/commands/20261107T193947-8f799d |
| 2026-11-07T19:41:00.881940+00:00 | `.venv-phase2/bin/python .cache/phase10-quality/restart-d.py before` | 0 | 0.429 | .cache/phase10-quality/commands/20261107T194100-a7f9db |
| 2026-11-07T19:41:01.359541+00:00 | `python3 scripts/docker.py compose restart api` | 0 | 2.077 | .cache/phase10-quality/commands/20261107T194101-6df281 |
| 2026-11-07T19:41:03.568585+00:00 | `.venv-phase2/bin/python .cache/phase10-quality/restart-d.py after` | 0 | 4.737 | .cache/phase10-quality/commands/20261107T194103-d0ad3e |
| 2026-11-07T19:41:08.371876+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10-quality/live/SC-01-D` | 0 | 6.282 | .cache/phase10-quality/commands/20261107T194108-25043d |
| 2026-11-07T19:41:41.395672+00:00 | `.venv-phase2/bin/python .cache/phase10-quality/run-scenario.py SC-01-E` | 0 | 13.306 | .cache/phase10-quality/commands/20261107T194141-851caa |
| 2026-11-07T19:42:36.038592+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10-quality/live/SC-01-E` | 1 | 10.33 | .cache/phase10-quality/commands/20261107T194236-096941 |
| 2026-11-07T19:43:11.640477+00:00 | `python3 .cache/phase10-quality/safe-logs.py` | 0 | 0.774 | .cache/phase10-quality/commands/20261107T194311-b11dbf |
| 2026-11-07T19:43:12.463094+00:00 | `python3 .cache/phase10-quality/runtime-check.py` | 0 | 0.502 | .cache/phase10-quality/commands/20261107T194312-c3b2e6 |
| 2026-11-07T19:43:13.013708+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase10-quality/preservation.py after` | 0 | 12.141 | .cache/phase10-quality/commands/20261107T194313-c17edc |
| 2026-11-07T19:43:54.002806+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10-quality/live/SC-01-E` | 1 | 10.839 | .cache/phase10-quality/commands/20261107T194354-edd2d5 |
| 2026-11-07T19:45:44.901538+00:00 | `node --input-type=module -e 'import {issue} from "./frontend/src/lib.ts"; import assert from "node:assert/strict"; assert.match(issue("model_timeout"),/took too long/);'` | 1 | 0.39 | .cache/phase10-quality/commands/20261107T194544-10759d |
| 2026-11-07T19:45:45.340470+00:00 | `git diff --check` | 0 | 0.096 | .cache/phase10-quality/commands/20261107T194545-e17753 |
| 2026-11-07T19:45:45.483376+00:00 | `git diff --cached --exit-code` | 0 | 0.023 | .cache/phase10-quality/commands/20261107T194545-2b77be |
