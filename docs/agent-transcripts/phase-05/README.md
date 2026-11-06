# Phase 5 actual evidence

The files contain actual bounded command/runtime output plus explicitly labelled manual reviews. They are not a complete coding-conversation export. No historic dialogue was reconstructed.

- `commands.jsonl`: UTC command/stdout/stderr/exit/duration. Bounded capture can truncate earlier output; final summaries/exit codes remain. Failed attempts are retained. No secret-printing commands are authorized.
- `live-*/results.jsonl`: real FastAPI/Pi/local Ollama runs, hybrid mode, requested questions/outputs, safe tool trace, passage IDs, latency/usage. Final batch `live-20261106T081843` completed exit0 despite turn interruption. Earlier automatic flags are not semantic quality passes.
- `opened-sources.json`: actual final citation GET responses and exact span checks, including independent S3. `support-review.json`: direct Codex semantic review and explicit incomplete/model-abstention failures, not independent expert review.
- `failure-review.json`: labelled narrative audit of real failed attempts/checker errors and corrections; original logs unchanged.
- `lifecycle-20261106T074854`: actual timeout/cancel/disconnect/retry/empty evidence, before-restart baseline and exact after-restart comparison. Prior failed checker run074747 retained.
- `hostile-source.json`: actual local Pi/SQL/model result on authored synthetic hostile evidence, separate retained DB; not a podcast/gold case or comprehensive security proof.
- `browser-check.json`: exact failed bootstrap projection; no UI navigation or browser pass.
- `preservation-baseline.json`:221 prior-file hashes taken before changes. `runtime-review.json`: actual versions/model digests/hardware/source counts, preserved data/protocol hashes/framing and private trace policy.
- `source-manifest.json`, `final-review.json`: final source identity, safe-content/document consistency and evidence audit. These complement actual runs; they do not turn mocks into live integration or a true quote into a good answer.

Raw RPC stdout and stderr are separate in the private `chat_traces` volume; earlier streams are ignored `.cache/phase5-private`, protected at parent0700. Shareable projections omit raw prompts/source packets except the deliberately inspected limited original passages. The private volume must not be published. The original Phase1 spike and Phase1–4 evidence are unchanged. Full transcript redistribution rights and genuine complete coding-conversation export remain unresolved.

See [Phase5 report](../../phase-05-report.md) and [operations](../../phase-05-operations.md). Stop before Prompt06 until the user gives a go-ahead.
