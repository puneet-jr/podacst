# Phase9 OpenRouter amendment

**Cloud validation: PASS for one reviewed public cited answer.** The saved HTTP400 was diagnosed before changing providers. A minimal follow-up JSON-mode compatibility fix and exactly one same-provider/model rerun passed in **6.513 seconds**. CitationS1 resolves to retrieved evidence and supports the answer. The original upstream error body was not retained and cannot be quoted. [Diagnosis and result](phase-09-openrouter-diagnosis.md). No commit/push or Prompt10.


## Actual provider and correction

The original Phase9 code used **direct Anthropic**, not OpenRouter. Its native initialization and mocked payload tests are correctly retained as Anthropic evidence. OpenRouter is now added as a separate explicit Pi provider, not relabelled Anthropic output.

Verified for the single corrective smoke, OpenRouter model and provider: `DEFAULT_PROVIDER=openrouter`, `OPENROUTER_MODEL=google/gemini-2.5-flash-lite`, Pi provider `openrouter`, API `openai-completions`, endpoint `https://openrouter.ai/api/v1`. Existing direct Anthropic support remains optional; local default Ollama0.6B chat/1.7B essay is unchanged. The key stays server-side and is omitted from local Pi children. Each cloud mode uses its own key; an Anthropic key cannot satisfy an OpenRouter configuration.

The live smoke is explicitly selected in a one-off service, leaving the normal app local. Pi forces one narrow read-only retrieval invocation before selecting a stored sentence ID. FastAPI validates the selected ID and emits exact source-backed text/citations. Both cloud turns are bounded to128 output tokens; input byte/context budgets and timeout/process cleanup remain. OpenRouter requests pin a single model with no fallback model list, `allow_fallbacks=false`, `require_parameters=true` and `data_collection=deny`. OpenAI-only grammar/reasoning fields and follow-up JSON response mode are omitted; the prompt requests a JSON object and the server strictly validates its evidence ID. Advice-only stages are wired separately with no tools or citation emission.

