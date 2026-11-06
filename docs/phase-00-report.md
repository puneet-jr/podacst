# Project progress

Baseline: Prompt 00, 6 November 2026 India time. Revision: no Git repository initialized; document hashes and file creation observations identify this baseline. No implementation exists.

## Current phase

Prompt 00 complete. Phase 0 exit gate: **PASSED (documentation/discovery only)**. Prompt 01 has not started.

## Output and behavior

- Created docs/PRD.md first, with the concrete five-part discovery brief, proposed metric, assumptions, reasoned scope, flows, acceptance criteria, risks and phased plan. No application code was created before or after it in this phase.
- Defined five SC-01 journeys and proposed >=4/5 target, kept numeric targets distinct from measurements and mandatory gates. Exact questions/evidence await corpus inspection before tuning.
- Created assumptions, risks, scenarios and decisions with verification plans, actual uncertainty, links and user consequences.
- Built all 29 requirement rows from the supplied plan; independently cross-checked all four PDF pages, Sections 2-8, every operational obligation and all eight deliverables. No omitted mandatory area identified.
- Created AGENTS.md and privacy/build ignores; copied the two exact planning files into the root (build-flow filename normalized for companion links).
- Audited actual environment, source provenance, official Pi integration options and cloud credential presence. Captured genuine bounded command logs; full-session-export gap remains explicit.

## Actual checks and evidence

| Check/command | Actual outcome and limit |
| --- | --- |
| Initial ls -la and rg --files; ancestor AGENTS.md checks | Empty workspace; no existing project/rules to overwrite. rg no-match exit 1, not an app failure. |
| pypdf PdfReader, all four pages and annotation URIs | Assignment read privately and mapped; original PDF/extracted body not copied. Source identity hash saved without body. |
| Compare root planning copies by SHA-256 | Copied originals byte-for-byte; hashes in provenance. |
| sysctl hardware, df, runtime --version commands | Apple M2, 8 GiB RAM, 8 cores, ~100 GiB free, Python 3.13.5, Node 24.9.0/npm 11.6.0; no model feasibility proof. |
| docker --version; docker compose version; docker info --format '{{.ServerVersion}}' | CLI/daemon 28.4.0 and Compose v2.39.2-desktop.1, exit 0 outside sandbox. No app stack exercised. |
| pg_isready -h 127.0.0.1 -p 5432 -t 2; psql --version | Accepting connections, exit 0; client 15.14. No auth/query/migration/pgvector/persistence test. |
| Ollama version and HTTP GET localhost:11434/api/tags | Installed client 0.30.11; actual unrestricted connection refused. Inventory unknown; no local generation. |
| PATH lookup and four cloud-key presence checks | Pi absent; four checked keys absent without printing values or opening credentials. |
| git rev-parse --show-toplevel | Exit 128: no project/ancestor Git repository. No commit/release revision or publication claimed. |
| Official GitHub/website reads | Pi RPC/models/extensions/providers/CLI and exact source package metadata inspected; corpus root no LICENSE observed. Compatibility and redistribution rights unverified. |
| Final documentation audit | Passed: baseline files, all 29 IDs once, eight deliverables, honest statuses, five-part opening brief, five journeys, local links, source hashes, valid saved logs, no app/PDF/corpus and bounded known-secret scan. Evidence: agent-transcripts/phase-00-checks.jsonl. |

The initial sandbox blocked hardware/socket/loopback checks. Corrected by authorized read-only unrestricted probes; this changed the initial PostgreSQL/Docker interpretation. Actual successes and failures are preserved in [agent-transcripts](agent-transcripts/README.md). There are **no app/unit/DB integration/browser/model test results** and no measured product scores.

## Open blockers and limitations

| ID | Actual blocker/uncertainty | Required next action / affected gate |
| --- | --- | --- |
| B-01 | Pi not installed; package candidate not published-install/compatibility proven. | In Prompt 01 validate package and installed help, use project-local dependency, prove real adapter/tool behavior. AG-01. |
| B-02 | Ollama is not serving; installed model inventory, headroom/tool/essay quality and latency unknown on 8 GiB. | Start host Ollama, inspect inventory/headroom before selecting/downloading a suitable model; actual controlled local smoke. MOD-02, Prompt 01. |
| B-03 | No checked cloud API key variables set. | Candidate securely configures an available provider key, never pastes into chat; select supported integration and prove live when available. MOD-01, Phase 9. Local spike independent. |
| B-04 | Transcript corpus root has no observed license; snapshot not yet pinned/fetched. | Inspect actual corpus in Phase 3, record revision/count and review redistribution before copying substantial fixtures. Do not commit corpus. |
| B-05 | Complete raw coding conversation export unavailable. | Preserve actual logs from now; add genuine sanitized export if client provides one. DEL-06 remains incomplete/unverified. |
| B-06 | Plan's 9 November deadline differs from older PDF; exact time/form validity unconfirmed. | Candidate verifies before release/submission. No form action taken. |

These documented downstream blockers do not prevent a truthful discovery baseline. No destructive actions, installs, downloads, database mutations, publication or submission occurred.

## Next phase and stopping point

Next is **Prompt 01: prove Pi + Ollama with one controlled retrieval fixture**, bounded lifecycle/protocol handling and isolated sessions. It first needs B-01/B-02 resolved; 8 GiB model suitability must be demonstrated, not assumed. Stop here after Prompt 00's brief/output report. Do not begin Prompt 01 during this phase.

## Changed files

Root: AGENTS.md, .gitignore, README.md, LENNY_BUILD_FLOW.md, LENNY_CODEX_PROMPTS.md.

Documentation: PRD.md, assumptions.md, risks.md, scenarios.md, requirements.md, decisions.md, assessment-audit.md, environment.md, provenance.md and this progress.md.

Evidence: agent-transcripts/README.md, phase-00-summary.md, phase-00-earlier-environment.json, phase-00-environment.jsonl, phase-00-source-audit.json, phase-00-assignment-source.json and phase-00-checks.jsonl. Final baseline manifest is phase-00-manifest.json.
