# Product requirements and discovery

First written6 November2026 before implementation. The customer framing is a stated working assumption,not a claim of client interviews. Current acceptance8 November is reconciled against the selected pre-experiment Phase10 candidate.

| Discovery element | Decision and actual evidence |
| --- | --- |
| User / job / pain | Product and growth practitioners need to turn long Lenny interviews into inspectable decision support and reusable writing. Manual transcript search is slow;generic advice is hard to verify. No external participants were recruited. |
| Primary success metric | Proposed target:4/5 frozen end-to-end scenarios without developer recovery. Actual original0/5,bounded experiment0/5. This is our product target,not a company requirement;mandatory workflows remain mandatory even if4/5 were achieved. |
| Assumptions | English transcripts as sole evidence;local single evaluator;host Ollama plus Docker fit8GiB M2;installed/pinned models;optional explicit cloud key. Full ingest fits serially,but tiny-model comprehension/abstention/essay quality is inadequate. [Register](assumptions.md). |
| Included / excluded scope | Include sessions,grounded research,follow-ups,source inspector,dedicated essay/review,Markdown/HTML viewer,exports,local+cloud configuration,persistence,tests/logging/setup. Exclude voice,arbitrary web/filesystem tools,external uploads,knowledge graphs,multi-user collaboration,billing and production SSO:these add trust/operations work without evidence of benefit to the required job. |
| Risks and trade-offs | Local privacy/no cloud spend versus latency and weak small-model judgment;PostgreSQL hybrid retrieval for operability versus missed broad queries;server-owned quotes/citations for integrity versus limited synthesis. Controlled tools prove framework use but do not prove autonomous routing. [Risks](risks.md),[decisions](decisions.md). |

## Intended journey and implemented behavior

Create/open a session → ask → inspect a cited original passage → follow up with fresh retrieval → draft an evidence-first essay → explicitly review factual support/readability → save Markdown/HTML → reopen after restart. The interface preserves unsent drafts;desktop panels resize/collapse/expand,tablet context opens on demand,and phones use single-panel navigation. `/` is an explicitly labelled example homepage;`/workspace` is the research app.

PostgreSQL is authoritative for messages,source snapshots,essays and artifacts. Pi actually invokes a narrow read-only transcript tool through an RPC adapter. Local chat renders one exact selected excerpt. Native tool serialization sometimes needs a strict documented normalizer. Server policy helps with private-fact gaps,but general unsupported/completeness behavior fails. The bounded multi-excerpt experiment did not improve0/5 and is excluded from the candidate.

Essay facts/citations are server-owned exact selected quotes;Pi drafts advice. Deterministic validation enforces1125–1375 words,six sections,lists/bold/IDs,but does not approve meaning. Review/edit and explicit acceptance are separate. A manually reviewed1208-word result required9 edits. Raw1216-word drafts remain failed despite length/IDs passing. Static exports preserve accepted content and source mappings;they are not model-generated executable HTML.

## Acceptance and measured outcomes

| Requirement | Actual status / evidence |
| --- | --- |
| Full pinned corpus,identity and source integrity |303/303 episodes,12770 passages;294 loaded/9 skipped/0 failed;repeat303 skipped/0 duplicates. Original data retained. |
| Retrieval relevance target85% Recall@8 | Full-index hybrid56.25% tuning16/81.25% observed holdout8. Not met;gold judgments cover nine development sources,not random full-corpus quality. |
| Source support and useful answers |13 Phase10 answerable outputs directly reviewed;4 adequate.16 quoted outputs had valid supported exact quotes,but many were irrelevant/incomplete. Unsupported gaps1/4 via existing guard. |
| Frozen five user scenarios |Original0/5;bounded rerun0/5. Not a user study. [Frozen definitions](scenarios.md),[results](phase-10-report.md). |
| Local/cloud boundary | Local default qwen3:0.6b chat/1.7b advice. Previous one-case Pi/OpenRouter Gemini chat passed6.513s;no cloud fallback. Anthropic has config/mocks,not a live validation claim. |
| Persistence/rendering | Prior reviewed artifact and both exports survive restart;API/source ownership and hostile renderer tests pass in stated scopes. Fresh isolated README rehearsal is reported separately. |
| Release acceptance | Quality gate open. Phase11 setup/docs verification does not erase these failures. |

## Delivery and next boundary

The selected candidate restores41 source hashes from the verified120-contract Phase10 baseline while retaining UI polish,full-index compatibility and OpenRouter fix. Bounded changes and all raw evidence remain separate and preserved. Phase11 rehearses a complete private local snapshot in a clean checkout/fresh volumes;the previously published snapshot is incomplete. No public-source push,video,upload or submission is authorized here. [Requirement/deliverable register](requirements.md),[Phase11 report](phase-11-report.md).