[Setup and variable table](handoff.md) · [OpenRouter quickstart](https://openrouter.ai/docs/quickstart) · [routing controls](https://openrouter.ai/docs/guides/routing/provider-selection) · [model documentation](https://openrouter.ai/google/gemini-2.5-flash-lite/api) · [Pi provider documentation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/providers.md).

## Verification boundaries

Focused settings/secret/endpoint/payload tests and frontend TypeScript/build are separate from live inference. The missing-key UI fixture uses zero model calls and DB writes. Native Pi initialization with a synthetic key sends no provider requests and cannot pass cloud validation. The actual live runner refuses missing credentials, executes one FastAPI/Pi/OpenRouter answer with real PostgreSQL and local retrieval, records provider/model/usage/tool trace/latency, then opens every citation. Raw output and source snapshots stay in the private trace volume; only IDs/counts/hashes and explicit review are publishable. Technical completion alone leaves validation pending manual source review.

Current state is recorded in [openrouter-validation.json](agent-transcripts/phase-09/openrouter-validation.json). Success requires an actual cited answer whose attached passage supports the claim; no cloud success is claimed before that check. OpenRouter and the upstream model provider may receive selected evidence/context/instructions and may bill the account. This is not a local-model quality improvement or autonomous essay verification. The earlier1,208-word essay remains manually reviewed; autonomous quality remains unverified. The remote snapshot still lacks deliberately unpublished earlier prerequisites.


## Actual verification results

- Full isolated PostgreSQL suite: **115 tests passed in18.572s**; nine Node policy tests and frontend TypeScript/Vite build pass.
- Installed Pi1.5.0 resolves `openrouter` / `google/gemini-2.5-flash-lite` at the expected endpoint with zero history using a synthetic key: initialization only, zero provider requests.
- Public OpenRouter catalog lists tools, tool_choice, JSON response formatting, max_tokens and temperature for the configured model. Catalog metadata is not account-level inference proof.
- Four isolated Chrome fixture checks pass: provider/model display, outgoing-data disclosure, unavailable key state and retained input; zero model calls/DB writes. Main app remains local.
- Public-scope verification fetched the pinned Sean Ellis transcript from GitHub, matched SHA256 `6af2a6e031826805e855ec262b1f228e3773b5b99265a1d01870f0d4e6e9ceda`, checked actual retrieved spans, and the in-container preflight verified all52 active scoped chunks plus guest/title against the public source. The smoke cannot use a different source/model or prior session history.
- Earlier, before the user configured the key, the live runner exited3 at credential preflight: **OPENROUTER_API_KEY is absent in the server environment**. Zero inference requests, no new session/message writes, no cited cloud answer. That earlier attempt made no cloud request. The subsequent actual live attempt is recorded below; it reached retrieval but did not produce a successful cited answer.

[Validation state](agent-transcripts/phase-09/openrouter-validation.json) · [actual stopped attempt](agent-transcripts/phase-09/openrouter-live-attempt.json) · [public preflight](agent-transcripts/phase-09/openrouter-public-preflight.json) · [public provenance](agent-transcripts/phase-09/openrouter-public-scope.json) · [Pi initialization](agent-transcripts/phase-09/pi-openrouter-initialization.json) · [UI fixture](agent-transcripts/phase-09/browser-openrouter-fixture.json).

The initial conditional live command was rejected by automatic approval review over possible sensitive evidence/context transfer. No process or provider request ran for that rejected command. After narrowing and proving the public-only scope, the reviewed command was approved; it then stopped on the missing key. See the explicitly labelled approval-result summary. No rejection was bypassed through another execution path. The next actual live attempt still requires the user's out-of-band key configuration and cannot pass until the cited output/source review succeeds.

A Starlette TestClient deprecation warning recommends httpx2; no speculative dependency upgrade was performed. Existing nonfatal shutdown ResourceWarnings remain recorded separately. No source output was fabricated or replaced with local/Anthropic output.


## One live smoke after key configuration: failed, preserved

On7 November2026 at08:56UTC, ran the documented command exactly once:

```sh
python3 scripts/capture_phase9.py python3 scripts/docker.py compose run --rm --no-deps -e DEFAULT_PROVIDER=openrouter api python -m backend.openrouter_live_check
```

Pi recorded and validated provider **openrouter**, model **google/gemini-2.5-flash-lite** and official endpoint `https://openrouter.ai/api/v1`. This was real inference, not a fixture, Anthropic substitution or local-model fallback. The first cloud-driven turn invoked `search_transcripts`; actual projected protocol records contain two turns and exactly one tool start/end. Local hybrid retrieval returned five public Sean Ellis passages. Fresh session had no prior history; all52 scoped chunks matched the pinned public source before execution.

The following answer-generation/selection stage failed with **provider_http_400**. FastAPI returned HTTP200 for the NDJSON stream, whose terminal event was **failed**; HTTP200 alone is not model success. End-to-end request duration **4.940503335s**. Session `edb879d1-5a0d-468e-b6ef-9c960af14c4d`; run `a1d3ea92-0d59-4fb4-a0c8-1627f27dbbbb`; request reference `fb06a3f14033447787fbb731fb709c9b`. Pi was reaped and the local tool bridge closed. No final answer/citations or usage accounting were produced. No citation-support pass can be claimed.

The safe code is extracted from Pi's provider error; detailed upstream error text was not retained under the default privacy policy, so the exact HTTP400 cause is **unverified**. Do not label it a missing key, assume a specific unsupported parameter, or call this a successful cloud answer. No corrective retry or model/provider change was performed because the user authorized one smoke test.

The raw stream and projected protocol remain private in the existing trace volume; sanitized result and event-count evidence are linked below. The configured key was checked against captured command logs, publishable files and this run's private artifacts without printing it; scan outcomes are recorded separately. Default Ollama configuration remains unchanged. The earlier1,208-word essay remains manually reviewed; autonomous quality remains unverified.

[Actual result](agent-transcripts/phase-09/openrouter-live-attempt.json) · [validation state](agent-transcripts/phase-09/openrouter-validation.json) · [protocol verification](agent-transcripts/phase-09/openrouter-live-protocol-check.json).


## Current corrective outcome

The prior failed attempt above remains historical evidence. The user authorized diagnosis and one corrective rerun. It passed through the same OpenRouter/Google model in6.512845794s after removing only the follow-up response_format flag; exact source and semantic citation review passed. Current state is passed for this one smoke, not a general quality claim. See [diagnosis](phase-09-openrouter-diagnosis.md) and [corrected actual result](agent-transcripts/phase-09/openrouter-live-corrected.json).
