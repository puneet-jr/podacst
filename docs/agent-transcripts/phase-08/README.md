# Sanitized Phase8 evidence

The published subset includes command metadata (no stdout/stderr), deterministic fixture checks, retrieval candidate IDs/timings, source-span/hash review, generation status/counts, output hashes and private screenshot hashes. `publication-evidence.json` records the manually reviewed1208-word result and9 explicit edits; autonomous essay quality remains unverified.

Full transcript/source payloads, raw API snapshots, raw model drafts, reviewed essay body, edit-plan text, command diagnostics and screenshots remain local and are deliberately excluded from this commit. Sanitized summaries preserve actual failures and measured timings; no evidence was fabricated.

The local UI journey used the full working tree. The user explicitly chose to leave Phase6/7 runtime prerequisites uncommitted, so this remote snapshot is incomplete. The browser regression also needs the local Phase7 artifact helper and labelled fixture. Mock UI results do not establish model quality, lifecycle cleanup or live persistence. Actual reload/reopen passed; service-restart proof is separately Phase7.

See [Phase8 report](../../phase-08-report.md). Stop before Prompt09.
