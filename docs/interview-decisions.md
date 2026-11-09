# Lenny Growth Assistant
## Design decisions and interview prep

### 45-second walkthrough

> I built a research workspace for product and growth teams using Lenny’s Podcast transcripts. Ask a question, open the exact passage behind the answer, then turn the evidence into a reviewed essay you can save and reopen as Markdown or HTML. FastAPI runs Pi with a single read-only retrieval tool, and PostgreSQL stores both the search index and the workspace history. The full development index covered 303 episodes. I verified specific chat, citation, and export flows, and the broader evaluation showed where the system still falls short, especially on multi-part questions and fresh essays.

## “Who is this for, and what problem does it solve?”

I designed it for a product manager or growth practitioner looking for actionable examples from past interviews. A question like “How did Lookout change onboarding?” can take several searches and transcript scans. The workspace puts the answer, the original passage, and any saved write-up in the same research session. The useful part is being able to check what the guest actually said before sharing the takeaway.

I assumed a single evaluator, an English transcript corpus, and a human review step for longer writing. That kept the scope on trustworthy research and reproducible handoff. Production authentication and hosted operations were outside that scope. [Product brief](https://github.com/vivekvattem/lenny/blob/main/docs/PRD.md)

## “Where does the agent actually fit?”

Codex assisted development. Pi is the runtime agent. FastAPI starts a fresh Pi process for a request and gives it one tool, `search_transcripts`, tied to the saved question and bounded session context. Pi invokes retrieval and receives candidate evidence. In the local chat path, the model chooses a supplied excerpt ID or signals that evidence is insufficient. The server validates that choice, attaches the exact source, and saves the result.

I kept the tool read-only and scoped it to the current question. Pi has no general shell, file, or web tools in this workflow. The application owns session state, retries, and persistence. On some local runs the small model emitted a tool request as text, so a compatibility adapter accepts only the expected request shape. Reliable autonomous tool routing remains open. [Architecture](https://github.com/vivekvattem/lenny/blob/main/docs/architecture.md)

## “Why hybrid retrieval and one PostgreSQL database?”

Product interviews mix exact terms with paraphrases. Sparse search helps with names, acronyms, and distinctive wording. Dense search helps when someone describes an idea in different words. I fuse the ranked lists, deduplicate results, apply interview scope, and pass a bounded evidence pack to Pi. The final full-index results gave me evidence to keep testing that design, with hybrid Recall@8 at **56.25% on tuning** and **81.25% on the previously observed holdout**, below my proposed 85% target.

PostgreSQL with pgvector keeps embeddings and full-text search beside transcript versions, sessions, citation snapshots, and artifacts. That gives the evaluator one database to run and lets the app commit answers and their source mappings together. The trade-off is that query plans and evidence packing both matter as the corpus grows. The full development index had **303 episodes and 12,770 passages**. A repeat ingest skipped all 303 episodes. [Architecture](https://github.com/vivekvattem/lenny/blob/main/docs/architecture.md) · [Full-corpus evaluation](https://github.com/vivekvattem/lenny/blob/main/docs/phase-10-report.md)

## “What does a citation actually prove?”

A citation lets the reader open the saved transcript text behind a specific reply. The server checks that the ID resolves and that the quote matches the original span. It stores a snapshot with the reply, so a later ingestion refresh can preserve what the user originally saw.

An exact quote can still answer the wrong question or cover only half of it. I evaluated citation integrity and semantic support separately. A live check needed the passage to substantiate the actual claim, and a multi-part question needed evidence for each requested part. [Architecture](https://github.com/vivekvattem/lenny/blob/main/docs/architecture.md) · [Scenario rubric](https://github.com/vivekvattem/lenny/blob/main/docs/scenarios.md)

## “Tell me about a failure you traced through the stack.”

In the Lookout follow-up, retrieval found the passage containing the next cohort’s **40% “very disappointed”** result. The excerpt packer dropped that sentence. In the saved replay, generic words like “for” and “they” gave earlier sentences the same overlap score, and overlapping excerpts could take up both slots. I changed that selection step to discount those words and avoid overlapping windows. The repaired live pair returned supported citations for both answers.

I also checked a separate unscoped follow-up on the published runtime. The trace recorded the earlier user message ID and subject, and the new answer used fresh retrieval. I kept that evidence separate from the first follow-up, which could be answered using its wording and retained interview scope. [Repair report](https://github.com/vivekvattem/lenny/blob/main/docs/phase-12-repair-report.md) · [Published-runtime verification](https://github.com/vivekvattem/lenny#verification-and-limitations)

## “Why local models, and what did cloud testing teach you?”

The baseline had to run on my 8 GB M2 Mac. I used host-native Ollama with `qwen3:0.6b` for chat and `qwen3:1.7b` for essay advice. That makes local inference available without a cloud key. The small models struggled with relevance, abstention, and long-form prose. OpenRouter is an explicit server configuration, disclosed in the UI, with automatic provider fallback disabled.

In one OpenRouter run, GPT-OSS-120B retrieved evidence successfully but returned an empty answer. Metadata showed the final turn ended at its **128-token cap**, with **125 reasoning tokens**. I raised the cap to **1,024** only for that model’s final turn after linked retrieval and verified the serialized request before running it live. The same question and follow-up then produced supported citations in **17.857 s** and **11.000 s**, including diagnostic overhead. That was a targeted check of the failure I measured. [Cloud token-budget report](https://github.com/vivekvattem/lenny/blob/main/docs/openrouter-120b-output-cap-test.md)

## “How much of the essay did the model write?”

The application assembles transcript excerpts and attaches their citations. Pi drafts the application advice, and the workspace exposes both evidence and advice for explicit review before export. The reviewed demo essay was **1,208 words** and required **nine manual edits**, covering six advice passages and three evidence selections.

A separate fresh **1,145-word** essay met the length and citation-ID checks but failed review. It included an unfinished statistic, an invented correlation, and repetitive advice. I use the reviewed essay to show the review and export workflow. The raw run is the evidence for where autonomous drafting still needs work. [Essay repair report](https://github.com/vivekvattem/lenny/blob/main/docs/phase-12-repair-report.md) · [Published-runtime verification](https://github.com/vivekvattem/lenny#verification-and-limitations)

## “How did you handle security and operational handoff?”

Transcript excerpts are untrusted data. They cannot expand Pi’s tool permissions. The server validates citation IDs and scopes source access to the owning session. HTML previews use sanitization, a restrictive content security policy, and a sandboxed iframe. Markdown and HTML exports reopen from saved records after a restart.

A fresh-clone rehearsal caught two startup issues. The README migration raced the API migration, so I made the API the sole Alembic migration owner. Then Docker accepted connections before the API was ready, so I added bounded polling that handles transient startup replies. The published runtime was checked on isolated volumes, including restart and reopening saved messages, citations, and exports. [Architecture](https://github.com/vivekvattem/lenny/blob/main/docs/architecture.md) · [Published-runtime verification](https://github.com/vivekvattem/lenny#verification-and-limitations)

## “What was your success metric, and why did it score zero?”

I proposed **at least four of five frozen workflows completed without developer intervention**. Each workflow passed only when all its required steps passed. Both full-index local runs scored **0/5**. A scenario could pass citation inspection or persistence and still fail on an incomplete answer, an incorrect abstention, or an essay that missed the rubric. The later smoke checks cover narrower workflows, so I report their results separately.

Recall@8 answers a different question. It measures how many labelled relevant passages appear in the top eight results. Even when the right passage is retrieved, it can be lost during excerpt packing or ignored during final selection. I use both metrics to identify which part of the pipeline failed. [Scenario rubric](https://github.com/vivekvattem/lenny/blob/main/docs/scenarios.md) · [Full-corpus evaluation](https://github.com/vivekvattem/lenny/blob/main/docs/phase-10-report.md)

## “What would you do next?”

I’d work on evidence selection for each part of a question and calibrate when to abstain. A shorter per-part shortlist helped the supported LNO question in an isolated experiment, but it also made an unsupported question look answerable because of overlapping vocabulary. That trade-off is why I’d test supported multi-part questions and unsupported lookalikes together. The end-to-end check should show what was retrieved, what reached the model, what it selected, and what each selected excerpt supports.

For essays, I’d check factual blocks for completeness and have a reviewer score a fresh draft before any edits. Then I’d rerun the same frozen journeys and use new questions to check generalization. That would give me evidence to decide whether to improve retrieval, constrain generation, or increase the model budget. [Known issues](https://github.com/vivekvattem/lenny/blob/main/docs/known-issues.md) · [Test plan](https://github.com/vivekvattem/lenny/blob/main/docs/test-plan.md)
