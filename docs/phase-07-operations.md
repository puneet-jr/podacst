# Phase 7 operations

Use `python3 scripts/bootstrap.py` after prerequisites. Host Ollama remains outside Docker. Chat uses GENERATION_MODEL (qwen3:0.6b); essays use ESSAY_MODEL (qwen3:1.7b). There is no cloud fallback. Apply current migrations without deleting volumes.

Standard workflow:

1. POST /api/sessions/{sid}/essays with typed topic/audience/constraints/client_message_id. Stream NDJSON progress. Requests and partial/failed drafts persist. One generation lease, fresh Pi histories and bounded lifecycle remain enforced.
2. GET /api/sessions/{sid}/essays/{rid} and /sources. Inspect actual evidence; count/IDs do not prove relevance/support. A weak packet with fewer than six usable source sections reports insufficient evidence.
3. Explicit editorial changes use POST /essays/{rid}/advice (`sections` maps1-based indices to text) or /evidence (`sections` maps indices to lists of `{start,end}` offsets). Evidence text is derived from the existing owned snapshot. All before/after changes remain logged. No completed essay can be silently edited.
4. POST /essays/{rid}/review. All rubric booleans plus deterministic validation must pass before the assistant reply is accepted.
5. In the same session, Save Markdown / Save HTML from an accepted reply. POST /artifacts accepts message_id/format; duplicate creates replay the same artifact. GET /artifacts, /{id}, /{id}/sources/{S-label} enforce ownership. Ordinary chat replies can also be saved, with their own provenance label.

Artifacts preserve message/citation identity and format deterministically. HTML exports are complete static documents with inline CSS; model text does not get a second factual rewrite. Preview supports paragraphs/headings/lists/quotes/emphasis/tables/code and constrained presentation styles. Raw HTML in Markdown, links/images, scripts/forms/embedded frames, navigation and remote resources are disabled. Original-source links are available only through the parent source inspector.

Verification commands used (all actual outcomes in phase-07/commands.jsonl):

- `python3 scripts/capture_phase7.py npm --prefix frontend run build`
- `python3 scripts/capture_phase7.py python3 scripts/docker.py compose build api web`
- `python3 scripts/capture_phase7.py python3 scripts/docker.py compose run --rm --no-deps api python -m backend.contract_check` (fresh retained DB; does not destroy the normal one).
- `PYTHONPATH=. python3 scripts/capture_phase7.py .venv-phase2/bin/python scripts/browser_phase7.py` (labelled old fixture + hostile browser cases; no generation).
- `python3 scripts/capture_phase7.py .venv-phase2/bin/python scripts/live_phase7.py` (one actual fresh endpoint run; refuses duplicate attempts).
- `PYTHONPATH=. python3 scripts/capture_phase7.py .venv-phase2/bin/python scripts/review_phase7.py` (documented explicit edits/review of that saved run, not inference; do not blindly rerun on a different draft).
- `python3 scripts/capture_phase7.py .venv-phase2/bin/python scripts/reopen_phase7.py` (API/web restart only, actual source/hash/browser reopen).

Browser checks use host-only pinned tooling and a fresh Chrome profile. The in-app connector is separately blocked during bootstrap. Review docs/phase-07-report.md before interpreting fixture/rendering, mocked DB tests or the manually edited live result as autonomous generation proof. Stop before Phase8.
