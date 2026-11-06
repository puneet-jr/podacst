# Local transcript ingestion

Run from the repository root with the Phase 2 Docker/host Ollama prerequisites. Keep the existing Mac Ollama service running; no cloud fallback exists. [Phase 3 report](phase-03-report.md) distinguishes actual smoke evidence from implemented full-ingestion capability.

## Snapshot and start

```sh
# Once only; refuses to overwrite an existing snapshot.
python3 scripts/fetch_corpus.py --revision be8ab89a890a833cbba2c892178f823fff178c65
python3 scripts/bootstrap.py
python3 scripts/docker.py compose exec -T api python -m backend.ingest \
  --root /corpus/be8ab89a890a833cbba2c892178f823fff178c65 --limit 3
```

An existing snapshot is reused by passing its root to ingestion, not refetched. `.cache/corpus/<SHA>.manifest.json` records complete discovered paths and byte hashes; missing/added/modified files are rejected. The runtime sees `/corpus` read-only. Do not change the snapshot or its manifest to simulate refresh. Fetch another exact upstream revision into its own folder when an update is desired. There is no source push or arbitrary user-supplied URL fetch route.

Inspect actual status at `http://localhost:8000/api/ingestion/status` or in the workspace status panel. Structured `embedding_progress`, `episode_loaded`, `episode_unchanged`, `episode_failed` and `ingestion_result` events expose progress without raw transcript text or vectors. `discovered` is the complete manifest size; `selected` is this run's limit; `loaded`, `skipped`, `failed`, `deleted` are per-run outcomes; `active_episodes/chunks` are current DB totals. A successful limit run remains `partial`. `pending_items` covers selected files not yet attempted; a preflight failure leaves those pending with an explicit run error rather than counting them as loaded.

The full command omits `--limit` and may use `--deadline-seconds 3600` (default 600). **It was not run at this gate.** Do not run multiple ingestion commands concurrently. A second writer returns `ingestion_busy`. Retained test DBs are isolated from the application and existing host databases. Never run `down -v`, drop a normal database or reset a volume.

## Bounds, resume and refresh

Default batch size four, allowed 1–8. Each call has a 20 s ceiling, at most three attempts, bounded backoff; HTTP 400/schema/vector/model failures are not silently retried/truncated. The per-episode budget is 180 s and the run budget 600 s by default, configurable up to 3,600 s. Metadata preflight/identity probes have their own finite client timeout. Actual input uses `search_document: `, `truncate=false`, model context 2,048 and keep-alive two minutes. Future query embeddings must use the model's `search_query: ` prefix.

Resume by running the same command again. Completed source/pipeline/model fingerprints skip without generating duplicate chunks; failed episodes retry from their start, not from an unsafe partially published vector set. At the next exclusive run, an abandoned `running` record becomes `interrupted`. Its committed episodes remain usable; uncommitted work is absent. There is no promise of resuming within an episode or forcibly canceling a host model operation. Termination closes the CLI process/DB connection; publication uses normal transaction rollback and the next run repairs status.

Each changed episode is fully parsed/embedded first. A single DB transaction stores its immutable original/version, inserts all new chunks, deactivates old chunks, advances the episode pointer and records its loaded outcome. Failure before publication retains the old active version. Deletions compare against the **entire validated manifest**, even with `--limit`, and retire the episode/chunks without erasing exact prior evidence referenced by saved answers. An empty/incomplete manifest is refused. Partial ingestion is episode-atomic, not a whole-corpus all-or-nothing refresh.

Only `chunks.active=true` may become searchable later. Preserve episode version and exact evidence alongside saved source associations. No product search endpoint exists yet.

## Identity and source semantics

The selected existing local model is `nomic-embed-text:latest`, digest `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`, 768 dimensions, document prefix `search_document: `. A mutable model tag alone is insufficient: preflight checks installed identity, embedding capability, native dimension and an actual vector probe. The DB pins the first successful profile, and publication checks it again. A changed model/digest/prefix is refused even if its dimensions match. A new profile needs an explicit versioned index/re-embedding design; changing an environment value is not an index migration.

Original UTF-8 including line endings/Unicode is preserved, with a separate normalized search representation. Offsets use Python/PostgreSQL characters, zero-based start and exclusive end; line numbers are one-based. Source SHA-256 hashes the original bytes. Stable episode UUID5 uses source URL/path; chunk UUID5 includes episode version, ordinal and fingerprint. Guest/title/date/video metadata is retained, with nullable values and warnings rather than guessed facts.

The parser uses a restricted SafeLoader, no YAML aliases, duplicate keys or arbitrary constructors. Timestamp-only continuation inherits the last known speaker; bracket format and speaker-only sources are supported; unknown timing stays null. A chunk's end marker is the last observed marker, not an inferred speech end. Sentence/turn grouping targets 550, caps 700 **estimated** tokens, allows at most 80 estimated overlap and splits oversized turns. Short tails occur. Exact contiguous slices can include intervening speaker headers; source spans remain authoritative.

Sponsor flags match phrases such as “brought to you by,” “sponsored by” and “our sponsor.” They annotate rather than delete passages. They can miss ads or flag discussion about sponsors; future retrieval must handle this and manually reviewed sponsor traps. A guest/title mismatch flag is a review hint, not a corrected attribution. Source text never supplies executable instructions.

## Reproduce checks and inspect failures

```sh
python3 scripts/docker.py compose exec -T api python -m backend.contract_check
python3 scripts/docker.py compose exec -T api python -m backend.ingestion_check
.venv-phase2/bin/python scripts/verify_corpus_smoke.py
```

Run sequentially; do not recreate the API during a check. The first creates a fresh retained contract DB, the second a fresh retained synthetic-fixture DB with actual local embeddings, the third uses the three real corpus files in the normal isolated app DB. Repeated smoke runs may legitimately skip already indexed episodes. No database cleanup is automatic. Record safe future commands with `python3 scripts/capture_phase3.py ...` only when they cannot print secrets. Capture stdout/stderr separately; never dump `.env`, resolved Compose credentials or model vectors.

`embedding_model_missing` / `embedding_identity_unavailable`: verify host Ollama and configured installed model, then actual container reachability. `embedding_dimension_mismatch`, `embedding_model_not_supported`, `index_embedding_identity_mismatch`: stop and review the model/index design; do not bypass the guard. `embedding_request_rejected`: inspect context/input size and approved model configuration; truncation stays disabled. `source_changed_after_manifest`: fetch a clean pinned snapshot; do not change a manifest hash merely to hide drift. Per-file failures preserve prior active evidence, return a failed run/CLI exit 1 and appear in recent errors. Unexpected errors expose safe codes, not raw content/credentials.

Official references used for this integration: [Ollama embed API](https://docs.ollama.com/api/embed), [Nomic model instructions](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5), [PyYAML safe loading](https://pyyaml.org/wiki/PyYAMLDocumentation). Actual installed behavior and digest checks, rather than documentation alone, support the gate. Rights remain unconfirmed; keep the full external corpus and confidential assignment out of source/publication.
