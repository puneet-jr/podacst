# Assumptions — reconciled8 November2026

Working product assumptions are not client approval. Observations refer to the selected pre-experiment Phase10 candidate unless noted.

| Assumption | Reason/user impact | Actual verification and residual uncertainty |
| --- | --- | --- |
| Local single evaluator,English corpus/output | Keeps setup/session isolation practical;no collaboration/SSO promise. | Fixed local user and cross-session ownership tested;not production tenancy. |
| Pinned transcript repository is sole factual source | Makes citations inspectable;no arbitrary web/upload trust boundary. |303 source hashes/12770 spans/model identity verified. Rights/redistribution remain unresolved. |
|8GiB M2 can run the local stack serially | Required local privacy/demo path. | Full ingest2635.389s,warm chats typically5–17s;heavy swap. Not a comfortable-memory/cold-install guarantee. |
| Small models can complete the product jobs | Low memory/cost;this was a risk to test,not a fact. | Rejected as a broad assumption:original0/5,bounded0/5;false/failed abstention,multi-part omissions,raw essay failures. |
| Exact citation IDs imply traceability | Required for source inspection/reopen. | Proven within checks;does not imply relevance,complete answer or entailment. |
| Approximately1250-word essay can be produced locally | Dedicated reviewed-writing workflow. | Raw length can pass1125–1375 while semantics fail. Reviewed1208-word result required9 edits. Autonomous quality remains unverified/failed on measured samples. |
| Cloud is optional/explicit | User controls external inference;no hidden rescue. | Pi/OpenRouter Gemini cited chat smoke passed6.513s;local default/fallback-off. Anthropic lacks live proof. Phase11 local rehearsal does not revalidate cloud. |
| Complete source/setup can be reproduced | Evaluator needs documented startup. | Public snapshot known incomplete;Phase11 uses an exact complete private local candidate revision/fresh volumes. Model/base-image download time on a new machine remains unmeasured. |
| Five frozen scenarios diagnose product value | Connect engineering choices to user jobs. | Proposed4/5 target,actual0/5 twice. No external participants/random sample/user-study claim. |

[Phase10 measurements](phase-10-report.md),[Phase11 setup/revision/results](phase-11-report.md). No assumption is upgraded by a fixture or an import-only integration.
