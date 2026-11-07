# Workspace design: Phase 8

Open directly into the research workspace. Warm neutral surfaces, charcoal text, restrained sage accents and a serif reading hierarchy keep long answers and documents readable. System fonts and local CSS need no external asset requests. Quiet status text replaces animation; reduced-motion preferences are respected.

## Information architecture

Sessions sit on the left; research, saved drafts and the composer occupy the middle; documents and source inspection share the contextual right area. The header shows the actual provider, separate chat/essay models and partial corpus count. The interview picker lists actual indexed interviews. Examples help start a focused question; evidence-led essay is a distinct composer action with an audience field.

Source inspection shows the immutable original passage, citation label, guest and observed timestamp/link where present. A valid ID means traceability, not factual support. Documents are labelled as fixture or live, with manual review/edit provenance. They render inside the existing scriptless sandbox. No raw message HTML or executable document controls were added.

## Interaction states

Questions save before generation. Searching/drafting progress uses status announcements, with a cancel control. Timeout, missing-model and other errors retain input; retries reuse the saved question identity. Saved-question recovery restores original scope. Each session keeps its unsent composer state in memory; a fresh session clears the old interview scope. That temporary unsent text is not promised durable across page reloads.

Saved essay drafts reopen with recoverable failure status. Review exposes exact source selection and advice separately. The server accepts only immutable original source spans; Unicode offsets are converted correctly. Unsaved edits disable conflicting navigation/new requests until saved or explicitly discarded. Five explicit quality confirmations and a review note gate acceptance. Counts and citation validity do not replace that review. Saving Markdown/HTML announces success only after the server responds; failed saves remain retryable.

## Responsive and keyboard behavior

Desktop uses independently scrolling reading panels. Below 1000px, labelled Sessions, Research, Documents and Sources tabs display one panel at a time. Tabs support arrow keys and Home/End with a roving tab stop; hidden panels cannot receive keyboard focus. Opening a source moves focus to its heading; closing it restores the invoking citation and originating panel. Late source responses cannot cross sessions. Errors remain visible outside a hidden research pane.

Native labels, a skip link, visible focus borders, readable line length and restrained live regions support keyboard navigation. Long document content scrolls inside its isolated preview; mobile documents have full reading width. Representative rendered contrast samples measured 12.4:1 body text, 8.72:1 primary button and 4.94:1 section label. These are samples, not a full accessibility certification.

## Verified boundaries

Actual isolated Chrome157 checks cover 1512px desktop, 390px mobile, 820px and1024px containment. Sixteen deterministic cases test navigation, review, save/reopen and failures without model calls or database writes. Separate real UI evidence covers local chat, follow-up, reviewed essay, both documents and reload/reopen. Final screenshots were visually inspected privately. No assistive-technology study, independent user study or other browser engine was tested. The in-app connector remains blocked; host Chrome automation is the actual browser used. See [Phase8 report](phase-08-report.md).
