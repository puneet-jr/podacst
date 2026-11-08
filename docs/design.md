# Design and interaction contract

The research task is primary:read a question,inspect its evidence,then make a reusable document. Warm paper,deep plum,restrained gold and serif editorial headings link the homepage and workspace. A shared waveform SVG and compact Lenny/Growth Assistant wordmark link home.

`/` prioritizes Open workspace and an interactive Ask→Trace→Make preview clearly marked Example/not live. It does not claim a generated or saved result. `/workspace` separates Sessions(saved research topics),Research(active question/composer/essay review),and context Sources/Documents(one compact tabbed reader). Selected provider/model/corpus status is discoverable;Models is a disclosure,not a provider picker.

| Layout | Actual behavior |
| --- | --- |
| Wide desktop≥1200px | Sessions/Research/context with visible mouse/keyboard dividers. Side widths,min/max,reset and collapsed state persist in localStorage and clamp on resize. Expanding context restores previous layout/focus when closed. |
| Tablet/narrow desktop | Research stays wide;context opens on demand with explicit close/focus return. |
| Phone≤600px | One panel at a time via existing navigation;composer controls stack. Viewport handling helps active inputs;real on-screen keyboard behavior is unverified. |

Start a session focuses the name field;opening a session reveals the composer. Suggestions fill drafts. Session rows truncate with full title available;older25-row pages load without losing drafts/selection. Lists and readers scroll independently. Citation buttons are visually distinct and open exact original text;heading focus moves into Sources and returns on close. The open reader and unsent drafts survive resizing/layout transitions. Essay review distinguishes fixed source quotes from editable application advice;acceptance requires explicit review.

Artifacts use a sanitized static HTML subset in an opaque script-disabled iframe with restrictive CSP. Markdown raw HTML is disabled. Parent source controls resolve owned snapshots. Model output does not get arbitrary execution or navigation permission.

States include empty/no session,working,partial saved draft,failed/cancelled/retry,missing dependency/key,empty corpus,source loading,review required and accepted/saved artifact. Baseline failures retain the question,but detailed failure reason disappears after reopening;this is a known limitation. The excluded experiment has additional false-abstention/error-copy defects.

Actual Chrome157 fixtures/real saved-content checks cover1440/1024/768/390px,focus/return,contrast samples,resize/storage/reset,draft/reader preservation and no overflow. Fixtures do not prove inference or persistence. The in-app connector remains bootstrap-blocked;physical keyboards,other engines and full accessibility certification are not claimed. Fresh README-rehearsal browser outcomes are in [Phase11 report](phase-11-report.md).
