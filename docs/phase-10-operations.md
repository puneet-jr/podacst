# Phase10 execution and resume

Current task uses the full local working tree and docs/regression-2026-11-07.md as baseline. Phase11/publication is not authorized. The exact pinned corpus already exists locally; all303 transcript hashes and source checkout revision were verified before ingestion. Do not refetch or overwrite it.

One serial ingestion process, batch size4 (one API request in flight),20s per-call timeout, at most3 finite attempts,180s per episode and3600s per run. Host Mac Ollama stays running. No cloud inference or model downloads. Resume a stopped/failed partial run with the same exact command; committed episodes skip and incomplete episodes retry atomically:

```sh
python3 scripts/capture_phase10.py python3 scripts/docker.py compose exec -T api python -m backend.ingest --root /corpus/be8ab89a890a833cbba2c892178f823fff178c65 --batch-size 4 --deadline-seconds 3600
```

Do not run two writers. A repeat of this command after completion is the idempotency check. Never reset/drop the normal database or remove volumes. Preserve earlier nine indexed episodes and all sessions/artifacts; pre-ingestion hashes are private .cache/phase10/db-before.json. Ingestion metadata/counts are not answer-quality results.

`scripts/capture_phase10.py` captures actual UTC stdout and diagnostics to separate bounded-line JSONL files in ignored .cache/phase10/commands and writes command metadata only to docs/agent-transcripts/phase-10/commands.jsonl. Raw source/model payloads stay private. Do not publish logs without secret/content review.

After verified ingestion: invoke `scripts/live_phase10.py scenarios --scenario SC-01-A` (then B,C,D,E) under the existing .venv-phase2 with one case at a time; read actual output/passages and run `scripts/browser_phase10.py --run .cache/phase10/live/first/SC-01-A` before completing that case's timed review. These runners never automatically award semantic passes. Exact frozen inputs/caps and follow-up/isolation requirements are in phase-10 scenario-protocol.json and docs/scenario-inputs.json. Keep raw and post-fix outcomes distinct; --attempt post-fix writes a separate directory. `quality` runs the preregistered10 answerable plus3 supplementary new-source cases plus4 unsupported cases, with90s per request and no automatic retries.

SC-01-D requires a controlled application restart/reopen proof. Perform it only when no model operation or test suite runs, snapshot the relevant saved API bodies first, and compare after readiness. Do not stop normal PostgreSQL or Ollama. Copy ephemeral /app/evidence/phase10 audits/evaluations to ignored host storage before a container recreation.

Retrieval evaluation retains the frozen v3 config and labels. Its original judgment scope describes nine source episodes; actual retrieved corpus counts must be reported separately for the current index. Held-out questions have been observed previously: label Phase10 execution as a rerun, not an unseen holdout. Keep all raw evaluation attempts and identify misses against the85% target honestly.


Completed full ingest and identical repeat both passed;see phase-10-report.md. Initial per-episode polling snapshot `.cache/phase10/ingestion-progress.json` stops at84/303 and is a historical intermediate observation,not final state. Final ingestion_result events,DB audits and `ingestion-results.json` are authoritative.

If the quality helper stops before inference,retain its directory/error and select only never-generated cases with repeated `--quality-case T04` (etc). Never overwrite a completed run or silently retry a model response. Helpers now retain readiness response bodies. Actual initial T04 preflight failure was archived separately;completed T01 was preserved.

Frozen five-case score0/5;post-fix C/E remainfailed. No automatic release acceptance from exit0. Original corpus/records retained and only dedicated Phase10 live sessions added. Stop before Prompt11.
