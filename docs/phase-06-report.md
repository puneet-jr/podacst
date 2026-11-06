# Phase 6 work in progress: essay gate blocked

Updated6 November2026. **Phase6 gate is NOT passed. No Phase7 work started.** The user authorized one corrected live workflow on resume; it ran once and its failed output is preserved. No further inference, model substitution or cloud fallback was used.

The dedicated API/skill/workflow is implemented: topic/audience/constraints and owned user context → Pi-controlled hybrid evidence retrieval → six-part cited outline → section drafting → deterministic validation → at most one content repair → saved explicit manual review. Additive0004_essays stores failed and unreviewed work separately from accepted assistant replies. A draft cannot bypass the count/format gates through manual approval. Natural-language auto-routing and a dedicated essay UI are not claimed; intent is explicit through POST /api/sessions/{sid}/essays.

## Actual local results

| Attempt | Model/path | Elapsed | Accepted essay words | Completed sections | Result |
| --- | --- | --- | --- | --- | --- |
| Initial104310 | Pi1.5.0/local Ollama qwen3:0.6b; tool required per stage |19.362s |0 |0/6 | Outline succeeded, but model wrote prose without the required section evidence tool. Adapter rejected it. |
| Corrected111551, single requested run | Same Pi/local model; real outline tool then no-tool pinned-snapshot writing |20.466s |0 |0/6 | Outline succeeded. Ollama returned HTTP400: Failed to initialize samplers: failed to parse grammar before section1 generation. |

The correction removed repeated tool routing: later fresh Pi turns receive saved section sources with tools disabled, while the outline still genuinely executes Pi's registered retrieval tool. No fake tool trace is added. The corrected run had1731 input/314 output tokens for its outline. Its section-writing request was9602 prompt bytes/850 output-token allowance, with no active tools. The grammar failure occurs before any section text; it is an integration limitation, not evidence that the model cannot write1250 words. The exact schema keyword/interaction causing rejection was not isolated, and no compatible fix is claimed.

Target1250; accepted1125–1375 including title/headings, excluding reference metadata. There is no final essay to count: the saved draft is null and all six essay sections are incomplete. The six-part outline is separate from essay body count. Structural, citation-to-claim, narrative and final factual-support acceptance cannot pass in the absence of a draft. Content repair used0/1 because generation failed before a repairable draft. This is not a successful local essay test.

## Citations and factual support

Both outlines reference actual saved source labels, not fabricated passage identities. Corrected mapping:

| Label | Exact passage ID | Observed content |
| --- | --- | --- |
| S1 | bdd3d954-095e-5f5a-8be1-5f38377168ff | Survey question and must-have-user feedback. |
| S2 | 53054eb0-beee-5be4-b2f1-99ca9b2eac2d | Lookout antivirus positioning/onboarding case. |
| S3 | f5f40dd8-e8fb-5e74-9834-e45e31331549 | Benefit-focused follow-up questions and understanding users. |
| S4 | 9d370308-1dd5-5657-bdf5-f159a62ce159 | Feature-level survey use/Nubank and subsequent discussion. |
| S5 | fecfa828-2e7a-51f2-ba0a-6bf77a2fb759 | Conversion friction/desire and funnel diagnosis. |
| S6 | ac3b448b-888b-5a93-b57a-87115b25c5c1 | Onboarding/retention caveats and growth sequencing. |

All are Sean Ellis passages from the pinned corpus, within the unchanged nine-episode/373-passage index. Preflight and stored sources demonstrate enough material to attempt the selected topic. Labels exist, but the outline is generic and semantically imperfect: its case section citesS1/S4 instead of the requested Lookout caseS2, and its limitations section cites conversion mechanicsS5 rather than the direct caveatsS6. These are planning weaknesses, not a claim-support pass.

The initial rejected prose contains an unsupported claim that surveys revealed users prioritize ease of navigation, attributed to malformed[S#1]. The suppliedS1 does not establish that claim. The raw fragment is99 words under the final citation-excluding counter, truncated in the first128-token tool-routing turn, never accepted as an essay section. The corrected attempt produced no section prose and therefore no final factual claims to review. Do not describe a valid outline label as verified support for a nonexistent essay.

## Verification and limits

Final container suite: **81 passed in6.790s**, fresh retained PostgreSQL database, migration0004_essays. It includes original regressions, six writing checks, three explicit adapter-boundary mocks and six real DB/API essay tests with deliberately mocked generation. Earlier78-test suite passed before the integration correction. Nine focused writing/adapter tests passed. These checks do not establish local essay quality.

Before the corrected run,17 saved code/skill/lock files matched the running image exactly; readiness confirmed host Ollama reachability and the partial nine-episode index. Git status reported no repository at that time. Neither the final81-test command nor a corrected live run was interrupted: tests had finished and no corrected live process existed on resume; exactly one corrected run was then started and finished exit2. Both failed attempts remain in their own directories. All recorded Pi processes were reaped and bridges closed.

Existing model digest7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435; local Nomic digest0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f. No dependency/model download. Preflight M2/8GiB:9483.81MiB host-wide swap,26% memory-pressure free percentage,111039811584 bytes disk free; snapshots, not peak/causal attribution. Larger hardware/model is not a proved remedy for this grammar rejection.

The guide was read directly and mapped in [writing-guide-mapping.md](writing-guide-mapping.md); style instructions and transcript facts are separate. [Operations](phase-06-operations.md) document budgets, persistence and review. Browser acceptance remains blocked from Phase5; no new visual/interaction pass. Full corpus, cloud, general model quality, essays/artifacts, clean evaluator, independent expert review and demo remain incomplete.

Evidence: [initial failed run](agent-transcripts/phase-06/live-20261106T104310/result.json), [corrected failed run](agent-transcripts/phase-06/live-20261106T111551/result.json), [outline](agent-transcripts/phase-06/live-20261106T111551/outline.json), [exact grammar error](agent-transcripts/phase-06/failure-diagnostics.json), [source verification](agent-transcripts/phase-06/pre-run-source-verification.json), [commands](agent-transcripts/phase-06/commands.jsonl). Full original source payloads/raw protocols remain private; public copies are explicitly sanitized as described in [publication notes](agent-transcripts/PUBLICATION.md).

Next technical investigation is a reduced provider response schema with server-side bounds retained, followed by an explicitly authorized new local test. That fix has not been implemented or proved. **Phase6 remains blocked; stop before Phase7.**
