# Actual build evidence and transcript capture

This directory starts in Prompt 00 on 6 November 2026. It contains actual bounded tool outputs plus an explicitly labelled narrative summary. It is not a fabricated conversation transcript.

| File | Evidence type and limits |
| --- | --- |
| phase-00-earlier-environment.json | Exact earlier exec_command result exported from its tool response; includes successful read-only unrestricted probes and actual Ollama connection refusal. No invented original timestamp. |
| phase-00-environment.jsonl | Actual commands captured with timestamps/stdout/stderr/exit codes during this session. Repeated audit is labelled as a new run, not reconstructed history. |
| phase-00-check-failure.json | Actual failed-check excerpt and diagnosis/correction; original time not captured. |
| phase-00-checks.jsonl | Actual final documentation integrity checks and results. These are not app tests. |
| phase-00-source-audit.json | Minimal factual projection of actual GitHub connector results; not a complete response or full coding transcript. |
| phase-00-summary.md | Labelled human-readable summary; never treat as raw dialogue. |

## Full-session export gap (B-05)

No full raw Codex conversation export has been provided through this session's tools. We have not searched private global session archives, copied confidential assignment tool output or fabricated historic user/assistant messages. Genuine command logs are available from discovery onward, but they are incomplete coding-agent transcripts. DEL-06 remains implemented in part and unverified until real sanitized agent exports/build history include actual failures and corrections.

## Future capture procedure

1. Capture tool executions at execution time: UTC start/end, phase, workspace/revision, command, exit code, bounded stdout/stderr and timeout state. Preserve initial failed attempts and corrective runs separately. Store full sensitive raw streams only in ignored private/raw-exports locations if needed.
2. For Pi application traces, record actual provider/model/version, controlled tool name/arguments safe projection, source IDs, duration and outcome. Keep RPC stdout separate from stderr diagnostics. This complements, rather than replaces, the coding-agent build transcript.
3. If the client exposes a real conversation export, export it privately, sanitize the genuine file and record export tool, revision, source hash, redactions/omissions and times. Never reconstruct dialogue from memory or convert summaries into a purported export.
4. Before committing, remove key values, personal content, confidential PDF text and unnecessary absolute personal paths. Do not print all environment variables or credential stores. Review outputs manually; a pattern scan alone is not proof of safety.
5. Record test failures/corrections and unavailable integration checks without rewriting history. Summaries stay clearly labelled, mock checks stay separate from live integration.

## Phase 1

[Actual Phase 1 commands and local Pi traces](phase-01/README.md) now include genuine failed attempts and corrections plus the final passing local batch. The complete coding-conversation export gap remains; app runtime traces do not substitute for such an export. Phase 0 files remain historical evidence.

## Phase 2

[Actual Phase 2 evidence](phase-02/README.md) includes real PostgreSQL/API migrations/contracts and restart/outage recovery, container Pi-to-host model traces, failed attempts/corrections and an explicitly failed browser bootstrap. Phase 1 artifacts are preserved unchanged. Full conversation-export gap remains.


## Phase 3

[Actual Phase 3 evidence](phase-03/README.md) separates parser/mock tests, actual PostgreSQL/provider fixture integrity, real pinned-corpus smoke/repeat, full parser audit and measured host constraints. Initial parser/verification SQL failures and corrections remain. Earlier phase evidence is unchanged; the full coding-conversation export gap remains.


## Phase 4

[Phase 4 evidence](phase-04/README.md) separates frozen source judgments, tuning corrections, untouched first holdout, unsupported diagnostics, actual DB/model/HTTP proof, mock/fixture checks, manual sampled review and quality-target failure. Earlier spike/evidence preserved unchanged. Actual command logs remain incomplete coding-conversation exports.


## Phase 5

[Phase5 actual evidence](phase-05/README.md) separates adapter mocks, PostgreSQL contracts, real local conversation/cleanup/hostile fixture, manual claim-support review, browser blockage and preserved failures. Final live verification completed despite turn interruption; no model rerun on resume. Private raw RPC contains prompts/evidence and is excluded from shareable source. Earlier phase evidence is unchanged; the full coding-conversation export gap remains.
