# Project progress

Updated6 November2026 India time. **Phase6 work in progress; essay gate BLOCKED. Stop before Phase7.** Phase5 local/API gate remains demonstrated in bounded extractive mode; browser acceptance remains blocked.

FastAPI saves questions, runs fresh Pi sessions with one controlled `search_transcripts` tool, retrieves hybrid PostgreSQL/local Nomic evidence and asks local qwen3:0.6b to select one exact excerpt or NONE. The server validates IDs/spans, renders the quote, saves immutable answer-source snapshots and exposes owned source inspection. Typed NDJSON progress, finite budgets, terminal states and retry identity are implemented. React chat/source inspection replaces the note-only composer.

Actual supported question and follow-up cite different Sean Ellis passages. Each displayed citation was opened and its stored original reviewed for support. The follow-up uses only the same session's prior user question/scope and retrieves again. Fresh separate sessions have independent Pi histories and no initial context. Actual timeout, cancel, disconnect, duplicate-free retry/replay, empty retrieval and restart/reopen passed. A separate real local synthetic hostile-source run selected the correct17-day excerpt. Mock/protocol, PostgreSQL and live-model evidence are distinct in the [Phase5 report](phase-05-report.md).

Limits: the model emits its first function request as text; a strict documented Pi hook adapts only the exact approved request, then Pi executes the registered tool. Native/autonomous routing remains unverified. The unsupported private-company request needed a server policy correction after an unrelated model selection. An independent Shreyas answer was incomplete; its isolation pass is not a semantic-quality pass. General abstention, synthesis and essays remain unproved. Failed attempts/corrections are retained.

Scope stays **nine of303 episodes,373 passages**,294 unindexed. No Phase5 ingest or new dependency/model download. Phase4 results are unchanged: sparse default selected before holdout,68.75% tuning/62.5% held-out recall; hybrid93.75% on only eight held-out cases is not a broad quality achievement. Chat explicitly uses hybrid under the current user instruction; standalone retrieval remains sparse by default.

Migration `0003_conversation` is applied. Isolated Compose DB/pgdata and the original six messages/sessions are preserved; host5432 untouched. Private RPC stdout/stderr are separate in restricted `chat_traces`; shareable evidence stores safe traces/IDs/hashes. Actual versions, constraints and source/image identity are recorded.

Browser again failed before navigation: `Importing module "node:process" is not allowed in node_repl`. Build/HTTP/source inspection do not prove visual, accessibility or interaction behavior. Product readiness, cloud, writing/artifacts, full corpus, independent review, rights, complete coding export, clean evaluator and demo remain pending. No publication or destructive reset.


## Phase6 current outcome

Dedicated app skill/route, cited outline, section drafting, deterministic validation, one repair and explicit manual review persistence are implemented.81 contract tests pass, but actual essay acceptance does not. Initial local run skipped its section tool and emitted unsupported uncited prose. One integration correction supplied pinned sources directly to no-tool Pi writing turns. The single corrected run then failed on OllamaHTTP400 grammar initialization before section1:0 accepted essay words,0/6 completed sections,20.466s. Six outline IDs resolve, with semantic mapping weaknesses; no final claim-support review can pass without a draft. Both attempts are preserved. See phase-06-report.md; no further inference or Phase7 work.

The user now explicitly authorizes Git initialization, phase-ordered retrospective commits and a non-force push to vivekvattem/lenny/main. Private originals are preserved before public evidence redaction. No earlier commit dates or file versions are fabricated; current shared files are grouped honestly at the final snapshot. Git publication is separate from completing the assignment, recording a demo or submitting it.

## 7 November 2026: Phase8 interface gate

Prompt08 PASSED for the reviewed local main journey: new session/question/source/follow-up, evidence-led essay, explicit edits/review, both artifacts and reload/reopen through actual Chrome.99 contracts,2 source-span tests, TypeScript/build and16 deterministic browser cases pass. Final1208-word essay required6 advice+3 source edits; raw1224 failed, initial evidence-gap attempt preserved. Reviewed workflow, not autonomous quality or4/5 release scenarios. Real chat8.031/6.798s, essay41.096s; local0.6B chat/1.7B essay unchanged. Desktop/mobile visual/focus checks pass; in-app connector still blocked separately. Stop before Prompt09. [Report](phase-08-report.md).
