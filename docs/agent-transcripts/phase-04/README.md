# Phase 4 actual evidence

Actual commands/results and labelled review metadata from 6 November 2026; not a complete coding conversation export. [Report](../../phase-04-report.md), [operations](../../phase-04-operations.md) and [evaluation rubric](../../../eval/README.md) explain scope.

| Path | Evidence and limits |
| --- | --- |
| commands.jsonl | Actual bounded commands/UTC/duration/exit/stdout/stderr/truncation; builds, real ingestion, tests and all evaluation attempts. No model/source-body output. |
| prior-evidence-baseline.json | Pre-Phase-4 hashes of original spike source and Phase 1–3 evidence; final audit rechecks them. |
| judgment-freeze.json | Before-results SHA/count/scope for 24 questions/32 original source anchors + four unsupported requests. Actual questions/anchors are in eval/retrieval-cases.json. |
| container-evidence/tuning-v1/ | Original low-score development run, 16 questions/three modes; no results overwritten. |
| container-evidence/tuning-v2-local/ | Intermediate lexical/sponsor/diversity/budget changes; separate measured attempt. |
| container-evidence/tuning-v3-local/ | Final budgeted-neighbor tuning comparison, before mode selection and holdout. |
| container-evidence/held-out-v3-first/ | First unchanged-candidate holdout: eight questions/three modes. Default selected from tuning, not reselected here. |
| container-evidence/unsupported-v3-first/ | Four unsupported requests/three modes; nonempty candidates, not generated answers or an abstention success rate. |
| metrics-summary.json | Actual tuning/holdout and descriptive all-case metrics; target not met for selected/default/all-case scope. |
| support-review.json | Supplemental direct reading of top-three sparse source excerpts for unsupported cases and selected misses. Scope is limited, not semantic certification. |
| live-api.json | Nine real proxy/API/DB checks, actual local hybrid and unchanged message/session hashes. |
| source-manifest.json / final-review.json | Final source/image identity and evidence/static/preservation audit, engineering vs quality gates separated. |

Each evaluation directory holds metadata-only `results.jsonl`, `report.json` and independently resolved source-to-chunk judgments. A runner `passed=true` means searches/source-integrity completed, **not** an 85% recall or product pass. Default sparse held-out recall was62.5%; dense87.5%, hybrid93.75% on a tiny eight-case subset. Full all-case results and sampling limits must accompany comparisons. No covert default reselection, relabelling or held-out rerun.

All model calls were to existing Mac Ollama/Nomic; no cloud inference, new weights/dependency or full source corpus exported. Nine episodes/373 chunks are indexed from303;294 remain. Sparse is intentionally selected, not a fallback after hybrid failure. Support remains unverified by design; generation/semantic abstention needs Phase5 implementation. Original Phase1 spike and Phase1–3 evidence remain unchanged. Browser, rights, clean evaluator and full coding-conversation export gaps remain.
