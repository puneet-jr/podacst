# Phase 5 report: cited local conversation and recovery

6 November 2026. **Local/API gate: PASS for the demonstrated bounded extractive workflow. Browser acceptance: BLOCKED. General answer quality: not passed.** Prompt06 is on hold until the user gives a go-ahead. The supplied prompt/build flow define the phase; the user's added hybrid/live-check requirements and explicit stop govern this execution.

The final three requested checks completed through **web proxy → FastAPI → Pi1.5.0 → Mac Ollama/qwen3:0.6b**, using actual PostgreSQL hybrid retrieval and local Nomic embeddings. No cloud output, model download or fallback. The index stays **9/303 episodes,373 passages**,294 unindexed. Phase4's historical results, sparse standalone default and unmet quality target remain unchanged.

| Final requested check | Retrieval | Duration, including HTTP/cleanup | Outcome and exact cited passage |
| --- | --- | --- | --- |
| Supported: Sean Ellis must-have survey question | hybrid; exact Sean Ellis scope | 8.963s | Supported quote; S1=`c0aa1ec1-9da2-5bc9-a1ed-550df1f12411`. |
| Follow-up: Lookout onboarding after antivirus discovery | hybrid; inherited same-session scope, fresh query | 7.048s | Supported onboarding quote; S1=`53054eb0-beee-5be4-b2f1-99ca9b2eac2d`. |
| Unsupported: private startup's exact2026 churn/dashboard access | hybrid; unscoped across indexed sources | 5.265s | Five related passages returned; final gap has no citation. Server policy corrected the model's unrelated E1 selection. |

These are individual measurements, not a percentile/SLA. Earlier successful repeats varied; development attempts are retained and are not independent quality estimates. Final evidence: [actual requests, full outputs, retrieved IDs, tool traces and usage](agent-transcripts/phase-05/live-20261106T081843/results.jsonl), [opened originals](agent-transcripts/phase-05/opened-sources.json), [manual support review](agent-transcripts/phase-05/support-review.json).

## Actual final outputs

**supported**

From the indexed transcript:

“It's a simple question that helps you figure out, does anyone consider your product a must-have, or ideally, who and how many people consider it, but ultimately it's about trying to figure out is your product a must-have, which could be equated to having product market fit. And so the question is, how would you feel if you could no longer use this product?” [S1]

**follow_up**

From the indexed transcript:

“So by setting the right expectations around it up front, you're going to bring people in with the right expectations. But then the second thing that we did was we streamlined onboarding so that the first thing that they did after signing up for the product was to set up the antivirus and then get a message "you're now protected from viruses."” [S1]

**unsupported**

The retrieved passages do not establish the requested fact. I cannot determine it from the indexed transcripts. Try a question supported by these interviews, or provide the missing information.

The first quote preserves Sean's qualification about product-market fit and includes the actual survey question, without inventing a threshold. Direct inspection of the stored original confirms Sean at observed00:03:19 said it. The follow-up's original identifies Lookout and, at observed00:10:50, explicitly describes antivirus-first onboarding and the protection message. The answer does not claim a universal causal effect or attribute all survey improvement to onboarding alone. Separate repositioning/outcome context remains visible in the original passage.

Both final S1 endpoints returned200 with exact original-span matches: ranges4975–5333 and12885–13229 in the source. S1 is per answer; the two labels point to different passage IDs. Every citation in the final run, including the independent-session S3, was opened. Observed transcript markers are not precise speech end times; safe pinned transcript/video links do not invent timing.

## Session context and framework evidence

Main session `2928f012-1f44-4c9b-bec3-cf24a3c8b7e1`: supported run `9907cfa8-5a22-4782-ad9a-dc4819e3552a`; follow-up `46f3fa09-dec1-4aa3-a1a5-838d7a4661cc`; unsupported `ebb1fa2e-1ae0-4578-bcbc-caa77edb7fb8`. Follow-up context contains only prior user ID `68447b84-880e-49da-a090-08c2e9117305`. It executes a new search and returns five different passage IDs. Previous assistant text is not supplied as factual evidence. Context is a bounded previous-user subject/scope heuristic, not general conversational reasoning.

