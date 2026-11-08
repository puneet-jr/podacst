# Phase 12 — publication preparation and demo review

**Review package ready; submission NO-GO.** Private base candidate `f89807d8db16c20e652590a6470810e5eb60b078`; standalone export `/private/tmp/lenny-publication-f89807d`. No commit, push, deployment, upload or submission. No candidate runtime changes. The normal working tree, bounded experiment, full index and saved work remain intact.

## Publication selection

Exported the 701 tracked candidate files without `.git` or history, plus explicitly listed Prompt 12 docs/helpers/safe evidence. All **41 pre-experiment runtime hashes match**. The export is a reviewable derivative tree, not a claim that a new Git revision was rehearsed or the existing public repository is complete. The candidate checkout remains clean at the exact requested SHA.

Runtime/source contents include React/CSS, FastAPI, Pi adapter/tools/skill, PostgreSQL migrations, Compose/Docker, pinned locks, ingestion/evaluation/operations helpers, tests and handoff documents. Bounded-pass multi-evidence/error-copy experiments are excluded because they are absent from the selected candidate; no root reset was used.

Of 469 historical evidence files: 347 JSON/JSONL files become metadata/hash projections, 99 raw output files become clearly labelled omission receipts, 22 narrative reports/ledgers remain, and one minimal **previously reviewed artifact fixture** remains for deterministic UI regression. Its final body and curated fact/citation mappings are distinct from raw transcript payloads; raw model-stage histories and edit-before text are removed. Original private files are untouched. Projection notices and original hashes are in `docs/publication-selection.json` and `docs/agent-transcripts/PUBLICATION.md`. The two 0/5 result receipts remain readable as scores; this is not a fabricated conversation export.

Excluded: credentials and `.env` (empty-key `.env.example` retained), confidential assignment PDF, full transcript/source payloads, raw provider/RPC streams, private logs and raw drafts, exact account balance, downloaded models/dependencies/build caches, database dumps and all Git history. The scanner compares configured secret values without printing them, checks common key patterns/excluded paths/raw evidence fields and baseline runtime hashes. **No findings after cleanup**; this is bounded review, not universal security or permission to redistribute source-derived quotations. Rights review remains required before external publication.

## Actual local UI preflight — separate from fixtures

README bootstrap on the same candidate with existing isolated volumes passed in **7.206s**. Project `lenny_phase11_eval`; web18080/API18000/DB55433, `lenny_rehearsal_phase11`. Explicit Ollama default, cloud keys empty. Existing smoke index **3/303 episodes, 112 passages**, Sean Ellis scope, **hybrid** for both requests. Normal full index remains **303/303, 12,770**. No inference/model download, ingestion or ranking changes outside the two authorized local chat requests.

| Exact UI prompt | Result | Elapsed | Citation/support review |
| --- | --- | --- | --- |
| How did Sean Ellis change onboarding at Lookout? | Completed, direct supported answer | **7.365s** UI / 7.234s server | S1 → `53054eb0-beee-5be4-b2f1-99ca9b2eac2d`; exact quote describes antivirus-first setup and protected confirmation. No measured engagement/conversion claim. |
| What did they report for the next cohort in the must-have survey? | Completed transport, **FAIL semantic completeness** | **4.436s** UI / 4.333s server | Same S1 passage; quote correctly describes initial 7%, but omits requested next-cohort 40% very-disappointed result. Stored passage contains 40%; none of 12 candidate spans does. |

Both operations really used **Pi → Ollama, qwen3:0.6b**, controlled `search_transcripts`, no cloud fallback. The follow-up retained the first user message as context and ran fresh retrieval. Pi session IDs differ; processes reaped/bridges closed. Each citation opened the actual stored passage; source heading focus and citation focus return passed. Context isolation/traceability is not a semantic-answer pass. Readable IDs, timings and review are in [local evidence](agent-transcripts/phase-12/local-live-review.json); full raw replies, source text and protocol events remain in private `.cache/phase12/local/`.

