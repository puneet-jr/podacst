# Phase 6: qwen3:1.7b Foundation comparison blocked before inference

6 November 2026. **No section verdict is available for 1.7B. Phase 6 remains blocked; stop before Phase 7.**

The user authorized a model-only comparison against the failed saved 0.6B Foundation section, with a full essay only after a section grounding pass. The earlier raw output and claim review are byte-for-byte preserved (all baseline-folder hashes verified). The verified Markdown transport fix was committed separately as `4323911`, `fix: draft essays as Markdown; record failed 0.6B grounding`, at the actual current timestamp 2026-11-06T20:41:17+05:30. That commit records a failed grounding check, not a verified essay fix. It has not been pushed.

## Commands and actual results

- Preflight: local `/api/tags` showed only qwen3:0.6b and nomic-embed-text:latest. `/api/providers` selected local 0.6B, no automatic fallback, cloud disabled. M2/8 GiB, 109,765,488,640 bytes disk free, 9,724.31 MiB host-wide swap. See `qwen17-preflight.json`.
- `python3 scripts/capture_phase6.py .venv-phase2/bin/python scripts/pull_qwen17.py`: invokes local Ollama POST `/api/pull` with `model=qwen3:1.7b, stream=true`. Exit 1 after 1,037.246 seconds: Ollama exhausted its retries with **TLS handshake timeout** from the model storage endpoint. See `qwen17-pull-failed.json`.
- Same command, one explicit download-resume attempt: exit 1 after 728.674 seconds: Ollama exhausted its retries with **connection reset by peer**. See `qwen17-pull-retry-failed.json`. This retried model transport, not inference. No daemon restart, model deletion, network-setting change or cloud inference.
- Final local `/api/tags` still lacks qwen3:1.7b. `/api/providers` remains local qwen3:0.6b with cloud disabled. All old probe files match their pre-task SHA256 values. See `qwen17-final-check.json`.

The failed weight file has 1,359,279,776 logical bytes (preallocated) and 571,424,768 allocated bytes. Neither proves a complete verified model. Keep partial weights for possible later resume; do not delete existing models. Final disk free 109,201,502,208 bytes; host-wide swap 10,408.06 MiB. These are snapshots, not model peak memory or causal attribution. Model fit, throughput and quality cannot be measured without successful installation/inference.

Signed storage URLs and network endpoint addresses are omitted from public failure evidence. Actual private originals remain in ignored `.cache`; error category, times, exit codes and progress are preserved. Model downloads use the network; prompts/inference were never sent to cloud.

## Comparison outcome

| Measure | Preserved qwen3:0.6b | qwen3:1.7b |
| --- | --- | --- |
| Section elapsed time | 16.323s | Not run; download failed |
| Words / target | 362 / 210 | No output |
| Exact generated citation IDs | None | Not measurable |
| Factual support | Core Lookout description partly supported; claimed engagement/conversion improvement unsupported | Not measurable |
| Prompt leakage | Purpose and Target | Not measurable |
| Grounding verdict | Failed | Blocked before inference |

The original [0.6B raw section](markdown-section-20261106T150144/section.md) and [claim review](markdown-section-20261106T150144/review.json) are unchanged. S2 supports Lookout's antivirus positioning and onboarding changes and a later must-have survey result; it does not establish measured engagement/conversion improvement. S3 does not supply that missing outcome. Citation existence alone would not prove such a claim.

**There is no 1.7B raw-output path: zero section requests and zero full-essay runs occurred.** Do not report this as a failed 1.7B grounding result or a model-fit failure.

`scripts/compare_qwen17_section.py` is prepared but **not executed**. If separately resumed after installation, it checks original Pi prompt, saved outline, S2/S3 IDs and hashes and runtime code against commit 4323911 before one invocation of the unchanged probe. Only child environment `GENERATION_MODEL=qwen3:1.7b` changes; running chat remains 0.6B. Planned unchanged settings: 4,096 context, 850 output tokens, temperature 0, thinking off, grammar off, no active tools, 90-second stage deadline and 210-word target. It records code/prompt/protocol identities and rejects a duplicate comparison directory. A first-load 1.7B sample vs an earlier 0.6B sample would not be a controlled performance benchmark. No improvement is presumed.

No production runtime source changed in this model-download attempt. Previously passed 82 backend and five Node checks remain separate from live-model evidence; they were not rerun to imply local quality. Host runner scripts were syntax-checked only. No app restart, database/volume mutation, full essay, retry of section generation or Phase 7 work. Download failure, rather than Pi integration/tool calling/response generation, is the present blocker.
