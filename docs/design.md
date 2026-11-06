# UI design notes: Phase 5 conversation

Implemented: a restrained three-part workspace with saved sessions on the left, the selected session/messages and composer in the center, and dependency/provider/corpus status on the right. Warm neutral backgrounds, dark green accents and system fonts keep attention on research. No external images/fonts are needed.

The current action is **Ask**, using real local hybrid retrieval and exact source excerpts. Writing/artifacts remain deferred. The original Phase2 foundation saved notes only; that behavior has been extended. Saved state follows a successful server transaction; failed saves retain the prompt and client message UUID for retry. Session loading/saving disables conflicting controls. The selected model and disabled automatic cloud fallback are visible. An empty corpus is displayed rather than hidden behind a ready badge.

Controls have explicit labels, button names, native keyboard behavior, visible focus styles and an alert region for errors. Messages render as escaped text; there is no HTML artifact renderer yet. CSS collapses the status panel below 1100 px and stacks the workspace below 650 px. These rules exist, but responsive appearance and keyboard/accessibility behavior have **not been browser-verified**.

The Browser runtime failed before connection with an unavailable node:process import; no screenshot, visual inspection or manual UI pass is claimed. HTTP serving/proxy and TypeScript/build checks passed. See [test-plan.md](test-plan.md) and [phase-02 report](phase-02-report.md). Source inspection and streamed progress/validated answers are now implemented; their actual browser interaction remains unverified. Essays/artifact previews remain deferred.


## Phase 3 status increment

The status panel now shows actual active episodes/passages, discovered source count, run loaded/skipped/failed/pending counts and partial status, polling the typed status endpoint every five seconds. Ingestion output does not enable answers or imply product readiness. Actual endpoint/proxy responses and TypeScript/build passed; visual/keyboard verification remains blocked by the existing browser runtime failure.


## Phase 5 states and trust

The composer saves before inference and shows starting/retrieving/selecting progress, cancel, retained failed question and bounded retry. Completed replies display exact quoted evidence with server-issued source buttons; source IDs inside user/model text alone are never made links. The inspector shows original passage, selected quotes, guest/title, hash/version/path, observed markers, missing-time honesty, sponsorship/metadata warnings and approved HTTPS transcript/video links. It renders escaped text, not source HTML. Session switching invalidates pending source lookups so stale responses cannot populate a new session. API ownership remains authoritative.

The UI exposes partial9/303 coverage, local model/fallback status and extractive output limits. Available dependency badges do not mean verified answer quality. Responsive CSS/labels/live regions exist and builds pass, but no browser navigation, screenshot, accessibility or manual interaction pass occurred. The source inspector is API-verified and visually unverified. Follow the Phase5 browser plan when runtime access returns.
