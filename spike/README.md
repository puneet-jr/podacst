# Phase 1 disposable local integration spike

This proves a narrow FastAPI/Python -> Pi RPC -> local Ollama -> fixture tool -> response path. It is not the product backend, a RAG evaluation or proof of essay quality. See [phase report](../docs/phase-01-report.md) for actual gate, failures, timing and limitations.

Requirements observed here: macOS arm64 M2 / 8 GiB, Python 3.13.5, Node 24.9.0 / npm 11.6.0, Ollama 0.30.11. Pi was installed project-locally from the package identified by pi.dev and checked against official source metadata. Installed CLI reports 1.5.0.

From the project root, reproduce the tested dependencies:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r spike/requirements.lock
npm ci --prefix spike --ignore-scripts --no-audit --no-fund
```

Inspect memory/disk and installed models before any pull. The existing nomic-embed-text model was embedding-only; this spike downloaded qwen3:0.6b (522,653,767 bytes). Its observed digest is `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435`, Q4_K_M. A tag may change; compare the local digest to this evidence before reproducing. The reported loaded footprint was about 1.02 GB, with 4,096 context. No larger model was downloaded.

The authorized Ollama server was started with:

```sh
OLLAMA_NO_CLOUD=1 OLLAMA_HOST=127.0.0.1:11434 OLLAMA_CONTEXT_LENGTH=4096 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1 ollama serve
```

Check for an existing server first; do not launch a duplicate or kill unrelated processes. If needed after checking suitability, `ollama pull qwen3:0.6b` is a first-run network download, not cloud inference. The model must already be local for the smoke checks. Keep cloud disabled.

Offline/mock checks (no model needed):

```sh
.venv/bin/python -m spike.capture .venv/bin/python -m unittest spike.test_adapter -v
.venv/bin/python -m spike.capture node --test spike/test_retrieval.ts
```

Real local smoke (requires loopback access and Ollama):

```sh
.venv/bin/python -m spike.capture .venv/bin/python -m spike.live
```

This runs five fresh sessions, inspects empty history, compares distinct synthetic markers/source values, exercises the actual TCP FastAPI path, in-flight rejection, abort, cancellation, generation deadline, startup timeout, disconnect and recovery. Every run saves a new evidence directory. The driver starts/reaps its own temporary API server; it never resets data. Run only one batch at a time.

Optional manual local endpoint:

```sh
.venv/bin/python -m uvicorn spike.api:app --host 127.0.0.1 --port 8001
```

POST /spike/run accepts a JSON prompt naming activation or retention; GET /spike/status exposes local process cleanup evidence. Example prompt: `For retention, what is the review window and evidence code? Use search_fixture and cite the source_id.` No shell/web/filesystem tool is exposed. The tool's only file read is its own fixed fixture. Source labels in the response come from tool results; model_text preserves what the model actually wrote.

The workflow deliberately guides one fixture query through Pi rather than claiming reliable autonomous tool selection. Earlier malformed/omitted calls and hallucinated values were rejected and retained in evidence. A small fixture success does not justify selecting this tiny model for the final app. See architecture/risks for bounds and remaining work. Stop after Phase 1; do not start Phase 2 as part of this spike.
