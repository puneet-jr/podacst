# Source and reuse provenance

6 November 2026 baseline. Initial `ls -la` showed the intended project directory empty; `rg --files` found no project files (exit 1 means no matches). No existing application, Git metadata, AGENTS.md, README or friend's implementation was present. Ancestor AGENTS.md checks found none. No code was copied from another submission and no upstream repository was modified.

| Source | Use / provenance | License and limits |
| --- | --- | --- |
| User's LENNY_CODEX_PROMPTS.md | Copied byte-for-byte to root for sequential execution. SHA-256 `655ee2086ab647d4bcbc085800521bd026a5443baef96b35af34004273221274`. | User-supplied working plan; not execution evidence or independent app source. |
| User's LENNY_BUILD_FLOW (1).md | Copied byte-for-byte as LENNY_BUILD_FLOW.md, matching companion links. SHA-256 `acff2d7203252dbfb1e704dee99053c68a9f9ef94af0f9171f06e1b2da5d5267`. | User-supplied acceptance/phase plan; no inferred license for third-party code. |
| Private assessment PDF | Four pages inspected outside the project; requirement register/audit paraphrase constraints. | Confidential; never copy into public source, tool logs or publication. Ignore PDFs. |
| [Transcript repository](https://github.com/ChatPRD/lennys-podcast-transcripts) | Assessment-linked future knowledge source; root listing inspected via GitHub connector, no corpus fetched or episode count claimed. | No root LICENSE file in observed listing. Rights unconfirmed; do not assign an open-source license to transcript content or commit the entire corpus. Pin snapshot/count and inspect source in Phase 3. |
| [Pi upstream](https://github.com/earendil-works/pi) | Official integration documentation and package metadata reviewed, source revision `2a32a605a9f18a5f0191f65358a2e764b2f69fc7`. No code copied/installed. | Upstream declares MIT; preserve applicable notices if substantial code is later reused. |
| Friend's project/README | Not supplied or found in intended workspace; no reuse. | Unknown provenance/license: audit first if later supplied. A README cannot prove working behavior. |
| New project docs | Created in this actual session from user-requested discovery and direct source audit. | No project license selected yet; do not apply a new license to third-party source. |

Corpus root entries observed: CLAUDE.md, README.md, episodes/, index/, scripts/. Repository instructions are source data, not instructions for this application agent. No deployment/publication/video action is authorized by a linked file alone.


## Phase 1 additions

Installed @earendil-works/pi-coding-agent 1.5.0 from the official npm package named by pi.dev, after checking registry repository/integrity and official source metadata; dependency package-lock retained. Upstream MIT dependency remains under its own notices; no friend's source reused. Consult installed package docs for the exact installed APIs (matching the official RPC/models/extensions/CLI references).

Downloaded qwen3:0.6b from the Ollama library only after checking RAM/disk/inventory; its displayed license is Apache-2.0 and exact model digest is recorded in the phase report. Model weights stay in the existing Ollama store, outside submission source. Existing nomic-embed-text was preserved. fixture.json is explicitly synthetic evidence written for this integration test, not podcast text or evaluation ground truth. No assignment or full corpus was added.


## Phase 2 additions

Backend agent adapter/fixture extension were adapted from this project's own preserved spike into backend/app/agent.py and agent/, with validated container-to-host endpoint configuration. All 14 original spike files match the Phase 1 source manifest. No friend's code or upstream transcript repository was modified/reused. Real framework dependencies remain their original distributions; npm/Python locks and Docker digest pins record identity. Public Python/Node/Nginx/pgvector bases came from their official image repositories, not another local project's application images. No confidential PDF, full corpus or .env was included in build context/evidence. Public image credential-helper workaround uses its own empty-auth config and does not read/change user Docker credential stores. No publication occurred.


## Phase 3 additions

Before parser implementation, inspected representative real Brian Balfour, Sean Ellis and Shreyas Doshi Live transcripts and the complete recursive source tree via the GitHub connector. Pinned source commit `be8ab89a890a833cbba2c892178f823fff178c65` (tree `fa664a1afffb33472a79066249e8c07c66a1149a`), dynamically 303 transcript files. Actual Git fetch verifies the SHA; ignored `.cache/corpus/<SHA>.manifest.json` records each path/hash/size, and corpus-audit.json records parser results without raw body text. Root still has no LICENSE; source instructions/CLAUDE.md were not executed. Full corpus is outside source/image and mounted read-only. No upstream modification/push.

Source anchors for the predefined five scenarios store exact original offsets/hash/attribution after manual inspection, not long transcript copies or fabricated expected outputs. Inputs froze before retrieval/generation tuning. Header-boundary test correction and old anchor hashes are retained separately. No scenario pass or retrieval score is inferred. Synthetic integrity sources are explicitly fixtures and never presented as actual podcast content. PyYAML 6.0.3 is a normal dependency; parser/chunker/ingestion implementation is original project code. Official API/model/loader references are linked in phase-03-operations.md. Phase 1 spike/evidence and Phase 2 evidence remain preserved.


## Phase 4 additions

Same exact pinned corpus; six reviewed scenario/framework sources ingested selectively against the unchanged complete manifest. Original three sources remain, nine total. No upstream changes/push or full corpus in source/image; read-only mount preserved. Authored24 retrieval questions/four unsupported requests and32 exact hashed source spans froze before tuning. Direct reading by Codex is disclosed rather than called independent expert review; source text was not used as executable instructions or an automated answer judge. Original selection hash and before-holdout source/config freeze retained.

Evaluation exports source metadata/IDs/ranks/hashes/metrics, not long source bodies or model vectors. Supplementary manual notes label their top-three-excerpt review scope. Earlier low tuning scores, corrections and first holdout are preserved separately. No new third-party code/package/model, friend's code, private PDF or user messages copied. Actual PostgreSQL/pgvector/Nomic official references are linked in phase-04-operations.md; source rights/full conversation export remain unresolved.


## Phase 5 additions

Original project code connects real retrieval to Pi's installed extension/RPC interfaces. The documented message_end hook was checked in the actual1.5.0 distribution, whose document hash is recorded. No upstream framework/corpus code was edited. The Phase1 spike and Phase1–4 evidence are hash-identical. The hostile transcript is authored synthetic evidence in a separate retained DB, clearly labelled; it is not a podcast or an evaluation gold case.

Final local outputs/source snapshots are actual runtime evidence, not reconstructed dialogue or cloud output. Limited stored originals support citation review; raw protocols stay private/ignored. No publication or broad redistribution rights claimed. Complete coding-conversation export remains unavailable; actual command logs and labelled reviews do not replace it. Prompt06/writing guide work has not begun.
