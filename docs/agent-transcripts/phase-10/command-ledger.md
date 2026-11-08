# Phase10 exact captured commands

Generated from actual command metadata; UTC start, monotonic seconds, actual exit. Exit0 of a live runner/evaluator is transport/protocol completion, not semantic acceptance. Stdout/stderr remain separate private JSONL under each stream directory. This is a command ledger, not a reconstructed conversation.

| UTC start | Exact command (after `python3 scripts/capture_phase10.py`) | Exit | Seconds | Private stream directory |
| --- | --- | ---: | ---: | --- |
| 2026-11-07T12:25:54.952612+00:00 | `.venv-phase2/bin/python .cache/phase10/host-preflight.py` | 0 | 10.101 | .cache/phase10/commands/20261107T122554-97eeee |
| 2026-11-07T12:26:41.704914+00:00 | `python3 scripts/docker.py compose exec -T api mkdir -p /app/evidence/phase10` | 0 | 0.726 | .cache/phase10/commands/20261107T122641-700160 |
| 2026-11-07T12:26:42.485538+00:00 | `python3 scripts/docker.py compose cp .cache/phase10/db-audit.py api:/app/evidence/phase10/db-audit.py` | 0 | 0.257 | .cache/phase10/commands/20261107T122642-e45bcf |
| 2026-11-07T12:26:42.805347+00:00 | `python3 scripts/docker.py compose exec -T api python /app/evidence/phase10/db-audit.py before` | 1 | 0.958 | .cache/phase10/commands/20261107T122642-29a9dd |
| 2026-11-07T12:27:03.698869+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase10/db-audit.py before` | 0 | 3.811 | .cache/phase10/commands/20261107T122703-8e2a13 |
| 2026-11-07T12:27:07.557009+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10/before.json .cache/phase10/db-before.json` | 0 | 0.174 | .cache/phase10/commands/20261107T122707-30ab22 |
| 2026-11-07T12:36:38.157623+00:00 | `python3 scripts/docker.py compose cp .cache/phase10/saved-records.py api:/app/evidence/phase10/saved-records.py` | 0 | 1.399 | .cache/phase10/commands/20261107T123638-1e547e |
| 2026-11-07T12:36:40.058642+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase10/saved-records.py before` | 0 | 6.548 | .cache/phase10/commands/20261107T123640-4f545c |
| 2026-11-07T12:36:46.852285+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10/saved-rows-before.json .cache/phase10/saved-rows-before.json` | 0 | 1.099 | .cache/phase10/commands/20261107T123646-97ff01 |
| 2026-11-07T12:38:34.617885+00:00 | `.venv-phase2/bin/python -m unittest discover -s eval -p test_metrics.py -v` | 0 | 0.955 | .cache/phase10/commands/20261107T123834-cb489f |
| 2026-11-07T12:41:28.611169+00:00 | `.venv-phase2/bin/python -m unittest backend.tests.test_scope_paths -v` | 1 | 1.559 | .cache/phase10/commands/20261107T124128-34fc7c |
| 2026-11-07T12:41:49.936937+00:00 | `.venv-phase2/bin/python -m unittest backend.tests.test_scope_paths -v` | 1 | 3.759 | .cache/phase10/commands/20261107T124149-adaa45 |
| 2026-11-07T12:42:20.117344+00:00 | `.venv-phase2/bin/python -m unittest backend.tests.test_scope_paths -v` | 0 | 0.584 | .cache/phase10/commands/20261107T124220-bbc3d0 |
| 2026-11-07T12:43:38.283569+00:00 | `.venv-phase2/bin/python .cache/phase10/scope-compatibility.py` | 0 | 2.53 | .cache/phase10/commands/20261107T124338-d71636 |
| 2026-11-07T12:45:31.042591+00:00 | `.venv-phase2/bin/python .cache/phase10/pagination-check.py` | 1 | 24.097 | .cache/phase10/commands/20261107T124531-6eea29 |
| 2026-11-07T12:46:47.932993+00:00 | `npm --prefix frontend run typecheck` | 0 | 5.356 | .cache/phase10/commands/20261107T124647-bf7270 |
| 2026-11-07T12:46:53.424667+00:00 | `npm --prefix frontend run build` | 0 | 7.002 | .cache/phase10/commands/20261107T124653-9d3829 |
| 2026-11-07T12:47:37.543325+00:00 | `python3 scripts/docker.py compose build web` | 0 | 30.947 | .cache/phase10/commands/20261107T124737-73f369 |
| 2026-11-07T12:48:08.659726+00:00 | `python3 scripts/docker.py compose up -d --no-deps web` | 0 | 3.993 | .cache/phase10/commands/20261107T124808-72e09b |
| 2026-11-07T12:48:12.777747+00:00 | `.venv-phase2/bin/python .cache/phase10/pagination-check.py` | 0 | 13.659 | .cache/phase10/commands/20261107T124812-83d77e |
| 2026-11-07T12:51:13.702811+00:00 | `.venv-phase2/bin/python scripts/browser_sessions.py` | 0 | 12.438 | .cache/phase10/commands/20261107T125113-b73b60 |
| 2026-11-07T12:51:31.730601+00:00 | `node --test frontend/test-source-span.mjs` | 0 | 0.718 | .cache/phase10/commands/20261107T125131-0700ef |
| 2026-11-07T12:51:32.733327+00:00 | `node --test agent/test_provider_policy.ts agent/test_conversation_policy.ts agent/test_essay_format.ts` | 0 | 0.685 | .cache/phase10/commands/20261107T125132-cd0032 |
| 2026-11-07T12:53:37.837828+00:00 | `python3 scripts/docker.py compose cp .cache/phase10/saved-records.py api:/app/evidence/phase10/saved-records.py` | 0 | 0.657 | .cache/phase10/commands/20261107T125337-be4e3b |
| 2026-11-07T12:53:38.549061+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase10/saved-records.py before` | 0 | 5.471 | .cache/phase10/commands/20261107T125338-7102d2 |
| 2026-11-07T12:53:44.178915+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10/saved-rows-before.json .cache/phase10/saved-rows-before.json` | 0 | 0.985 | .cache/phase10/commands/20261107T125344-be0257 |
| 2026-11-07T12:54:32.675802+00:00 | `.venv-phase2/bin/python .cache/phase10/models.py` | 0 | 0.383 | .cache/phase10/commands/20261107T125432-0b90a2 |
| 2026-11-07T12:56:03.397949+00:00 | `.venv-phase2/bin/python scripts/browser_sessions.py` | 1 | 17.489 | .cache/phase10/commands/20261107T125603-2695a4 |
| 2026-11-07T12:57:23.931798+00:00 | `npm --prefix frontend run typecheck` | 0 | 4.827 | .cache/phase10/commands/20261107T125723-bda7cf |
| 2026-11-07T12:57:28.880593+00:00 | `npm --prefix frontend run build` | 0 | 8.827 | .cache/phase10/commands/20261107T125728-0767cd |
| 2026-11-07T12:57:42.384165+00:00 | `python3 scripts/docker.py compose build web` | 0 | 21.543 | .cache/phase10/commands/20261107T125742-984e62 |
| 2026-11-07T12:58:04.155042+00:00 | `python3 scripts/docker.py compose up -d --no-deps web` | 0 | 4.285 | .cache/phase10/commands/20261107T125804-a548e5 |
| 2026-11-07T12:58:08.579954+00:00 | `.venv-phase2/bin/python scripts/browser_sessions.py` | 0 | 35.076 | .cache/phase10/commands/20261107T125808-4fa8d0 |
| 2026-11-07T13:00:07.659510+00:00 | `python3 scripts/docker.py compose cp .cache/phase10/db-audit.py api:/app/evidence/phase10/db-audit.py` | 0 | 1.929 | .cache/phase10/commands/20261107T130007-110533 |
| 2026-11-07T13:06:46.818086+00:00 | `python3 scripts/docker.py compose build api` | 0 | 10.552 | .cache/phase10/commands/20261107T130646-bb3486 |
| 2026-11-07T12:27:20.611700+00:00 | `python3 scripts/docker.py compose exec -T api python -m backend.ingest --root /corpus/be8ab89a890a833cbba2c892178f823fff178c65 --batch-size 4 --deadline-seconds 3600` | 0 | 2640.056 | .cache/phase10/commands/20261107T122720-deeed8 |
| 2026-11-07T13:11:39.625723+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase10/db-audit.py after` | 0 | 7.36 | .cache/phase10/commands/20261107T131139-cc949d |
| 2026-11-07T13:11:47.078824+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10/after.json .cache/phase10/after-first.json` | 0 | 1.07 | .cache/phase10/commands/20261107T131147-327822 |
| 2026-11-07T13:11:48.225210+00:00 | `python3 scripts/docker.py compose exec -T api python -m backend.ingest --root /corpus/be8ab89a890a833cbba2c892178f823fff178c65 --batch-size 4 --deadline-seconds 3600` | 0 | 3.506 | .cache/phase10/commands/20261107T131148-7de506 |
| 2026-11-07T13:11:51.811351+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase10/db-audit.py after-repeat` | 0 | 3.339 | .cache/phase10/commands/20261107T131151-07fab9 |
| 2026-11-07T13:11:55.207333+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10/after-repeat.json .cache/phase10/after-repeat.json` | 0 | 0.244 | .cache/phase10/commands/20261107T131155-9ae09c |
| 2026-11-07T13:11:55.501560+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10 .cache/phase10/runtime-audits` | 0 | 0.18 | .cache/phase10/commands/20261107T131155-7ebd71 |
| 2026-11-07T13:13:05.488398+00:00 | `python3 scripts/docker.py compose up -d --no-deps api` | 0 | 3.229 | .cache/phase10/commands/20261107T131305-a33f91 |
| 2026-11-07T13:13:08.781593+00:00 | `.venv-phase2/bin/python .cache/phase10/ready.py` | 0 | 5.101 | .cache/phase10/commands/20261107T131308-351ec2 |
| 2026-11-07T13:13:13.985428+00:00 | `.venv-phase2/bin/python scripts/live_phase10.py scenarios --scenario SC-01-A` | 0 | 8.604 | .cache/phase10/commands/20261107T131313-3b4922 |
| 2026-11-07T13:14:09.765117+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10/live/first/SC-01-A` | 1 | 36.204 | .cache/phase10/commands/20261107T131409-fbb17c |
| 2026-11-07T13:15:07.125926+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10/live/first/SC-01-A` | 0 | 6.152 | .cache/phase10/commands/20261107T131507-a628c2 |
| 2026-11-07T13:15:54.070733+00:00 | `.venv-phase2/bin/python scripts/live_phase10.py scenarios --scenario SC-01-B` | 0 | 27.788 | .cache/phase10/commands/20261107T131554-dbf587 |
| 2026-11-07T13:17:40.672962+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10/live/first/SC-01-B` | 0 | 7.149 | .cache/phase10/commands/20261107T131740-340d72 |
| 2026-11-07T13:18:00.858809+00:00 | `.venv-phase2/bin/python scripts/live_phase10.py scenarios --scenario SC-01-C` | 0 | 49.942 | .cache/phase10/commands/20261107T131800-b88431 |
| 2026-11-07T13:23:35.738352+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10/live/first/SC-01-C` | 0 | 8.587 | .cache/phase10/commands/20261107T132335-b52058 |
| 2026-11-07T13:26:03.318742+00:00 | `.venv-phase2/bin/python scripts/live_phase10.py scenarios --scenario SC-01-D` | 0 | 17.64 | .cache/phase10/commands/20261107T132603-3602f8 |
| 2026-11-07T13:26:56.791206+00:00 | `.venv-phase2/bin/python .cache/phase10/restart-scenario-d.py before` | 0 | 0.446 | .cache/phase10/commands/20261107T132656-27f17b |
| 2026-11-07T13:26:57.286860+00:00 | `python3 scripts/docker.py compose restart api` | 0 | 2.047 | .cache/phase10/commands/20261107T132657-ea5deb |
| 2026-11-07T13:26:59.410558+00:00 | `.venv-phase2/bin/python .cache/phase10/restart-scenario-d.py after` | 0 | 3.626 | .cache/phase10/commands/20261107T132659-814bd6 |
| 2026-11-07T13:27:03.113983+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10/live/first/SC-01-D` | 1 | 18.982 | .cache/phase10/commands/20261107T132703-982369 |
| 2026-11-07T13:28:30.984427+00:00 | `.venv-phase2/bin/python scripts/live_phase10.py scenarios --scenario SC-01-E` | 0 | 18.598 | .cache/phase10/commands/20261107T132830-62b432 |
| 2026-11-07T13:32:37.177308+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10/live/first/SC-01-E` | 1 | 9.483 | .cache/phase10/commands/20261107T133237-d717ad |
| 2026-11-07T13:51:43.262121+00:00 | `python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval --split tuning --config eval/retrieval-local-v3.json --output /app/evidence/phase10/eval-tuning-first` | 1 | 8.047 | .cache/phase10/commands/20261107T135143-6d44e5 |
| 2026-11-07T13:54:05.561734+00:00 | `python3 scripts/docker.py compose cp .cache/phase10/sql-probe.py api:/app/evidence/sql-probe.py` | 0 | 0.603 | .cache/phase10/commands/20261107T135405-76dd22 |
| 2026-11-07T13:54:06.216364+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/sql-probe.py` | 1 | 4.533 | .cache/phase10/commands/20261107T135406-5d79af |
| 2026-11-07T13:55:32.833709+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10/live/first/SC-01-D` | 0 | 6.319 | .cache/phase10/commands/20261107T135532-78b414 |
| 2026-11-07T13:56:59.898260+00:00 | `python3 scripts/docker.py compose cp .cache/phase10/lexical-cte.sql api:/app/evidence/lexical-cte.sql` | 0 | 0.565 | .cache/phase10/commands/20261107T135659-a72e04 |
| 2026-11-07T13:57:00.518171+00:00 | `python3 scripts/docker.py compose cp .cache/phase10/sql-probe-precomputed.py api:/app/evidence/sql-probe-precomputed.py` | 0 | 0.172 | .cache/phase10/commands/20261107T135700-a2015b |
| 2026-11-07T13:57:00.737880+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/sql-probe-precomputed.py` | 0 | 3.335 | .cache/phase10/commands/20261107T135700-8401c9 |
| 2026-11-07T13:57:04.131737+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10 .cache/phase10/query-diagnostics` | 0 | 0.202 | .cache/phase10/commands/20261107T135704-e4272d |
| 2026-11-07T13:57:13.643464+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10/live/first/SC-01-E` | 0 | 5.437 | .cache/phase10/commands/20261107T135713-7789a6 |
| 2026-11-07T13:59:14.774844+00:00 | `python3 scripts/docker.py compose cp .cache/phase10/sql-probe-nojit.py api:/app/evidence/sql-probe-nojit.py` | 0 | 0.518 | .cache/phase10/commands/20261107T135914-9da1dd |
| 2026-11-07T13:59:15.341174+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/sql-probe-nojit.py` | 0 | 2.051 | .cache/phase10/commands/20261107T135915-02e467 |
| 2026-11-07T13:59:17.445366+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10 .cache/phase10/query-diagnostics-nojit` | 0 | 0.209 | .cache/phase10/commands/20261107T135917-748d57 |
| 2026-11-07T14:01:24.141709+00:00 | `.venv-phase2/bin/python -m unittest backend.tests.test_evidence_first backend.tests.test_scope_paths -v` | 0 | 0.801 | .cache/phase10/commands/20261107T140124-fe0a53 |
| 2026-11-07T14:01:25.001135+00:00 | `python3 scripts/docker.py compose build api` | 0 | 4.639 | .cache/phase10/commands/20261107T140125-064a32 |
| 2026-11-07T14:02:53.096979+00:00 | `python3 scripts/docker.py compose run --rm --no-deps -e DEFAULT_PROVIDER=ollama -e OPENROUTER_API_KEY= -e ANTHROPIC_API_KEY= api python -m backend.contract_check` | 0 | 42.779 | .cache/phase10/commands/20261107T140253-ee2b7e |
| 2026-11-07T14:05:37.565349+00:00 | `python3 scripts/docker.py compose up -d --no-deps api` | 0 | 3.298 | .cache/phase10/commands/20261107T140537-a1e836 |
| 2026-11-07T14:05:41.136609+00:00 | `.venv-phase2/bin/python .cache/phase10/ready.py` | 0 | 8.503 | .cache/phase10/commands/20261107T140541-2f4e41 |
| 2026-11-07T14:05:49.778290+00:00 | `python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval --split tuning --config eval/retrieval-local-v3.json --output /app/evidence/phase10/eval-tuning-after-query-fix` | 0 | 33.321 | .cache/phase10/commands/20261107T140549-7fa247 |
| 2026-11-07T14:06:23.279417+00:00 | `python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval --split held_out --config eval/retrieval-local-v3.json --output /app/evidence/phase10/eval-held-out-after-query-fix` | 0 | 14.81 | .cache/phase10/commands/20261107T140623-81350a |
| 2026-11-07T14:06:38.413359+00:00 | `python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval --split unsupported --config eval/retrieval-local-v3.json --output /app/evidence/phase10/eval-unsupported-after-query-fix` | 0 | 13.098 | .cache/phase10/commands/20261107T140638-d0514e |
| 2026-11-07T14:06:51.817114+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10 .cache/phase10/evaluations-after-query-fix` | 0 | 1.025 | .cache/phase10/commands/20261107T140651-05e848 |
| 2026-11-07T14:10:51.112203+00:00 | `.venv-phase2/bin/python scripts/live_phase10.py quality` | 1 | 23.234 | .cache/phase10/commands/20261107T141051-bc4192 |
| 2026-11-07T14:11:35.949308+00:00 | `.venv-phase2/bin/python -c 'import httpx,json; r=httpx.get("http://127.0.0.1:8080/api/health/ready",timeout=30,trust_env=False); print(r.status_code); print(json.dumps(r.json(),indent=2))'` | 0 | 1.721 | .cache/phase10/commands/20261107T141135-f8b44e |
| 2026-11-07T14:11:02.477659+00:00 | `.venv-phase2/bin/python .cache/phase10/release-regression.py` | 0 | 47.344 | .cache/phase10/commands/20261107T141102-eb984e |
| 2026-11-07T14:12:58.691978+00:00 | `.venv-phase2/bin/python .cache/phase10/home-check.py` | 1 | 42.583 | .cache/phase10/commands/20261107T141258-75733d |
| 2026-11-07T14:12:08.187048+00:00 | `.venv-phase2/bin/python scripts/live_phase10.py quality --quality-case T04 --quality-case T07 --quality-case T09 --quality-case T11 --quality-case T13 --quality-case T15 --quality-case H17 --quality-case H21 --quality-case H24 --quality-case N01 --quality-case N02 --quality-case N03 --quality-case U01 --quality-case U02 --quality-case U03 --quality-case U04` | 0 | 126.905 | .cache/phase10/commands/20261107T141208-f0c38b |
| 2026-11-07T14:14:20.411394+00:00 | `.venv-phase2/bin/python .cache/phase10/home-check.py` | 0 | 6.734 | .cache/phase10/commands/20261107T141420-dd751d |
| 2026-11-07T14:14:36.075917+00:00 | `.venv-phase2/bin/python scripts/live_phase10.py scenarios --scenario SC-01-C --attempt post-fix` | 0 | 42.814 | .cache/phase10/commands/20261107T141436-32a746 |
| 2026-11-07T14:15:48.960272+00:00 | `python3 .cache/phase10/review-quality.py` | 0 | 0.138 | .cache/phase10/commands/20261107T141548-5c0537 |
| 2026-11-07T14:16:05.627522+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10/live/post-fix/SC-01-C` | 0 | 9.718 | .cache/phase10/commands/20261107T141605-46b5ff |
| 2026-11-07T14:16:57.519293+00:00 | `python3 .cache/phase10/review-post-essay.py` | 0 | 0.128 | .cache/phase10/commands/20261107T141657-20de16 |
| 2026-11-07T14:16:56.133211+00:00 | `.venv-phase2/bin/python scripts/live_phase10.py scenarios --scenario SC-01-E --attempt post-fix` | 0 | 21.663 | .cache/phase10/commands/20261107T141656-be030a |
| 2026-11-07T14:17:29.084415+00:00 | `.venv-phase2/bin/python scripts/browser_phase10.py --run .cache/phase10/live/post-fix/SC-01-E` | 0 | 7.69 | .cache/phase10/commands/20261107T141729-d32015 |
| 2026-11-07T14:17:59.319550+00:00 | `npm --prefix frontend run typecheck` | 0 | 2.413 | .cache/phase10/commands/20261107T141759-0c3072 |
| 2026-11-07T14:18:01.786232+00:00 | `npm --prefix frontend run build` | 0 | 2.816 | .cache/phase10/commands/20261107T141801-44ea4e |
| 2026-11-07T14:18:04.657216+00:00 | `node --test frontend/test-source-span.mjs` | 0 | 0.2 | .cache/phase10/commands/20261107T141804-1918ae |
| 2026-11-07T14:18:04.907303+00:00 | `node --test agent/test_provider_policy.ts agent/test_conversation_policy.ts agent/test_essay_format.ts` | 0 | 0.23 | .cache/phase10/commands/20261107T141804-8b507a |
| 2026-11-07T14:18:03.995114+00:00 | `python3 .cache/phase10/runtime-check.py` | 0 | 1.343 | .cache/phase10/commands/20261107T141803-2c5218 |
| 2026-11-07T14:18:05.394729+00:00 | `python3 scripts/docker.py compose cp .cache/phase10/db-before.json api:/app/evidence/phase10/before.json` | 0 | 0.321 | .cache/phase10/commands/20261107T141805-7f987e |
| 2026-11-07T14:18:05.205434+00:00 | `.venv-phase2/bin/python -m unittest discover -s eval -p test_metrics.py -v` | 0 | 0.772 | .cache/phase10/commands/20261107T141805-f5eecd |
| 2026-11-07T14:18:05.767743+00:00 | `python3 scripts/docker.py compose cp .cache/phase10/db-audit.py api:/app/evidence/phase10/db-audit.py` | 0 | 0.215 | .cache/phase10/commands/20261107T141805-48a085 |
| 2026-11-07T14:18:06.036874+00:00 | `python3 scripts/docker.py compose cp .cache/phase10/saved-rows-before.json api:/app/evidence/phase10/saved-rows-before.json` | 0 | 0.295 | .cache/phase10/commands/20261107T141806-24bf9a |
| 2026-11-07T14:18:06.386980+00:00 | `python3 scripts/docker.py compose cp .cache/phase10/saved-records.py api:/app/evidence/phase10/saved-records.py` | 0 | 0.193 | .cache/phase10/commands/20261107T141806-2b0115 |
| 2026-11-07T14:18:06.625184+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase10/saved-records.py after` | 0 | 2.371 | .cache/phase10/commands/20261107T141806-ebc3f3 |
| 2026-11-07T14:18:09.082741+00:00 | `python3 scripts/docker.py compose exec -T -e PYTHONPATH=/app api python /app/evidence/phase10/db-audit.py after-live` | 0 | 5.649 | .cache/phase10/commands/20261107T141809-67dea3 |
| 2026-11-07T14:18:14.792822+00:00 | `python3 scripts/docker.py compose cp api:/app/evidence/phase10/after-live.json .cache/phase10/after-live.json` | 0 | 0.292 | .cache/phase10/commands/20261107T141814-300423 |
| 2026-11-07T14:18:15.135426+00:00 | `.venv-phase2/bin/python .cache/phase10/ready.py` | 0 | 1.415 | .cache/phase10/commands/20261107T141815-cdf370 |
| 2026-11-07T14:19:04.731282+00:00 | `python3 -c 'import json,shutil,subprocess; print(json.dumps({"disk_free_bytes":shutil.disk_usage(".").free,"memory_bytes":subprocess.check_output(["sysctl","-n","hw.memsize"],text=True).strip(),"swap":subprocess.check_output(["sysctl","-n","vm.swapusage"],text=True).strip()}))'` | 0 | 0.074 | .cache/phase10/commands/20261107T141904-a7fe77 |
| 2026-11-07T14:25:14.313117+00:00 | `python3 .cache/phase10/hygiene.py` | 0 | 0.479 | .cache/phase10/commands/20261107T142514-8af116 |
| 2026-11-07T14:25:45.439160+00:00 | `git diff --check` | 0 | 0.101 | .cache/phase10/commands/20261107T142545-ab8a18 |
| 2026-11-07T14:25:45.695263+00:00 | `git diff --cached --exit-code` | 0 | 0.027 | .cache/phase10/commands/20261107T142545-fdd753 |