Smallest evidenced next change: fix the general sentence-packing coverage boundary in `backend/app/conversation.py::sentence_items`, which currently keeps two lexically ranked spans per passage, before changing retrieval ranking. Test the saved failing passage/query to preserve the requested outcome sentence under existing budgets, then the same live pair with the full index. This does not establish a sufficient fix for every multi-part scenario. Keep citation/exact-span checks; avoid scenario-specific rules. **No product fix or retry in this frozen preparation.**

## Reviewed essay and timed screen rehearsal

Imported only the historical reviewed **1,208-word essay and its two unchanged exports** into a clearly labelled fixture session in the isolated candidate database. Six source snapshots matched the candidate's exact chunk text/hash before insertion. No normal rows copied/updated wholesale and zero model calls for this fixture. Import refuses an existing fixture and asserts the isolated database name.

The label says **reviewed fixture, nine manual edits, not fresh generation**. The recorded nine edits are six application-paragraph rewrites and three evidence-span edits (sections 2, 4 and 6): remove dangling/truncated claims, use the benefit-question sequence and remove the unfinished LogMeIn 95% clause. Formatting performs no inference. Markdown SHA-256 `622acbd2368356f8cd4ea5103383fc428539aa4b8093f78194bc780598b7693f`; HTML `91ea1f66278d0d25638eb51074c1960340a57ceaf9229028d6f57397ceb9c022` match the earlier reviewed artifacts.

**Timed screen walkthrough: 145.602s (2m 26s)** with silent narration slots, homepage → provider disclosure → freshly generated saved question/follow-up → source inspection → reviewed essay → Markdown/HTML. This timed navigation reopens the preceding live UI outputs; it is **not a second inference run, camera recording or audio performance**. Both formats show six headings, sandboxed previews and all six artifact citations. Desktop1440/phone390 containment, source focus/return, reload and no page/console errors passed. [Rehearsal receipt](agent-transcripts/phase-12/demo-rehearsal.json), [script](demo-script.md).

After an idle isolated API/web restart, all four local messages/two citation snapshots and the two reviewed artifacts reopened unchanged via API; browser opened both formats and showed **Ollama/local, Chat qwen3:0.6b**, matching actual run provider/model. No new inference. [Restart receipt](agent-transcripts/phase-12/restart-reopen.json).

The candidate still has no interactive provider picker. The user explicitly approved the README configuration flow and UI disclosure; no new candidate or feature was introduced.

## Separate cloud verification — BLOCKED, zero inference

