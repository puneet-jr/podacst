# Reviewed retrieval baseline

This is a small development evaluation, not a company benchmark or a user study. Questions and exact source-span judgments in `retrieval-cases.json` froze before any retrieval scores: 24 answerable cases (16 tuning, eight held out), plus four separate unsupported requests. Direct source reading was performed by Codex; labels are not independent expert judgments. Nine source episodes/373 chunks were indexed from the pinned 303-file snapshot. Selection was intentional for scenario/framework coverage, not random or representative; remaining sources can introduce distractors and change results.

All gold evidence is tied to original path, byte hash, exact character span, speaker/observed marker and span hash. The evaluator resolves each frozen span to actual active chunk IDs containing the entire span. This happens without consulting retrieval ranks; no match is a hard evaluation error. Character spans remain authoritative when overlapping chunks offer alternatives. Named guest matches alone receive no credit. Source text never becomes agent instructions or an answer judge.

## Reproduce

Keep Mac Ollama running with the existing pinned Nomic model and use the documented isolated Compose DB. Fetch/validate the exact source snapshot and ingest the six additional paths listed in the Phase 4 report before evaluation. Existing three smoke episodes remain indexed. Do not manufacture labels from retrieved results.

```sh
python3 scripts/docker.py compose exec -T api python -m backend.contract_check
.venv-phase2/bin/python -m unittest discover -s eval -p test_metrics.py -v
python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval \
  --split tuning --config eval/retrieval-local-v3.json --output /app/evidence/tuning-new-attempt
# Only after a candidate/configuration has been fixed:
python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval \
  --split held_out --config eval/retrieval-local-v3.json --output /app/evidence/held-out-new-attempt
python3 scripts/docker.py compose exec -T api python -m backend.evaluate_retrieval \
  --split unsupported --config eval/retrieval-local-v3.json --output /app/evidence/unsupported-new-attempt
```

Output directories must be new; attempts never overwrite one another. Copy `/app/evidence` to the host before recreating a container. The runner stores metadata/hashes/ranks/metrics, not raw source bodies or vectors. It checks returned exact text against actual versioned PostgreSQL originals on every result. No cloud inference or LLM grading occurs. A measured local-model warmup is recorded separately; query summaries use warm operations with mode order rotated per question. Latency includes service embedding/SQL/selection, excludes evaluation-only judgment/source verification, HTTP transport, downloads and generation. Sparse mode has no embedding call; dense/hybrid do.

Original v1 and v2 attempts are retained as separate measured development results. `retrieval-selection.json` freezes the v3 source/config hashes and sparse default before held-out execution. Once observed, held-out cases are no longer unseen; future tuning requires another independent holdout, and any rerun must be labelled a rerun. Follow-up cases use fixed reviewer-supplied query rewrites; no generated context resolver is tested here.

## Metrics and limits

- **Passage Recall@8:** unique returned IDs intersect judged relevant IDs divided by all judged relevant IDs, macro-averaged across questions. Fewer than eight may return because of the token budget/caps; this is recall under the recorded packet constraints. Overlapping alternatives are separately judged relevant IDs, making this stricter than fact/anchor coverage.
- **MRR@8:** reciprocal of the first judged-relevant rank, zero if absent.
- **nDCG@8:** binary judged relevance with log2 rank discounts, normalized against an ideal list of up to eight relevant IDs. Neighbor expansions count in their final packet positions, not as independently scored RRF hits.
- **Anchor recall:** fraction of frozen support spans with at least one containing chunk returned. Cross-episode cases require each distinct support anchor; one speaker alone is insufficient.
- Report per-mode sample size, counts, scope breakdown, median and nearest-rank p95 latency. With only eight held-out cases, a p95 is effectively a maximum, not a stable tail estimate.

Judgments are incomplete: a valid alternative passage that was not frozen receives no metric credit. Thus a strict source-span miss is not automatically a semantic-answer failure. Do not retroactively relabel misses to improve the score. Precision, full answer support, unsupported-answer handling, autonomous routing and essay quality are not established by these metrics. The PRD's proposed 85% retrieval target is distinct from the engineering gate; do not mark it achieved from a successful runner exit or a selected subset.

## Manual support-review rubric

For each reviewed packet, resolve exact source/hash/version; inspect the passage itself and necessary adjacent context. Classify support as full / partial / absent for the specific requested claim, rather than matching a guest name or topic. Check numerical qualifications, historical prediction vs current fact, speaker attribution and contradictions. Cross-episode synthesis needs evidence from each account and must be labelled synthesis. Sponsored promotions cannot establish substantive effectiveness or guarantees; flags can denote mixed passages and are imperfect. Source title/date/video metadata can be wrong (notably the live Shreyas file); preserve original metadata and use path/hash/body, without inventing corrections.

Unsupported requests are separate diagnostics with no Recall@8 denominator. Directly inspect their candidate packets and record why the requested fact is absent. Nearest-neighbor systems can return plausible related text for nonsense/private/future requests. The service returns bounded `review_required` candidates with `support_verified=false`, or `empty_evidence` with a limitation. This defines the evidence contract; it does not prove a generation system will abstain. The Phase 5 agent must review support or acknowledge insufficiency, never turn a rank score into confidence. Manual review notes and remaining defects are linked in the Phase 4 report.
