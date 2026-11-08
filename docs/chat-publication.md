# Chat publication candidate — 9 November 2026

Complete sanitized tree selected from **bffcace365fe97e538599d12acb6989c9e0beab7**,whose tested runtime is3dc814552104edc83072503811c56dbe452e9552. The existing audited publication manifest's743 file hashes matched before copying. The full source/runtime dependencies are included;the old partial remote history is retained as the parent of the publication commit.

Permitted additions:the exact previously verified OpenRouter GPT-OSS120B final-answer cap guard and its regression/wire probe;an explicit reviewed1208-word/nine-edit fixture with unchanged Markdown/HTML exports and only curated source IDs/span hashes;a no-inference isolated import command;README publication/rehearsal instructions. No Voice Mode code,dictation,experimental part shortlists,unmerged multi-excerpt generation policy or later runtime/storage/retry overlays are included.

The OpenRouter patch changes only the final answer for exactly openai/gpt-oss-120b after linked search_transcripts evidence:1024 tokens. Tool requests,local Ollama,other models and routing retain their existing limits. All11 Node policy/conversation/format regressions passed after exact-diff review. An offline installed-SDK wire check is part of the exact-tree rehearsal;no new cloud inference is authorized or needed. The historical Nov8 cloud pair passed;availability/credits are not newly certified.

The final release action is conditional:rehearse this exact commit from a fresh clone using the README and new volumes;live Ollama onboarding question and “What happened with the next cohort?” must both have supported citations;the reviewed essay and both exports must reopen after restart. Audit the complete tree and parent diff before non-force push. The verification receipt is kept outside the tested tree so recording results cannot silently change the tree after rehearsal. A failed gate means no push.

## Unresolved limitations retained

- Original Phase10 scenarios **0/5**,bounded rerun **0/5**,proposed target4/5. This publication is not a new scenario evaluation or assignment-quality pass.
- LNO multi-part completeness/abstention remains unresolved. Later unmerged experiments reproduced false abstention with adequate evidence and one shortlist experiment regressed unsupported-question handling. Those code changes are excluded;no LNO fix or general grounding pass is claimed here.
- The most recent candidate raw essay was **1145 words**,zero edits,and failed semantic/readability review despite passing count/IDs. Earlier1216/1157-word raw failures remain documented. The **1208-word essay has nine disclosed manual edits** and is a separate reviewed fixture;autonomous essay quality remains unverified.
- Full historical index303/12770 is preserved in existing databases. A fresh README smoke indexes three interviews/112 passages;report that coverage honestly. No full-corpus ingestion rerun or new retrieval score is implied. Full-index hybrid recall56.25% tuning/81.25% observed holdout remains below85%.
- Candidate chat selects one bounded exact excerpt. It does not solve general multi-part answers/coreference. The local/provider/citation/persistence checks are narrow workflow evidence.
- This is a local single-evaluator tool,not production authentication or a public hosted service. Publishing source does not deploy the app,submit the assignment,record/upload a demo,or resolve all deliverables.

The sanitized source tree excludes real.env/credentials,private protocol/SQL/model/source traces,raw transcript exports,downloaded corpus/models,local databases,dependencies/build outputs,the confidential assignment PDF,and private Git snapshot history. Reviewed final documents are deliberate labelled fixtures,not raw transcript payloads. The original minimal1270-word Phase7 rendering fixture remains separately labelled;the new1208-word fixture is the exact previously reviewed Phase8 result and exports.

## Fresh startup migration ownership correction

The first publication rehearsal at29814edd failed when README immediately launched a second migration while the API entrypoint was creating the fresh Alembic schema. PostgreSQL reported a duplicate pg_type entry for alembic_version. That failed attempt and all its volumes are retained.

The documented Compose flow now has one migration owner:the API entrypoint upgrades the schema before exec of Uvicorn. scripts/bootstrap.py only validates configuration and starts Compose; scripts/docker.py only dispatches Docker; Compose contains no independent migration job. The README removes the duplicate exec step and requires waiting on /api/health/ready,which additionally checks CURRENT_REVISION. The fresh rehearsal uses a new project lenny_release_20261109r2 and unused ports/volumes. No retrieval,prompt,timeout,model or UI behavior changes. Results remain external and publication remains conditional on the full exact-tree rehearsal.

## Bounded readiness correction

The a9909cc rehearsal removed duplicate migrations but curl exited52 before Uvicorn listened. scripts/wait_ready.py now polls the existing endpoint with a90-second deadline and3-second attempt bounds,including transient transport failures and not-ready status. Only HTTP200 plus status ready succeeds;failure reports the last sanitized result and API-log command. The API remains the sole startup migration owner. Mock transport/deadline tests are separate from the new lenny_release_20261109r3 fresh-volume rehearsal. Prior failed attempts and quality limitations remain preserved.
