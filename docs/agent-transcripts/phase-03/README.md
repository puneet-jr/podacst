# Phase 3 evidence

These are actual command outputs and labelled audit/review metadata from 6 November 2026, not a complete conversation transcript. [Report](../../phase-03-report.md) and [operations](../../phase-03-operations.md) explain scope and exact commands. Earlier Phase 1/2 evidence is preserved.

| Path | Meaning |
| --- | --- |
| commands.jsonl | Actual bounded commands, UTC start/duration, exit codes, separate stdout/stderr and truncation flag. Later captures also include end time. Initial parser failure and corrected tests/builds are retained. |
| corpus-audit.json | Corrected full parser audit: 303 source paths/hashes, 12,770 candidate chunks, zero parse errors; this audit embedded nothing. |
| scenario-anchor-correction.json | Why source offsets were corrected before retrieval/generation tuning, with old anchor hashes; questions/source choices unchanged. |
| sponsor-review.json | Manual review notes and exact source anchors for sponsor introductions in three real episodes; not a sponsor classifier score. |
| smoke-20261106T053650/results.jsonl | Failed initial verifier: wrong SQL inspection function; failure occurred before ingestion. |
| smoke-20261106T053920/results.jsonl | Actual real-corpus ingestion twice, read-only DB proofs and seven passing invariants; 3/303 episodes, 114 chunks. |
| container-evidence/ingestion-integrity-lenny_ingest_49ebd8d3882f/result.json | Twelve checks on retained isolated PostgreSQL with real Ollama and explicitly synthetic sources. Failure after one real embedding batch and different digest are deliberate injections. |
| redactions.json | Actual source excerpt/path sanitization with original/sanitized hashes. Commands, failures and results preserved; private originals stay ignored. |
| source-manifest.json | Final source/doc hashes; no Git revision exists. Scenario-inputs hash identifies the pre-tuning freeze. |
| preservation.json | Original spike/Phase 1 hashes checked; current Phase 2 evidence hashes retained for future preservation. |
| final-review.json | Final evidence-backed gate checks and explicit unverified limits; no fabricated performance or scenario outcomes. |

The successful corpus smoke used existing host Ollama `nomic-embed-text:latest`, exact digest in the logs, 768 dimensions. It is separate from parser/mock tests, fixture integrity tests and Phase 1 Pi generation. No cloud inference. `partial` is intentional: remaining 300 episodes are not indexed. No retrieval quality, generated answer/essay, browser UI or full ingestion rehearsal is claimed. Full coding-conversation export remains unavailable (B-05).

Personal home paths and substantial inspected source-body excerpts were removed from shareable outputs with hashes/omissions recorded. Raw corpus stays external/ignored; metadata anchors allow local reproduction. Read [provenance](../../provenance.md) and the unresolved redistribution-rights constraint before any publication.