Independent session `0d0440c8-893e-4709-b17a-def35be886e1` has empty initial context and a different Pi session/history. All four final Pi IDs are distinct, and the adapter checks zero initial messages. Isolation passes. Its Shreyas leverage-tasks answer is genuinely quoted but incomplete: it discusses Patrick/ROI rather than defining the requested tasks. Its source S3=`76021723-d6c7-5117-a4a6-940e9a1d0d40` resolves correctly; that does **not** make the answer semantically adequate. This remains a known quality defect.

Each operation actually executes Pi's registered `search_transcripts({"query":"current"})` and receives its result before local model selection. The tool's actual query/scope are server-pinned. A single-use capability authorizes only this read-only bridge. Default shell, arbitrary filesystem/web tools, MCP and unreviewed extensions are disabled. The final follow-up used a native function call; supported/unsupported/independent requests needed the strict first-turn textual-request adapter. This proves the framework integration and a validated compatibility path, not reliable native/autonomous calling.

The documented same-role `message_end` replacement hook and installed1.5.0 implementation were inspected before using normalization. Only the exact approved first-turn tool/arguments are accepted; source/tool-result/later/final-answer examples are rejected. Raw model serialization and actual tool execution remain separately inspectable. [Official Pi extension reference](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md); [official Ollama compatibility reference](https://docs.ollama.com/api/openai-compatibility). Installed-doc hash and safe provider/tool metadata are in runtime-review.json.

## Recovery and focused tests

| Actual command/check | Result and scope |
| --- | --- |
| `python3 scripts/docker.py compose exec -T api python -m backend.contract_check` | Final66 passed in6.668s; exit0. Created new isolated contract database: lenny_contract_937b1d094280. Fresh DB retained.42 unit/parser/mock +24 PostgreSQL/API; conversation DB selections/timeouts are deliberately mocked. Retrieval fixtures use actual local embeddings/SQL. |
| `python3 scripts/docker.py compose exec -T api node --test agent/test_conversation_policy.ts` | Four passed: exact first-turn adaptation, rejecting final examples, unapproved arguments/tools and source/later-turn authorization. |
| `.venv-phase2/bin/python scripts/live_phase5.py --base-url http://127.0.0.1:8080` | Final run081843 completed exit0, all requested contracts/isolation pass. Manual quality limits above remain. |
| `.venv-phase2/bin/python scripts/lifecycle_phase5.py` | Actual timeout1.108s, explicit cancel2.379s, disconnect3.214s including cleanup; all Pi reaped/bridge closed. Retry reused same user/run, attempt2; completed replay0.032s without inference. Empty retrieval returned NONE/gap. Four users/two successful replies=six messages. |
| Idle `compose up -d api` recreation, then `.venv-phase2/bin/python scripts/reopen_phase5.py` | Identical saved messages/source snapshot after restart, completed state preserved; unknown/cross-session source404; readiness200, partial corpus/product_ready=false. |
| `python3 scripts/docker.py compose exec -T api python -m backend.conversation_check` | Actual Pi/local Ollama/embedding/SQL with hostile synthetic source, separate retained DB `lenny_chat_fixture_4dc1ffccbcc3`: correct17-day quote, exact citation,5.888s, no obeyed999-day/shell directive. One fixture, not comprehensive security proof; before final speaker-boundary hardening. |
| `npm --prefix frontend run build` and Docker web build | TypeScript/Vite passed; final proxy streams actual local checks. No browser interaction pass. |
| `scripts/review_phase5.py` and `scripts/inspect_phase5.py` | Read-only preservation/runtime/framing audit and actual final citation opening passed. |

[Lifecycle and restart proof](agent-transcripts/phase-05/lifecycle-20261106T074854/results.jsonl), [restart snapshot comparison](agent-transcripts/phase-05/lifecycle-20261106T074854/restart-after.json), [hostile fixture](agent-transcripts/phase-05/hostile-source.json), [exact captured commands](agent-transcripts/phase-05/commands.jsonl). HTTP200 alone is not an inference success; terminal run states are checked. The full operational commands/limits are in [operations](phase-05-operations.md).

Unknown IDs, malformed selections, exact Unicode/decimal/quoted punctuation, speaker separation, unsafe links, association transaction rollback, old-source snapshot retention and orphan recovery have focused contract tests. Default deadline75s/max90s, one retrieval/two provider turns, context4096/output128, prompt cap12800 bytes; at most16 excerpt groups/6000 text bytes from eight passages/3200 estimated source tokens. No unvalidated token stream. Final model inputs1274–1548 tokens and10 output tokens per final selection; these are selected excerpts, not long answers. The context/byte budget limits operation size but does not establish completeness.

## Failures and corrections

Initial requests copied schema examples without calling tools and failed `rpc_rejected`. Later the model serialized its function request as text. After strict adaptation, actual tools ran but multi-ID example copying and unrelated selections remained. Simplifying to one evidence ID, preserving the raw query after a failed rewriting attempt and fixing closing-quote sentence extraction produced the correct two answers. A final source review added a regression preventing excerpt groups from crossing speaker headers. All earlier attempts are retained; old automatic flags were not rewritten into semantic passes.

The unsupported private-data request still fails model abstention: raw selection is E1; a narrow server rule supplies the honest final gap after real retrieval/model work. It does not handle all unsupported classes. Test scripts also had corrected bookkeeping errors (expected8 instead of6 messages; assumed source.message_id); an initial JSX error and test connection warning were corrected. The final suite has no prior connection ResourceWarning; a Starlette/HTTPX test-client deprecation remains. [Failure audit](agent-transcripts/phase-05/failure-review.json) names each attempt/correction.

## Machine, preservation and outstanding limits

Existing pins/models remain: Pi1.5.0/Node24.9.0, Python3.13.5/FastAPI0.138.1, SQLAlchemy2.0.57/Alembic1.20.1/psycopg3.2.12, PostgreSQL16.15/pgvector0.8.7, Ollama0.30.11. qwen3:0.6b digest `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435`; local Nomic digest `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`. No new dependency/model version was claimed compatible without actual existing build/test evidence.

Post-check M2/eight cores/8GiB snapshot:9584.31MiB host-wide swap,24% memory-pressure free percentage,109921341440 disk bytes free. API66.3MiB/768MiB limit, DB126.8/512, web7.422/64 then. Earlier loaded qwen footprint was1022309171 bytes/context4096. This is not peak telemetry or causal swap attribution. Keep one bounded generation; a larger local model needs separate measured memory/quality work or more RAM. Larger context/model, free synthesis, deterministic server-only retrieval and cloud are alternatives with latency, fidelity, framework-role or privacy trade-offs, not tested upgrades. D-14–16 record the choice/downside/user impact.

All221 protected prior files, original spike and Phase1–4 evidence remain hash-identical. Original six message/session hashes match; host5432 and existing pgdata untouched. Actual schema is0003_conversation; only nine podcast episodes/373 chunks remain active. Private raw RPC/diagnostics survive API recreation in0700 chat_traces; safe metadata/hashes are recorded. Raw retention needs future policy. Source/image identity and final safe-content audit are in source-manifest.json/final-review.json; no Git revision exists.

Browser is separately **blocked before connection**: `Importing module "node:process" is not allowed in node_repl`. No navigation, screenshot, source-button interaction, responsive or accessibility pass is claimed. Chat/source inspector code/build and HTTP source inspection are demonstrated. [Actual Browser error](agent-transcripts/phase-05/browser-check.json). Independent expert review,>=10 unique-answer quality review, general abstention/routing, full corpus, essays/artifacts, cloud, clean evaluator, rights, complete coding export and final demo remain open.

On resume, the final live command was still recoverable and completed exit0 with all five JSONL rows; the66-test suite had also completed. No verification needed restarting. Only read-only final/source review and unfinished documentation were completed. **Stop at Phase5 and wait for user go-ahead before Prompt06.**
