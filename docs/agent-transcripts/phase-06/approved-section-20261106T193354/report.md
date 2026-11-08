# Approved-fact Lookout section: failed, no full essay

7 November2026 India time (raw timestamps UTC6 November). The user authorized a new workflow: fixed factual statements and citations, model-written transitions/labelled advice, one1.7B section, full essay only on section pass. **Section failed; stop before Phase7.**

## Approved factual boundary

[approved-facts.json](approved-facts.json) was saved before inference. Five source-backed statements cover the correct product-level7% survey finding and antivirus subgroup, Lookout positioning/onboarding, next-cohort40% survey response, qualified need to understand must-have users and the benefit-question sequence. Each is paired with its exact S2/S3 label AND immutable chunk ID, source-text hash and exact evidence anchor. Anchors and source identity were validated against the original stored excerpts in the host and container. Semantic approval is a direct human-style source review by Codex, not automatically proved by substring matching.

S2:53054eb0-beee-5be4-b2f1-99ca9b2eac2d. S3:f5f40dd8-e8fb-5e74-9834-e45e31331549. Same snapshots as both failed runs; neither prior output/review changed. No measured engagement/conversion gain, isolated onboarding causal estimate or guaranteed product-market fit was approved.

New backend/app/approved_writing.py accepts standalone fact tokens and keeps factual text/citations server-owned: each token maps atomically to its fixed statement and source label. Missing/reordered/duplicated/inline markers, model citations, extra factual blocks, unsafe Markdown and obvious factual/guarantee additions in advice reject the entire draft. No silent repair or deletion. Free prose must be labelled Application; lexical screens are not semantic proof and manual review still rejects factual assertions hidden under that label. This is Markdown source assembly, not an HTML artifact/browser renderer or Phase7.

## Actual test and failure

Command: `python3 scripts/capture_phase6.py .venv-phase2/bin/python scripts/approved_section_phase6.py`.

First launch failed before any model/session creation with a host import-path error; corrected by adding the project root to sys.path. Both actual command results are preserved. The subsequent launch executed **one** Pi/local Ollama request, normal stop, no model retry, exit2 on contract rejection. No direct Ollama generation bypass.

Model qwen3:1.7b, digest8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7. Same existing Pi snapshot-writing path:4096 context,850 output,temperature0,thinking off,grammar off,no active tools,90s stage deadline. New prompt/factual projection intentionally differs from the previous free-prose test. Model sees approved statements, not the unfiltered excerpts; the actual original excerpts remain in PostgreSQL and are validated as authority. The new renderer module is loaded into the isolated test child from reviewed source; running API/chat were not changed or restarted.

Actual result: **27.678s,360 raw words vs210 target**,1308 input/437 output tokens. All five approved statements appear verbatim, preserving the corrected7% wording, but the model repeats them in a long Application paragraph with inline tokens rather than standalone blocks. There are **zero S2/S3 citation IDs** in its raw output. The renderer fails with `advice_markup_or_instruction_invalid` when it encounters inline markers; zero accepted rendered sections and no section.md is created. Raw draft is saved BEFORE validation in both private evidence and [raw.md](raw.md). It was not edited into a passing answer.

Manual review independently fails: new universal claims about the first step in any product process, interview use, guaranteed needs alignment and essential conditions for any product success are not established by S2/S3. Application labels do not turn these assertions into proposed actions. The draft also leaks commentary about what the Foundation section should focus on. The giant middle paragraph, repetitive generalized advice and excess length impair readability. It does not explicitly claim measured Lookout engagement/conversion gains; avoiding that specific error does not cure these failures. [review.json](review.json) records the complete support assessment and checks every approved statement.

Normal termination: fresh Pi history0, process reaped, bridge closed. [protocol-check.json](protocol-check.json) records455 JSON stdout frames, separate diagnostic hashes, one local provider request and grammar=false. Original raw protocol/diagnostics stay separate in private chat_traces. New draft/run/source copies persist in a fresh owned PostgreSQL session; this partial probe remains failed and is not an accepted assistant essay.

## Verification and gate

Ten focused unit/writing tests passed (three new renderer contracts plus seven existing writing regressions): atomic fact/citation placement, rejection of citation/factual injection and malformed tokens, source/anchor drift. These are distinct from the failed real local smoke. Prior82 backend/five Node results were not rerun or promoted to new quality evidence. No production route was migrated; no full1250-word workflow is claimed fixed.

Chat remains local qwen3:0.6b with cloud disabled, both old failed runs unchanged (preservation.json). New evidence, renderer/tests and isolated runner remain local, no commit/push. The full essay was NOT run because the single section failed. Original1125–1375-word, six-part structure/claim-support rubric remains unchanged and unmet. No retry, fallback, Phase7 or browser acceptance claim.
