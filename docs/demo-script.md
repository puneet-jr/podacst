# Camera demo plan — 2 minutes 40 seconds

Candidate `f89807d8db16c20e652590a6470810e5eb60b078`, `http://localhost:18080/` and `/workspace`. This is a script and screen rehearsal, **not a completed camera recording**. Keep camera enabled during the real recording; show readable browser text, never `.env`, terminal environment or request headers. Do not imply the current quality gate passed.

## Preflight and exact local prompts

Use the README isolation environment and `python3 scripts/bootstrap.py`; confirm `/api/health/ready`, `/api/providers`, Ollama selected, `qwen3:0.6b` chat, `qwen3:1.7b` essays, hybrid retrieval. Rehearsal coverage is **3/303 episodes, 112 passages**; the preserved normal index has 303/12,770. Select Sean Ellis explicitly. Fresh session only; no cached answer presented as live.

1. **How did Sean Ellis change onboarding at Lookout?**
2. **What did they report for the next cohort in the must-have survey?**

Actual UI preflight: 7.365s / 4.436s. Both use real Pi → local Ollama and controlled retrieval. First answer directly supports antivirus setup and the protected confirmation. Follow-up **fails completeness**: returns the initial 7% quote rather than the next cohort's 40% “very disappointed.” The citation opens the correct stored passage, which contains the missing result; the model's bounded sentence packet omitted it. Do not silently replace this with a successful prompt or a cloud answer. The first interaction is suitable for a supported local demonstration; the pair is suitable only as a candid limitation walkthrough.

Open **Reviewed essay fixture · 1,208 words · 9 manual edits · not fresh generation**. It was imported offline into the isolated candidate after all six exact source hashes/text mappings matched; it is the historical reviewed output, not a newly generated essay. Markdown and HTML bodies match the previously reviewed hashes.

## Camera narration and screen cues

| Time | Screen/action | Narration |
| --- | --- | --- |
| 0:00–0:18 | Homepage, then Open workspace | “Product teams hear useful podcast advice but struggle to recover the evidence and turn it into a practical next step. This workspace keeps a question, its source passage and a saved playbook together.” |
| 0:18–0:35 | Fresh session, provider/model disclosure, Sean Ellis scope | “This release candidate uses local Ollama with qwen3:0.6b for chat. Pi runs a narrow read-only retrieval tool; PostgreSQL stores sessions and evidence. This isolated rehearsal has three episodes, not the full index.” |
| 0:35–1:05 | Submit first prompt live, open S1, focus original passage | “How did Sean Ellis change onboarding at Lookout? The answer quotes antivirus-first setup and a protected confirmation. Here is the exact stored passage and its source identity. This is support for the onboarding change, not proof of higher engagement or conversion.” |
| 1:05–1:32 | Submit follow-up live, open S1; show final next-cohort sentence | “What did they report for the next cohort? This run misses the requested result. Its quote is real, but it describes the initial seven percent. The original passage says forty percent very disappointed in the next cohort. Retrieval found it; sentence selection lost it. Follow-up quality remains blocked.” |
| 1:32–2:05 | Open reviewed session, Documents, Markdown then HTML | “This saved 1,208-word essay was manually reviewed with nine edits: six application rewrites and three evidence-span edits. It is not an autonomous generation result. Both exports preserve citations. A fresh raw essay met the length band but failed claim and readability review.” |
| 2:05–2:40 | Show source, static artifact preview, final limitations | “The trade-off is local privacy and predictable cost versus limited model capability. Hybrid PostgreSQL retrieval keeps operations simple, but exact quotes alone do not guarantee a useful answer. Both frozen scenario runs scored zero of five against our proposed four-of-five target. The next fix must preserve relevant evidence and pass semantic review before release.” |

Narration slots plus measured inference fit 2–3 minutes at a natural pace; rehearse speech aloud with camera before recording. The automated timed screen pass has silent narration slots and reopens the just-generated answers; it is explicitly **not another live inference recording**. Do not edit the missed follow-up out while claiming this pair passed.

## Nine-edit disclosure

Six application paragraphs were rewritten after source review to remove repetitive/overstated advice and frame actions, observed metrics and hypotheses carefully. Three evidence selections were changed in sections 2, 4 and 6: remove a dangling quotation, use the benefit-question sequence, and remove the unfinished LogMeIn 95% clause. This is the application's recorded edit count, not a count of keystrokes. No model regeneration is implied by those manual edits. Formatting the accepted essay as Markdown/HTML made no new model call.

## Separate OpenRouter walkthrough — currently blocked

Do not splice cloud footage into the local demo. Read-only `/api/v1/key` and `/api/v1/credits` checks succeeded, but usable credits are unavailable; **zero cloud inference requests in Prompt 12**. Historical one-case success is not current-candidate pair verification.

After credits are available: use the README server configuration (`DEFAULT_PROVIDER=openrouter`, `OPENROUTER_MODEL=google/gemini-2.5-flash-lite`, real key only in ignored server `.env`) and recreate only the isolated API. The user approved this configuration flow plus UI disclosure; this candidate has no interactive provider picker. Keep the key out of the frontend, browser, shell arguments and logs. Open a new UI session; verify OpenRouter/cloud and Gemini disclosure, select Sean Ellis, run exactly the two public prompts above, and open each citation. Record actual response-run provider/model, elapsed times, exact passage IDs and support review. Preserve any failed/irrelevant follow-up. If only the question succeeds, demo only that interaction as a cloud success and explicitly disclose the failed pair. Restore Ollama via README configuration and confirm UI/model before any local segment.

No deployment, publication, upload or submission is part of this rehearsal.
