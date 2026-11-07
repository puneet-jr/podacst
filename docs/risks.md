# Risk and trade-off register

Baseline, 6 November 2026. Owner for all entries: project builder; candidate owns credentials and publication. Likelihood/impact are planning judgments, not measured probabilities. Mitigations below are planned, not verified implementation.

| ID | Risk; likelihood / impact | Mitigation and linked decision | Verification / actual outcome | Residual limitation |
| --- | --- | --- | --- | --- |
| RK-01 | Hallucinated/overstated facts; high / high | Evidence-only generation, server source IDs, preserve qualifications, unsupported response; D-02. | RAG-01/KB-02: >=20 reviewed retrieval cases, >=10 answer support reviews, follow-ups/sponsor traps/unknown-ID tests; not run. | Valid source IDs do not prove entailment; sample review cannot cover all future prompts. |
| RK-02 | Local latency makes research/writing frustrating; high / high | Bound context/output/tools, finite retries, cancellation and visible progress; D-03. | Measure actual warm and cold times; freeze scenario caps from baseline before release. No timings measured. | Essays may remain slow with 8 GiB shared among OS, model and Docker. |
| RK-03 | Cloud spend or rate limits; medium / medium | Default local, explicit provider selection, bounded calls; D-04. | MOD-01/03 failure/cost-path checks; no keys detected, no calls made. | Local hardware/electricity still cost; provider prices/limits remain external, no budget verified. |
| RK-04 | Small model cannot follow tools or write supported long essays; high / high | First prove Pi/local controlled tool; simplify schema/context, measure a model fitting available memory; D-03. | Prompt 01 tool/isolation/cleanup then Phase 6 essay review; blocked until Pi installed and Ollama running. | Hardware exists but reliable inference is not established. No silent cloud rescue. |
| RK-05 | Sensitive sessions/credentials leak via tools, logs or cloud; medium / high | Narrow tools, scoped sessions, server-side secrets, redact, explicitly explain transmitted fields; D-01/04. | Cross-session, redaction, prompt-injection and provider-boundary checks; not run. | Local evaluator context is not production tenancy. Cloud mode sends selected evidence/context/instructions off device. |
| RK-06 | Generated HTML executes code, exfiltrates or escapes styles; high / high | Sanitizer/allowlist plus script-disabled opaque-origin iframe and restrictive CSP; block external resources and control navigation/forms; D-05. | ART-03 hostile browser cases: scripts/handlers/SVG/CSS URLs/images/links/frames/malformed HTML; not run. | Restrictions reduce HTML capabilities; only tested policy can be claimed supported. |
| RK-07 | Source redistribution or unattributed reuse; medium / high | Keep corpus/PDF private, record provenance and review license before copying; D-06. | Empty workspace verified; no friend's code supplied or reused; no corpus root LICENSE observed. | No root license does not establish permission; rights review remains pending. |
| RK-08 | Deadline slips before mandatory local integration and handoff; high / high | Sequential phase gates; remove optional history/exports/topics first; D-07. | Prompt 00 docs only; later gates pending. Candidate deadline confirmation pending. | Original schedule is aspirational; no guarantee all gates fit the remaining time. |

Update likelihood, implementation links, exact verification, failures/corrections and residual risks at every relevant phase. Mandatory gates remain mandatory even if SC-01 reaches 4/5.


## Phase 1 evidence update

- RK-01: manually inspected final synthetic answers for correct 13/17-day windows and CEDAR/BIRCH evidence codes. Tool-less/invented answers and failed tool results were rejected in earlier batches. Real transcript semantic grounding remains untested.
- RK-02: final explicit fixture repeats n=5 took 1.205-2.248 s (median 1.729 s), excluding downloads and cleanup. Real abort/cancel/deadline cleanup passed; this does not establish essay latency. Swap varied materially with other host workload; do not infer full-stack headroom or attribute host-wide changes to this spike.
- RK-04: remains high. Optional tool selection, formatting and enum constraints were unreliable on qwen3:0.6b. Explicit single-topic guidance produced the final 5/5 fixture batch; this is not a broad quality/reliability estimate. Do not promote the model to final product default without real RAG/essay tests.
- RK-05: tested child environment excludes cloud keys/proxies, fresh Pi config/history prevents observed cross-request markers, tool policy is restricted and Ollama cloud was disabled. No production security or OS egress-isolation claim; full app redaction/session checks still pending.
- RK-08: Phase 1 local boundary passed; later mandatory gates remain. No optional feature was added to hide model limitations.

Exact evidence, failed batches, model footprint and actual commands: [phase-01-report.md](phase-01-report.md). RK-03 (cloud), RK-06 (artifact rendering) and RK-07 (corpus rights) are unchanged and unverified for the product.


## Phase 2 evidence update

- RK-02/04: container Pi -> host Ollama fixture run took 3.945 s with the foundation stack present; no essay/full-corpus latency or autonomous tool-selection claim. Keep bounded model configuration and re-evaluate later.
- RK-05: fresh separate DB/project/volume avoids touching existing host data. Scoped API queries, independent persisted messages, retry identity, safe structured errors and content/credential-free logging were exercised on actual PostgreSQL. Fixed local evaluator/no SSO remains a limitation.
- RK-08: stack/migration/API gate passed. Owned Docker helper hangs and an exit-137 test/restart collision are preserved with corrections. Final checks ran sequentially. Browser inspection failed before connection, so UI accessibility/responsive verification is still open.

The DB outage was real: live 200, ready/write 503, failed transaction absent after restoration and old messages unchanged. Other operational failures and untrusted artifact rendering remain later checks, not assumed mitigated. See phase-02-report.md.


