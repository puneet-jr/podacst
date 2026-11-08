# Server-assembled Lookout section: facts/citations pass, advice fails

7 November2026 India time. **Overall section verdict: FAILED. No full essay or Phase7.**

The user requested server-owned factual assembly and citations, plus one short Pi/qwen3:1.7b advice paragraph with no case restatement, historical additions or promised outcomes. Original approved facts are fixture data, not a replacement for evidence retrieval in a future topic-specific full workflow.

## Changes and bounds

The server now renders every approved statement and its citation directly, in fixed order. It supplies the Foundation heading and Application label. The model sees no facts, excerpts, fact tokens or citation IDs. New agent/application_advice.ts sets a narrow advice-only system prompt, local provider check, no active tools, one provider request,256 output/4096 context,temperature0,thinking off,plain text with no structured grammar and a4,000-byte prompt bound. The existing validated Python PiRPC starts a fresh isolated Pi process and handles cleanup. This is meaningful Pi-driven advice generation, not a direct Ollama bypass.

backend/app/approved_writing.py adds plain-paragraph screening and atomic server section assembly. Reject labels/IDs/markup, obvious history/guarantees and overly short/long advice; semantic review remains mandatory. The attempted assembled candidate is saved even when advice validation rejects it, clearly distinct from an accepted section. No silently shortened or corrected model output.

## One actual live run

Command: `python3 scripts/capture_phase6.py .venv-phase2/bin/python scripts/server_section_phase6.py`. Exit2, one local provider request, no retry. Model qwen3:1.7b digest8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7. Fresh Pi history0, normal stop, process reaped. Prompt792 bytes,input168/output42 tokens. Elapsed **7.545s**. Chat/API remainqwen3:0.6b with cloud disabled; no app restart or dependency/model download.

Raw model output36 words; complete assembled candidate **175 words including heading**, target210. The35-word shortfall is reported, not turned into a new hidden hard range. Five fixed factual paragraphs keep S2/S3 attached correctly: S2three times, S3twice. Original approved registry is copied byte-for-byte; original source hashes and exact new owned API snapshots verified. See citation-check.json and preservation.json. All earlier failed runs remain unchanged.

The model wrote a concrete comparison action, then: “This helps ensure your product aligns with your messaging and provides a clear path for users.” That is an unsupported benefit/outcome assertion, not just proposed advice. The screen rejected it as application_factual_or_outcome_claim; direct review independently agrees. No explicit Lookout engagement/conversion improvement was invented, and no IDs or instructions leaked, but the overall user constraint still fails.

The five server-rendered claims are supported by S2/S3: correct product-level7% survey and antivirus subgroup; positioning/onboarding changes; combined expectations/speed to value plus later40% survey cohort; qualified need to understand must-have users; primary-benefit question sequence. The later survey cohort is not a measured engagement/conversion result or proof of onboarding-only causality. All factual citations remain adjacent to their exact statements. Readability is improved by clean server formatting, but remains a compact evidence summary with a short length and an unsupported final advice sentence. See review.json for each claim/sentence.

## Saved evidence and gate

- model-output.md: exact unmodified model response.
- assembled-section.md: exact candidate, including rejected advice, not accepted for publication.
- approved-facts.json, inputs.json, result.json, command.json, citation-check.json, preservation.json, review.json.
- Private Pi stdout protocol and stderr diagnostics remain separate under chat_traces/server-sections/<run>/advice.

Twelve focused unit/writing checks passed, including two new assembly/advice checks, separately from the failed real model test. No standard product essay route migration, browser/HTML verification, reliable advice-generation claim or full essay pass. Files stay local/uncommitted; no push. Because the section failed, no topic-retrieval/full-essay run was initiated. Original1125–1375-word, six-section structure/citation/claim rubric remains unchanged and unpassed. Stop before Phase7.
