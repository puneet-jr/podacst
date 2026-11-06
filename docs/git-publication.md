# Ordered publication of the saved workspace

The user explicitly requested initialization and a non-force push to `vivekvattem/lenny` on `main`. GitHub reported an empty public repository, and `git ls-remote` returned no refs. The local workspace had no Git repository. Git was initialized on main; existing configured author identity is used and Git supplies actual current author/committer timestamps. No dates are backdated or taken from phase-report timestamps.

These commits organize a saved working snapshot in requested phase order. They are **not a reconstruction of historical development commits or independently runnable historical releases**. Earlier versions of shared files are unavailable. The first commit's PRD/scenario documents already contain later updates and are labelled a current snapshot. Current Compose configuration is grouped with the foundation even though later corpus/trace mounts are present. Current shared backend/runtime/frontend files are grouped at the final commit with Phase6 WIP, rather than inventing earlier versions. New phase-specific modules/migrations/evidence are grouped with their relevant phase.

1. Discovery, current PRD snapshot and acceptance scenarios.
2. Preserved Pi/Ollama spike and actual local integration evidence.
3. Current Compose/PostgreSQL foundation, dependency locks and startup tooling.
4. Source ingestion, embeddings, versioned refresh and integrity evidence.
5. Retrieval, frozen evaluation cases/configuration and measured quality limits.
6. Grounded chat tools, persisted source workflow and actual local recovery evidence.
7. Shared current runtime/UI integration and Phase6 essay work in progress, including its failed live tests, operations and publication audit.

Phase6 is blocked: the single corrected run produced an outline but no essay section before Ollama rejected the response grammar. Its real failed output is retained;81 contract tests are separate from that failed local gate. No Phase7 feature or successful essay is represented.

Publication review checks staged blobs for configured secret values without displaying them, common key/token signatures, binary/unexpected large files, forbidden paths and full source payloads. `.env.example` is retained; `.env`, confidential PDFs, downloaded corpus/weights, generated dependencies/builds, private credential directories, raw private traces and originals are excluded. Full evidence originals remain hash-identical in ignored `.cache/publication-originals`; public redactions are documented in [publication-redactions.json](publication-redactions.json) and [evidence notes](agent-transcripts/PUBLICATION.md). Limited attributed selected answer quotes remain as runtime evidence.

Push is explicitly authorized and must be non-force. Preserve any unexpected remote work; inspect a changed remote head rather than rewriting it. The final user-facing result reports actual remote commit IDs and the excluded paths after push. Demo upload, form submission and Phase7 remain unauthorized.
