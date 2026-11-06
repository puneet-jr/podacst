# Genuine Phase 2 evidence

- commands.jsonl: actual captured commands, UTC times, exit codes, bounded stdout/stderr; includes credential-helper cancellations and the interrupted exit-137 check, plus corrective successes. Truncation is explicitly flagged.
- live-*/results.jsonl: actual HTTP/Compose persistence, restart, outage and recovery runs. Final gate: live-20261106T050703. Synthetic message bodies are retained only as test evidence; application diagnostic logs omit content.
- container-agent/: actual containerized Pi fixture protocol stdout.jsonl, separate stderr.log and result.json. This is model/framework evidence, not transcript-RAG success.
- browser-bootstrap-failure.json: actual browser tooling failure before connection; no visual pass inferred.
- phase-01-preservation.json: Phase 1 spike match and evidence hashes; Phase 1 files preserved.
- final-review.json and source-manifest.json: final bounded integrity checks and source/image identity; no invented Git commit.

All content is from actual execution or clearly labelled summaries. Home path strings are sanitized to $USER_HOME and recorded in redactions.json. No credential values, .env, confidential PDF or corpus were copied here. The full Codex conversation export gap remains; application agent traces and command logs do not pretend to be that export. Nothing was published or submitted.
