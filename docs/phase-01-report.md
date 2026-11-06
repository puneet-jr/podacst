# Prompt 01: local Pi integration spike

Completed 6 November 2026, India time. **Phase 1 exit gate PASSED for the documented explicit fixture workflow.** This does not establish a production agent, real transcript RAG, persistence, essay quality or autonomous intent routing. Prompt 02 has not started.

## Brief and actual output

Implemented a disposable Python/FastAPI -> Pi JSONL subprocess -> local Ollama path. Pi calls the sole schema-validated, read-only `search_fixture` tool, receives fixed synthetic evidence, then continues generation using that result. Default shell, arbitrary filesystem/web tools, MCP and unrelated resources are disabled. The Python layer validates framing/errors, enforces budgets, rejects missing/failed tool calls and adds source labels from executed tool results.

Actual final response example: `The review window for the experiment is 13 days, and the evidence code is CEDAR-7319. [FIXTURE-A]`. The bracketed label is server-added from the tool trace; model_text separately preserves the model's original answer. These are invented integration fixtures, not podcast facts.

The selected boundary is **explicit retrieval first**: Pi's extension recognizes one of two fixture topics and anchors the exact query before generation. The local model still emits the actual tool call and Pi executes/validates it and supplies the result to the next model turn. A direct-model bypass was not used. This simplification is justified by the recorded failed attempts below; no reliable general autonomous routing is claimed.

## Actual environment and versions

| Item | Tested observation |
| --- | --- |
| Machine | Apple M2, 8 physical cores, 8 GiB RAM; macOS 26.5.2 arm64. |
| Pre-download inspection | ~100 GiB free disk; memory_pressure free percentage 29%; swap used 16,978.50 MiB. Only nomic-embed-text was already available, embedding-only. |
| Ollama | Existing 0.30.11 installation started on 127.0.0.1:11434 with cloud disabled, one parallel request, one loaded model and 4,096 default context. |
| Generation model | qwen3:0.6b, reported 751.63M parameters, Q4_K_M, 522,653,767 bytes downloaded; digest `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435`. |
| Loaded memory/context | Ollama /api/ps reported 1,022,309,171 bytes and the same size_vram, context_length 4096. Shared-memory usage is not an isolated system-memory benchmark. |
| Pi | Official pi.dev npm package @earendil-works/pi-coding-agent, installed CLI 1.5.0. Registry identity/repository/integrity checked; npm package-lock retained. |
| Node/npm | 24.9.0 / 11.6.0. |
| Python stack | Python 3.13.5, FastAPI 0.138.1, Uvicorn 0.49.0, HTTPX 0.28.1, Pydantic 2.14.3, Starlette 1.10.0; exact tested environment frozen in spike/requirements.lock after checks. |
| Final host reading | Memory free percentage 25%; swap used 4,345.69 MiB; ~113 GiB disk free. Other host workloads changed during testing; do not attribute this swap change to the spike or claim comfortable full-stack headroom. |

No larger model was downloaded. Full-stack model suitability, long-context synthesis and 1,250-word essays remain unverified. The existing embedding model was preserved, not exercised as part of this gate.

## Verification actually run

Final live batch: [20261106T042120-59b3c6/results.jsonl](agent-transcripts/phase-01/20261106T042120-59b3c6/results.jsonl), 09:51:20-09:51:36 India time. Each run has separate stdout.jsonl and stderr.log. Protocol contains actual Pi events; diagnostics contain local provider/tool policy and evidence IDs.

