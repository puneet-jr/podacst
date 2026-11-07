# Assumption register

Baseline: 6 November 2026 India time. Client interviews have not occurred. Status means unverified / verified / rejected; hardware facts do not verify model feasibility. Owners: project builder unless stated otherwise.

| ID | Assumption and reason it is open | Impact if false | Validation and actual status | Decision / requirements |
| --- | --- | --- | --- | --- |
| AS-01 | One local evaluator; the brief requests local deployment without a tenancy specification. | Need authentication, permissions and deployment redesign. | Confirm evaluator topology; unverified. Still isolate sessions and local user metadata. | D-01; SES-01, DB-01 |
| AS-02 | English corpus/output; no localization or language rubric supplied. | Translation and multilingual retrieval change quality tests and latency. | Inspect representative corpus in Phase 3 and confirm output expectation; unverified. | D-01; KB-01, RAG-01, ESS-02 |
| AS-03 | Transcript-only factual authority; assessment explicitly requires strict grounding. | Extra sources require a changed source/security contract. | Verified as requirement by direct PDF Sections 3.3/4.1 reading; future implementation compliance unverified. | D-02; KB-02, RAG-01 |
| AS-04 | Host can run a useful local model alongside services; suitable model unspecified. | Local demo/tool/essay gate may fail or be too slow. | Hardware verified M2/8 GiB/8 cores. Phase 1 started Ollama and proved qwen3:0.6b explicit fixture tools: final 5/5, 1.205-2.248 s. Earlier autonomous/schema attempts failed. Full-stack fit, real RAG and essay quality remain unverified; see phase-01-report.md. | D-03; AG-01, MOD-02 |
| AS-05 | First-run network/model/corpus downloads are permitted; offline bootstrap not specified. | Need pre-provisioned assets and revised setup instructions. | Official docs reachable via tools; actual package/model download path unverified. No model downloaded. | D-03; OPS-01, KB-01 |
| AS-06 | Candidate can separately supply a cloud API credential; account/budget not supplied. | Live cloud verification blocked; requirement cannot be marked verified. | Four checked inherited key variables absent; no credential files read. Key existence elsewhere and live access unverified. | D-04; MOD-01, MOD-03 |
| AS-07 | Production SSO is unnecessary for local evaluation; no identity provider requested. | Add authentication and revisit data isolation/deployment. | Unverified client deployment assumption; no production authentication claim. | D-01; SES-01, DB-01, ART-03 |
| AS-08 | Planning deadline is 9 November 2026 India time; plan records a newer candidate deadline than PDF. | Sequence and release buffer may be wrong. | Current plan records 9 November; PDF prints 15 September. Exact time and current form validity unverified, candidate owns confirmation. | D-07; DEL-08, OPS-05 |
| AS-09 | Public source access permits assessment use but not blanket redistribution of transcripts. | Licensing/rights may restrict fixtures or publication. | Root listing has no LICENSE; do not infer permission. Full rights review pending before redistributing substantial source text. | D-06; KB-01, DEL-01 |

Evidence: [environment.md](environment.md), [provenance.md](provenance.md), [assessment-audit.md](assessment-audit.md). Revisit AS-04 in Prompt 01 before selecting/pinning a model, AS-02/09 in Prompt 03, AS-06 before live cloud calls and AS-08 before release.

Phase 1 updates AS-04/05 partially: official Pi and the small model downloaded successfully; model identity and loaded footprint observed. This verifies first-run access for these assets, not full corpus availability or future network conditions. AS-04 remains unverified for the intended product, even though its narrow fixture spike passed.


## Phase 2 update

AS-01/07: actual fixed local user metadata/scoping, UTC messages and independent sessions passed real PostgreSQL/API tests, including exclusion of another user's rows. This verifies the implementation behavior, not a client interview or production authentication requirement. AS-04: host Ollama plus container Pi fixture succeeded with the DB/API/web present; broad retrieval/essay quality and full-corpus memory remain unverified. AS-05: public image/dependency downloads worked after isolating a stalled Docker credential helper. No full corpus download or Linux network rehearsal is implied. AS-06/08/09 remain open. Evidence: phase-02-report.md; decisions D-08/09.


## Phase 3 update

AS-02: representative real sources are English; the 303-file parser audit succeeded, including one genuinely untimed speaker-only file and bracket timestamps. This supports the selected parser scope, not a client language confirmation or multilingual quality claim. AS-04: actual existing local Nomic embeddings worked with PostgreSQL/API/web present; 3 episodes/114 passages in 24.078 s. Post-smoke swap 8194.56 MiB and 28% memory-pressure free percentage do not establish headroom or full-corpus/essay fit. AS-05: exact public corpus download worked; snapshot/count/hash manifest recorded. No model downloaded in this phase. AS-09: no root license in pinned source; full raw corpus remains ignored, no redistribution permission inferred. Other client assumptions remain open. D-10/11 and phase-03-report.md capture evidence and limits.


## Phase 4 update

AS-02/04: English lexical/dense retrieval worked on nine indexed episodes/373 passages with the existing local embedding model. This does not validate multilingual output or qwen3 research/essay quality. Sparse tuning-selected default did not generalize well to eight held-out questions; quality target remains unmet, so usefulness must not be inferred from model/API availability. AS-05: six additional manifest-selected sources embedded locally in43.533s with no new download. AS-09: corpus remains ignored, root redistribution rights unresolved; shareable eval stores authored questions and hashes/offsets, not raw source passages. Post-evaluation swap8520.81MiB on8GiB is host-wide, not peak/causal capacity proof. See D-12/13 and phase-04-report.md.


## Phase 5 update

AS-04: existing qwen3:0.6b supports the measured bounded extractive workflow with PostgreSQL/Pi/host Ollama. It sometimes emits textual tool requests, needs narrow schema/context and does not reliably abstain from unrelated evidence. One independent answer was incomplete. This partially validates local feasibility; general research/essays remain unverified. No larger model downloaded. Final requested checks8.96/7.05/5.26s, context4096/output128. Post-check host-wide swap9584.31MiB on8GiB,24% free percentage is a snapshot, not model peak/headroom proof. AS-01/07: real API context/session/source ownership and recovery pass for the fixed local evaluator, without production authentication or browser claims. AS-06/08/09 and independent semantic review remain open. See phase-05-report.md and D-14–16.

## Phase8 observed boundaries

Local M2/8GiB supports this sampled chat0.6B/essay1.7B journey, not a throughput guarantee:8.031s/6.798s chat and41.096s drafting, excluding review time. No models downloaded. Eight candidate passages allowed six usable writing sections for this topic; other topics may still fail evidence sufficiency. Same app backend drives real Chrome interactions; deterministic UI fixtures are separately labelled, with zero inference/database writes. Reviewed1208-word acceptance needed9 edits. Browser fallback works while in-app connector remains blocked. Unsent text is session-specific page memory, not durable storage. [Report](phase-08-report.md).
