# GPT-OSS-120B final-answer cap test — 8 November 2026

**PASS for the exact cited question/follow-up pair.** Base `bffcace365fe97e538599d12acb6989c9e0beab7` plus an **uncommitted isolated test patch**. No commit,push,deployment,upload or submission. Broader scenarios and essay quality were not rerun.

## Scoped change

The effective OpenRouter wire cap was `max_tokens:128` in `agent/provider_policy.ts::openrouterConversationPayload`. Python/Pi also advertise a128 default,but the extension's late request hook controls the serialized cap. No shared Python/Ollama/default model limit was changed.

The patch selects **1,024** only when all conditions hold:model is exactly `openai/gpt-oss-120b`;provider turn is2;nonempty controlled retrieval evidence IDs exist;and the serialized history contains a tool result linked to an assistant `search_transcripts` call. Otherwise128 remains. The tool-call turn,other OpenRouter models,local Ollama,essay advice,routing,prompts,temperature,context and retry behavior remain unchanged.

Files left in this isolated checkout for review:

- `agent/provider_policy.ts`:scoped cap selection.
- `agent/test_provider_policy.ts`:positive and negative guard regression.
- `scripts/probe_gptoss_output_cap.mjs`:offline installed-SDK/real-extension wire probe.
- This report.

## Verification before inference

New regression initially failed128 versus1024;then **11/11 Node policy/conversation/Markdown checks passed**. `git diff --check` passed. Rebuilt only `lenny_phase12_repair` API image;original databases/volumes and other stacks preserved.

Before sending a cloud question,the running container executed the actual `conversation.ts` hook through the installed Pi/OpenAI-compatible serializer. Fetches were intercepted in that separate Node process with synthetic responses;no network request occurred. The actual serialized bodies showed:

| Model | Tool-call cap | Final-answer cap |
| --- | --- | --- |
| openai/gpt-oss-120b |128|**1024**|
| google/gemini-2.5-flash-lite |128|128|
| local qwen3:0.6b |128|128|

Tool call/result IDs remained linked;provider.only absent;fallback disabled. The loaded policy/extension hashes matched checkout files. The probe also retained Ollama's existing128-token max_completion_tokens alias. Its first run stopped before inference because the probe incorrectly required that alias to be absent;corrected only the assertion,preserved that failure at `/private/tmp/lenny-openrouter120b-cap1024/evidence/20261108T065326/`,and reran the probe successfully. That preliminary check made **zero cloud generation requests**. There was one actual question attempt and its conditional follow-up,no model retries.

## Real public-only run

Backend and UI selected **OpenRouter / openai/gpt-oss-120b** before the request. Default routing retained `allow_fallbacks:false,require_parameters:true,data_collection:deny`,with no provider.only. Existing key supplied only through server configuration/environment;no key/header/credential file copying to clients or Git.

All52 active Sean Ellis chunks matched the pinned public transcript revision/hash before inference. Fresh session;first context empty,follow-up uses the first public user question. Hybrid retrieval ran and completed on **both** turns,with one controlled search call per question.

Exact question:**How did Sean Ellis change onboarding at Lookout?**

Exact follow-up:**What did they report for the next cohort in the must-have survey?**

| Request | Pi/native finish | Final output tokens | Reasoning subset | UI latency | Final upstream vendor | Citation support |
| --- | --- | --- | --- | --- | --- | --- |
| Question | stop / stop | 147 | 129 | 17.857s | Venice | PASS |
| Follow-up | stop / stop | 144 | 123 | 11.000s | unconfirmed | PASS |

Reasoning counts are included in output counts. Tool-call turns remained within their128 caps:35 output/0 reasoning for the question,37/0 for the follow-up. Final answer text was present;final-turn tool-call counts were0. Streaming and get_messages metadata agree. No sanitized model error code was recorded. Timing includes the metadata-only diagnostic/read-only provider lookups.

The question's tool-call vendor was **PrimeIntellect** and its final-answer vendor **Venice**,confirmed from generation metadata. Follow-up vendor metadata was unavailable (read-only lookup404);no inference retry or vendor attribution was invented. Those lookup404s are not answer failures. Default routing may select different vendors for the separate model turns;no fallback was requested.

Both answers cite **S1 →53054eb0-beee-5be4-b2f1-99ca9b2eac2d**,source SHA `6af2a6e031826805e855ec262b1f228e3773b5b99265a1d01870f0d4e6e9ceda`. Original source panels opened in the browser with focus/return checks;all attached spans were exact. The emitted quote hashes match the previously reviewed,supported Ollama answers byte-for-byte:

- Question:supports antivirus-first setup and protected confirmation;no measured engagement/conversion improvement is claimed.
- Follow-up:supports next-cohort40% very-disappointed survey wording;it is a survey response,not a measured engagement/conversion outcome.

No transcript or reasoning text,raw response payload,authorization header or API key was written to the new diagnostic logs. Records contain only permitted metadata,IDs/hashes and test results. Pi processes/bridges cleaned up for both requests. Prior raw/failed evidence remains unchanged.

## Restoration and review state

Ollama restored in backend/proxied provider endpoint and **actual UI**:chat **qwen3:0.6b**,essays **qwen3:1.7b**,local provider active for the demo. Temporary Python diagnostic mount removed;running Python adapter matches original bffcace bytes. The requested TypeScript cap patch remains both in the isolated checkout and rebuilt API image;the Ollama extension is byte-identical to HEAD. `.env` unchanged. All8 retained protocol/diagnostic files and captured harness files passed the configured-key check. No new local inference was made during restoration.

Evidence:

- [Pre-inference serialized wire proof](agent-transcripts/openrouter-cap-publication/serialized-cap-preflight.json)
- [Actual result/finish and token metadata](agent-transcripts/openrouter-cap-publication/result.json)
- [Citation review](agent-transcripts/openrouter-cap-publication/citation-review.json)
- [Final UI,image and credential verification](agent-transcripts/openrouter-cap-publication/final-verification.json)

Review URL:http://localhost:18081/workspace. The main checkout,index,previous publication trees and prior saved work were not modified;the isolated database contains the authorized new test session. This is a narrow cloud pair pass;historical0/5 scenario results and raw-essay limitations remain unchanged.

Publication note,9 November2026:the exact two-file patch was reviewed and its11 Node regressions rerun successfully before inclusion. The links above are sanitized projections of the original Nov8 metadata. This is historical cloud evidence;the current release rehearsal remains local-only.
