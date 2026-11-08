# Saved OpenRouter400 diagnosis and one corrective rerun

**Corrective smoke PASS:** OpenRouter / `google/gemini-2.5-flash-lite`,6.512846s, citationS1 resolves to the actually retrieved public passage and supports the answer. Provider/model unchanged; exactly one rerun. No automatic fallback or manual answer edit. [Actual result](agent-transcripts/phase-09/openrouter-live-corrected.json).

## What the original saved evidence actually contains

Original run `a1d3ea92-0d59-4fb4-a0c8-1627f27dbbbb` failed in4.940503s. The available sanitized error is **provider_http_400**. There is **no retained upstream error message body to quote**. The saved stdout has29 projected protocol records:two model turns and one tool start/end. The response stream ends in failed. Stderr contains only diagnostic byte counts. `get_messages` response data, HTTP headers and historical request bodies were not saved. The generic RemoteError discarded the provider text after extracting the status. No original error sentence has been invented or reconstructed.

The native `search_transcripts` invocation and successful retrieval prove the first cloud-driven turn succeeded far enough to call the tool. It did not fail on initial authentication or initial tool selection. The failure occurred after evidence was returned and before a cited answer. Historical tool-call IDs and literal serialized arguments/results are unavailable, so the saved trace cannot independently rule out every serialization defect.

## Installed-Pi serializer comparison (offline, synthetic)

Used actual installed `@earendil-works/pi-ai`1.5.0 and the app's provider-request transformer. Captured only metadata inside onPayload, then deliberately stopped before fetch: **zero network/provider calls**. Synthetic history is clearly labelled; this is not a recovered historical payload.

| Field | First turn | Follow-up before fix |
| --- | --- | --- |
| Model | google/gemini-2.5-flash-lite | Same |
| Roles | system,user | system,user,assistant,tool,user |
| Tool definition count |1 |1 retained |
| Tool choice | forced search_transcripts | none |
| Tool call/result | none yet | assistant.tool_calls; function arguments JSON string; tool-role JSON text; IDs match in the probe |
| max_tokens / temperature |128 /0 |128 /0 |
| stream / usage |true /include_usage |same |
| response_format |absent |json_object |
| Routing |fallbacks false, require_parameters true, data_collection deny |same |

Pi's installed serializer writes assistant function arguments using JSON.stringify and tool-result content as JSON text with the corresponding tool_call_id. The offline probe finds no ID-link break. Again, this is not proof of the lost original ID values. [Original offline metadata](agent-transcripts/phase-09/openrouter-sdk-offline-original.json).

## Specific issue and smallest fix

The follow-up uniquely combined tool definitions/history with JSON response MIME mode. Google's [structured output documentation](https://ai.google.dev/gemini-api/docs/structured-output) and [tools documentation](https://ai.google.dev/gemini-api/docs/tools) describe combined structured output/tools support for the Gemini3 series, rather than2.5. This establishes a concrete compatibility defect in our request construction; it does not recover the original provider's error text.

Removed only `response_format` from the OpenRouter conversation transform. Both requests still ask for the same bounded result, with identical model, tool/history, matching call/result linkage, routing policies, max128 output, temperature0 and input/context limits. The prompt still requests the JSON evidence_id object; Python still strictly parses it and validates the ID against executed retrieval evidence. No parser relaxation, citation insertion, invented facts, message-history rewrite or provider change. The exact offline before/after metadata diff is solely turn2.response_format:json_object -> absent. [Fixed offline metadata](agent-transcripts/phase-09/openrouter-sdk-offline-fixed.json).

Ten Node policy tests pass, including an explicit regression preserving tool replay while dropping JSON mode; nine focused Python conversation tests pass. The first Python check was sandbox-blocked on localhost binding; rerun with authorized loopback access passed. That was a test-environment error, not a model failure. No additional inference was used by the probes/tests.

## One real corrective test and claim review

Same documented public-only FastAPI/Pi/OpenRouter smoke ran once, after rebuilding the API image. Public pinned transcript hash, all52 scoped chunks and empty prior history guards remain. New run `5c0f723b-4a11-4ef3-bbb7-0fceb24783f5`, session `157d4419-4739-44b3-9988-d69642468bae`, request reference `7a8a7ae53f784f30ab2643c352e8d5df`. Completed in **6.512845794s**, native search_transcripts query=current once,10 candidate evidence IDs. No textual tool normalization. API stream ends completed. Process reaped and bridge closed.

The answer quotes Sean Ellis's survey question, “how would you feel if you could no longer use this product?” Citation **S1** resolves via the source endpoint (HTTP200) to retrieved chunk `c0aa1ec1-9da2-5bc9-a1ed-550df1f12411`. The quote exactly matches its immutable original span; the stored passage has SHA256 `498e939ea74c0d2a17a9c5873cc10c29772edfca5374caae15d19e379a3af384`, and directly answers the question asked. Direct review found no added factual claim beyond that quoted evidence. No final answer was manually edited.

Recorded usage input1486/output10 is the final selection turn only, not total two-turn billing. This single successful smoke does not establish broad model reliability or essay quality. The earlier1,208-word essay remains manually reviewed; autonomous essay quality is unverified. Initial failure/raw private output remain preserved; no further cloud retry. Keys/headers/full payloads stay out of logs, with exact-key scans recorded separately. No commit/push or Prompt10.