| Check | Actual result |
| --- | --- |
| Five fresh sessions, alternating fixture topics | **5/5 passed**; one successful controlled tool call per request, correct window/code, source attribution from tool evidence. Unique session IDs, empty initial history and no prior synthetic team markers in subsequent histories. |
| Fresh-session latency | 1.766, 1.303, 1.205, 1.729, 2.248 seconds; median **1.729 s**, range **1.205-2.248 s**, n=5. Includes fresh Pi startup, two model turns and tool, excludes dependency installation/downloads and cleanup. Warm model weights; small fixture only. |
| Actual FastAPI TCP request | HTTP 200; supported activation answer and tool trace, ~2.163 seconds wall time. |
| Actual Pi RPC busy rejection | Second unqueued prompt rejected with actual RPC error; not misread as successful generation. |
| Actual cooperative abort | Owned Pi PID reaped; cleanup ~0.025 s. |
| Actual task cancellation during run | Pi PID reaped; cleanup ~0.060 s. |
| Deadline after real agent_start | Timed out during a live operation, Pi PID reaped; cleanup ~0.039 s. |
| HTTP startup/request timeout | HTTP 504, empty active registry, child reaped. Tiny 0.05 s timeout intentionally exercises startup cancellation, distinct from the generation deadline above. |
| HTTP client disconnect | Real socket closed after child creation; disconnected outcome recorded, child reaped and active registry empty. |
| Single-request admission | Concurrent HTTP request received 409. |
| Recovery after timeout/disconnect | Normal retention request HTTP 200 with correct 17-day/BIRCH-4826 evidence. |
| Python protocol/API mocks | **14 tests passed**, including multibyte fragmentation/Unicode separators, invalid/truncated/oversize framing, response-ID correlation/out-of-order responses, RPC/model/tool errors, tool/turn bounds, command allowlist, stubborn-process kill, cancellation and request limits. |
| TypeScript tool/policy tests | **5 tests passed**: bounded query schema and evidence, invalid/ambiguous queries, explicit topic routing, tool budget/cancel and local provider/request policy. |
| Dependency consistency | pip check: no broken requirements; installed Pi version and npm direct dependency inspected. These prove this spike's compatibility, not later app components. |

Commands: `.venv/bin/python -m spike.capture .venv/bin/python -m spike.live`, `.venv/bin/python -m spike.capture .venv/bin/python -m unittest spike.test_adapter -v`, `.venv/bin/python -m spike.capture node --test spike/test_retrieval.ts`, plus version/install/probe commands preserved in [commands.jsonl](agent-transcripts/phase-01/commands.jsonl). Mock outputs are not counted as live local success. No DB integration or browser tests were run; no UI exists yet.

## Failed attempts and corrections (retained, not replaced)

| Evidence | Actual failure and correction |
| --- | --- |
| runs/initial | Initial natural-language question triggered a real tool call and correct answer in ~7.003 s, but the model omitted a requested source label. Server attribution now comes from executed evidence, separately from model wording. |
| CLI help command | Initial help invocation tried to create global ~/.pi/agent and hit sandbox EPERM. Repeated with project-isolated configuration; help succeeded. Runtime always uses temporary config. No global Pi settings changed. |
| First Python suite | 13 passed / 1 error: call method parameter name collided with a payload command keyword before the shell-denial test could run. Renamed the method parameter and reject reserved envelope fields; all 14 then passed. |
| 20261106T041456-ca97fd | 0/5 repeats passed: overly rigid answer-format instruction led to omitted tool calls/invented values; one response stream lacked finish_reason. Adapter rejected them. |
| 20261106T041551-923157 | 0/5: requesting first-turn tool_choice alone did not fix omitted calls. Kept failure; no cloud substitution. |
| 20261106T041735-8d0e8c | 3/5: simpler prompt restored activation calls; retention queries violated enum schema. Pi validation rejected them. |
| 20261106T041841-561e3e | 4/5: bounded text query improved behavior; one ambiguous query named both topics and was correctly rejected. |
| 20261106T042007-0069ba | 0/5: removing example topics made the model omit topic words from search queries. Rejecting those remained correct. |
| Final explicit route | Anchored the exact single-topic query before the model call; 5/5 fresh repeats and all live lifecycle/API checks passed. Earlier failures remain in their own directories and command history. |

These are development iterations, **not SC-01 product acceptance results**, held-out evaluation or a general tool reliability estimate. The primary product metric remains unmeasured. Changing fixture descriptions/prompts had large effects; this model must not yet be selected for the final app's broad research/writing work.

## Build-flow gate and stopping point

Checked against Prompt 01 and Build Flow Sections 2, 5 and 8: actual framework/local-model/tool/result/final flow; bounded context/output/iterations/deadline; fresh session isolation; timeout/cancel/disconnect cleanup; focused mock protocol tests distinct from local runs; exact installed versions and failed attempts; assumptions/risks/decision and architecture draft updated. The expressly allowed simplified retrieval workflow was needed and is documented. **Gate passed within that limited scope.**

Pi subprocesses and temporary API servers were reaped. The user-authorized localhost Ollama server remains running. The spike model was explicitly unloaded with ollama stop qwen3:0.6b afterward; /api/ps returned an empty model list. The downloaded model and existing embedding model remain installed. No external publication, database reset, cloud inference or Phase 2 implementation occurred. Next is Prompt 02, only after the user authorizes that phase.
