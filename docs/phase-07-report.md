# Phase 7: artifact viewer and reviewed endpoint integration

7 November 2026, India time. **Reviewed integration gate passed.** Fixture rendering, fresh generation, manual review, browser security and restart checks are separate evidence. Stop before Prompt08.

Phase6 was first recorded exactly as requested: **“reviewed essay passed; standard endpoint verification pending.”** The pending check is now demonstrated for one fresh, explicitly edited and reviewed endpoint run. This does not establish autonomous essay quality.

## Rendering fixture: no new inference

The previously reviewed1,319-word essay remains unchanged in its original session. Its Markdown and complete HTML/CSS exports carry `reviewed_fixture` provenance and the visible label “Reviewed essay fixture · rendering check only.” Both rendered six sections, emphasis and citation labels in an actual isolated Chrome browser; S2 opened the actual stored Lookout passage. This is rendering evidence, not generation success. `browser-fixture.json` and `browser-fixture-initial.json` record the checks.

Artifacts are created from an owned completed assistant message. Server formatting copies its content/citations; no extra model call rewrites it into HTML. Markdown uses CommonMark parsing with raw HTML disabled. Complete HTML/CSS documents use a parser-based HTML allowlist, constrained inline CSS and a trusted stylesheet. The preview is a script-disabled, opaque-origin sandbox iframe with a restrictive CSP and no referrer. Scripts, forms, images, nested frames, navigation and external resources are not supported. Original citation labels remain in the body; source buttons outside the iframe inspect immutable snapshots. Ordinary chat documents are labelled “Saved conversation,” not essay fixtures.

## Fresh standard endpoint run

Actual `POST /api/sessions/{sid}/essays` in `live_phase7.py` executed the new evidence-first service. It performed fresh hybrid topic retrieval from the unchanged nine-episode/373-passage index, selected exact guest-source spans with stored offsets/hashes and generated only application advice through Pi/localqwen3:1.7b. No fixture file or manually prepared Phase6 plan was injected.

One full run,43.356s total, six fresh Pi stages and one bounded length revision (seven provider requests). Tool policy stayed empty, no structured grammar, context4096/output384, temperature0, thinking off,90s per-stage/600s overall. Safe protocol hashes/diagnostics prove every request used localqwen3:1.7b; all processes reaped and initial histories empty. Chat remainsqwen3:0.6b; no cloud inference or model download. Raw protocol and diagnostics stay private separately.

**Raw output was not accepted.** After the automatic length repair it contained1,143 words, but leaked “91 words” as an uncited paragraph, clipped a quotation and did not present enough context for the requested case/benefit sequence. `result.json`, `draft.md`, `events.jsonl` and protocol projections preserve that actual failure.

Through explicit standard review APIs, Codex revised all six advice paragraphs and three source selections. Evidence edits accept only offsets into the existing owned immutable source, never arbitrary factual text. They added complete Lookout intervention/outcome context, the benefit-question sequence and complete limitations sentences. Advice edits removed instruction leakage, weak metrics, repeated caveats and outcome assurances. These are **substantial manual editorial changes**, not untouched model output or autonomous success. Before/after text and source spans remain in metadata and `manual-edit-request.json`.

Final reviewed essay: **1,270 words**, within the unchanged1,125–1,375 range; six complete sections, five action bullets, one selective bold span and13 exact cited factual blocks across S1–S6. Individual section lengths remain targets. Every source span/hash and adjacent citation was checked; the whole original passages were reviewed for context. The Lookout7% refers to disappointment without the product;40% is the subsequent survey cohort. No measured engagement/conversion improvement, survey guarantee or isolated onboarding effect is claimed. Advice proposes experiments, observations and decisions, with expected effects as hypotheses. The result is quote-heavy and evidence-led rather than an original narrative.

The normal review endpoint saved the accepted assistant reply and its sources. Markdown and HTML artifacts were then created from that reply, labelled `live_endpoint` and “manually reviewed and edited.” Artifacts list the generation run and manual-edit count. This is distinct from the rendering fixture.

## Actual browser and restart verification

The in-app browser connector still fails during bootstrap (`node:process` import forbidden). Actual browser checks used a fresh isolated headless **Chrome157.0.8103.38** context via host Playwright; no existing browser profiles or signed-in sessions were read. This fallback is explicitly separate from the unavailable connector.

Hostile HTML exercised script/event handlers, forms, SVG/MathML, nested frames, external images/CSS, navigation/refresh and parent-style injection in the actual viewer. Sanitizer and iframe checks observed **zero attack-origin requests, dialogs, popups, navigation, parent DOM modification or parent-style changes**; console and page errors were empty. These are sampled fixtures in one browser version, not a universal security guarantee.

Restarted API and web only; retained databases, volumes and host Ollama. Both live artifacts reopened through API and browser. Content/preview hashes and all six original source hashes matched before/after. The accepted essay remained completed and byte-identical; S2 source inspection worked after restart. Basic390px containment and desktop viewing passed without horizontal overflow. This is not full Phase8 accessibility/responsive acceptance. `restart-reopen.json` and `final-visual.json` contain the results.

## Checks, changes and limitations

- Final **98 unit/contract/real PostgreSQL/API checks passed**; generation in contract tests is explicitly mocked. Separate actual local run above. Earlier97-test run also passed before adding the source-span bounds contract.
- Frontend TypeScript/build and Docker API/web builds passed. The final viewer clarifies that retrieved highlights differ from the full original citation context.
- Proved and pinned parser dependencies: nh3 0.3.7, markdown-it-py4.2.0, mdurl0.1.2. Host-only browser tooling is in scripts/browser-requirements.lock. No new schema migration was needed: the foundation artifact table and Phase6 long-message fix were retained.
- Focused tests cover unsafe parsing, raw-HTML Markdown handling, bounded source edits, artifact ownership, unknown citations, both saved formats and duplicate-create replay.
- A host-only unit launch initially lacked a synthetic DB setting and was corrected before passing. The first HTML preview showed duplicate title text; sanitization was corrected and the final browser display inspected. All actual command outcomes are retained in commands.jsonl. Logs are bounded; some full-suite output tails are explicitly marked truncated.

Changes are in backend/app/artifacts.py, evidence_first.py, model-specific PiRPC configuration, standard essay/review APIs and frontend/src/ArtifactPanel.tsx. Runtime setup and the existing databases/models are preserved. No push/publication is part of this phase.

Manual source review and editing remain necessary. The app does not claim arbitrary facts are automatically approved. Editorial review is currently API-based; a dedicated essay review UI, full user journey, comprehensive accessibility, other browsers and full-corpus quality remain later work. HTML is server-derived static formatting of an accepted reply, not a separate model-authored freeform website. Arbitrary scripts, uploads, external resources and artifact revision history are outside this implementation.

Evidence: [fresh raw run](agent-transcripts/phase-07/live-20261106T212600/result.json), [reviewed essay](agent-transcripts/phase-07/live-20261106T212600/essay.md), [claim review](agent-transcripts/phase-07/live-20261106T212600/claim-review.json), [manual changes](agent-transcripts/phase-07/live-20261106T212600/manual-edit-request.json), [fixture/browser security](agent-transcripts/phase-07/browser-fixture.json), [restart/reopen](agent-transcripts/phase-07/restart-reopen.json). Screenshots remain in the local ignored browser-evidence directory; their hashes are recorded separately.
