# Risks and trade-offs — reconciled8 November2026

Owner:project builder for implementation;candidate for credentials/publication/video/submission. Likelihood/impact are judgments,not measured probabilities.

| Risk | Actual outcome / mitigation | Residual/user impact |
| --- | --- | --- |
| High:irrelevant/incomplete supported quotes | Exact ID/span/source validation prevents invented quotes;Phase10 completeness4/13 and0/5 scenarios still fail. | Users may get correct text that does not answer their decision. No general synthesis/abstention guarantee. |
| High:unsupported premises / model judgment | Private-fact guard helped1/4 gaps;bounded multi-excerpt experiment falsely abstains and is excluded. | Related search hits are not proof. Need general support/completeness repair,not scenario-name filters. |
| High:essay semantic/readability failure | Server-owned facts/citations and explicit manual review;raw1216 words still fail. | Manual source selection/advice editing required;reviewed1208-word artifact is not autonomous success. |
| High:retrieval quality/performance | Full index complete;hybrid56.25% tuning/81.25% observed holdout below85%;some long queries hit3s SQL timeout. | Broad questions miss evidence or fail. Historical E error cause uncertain;bounded new trace proves its own retrieval timeout only. |
| Medium:local memory/latency |8GiB M2,serial models/services,bounded calls/context/output/retries. Full ingestion fits but heavy swap. | Variable startup/readiness/latency;no larger-model download or concurrency without fresh measurements. |
| High:sensitive data/log/cloud exposure | Narrow tools,server keys,private default projections,explicit cloud routing/no fallback,bounded secret scans. | Older raw traces remain sensitive;not production auth or universal secret assurance. |
| High:unsafe generated HTML | Markdown HTML-off,nh3 allowlist,CSP and opaque script-disabled iframe;hostile fixtures pass. | Supported static subset/Chrome scope only;no arbitrary script/network permission. |
| Medium:state loss/retries | PostgreSQL atomic writes/client identities/immutable sources;restart/cancel tests. | Single-worker deployment;distributed leases,immediate Ollama GPU cancellation and full restore rehearsal unproved. |
| High:incomplete publication/setup | Root uncommitted prerequisites preserved;private exact candidate excludes experiment;Phase11 isolated rehearsal. | Current public snapshot is not complete source. No release recommendation from a private snapshot alone. |
| Medium:deadline/rights/deliverables | Keep explicit requirement/status register and no fabricated submission. | Candidate must verify deadline/form,rights,complete coding export,video/camera/access and receipt. |

Quality/release gate remains open even if setup succeeds. [Known issues](known-issues.md),[Phase10](phase-10-report.md),[Phase11](phase-11-report.md).
