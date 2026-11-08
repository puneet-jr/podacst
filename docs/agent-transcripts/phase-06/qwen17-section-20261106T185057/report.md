# Phase 6 one-section comparison: failed grounding

7 November 2026, India time (raw UTC logs are 6 November). **Section failed; full essay not run. Stop before Phase 7.**

Command: `python3 scripts/capture_phase6.py .venv-phase2/bin/python scripts/compare_qwen17_section.py`. Exit 2 from the section checks, not a transport failure. One actual Pi/local Ollama request, no repair/retry. Child command: `python3 scripts/docker.py compose exec -T -e GENERATION_MODEL=qwen3:1.7b api python -m backend.markdown_section_check`.

Installed local model digest `8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7`; Ollama reports Q4_K_M and parameter_size 2.0B for this tag. Same template/default parameter strings as 0.6B. Model change was scoped to the exec child; chat/API stayed qwen3:0.6b, cloud disabled. No dependency, config or production code change.

The runner verified identical actual user prompt, saved outline, S2/S3 source IDs and body hashes, runtime code matching4323911, provider prompt9359 bytes and850-output-token budget. Same4096 context, temperature0, thinking off, grammar off, no active tools,90-second deadline. Retrieval mode: saved hybrid snapshot, no re-search/reranking. One fresh Pi session, initial history0, normal stop, process reaped and bridge closed; input2013/output333 tokens. Safe protocol metadata and diagnostics are separate in comparison-verification.json; private full RPC stdout/stderr remain in the trace volume.

| Measure | 0.6B baseline | 1.7B |
| --- | --- | --- |
| Section lifecycle time |16.323s|29.050s|
| Words (target210) |362 (+152)|289 (+79)|
| Generated citation IDs |None|None|
| Literal Purpose/Target labels |Both|Neither|
| Other instruction leakage |Present|Saved purpose copied after Application|
| Grounding gate |Failed|Failed|

1.7B was73 words shorter and12.727 seconds slower in these individual samples. No warmup was added; residency and host load were uncontrolled, so this is not a model performance benchmark. The210 target remains guidance, not a newly invented hard tolerance. The decisive failures are absent citations and semantic problems.

Every factual paragraph lacks[S2]/[S3]. Both supplied labels resolve through the NEW probe's owned API and match saved hashes, but none is used. S2 is53054eb0-beee-5be4-b2f1-99ca9b2eac2d; S3 isf5f40dd8-e8fb-5e74-9834-e45e31331549. Full source bodies stay private. The15-entry direct claim review in review.json covers all paragraphs, including supported core facts and unsupported inferences.

The clearest factual distortion: the draft says7% were disappointed without the antivirus feature. S2 says7% would be very disappointed without the PRODUCT, and most of that group valued antivirus. S2 supports Lookout's mobile-security identity, antivirus positioning, antivirus-first onboarding and protection confirmation, all uncited here. S3 supports investigating must-have users and their benefits, not generic guaranteed outcomes.

Unlike0.6B, this draft does not explicitly claim improved engagement or measured conversion rates. It still says repositioning ensured antivirus-valuing users were more likely to convert. S2 describes a conversion-filter mechanism, not measured conversion improvement; it reports a later must-have survey cohort. Neither excerpt establishes measured engagement/conversion gains. Claims about significant behavior effects from positioning alone, a seamless experience and guaranteed clearer onboarding also overstate or generalize the evidence. The opening Application label repeats a drafting instruction; it does not qualify all later historical claims.

Raw output is preserved unchanged as [section.md](section.md), with [result.json](result.json), [review.json](review.json), [source-resolution.json](source-resolution.json), [inputs.json](inputs.json) and [comparison-verification.json](comparison-verification.json). Original0.6B files match all preservation hashes. No full essay, original1125–1375-word rubric pass, verified essay fix or Phase7. Prior82 backend/five Node tests remain separate evidence and were not rerun to mask this live failure.