## Phase 3 evidence update

- RK-01: exact source byte hashes, spans and immutable originals passed actual DB checks, improving traceability. They do not prove a future answer claim is supported. Sparse/dense/hybrid retrieval evaluation and manual semantic reviews are still unrun. Metadata conflicts and sponsor heuristics remain explicit review risks.
- RK-02/04: actual local Nomic smoke took 24.078 s for 114 chunks; unchanged repeat 0.247 s. Not an answer/essay benchmark. Post-smoke 8194.56 MiB host swap and 28% free percentage show workload sensitivity; full ingestion/model coexistence/quality remain unverified. No larger model or cloud rescue.
- RK-05: corpus read-only mount, YAML restrictions, hash manifests, local-only embedding configuration and safe metadata-only traces implemented. Saved conversation hashes stayed unchanged. Episode-atomic refresh, injected failure rollback, incompatible profile rejection, writer exclusion and stale-run recovery passed actual PostgreSQL/provider checks. This is not production egress confinement/security certification.
- RK-07: pinned public corpus fetched locally, no root license; no full corpus/source excerpts committed for redistribution. Scenario anchors store hashes/offsets, not reproduced long passages. Rights remain open.
- RK-08: Prompt 03 smoke gate passed; full corpus indexing and dependent product quality remain later work. Parser boundary/verification SQL failures and corrections retained. Browser runtime gap and coding-conversation export gap remain.


## Phase 4 evidence update

- RK-01 remains high: exact source integrity passed but selected sparse held-out Recall@8 is62.5%, especially weak unscoped (25%, n=4). Hybrid93.75% on the same tiny holdout does not establish general target achievement; all-24 hybrid75%. Cross-episode evidence completeness, imperfect sponsorship flags and incomplete/non-independent gold remain risks. Do not turn valid IDs or rank scores into semantic assurance.
- RK-02: warm service retrieval medians on eight held-out questions sparse69.55/dense83.33/hybrid105.80ms; observed p95 equals maximum for this tiny sample. Dynamic lexical frequency weighting adds SQL work; full-corpus tail latency not measured. Post-evaluation swap8520.81MiB; no essay/full-stack headroom inference.
- RK-04: query embeddings use the proved768-dimensional local Nomic profile, but no real corpus generation/tool routing/essay quality test was added. qwen3 limitations remain.
- RK-05: read-only consistent snapshots, exact parameterized scopes, bounded token/output/neighbor limits and safe retrieval logs passed tests/real API proof. Saved conversation hashes unchanged. Mocked model outage rejects explicit hybrid without hidden fallback; default sparse is a frozen policy, not failure substitution. No production security/egress/authentication claim.
- RK-08: implementation/baseline gate passed with quality defects explicitly open. Original low scores/corrections retained; no reranker or optional UI polish to conceal them. New independent evaluation is needed before changing/claiming mode policy. Generated unsupported-answer handling remains Phase5: all12 retrieval diagnostics returned related candidates and cannot count as abstentions.

Additional tracked Phase4 defects: P4-Q1 unscoped/multi-source misses; P4-Q2 unstable mode selection on small biased sample; P4-Q3 incomplete gold and mixed sponsor/metadata ambiguity; P4-Q4 remaining294 sources/unmeasured distractors. None is waived by passing engineering checks. Browser/full-export/cloud/rights gaps remain.


## Phase 5 evidence update

- RK-01/04 remain high. Exact excerpt selection prevents newly invented factual prose but can still choose irrelevant/incomplete text. Earlier follow-up misses and the final incomplete Shreyas answer remain recorded. The final private churn/dashboard question needed server policy after a wrong model choice; general abstention is unproved. A native follow-up call occurred, while other final requests required strict textual-call adaptation. Broader routing/synthesis/essay quality is not verified.
- RK-02: final supported/follow-up/unsupported requests took8.96/7.05/5.26s; earlier repeats varied. One generation, bounded evidence,4096 context/128 output and deadlines reduce runaway work. Host-wide swap9584.31MiB,24% free percentage is not peak/causal telemetry. Larger local models need separate fit/quality proof; no download/cloud rescue occurred.
- RK-05: actual cancellation/disconnect/timeout reaped Pi/closed bridge; scoped fresh context and citation ownership passed. Prompt-injection fixture selected the true17-day synthetic fact through actual Pi/local Ollama. One fixture plus a narrow regex/capability guard is not comprehensive resistance. Raw RPC is private0700/separate from diagnostics in a retained volume; unbounded historical retention, fixed local identity and lack of OS egress confinement remain limitations.
- RK-07: final citation review retains limited original evidence excerpts locally; full corpus/PDF stay ignored. No publication or redistribution permission inferred. Rights remain unresolved before public release.
- RK-08: local/API gate demonstrated, browser acceptance still blocked before connection. Final66 checks/four policy checks passed; earlier failed attempts and corrected checker mistakes preserved. No critical integration result is inferred from a mock. Prompt06 waits for user go-ahead.

## Phase8 residual risks

UI verification now includes real isolated Chrome desktop/mobile and16 deterministic failure/navigation checks, correcting earlier browser-wide blocker claims; in-app connector remains unavailable. One browser/sample contrast review is not full accessibility coverage. Actual main journey passes after9 explicit source/advice edits: generation can still clip quotes and produce weak/unsupported instructions. Review time is material; do not advertise autonomous essay quality. Candidate buffering fixes measured evidence starvation without improving corpus coverage or guaranteeing diverse evidence. Unsent composer drafts persist only while the page stays open. SC-01 frozen scenarios and general ten-answer quality remain unrun. [Report](phase-08-report.md).