Read-only official OpenRouter `GET /api/v1/key` and `GET /api/v1/credits` returned HTTP200. The key limit is exhausted and account balance non-positive: **usable credits unavailable**. Key, authorization headers, full payloads and exact balance are private; [public receipt](agent-transcripts/phase-12/credit-check.json) contains only availability/status booleans. [Official key documentation](https://openrouter.ai/docs/api/api-reference/api-keys/get-current-api-key), [credits documentation](https://openrouter.ai/docs/api/api-reference/credits/get-remaining-credits).

**No cloud question or follow-up was attempted. Current-candidate cloud pair remains pending.** Historical Pi/OpenRouter `google/gemini-2.5-flash-lite` cited smoke6.513s is retained as historical evidence, not substituted for this check. No claim about a current successful cloud interaction or safe live follow-up can be made. The known single historical question is not yet verified safe to demo on this candidate.

Smallest unblock is usable credit/key allowance, then README server-side `DEFAULT_PROVIDER=openrouter` configuration and isolated API recreation. Open a fresh UI session, inspect OpenRouter/Gemini disclosure, run the two frozen public prompts in [demo script](demo-script.md), inspect actual run provider/model and each passage, and record latency/support. Preserve a failed follow-up and restrict a successful cloud-demo claim to the interaction that actually passed. Restore Ollama for the local segment. No code/provider change justified by a billing limit.

## Historical quality remains failed

- **Original frozen scenarios 0/5; bounded rerun 0/5; proposed target 4/5.** Both original files, private raw essay and retrieval-timeout trace retain their Phase 11 hashes. No new frozen batch or metric retuning.
- Full-index Recall@8: tuning16 **56.25%** / previously observed held-out8 **81.25%**, proposed85%. Hold-out is already observed. Three-episode demo is not a comparable retrieval benchmark.
- Phase 11 fresh survey answer6.837s was a supported **feature-level adaptation in the Nubank discussion**, only partially relevant to the general product-level wording question. Follow-up5.033s was supported Lookout onboarding. Do not call the pair a complete-answer acceptance pass.
- Phase 11 raw essay **1,157 words**,46.650s,zero manual edits,not accepted: deterministic length/IDs pass, full claim/readability review fails (unfinished95% predicate/open quote/repetition/unsupported retention inference). Bounded Phase 10 raw **1,216 words**,53.522s also fails. Reviewed1,208-word/nine-edit essay is a separate assisted result.

Useful grounded answers/follow-ups/evidence-gap handling and a useful grounded approximately1,250-word essay are **explicit assignment requirements**. The 4/5,85% and1,125–1,375 thresholds are **our proposed acceptance targets**, not company-set numbers. Failing a proposed threshold alone is not a new requirement; these traces also demonstrate concrete failures of required behavior. Public source, real coding transcripts and camera-enabled video are explicit deliverables still incomplete externally. [Eight-deliverable and Section5 checklist](submission-checklist.md) maps each gap and smallest next verification.

## Checks, failures and preservation

[Exact commands, UTC, cwd, exits and durations](agent-transcripts/phase-12/command-ledger.md); metadata JSONL accompanies it. Captured stdout and diagnostics are separate and private.

- Candidate frontend typecheck **PASS1.670s**, production build **PASS3.030s**; 2/2 source-span tests and10/10 Node policies pass,0 failures/skips. These are deterministic tests, not cloud inference.
- Sanitized reviewed-fixture actual Chrome157 regression **16/16 named checks**,11.970s,zero model calls/DB writes. Includes hostile fixture resource containment, review gate, documents, retry/session/draft/focus/mobile behavior. API interception is explicitly fixture evidence; it does not prove live model quality.
- Source/export audit **41/41 runtime hashes**, configured-value and common-pattern checks, no raw historical payload fields/path findings after cleanup. Initial audit failure from seven Python cache files was preserved; removed only those generated export caches, no source changes.
- First browser helper failed on an overly exact scope-label locator **before any inference**. Corrected the helper, then ran the single real pair. A diagnostic GET used the wrong run route; actual completed-run evidence was recovered from the captured NDJSON events without another inference.
- First read-only normal preservation command missed `PYTHONPATH=/app` and exited before reading data. Corrected command passed in12.114s. All normal **73 sessions,181 messages,14 essays,17 artifacts**, all source/run associations and **303/12,770** full chunk/vector rows match prior hashes; no product data modified.
- Baseline **120/120** backend contracts remain Phase 11 evidence, not re-counted as a new Phase 12 execution. No backend runtime/test change in this phase justified another database suite or failure injection.
- Candidate Git remains clean at f89807d; root index empty. Root product/UI/experiment files unchanged by this phase. No commits/pushes, cloud inference, downloads or destructive operations.

Prepared [interview notes](interview-notes.md), eight-deliverable checklist and demo script. Before publication: required answer/abstention/raw-essay quality, current cloud pair after credit restoration, complete sanitized coding export, source rights and exact deadline/form/access review. Camera recording/upload and all publication/submission actions remain separate authorized steps. **Stop here for review.**

Local review archive: `.cache/phase12/lenny-publication-f89807d.tar.gz`; SHA-256 and full tree manifest are in `docs/agent-transcripts/phase-12/package-receipt.json` and exported `docs/publication-files.json`. Neither archive nor tree was uploaded.
