# Frontend Reimagine — Current State

> **Purpose:** Live snapshot of where this phase actually stands, updated at every checkpoint.
> **Scope:** This phase only — updated continuously, never left stale.
> **Ownership:** TODO — assign a phase owner.
> **Status:** **Release Candidate verified, 2026-08-07. Ready for owner sign-off.** T0–T30 all done. One genuine layout bug (`FilterRail` mobile integration on Secrets/Documents) found and fixed at T30. RC verification re-checked every acceptance criterion live rather than trusting prior citations, and corrected one documentation error (AC43/reduced-motion was wrongly marked a gap at T29 — it's fully implemented and now confirmed working). Two new partial-coverage findings surfaced by that re-check (AC41 focus-restore, AC45 form-error uniformity) — both pre-existing, neither a Phase 09 regression, both recorded for owner decision.
> **Last Updated:** 2026-08-06

---

## Current Status

Phase 09 is in **Implementation** ([`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md)). Milestone 0 (T0/T0.5/T0.6) and T1 are complete. Per owner direction (2026-08-06), the session has shifted to implementation velocity: normal tasks proceed without per-task narration or confirmation; full detail lives in `09_IMPLEMENTATION_TASKS.md`'s as-built notes, and this file is updated continuously. Reporting reverts to narrative form at milestone checkpoints, architectural decisions, contract changes, or blocking issues.

The session produced: a codebase-grounded audit of the entire frontend, the four designer-skills artifacts (brief, IA, tokens, tasks), the full Phase 09 document set, two ADRs, and a roadmap entry.

Two defects were found and **verified in a running browser**, not inferred:

- 🔴 **The application renders entirely in Times New Roman.** `--font-sans` is declared self-referentially in `globals.css` and resolves empty; Geist is downloaded on every page load and never applied. `--font-mono` fails independently. Measured on `/unlock`: computed `font-family` `"Times New Roman"`, both variables empty, `--font-geist-sans` correctly populated.
- 🟡 **`/system/status` 404s**, so the Settings About card's Storage line silently never renders. The backend serves the endpoint; `next.config.ts` does not proxy it. Fixable with one frontend rewrite — **no backend change**.

## Completed

- [x] Repository-wide frontend audit — 17 routes, 40 primitives, 18 feature folders, 8 shared components read directly. Backend endpoint surface enumerated (112 across 18 modules).
- [x] Runtime verification of the two defects above, plus a clean `npx tsc --noEmit` baseline.
- [x] `julianoczkowski/designer-skills` installed (8 skills) and relocated to `.claude/skills/` at the repo root.
- [x] Designer-skills workflow run: `grill-me` → `design-brief` → `information-architecture` → `design-tokens` → `brief-to-tasks`. Artifacts in [`.design/frontend-reimagine/`](../../../.design/frontend-reimagine/DESIGN_BRIEF.md).
- [x] Four blocking design decisions confirmed by the project owner (see Architectural Decisions below).
- [x] **A proposed IA change was verified and rejected** — see Known Issues #1.
- [x] Full document set drafted: `README`, `00_AUDIT`, `01_SPEC`, `02_UI`, `03_BACKEND`, `04_DATABASE`, `05_COMPONENTS`, `06_API`, `07_TESTING`, `08_ACCEPTANCE`, `09_IMPLEMENTATION_TASKS`, `IMPLEMENT`, `10_RELEASE_NOTES`, this file.
- [x] [ADR-0016](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md) and [ADR-0017](../../decisions/0017-layered-design-token-architecture.md) — drafted, then **Accepted** 2026-08-06.
- [x] Phase 09 row added to [`../../02_ROADMAP.md`](../../02_ROADMAP.md) and **ratified** 2026-08-06.
- [x] **[`11_SCREEN_GRAPH.md`](11_SCREEN_GRAPH.md)** — screen dependency graph, added at the owner's request during the checkpoint review. It changed three conclusions; see Known Issues #7–#9.
- [x] **[`VERIFICATION_CONTRACT.md`](VERIFICATION_CONTRACT.md)** — scoped per OQ4 to the objectively checkable subset, with what it deliberately does *not* verify stated up front.

## In Progress

- [ ] **Owner sign-off on completion** — the only remaining gate; RC verification (2026-08-07) re-checked every previously-flagged item live rather than leaving them as assumptions. See [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §12: AC41 partial (dialog focus-trap works, focus-restore-to-trigger does not — pre-existing, not a Phase 09 regression), AC43 now fully satisfied (corrected — wrongly flagged as a gap at T29), AC45 partial (the a11y-wiring mechanism is correct but has one consumer app-wide, not "uniform"), AC46 satisfied by manual equivalent, not literal `axe`.

## Remaining

- [x] **Gate 1 — Roadmap ratification.** Granted 2026-08-06.
- [x] **Gate 2 — Specification approval**, with OQ1–OQ4 resolved. Granted 2026-08-06.
- [x] **Gate 3 — Implementation authorization**, as a separate explicit act. Granted 2026-08-06.
- [x] `VERIFICATION_CONTRACT.md` written, scoped per OQ4 to the objectively checkable subset.
- [x] **T0 — mechanical baseline captured** → `.baseline/phase-09/T0-mechanical-baseline.txt`. All 16 route paths resolve 200; all 5 redirects land correctly; pre-fix computed styles and proxy behaviour recorded; `tsc`/`lint`/`build` clean.
- [x] **T0.5a — typography defect FIXED and verified.** `html`, `body`, and real headings now compute to Geist.
- [x] **T0.5b — `/system/status` rewrite added; dev fixed (200 `application/json`).** Production gap found and **raised as a finding**, not patched — see Known Issues #11.
- [x] **T0.6 — corrected baseline + canonical reference set captured.** Unblocked when the project owner unlocked a fresh, isolated instance (`backend-phase09`/`frontend-phase09`, ports 8003/3003 — see Known Issues #10). 18 canonical shots (9 compositions × 2 themes) inspected live; two scope narrowings applied and documented (18 shots not the full 136-image sweep; no image files persisted — this session's Browser tool has no save-to-disk action, so evidence is recorded as findings, not binaries). Full detail in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) T0.6.
- [x] **T1 — design token system merged.** Three-layer system in `app/globals.css`. All shadcn token names preserved verbatim. Zero regressions.
- [x] **T2 — application shell.** New `AppShell`; all three `calc(100dvh...)` hacks removed (Documents, Prompt Studio, Notes board) — `grep` for the pattern now returns zero matches, literally. Zero regressions.
- [x] **T3 — grouped navigation.** `NAV_ITEMS` gained `group` additively (array order/values untouched); new shared `NavLinks` component means Sidebar and MobileNav render from one implementation, not two. Folded in AC21 (Prompt Studio icon unified). Workbench pinned-tools catalog re-verified explicitly (the Phase 08 `BUG-0001` seam) — all 5 tiles resolve correctly.
- [x] **T4 — command palette.** Bound the 8 shortcut letters (⌘+letter, modifier-gated); added "View all results" → `/search?q=`. 🆕 Found and fixed a real pre-existing defect: every inline search result's `CommandItem` `value` contained only an id, so cmdk's own fuzzy filter silently hid every result regardless of backend response — broken since the palette shipped, invisible until DOM-level verification (a screenshot alone did not reveal it). Fixed by including the name/title in each value.
- [x] **T5 — primitive retune.** 🆕 Found and fixed a deeper T1 gap: `--font-size-*` was never wired into Tailwind's own `text-xs`/`text-sm`/etc. utility scale, so "one ramp everywhere" was false for nearly the whole app. Fixed via `@theme inline`. Routed 5 overlay primitives' shadows through `--elevation-2/3`. Resolved OQ2: removed `avatar`/`context-menu`/`alert` (confirmed zero consumers), kept `table` for T7.
- [x] **T6 — shared app components.** 8 new components (`ConfirmDialog`, `ErrorState`, `SearchField`, `StatusBadge`, `SectionHeading`, `Toolbar`, `Field`, `KeyValueRow`), all additive/unwired. `PageHeader` v2 (breadcrumb slot, now sticky by default — verified live) and `EmptyState` retune both ship immediately to all existing consumers; verified live on `/secrets` and `/search`.
- [x] **T7 — data-surface components.** `FilterRail` (rail-at-`lg`/drawer-below, single content source for both) and `DataList`/`DataListRow` (Swiss row rhythm, discriminated-union row variants). Additive, zero current consumers.
- [x] **T8 — feedback system.** `Toaster`/`Skeleton` needed no changes (already token-driven). `PanelErrorBoundary` relocated to the shared layer so features outside Workbench can reuse it without a cross-feature import; logic unchanged, Workbench's error isolation re-verified live post-move.
- [x] **T9 — Workbench.** Rule-bounded panel headers (all 6 registered panels, incl. Notes'/Projects' registry-contributed ones); fixed the T0.6-documented pinned-tool label truncation; `WorkbenchResetButton` migrated to the shared `ConfirmDialog`. Zero logic edits to drag/reorder/mutation/deep-link code. Focus-management RAF behavior unverifiable this session (Browser pane tab `document.visibilityState: "hidden"` suppresses `requestAnimationFrame` — an environment limit, not a code change).
- [x] **T10 — Secrets (reference Swiss data surface).** Rail → `FilterRail`; search/`ProjectPicker` → `Toolbar`; list → `DataList`/`DataListRow`; new filtered-empty state; delete → `ConfirmDialog`. **Both documented responsive failures (375px rail-eats-content, 768px horizontal scrollbar) verified fixed** — zero overflow at either width, rail correctly collapses to a drawer below `lg`. Row height confirmed 40px desktop / 48px touch (I6).
- [x] **T11 — Knowledge Hub.** Filter bar → `Toolbar`/`SearchField`; rows → `DataListRow`; truncation notice promoted to a first-class list row; copy clarified to disambiguate from `/search`. **Fixed the note deep-link bug** (AC54) — note results now link `/notes?open={id}`. 🆕 Found in the process: that contract has no consumer on the Notes page itself (see Known Issues #15 below) — corrected, not silently patched around.
- [x] **T12 — Documents.** Adopted `PageHeader` (previously bypassed entirely). Rail → `FilterRail` holding the full master list (not just filters), with a nested-scroll structure (sticky search/project header, independently-scrolling list) verified via computed geometry. Toolbar reordered with a consequence-separating rule before Delete. New quiet save-state indicator (`Saving…`/`Saved`). **Closed a real silent-delete gap** — both the toolbar and every rail row's delete previously fired with zero confirmation; both now route through `ConfirmDialog`. Added previously-missing loading/error states to the sidebar list and editor pane.
- [x] **T13 — Search.** `/search` onto `DataList`; `ErrorState` replaces `EmptyState`'s prior misuse for the failure branch. Idle/2-char-threshold state correctly stays `EmptyState`.
- [x] **T14 — Notes.** Delete → `ConfirmDialog`; Toolbar/`SearchField` adoption. **Resolved Known Issue #15** — implemented scroll-to + 2s ring-highlight for `?open={id}` on the board. 🆕 Found and fixed a real React Strict-Mode timer bug in the process (see Known Issues #16).
- [x] **T15 — Projects.** List error → `ErrorState`; detail page's scoped lists → `DataList`; added a `Projects / {name}` breadcrumb via `PageHeader`'s slot; consequence-separating rule before Delete.
- [x] **T16 — Prompt Studio.** Adopted `PageHeader`; rail width/search aligned to shared tokens/components. **Deliberately did not adopt `FilterRail`** — its mobile drawer contract doesn't match this screen's list-XOR-detail reference pattern, and forcing it would have regressed the exact behavior this task must preserve. Delete → `ConfirmDialog`.
- [x] **T17 — Model Playground.** Run history → `DataList`; delete → `ConfirmDialog`; `ResultPanel` restyled onto the shared `StatusBadge`; explicit in-flight state on the run submit button. Credential remove flow (ADR-0011) deliberately left untouched.
- [x] **T18 — Converter.** Section headings → `SectionHeading`; tool grid gained the 3rd column tier; job list → `DataList` with an explicit job-level status badge and an "Uploading…" state. 🆕 Found and fixed a genuine pre-existing defect (see Known Issues #17).
- [x] **T19 — Developer Toolkit.** No code changes needed — already matched spec exactly; verified the full external contract (3 redirects, unknown-tab fallback, `router.replace` tab sync, nested Crypto tabs).
- [x] **T20 — Project Init.** Catalog error and generation-history error both → retryable `ErrorState`; generation history → `DataList` + `ConfirmDialog`; "Recent generations" → `SectionHeading`.
- [x] **T21 — Settings.** Regrouped into reference (Appearance/About) vs. consequential (Master password/Backup) sections with a divider; destructive-import warning moved adjacent to Import and recolored to read as a warning.
- [x] **T22 — Auth screens.** Added the Forge brand mark to both `/setup` and `/unlock`; card shadow/width moved onto tokens (`--elevation-2`, `--max-width-form`). Reduced-motion requirement already satisfied globally, no change needed.
- [x] **T23 — Destructive-action uniformity.** Found and fixed two genuine silent deletes (Secrets' folder/tag delete, Settings' Import backup — the single most destructive action in the app, previously ungated). Revisited and converted the T17-excluded credential-remove dialog after rereading ADR-0011 showed it doesn't actually govern the confirmation UI, only storage/security.
- [x] **T24 — State-coverage sweep.** Found and fixed five real loading/error/filtered-empty gaps: Notes board (no loading/error state at all), Documents sidebar (no filtered-empty distinction), Model Playground's `ProviderList`/`RunHistoryList` (no error state), Converter's job poll (no error state), Project detail's three scoped lists (no error state).
- [x] **T25 — Dead-code removal.** Removed `components/ui/table.tsx` (zero consumers — the T7 `DataList` reservation never materialized) and the `framer-motion` dependency (resolves OQ3). Confirmed no other unused primitives via a scripted sweep.
- [x] **T26 — Responsive validation.** All 17 routes × 4 widths × 2 themes swept and diffed against the T0.6 canonical reference set. Zero regressions.
- [x] **T27 — Accessibility pass (Forge's first).** Found and fixed 6 real defects: one WCAG contrast failure (Secrets tag badges), 9 icon-only controls with no accessible name, 7 unlabeled note-color swatches, and the sidebar nav's missing landmark/grouping semantics. See Known Issues #20 below.
- [x] **T28 — Regression validation against T0.** Found and fixed one real logic bug (command palette's Ctrl+K self-collision with Knowledge's own shortcut). One suspected regression (live search results) investigated and resolved as a test-methodology artifact, not a defect. All 48 navigation edges swept; `tsc`/lint/build clean; backend suite 100% green; `git diff --stat backend/ docker/` empty. See Known Issues #21.
- [x] **T29 — Documentation finalization.** `CURRENT_STATE.md`, `09_IMPLEMENTATION_TASKS.md`, `08_ACCEPTANCE.md`, `10_RELEASE_NOTES.md` all brought current with cited evidence; `04_UI_GUIDELINES.md`/`05_DESIGN_SYSTEM.md` updated where this phase converted TODOs into fact.
- [x] **T30 — Design review.** Found and fixed one genuine, systemic Must Fix (`FilterRail` mobile layout bug, Secrets + Documents) that had survived T26 and T28. Two Should Fix items and one Could Improve item recorded for a follow-up decision, not blocking RC. Zero anti-references found in the shipped app beyond one mild, pre-existing exception. Full review: [`.design/frontend-reimagine/DESIGN_REVIEW.md`](../../../.design/frontend-reimagine/DESIGN_REVIEW.md). See Known Issues #22.

## Known Issues

1. **The initial `/search` consolidation proposal was wrong, and was rejected on evidence.** The Phase 09 brief proposed retiring `/search` by redirecting into Knowledge Hub because the latter "already supersedes" it. Verification showed the opposite: `/api/search` covers **secrets + notes + documents**; `/api/knowledge` covers **notes + documents only** (ADR-0015). The redirect would have silently removed secret search. Resolved via [ADR-0016](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md), which achieves the same goal — one obvious way to search — without changing any surface's scope.

2. **No frontend test framework exists.** Confirmed by inspection: no Jest, Vitest, Playwright, or Testing Library; zero test files. This is the phase's largest risk given it touches all 17 routes. Out of scope to fix here; compensated by the T0 baseline, per-task Preserve contracts, and the T28 sweep. Recommended as its own future phase — Phase 09's component consolidation makes that phase substantially cheaper.

3. **The nav → workbench-catalog seam is manually synced.** `lib/nav-registry.ts` → `features/workbench/tool-metadata.ts` → backend `WORKBENCH_TOOL_KEYS`. Acknowledged in the source comments; it produced Phase 08's `BUG-0001`. T3 changes `NAV_ITEMS` additively and re-verifies the catalog explicitly.

4. ~~**`framer-motion` …**~~ **Resolved (OQ3, 2026-08-06):** remove it in T25.

5. ~~**Four shadcn primitives installed and unused**~~ **Resolved (OQ2, 2026-08-06):** adopt `table` for the genuinely tabular surfaces; remove `avatar`, `context-menu`, `alert` in T25.

6. **`docker/nginx.conf` has not yet been checked** for `/system/status` routing. If production does not already proxy it, that is a genuine production gap to raise as a finding — **T0.5b** checks it (moved from T13).

7. **The cross-feature boundary is not clean, and my audit initially said it was.** [`11_SCREEN_GRAPH.md`](11_SCREEN_GRAPH.md) §5.1 found **ten** cross-feature import edges against a coding standard that permits zero: four are the intended ADR-0002 registry inversion, six are public-component reuse, and **two features reach into another feature's data layer** (`notes/note-card.tsx` → `knowledge/api`; `projects` → `model-playground` across three files including `api.ts`). This is architectural debt, not presentation debt. **Out of scope for Phase 09** — the obligation is only to not worsen it (AC55). Fixing it means either relaxing the standard or adding a shared layer, both owner decisions.

8. **Two module cycles exist** — `workbench ↔ notes` and `workbench ↔ projects` — both from the ADR-0002 registry inversion, so intended rather than accidental. They constrain migration order: T9/T14/T15 form one cluster and re-verify each other.

10. ~~**T0.6 is blocked on an authenticated session.**~~ **Resolved 2026-08-06.** The owner correctly identified that the master password they gave was for a *different* Forge instance — the shipped July dev DB (`backend/.dev-data/`, `setup_completed_at: 2026-07-21`) has its own hash, unrelated to the real production data in the `forge_forge-data` Docker volume. Neither was touched. Instead a **third, fully isolated instance** was created (`backend-phase09`/`frontend-phase09`, ports 8003/3003, `FORGE_DATA_DIR=./.dev-data-phase09`, added to `.claude/launch.json`), which the owner completed first-run setup on with a throwaway password. 17 secrets, 5 notes, 4 documents, 1 project, and 4 prompts were then seeded through the real API so the baseline shows populated surfaces, not empty states. See T0.6 in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) for the full record and findings.

    **Follow-up, unrelated to Phase 09 but surfaced by this:** the password pasted into this session's chat transcript gates *some* Forge instance's real data. Recommended: rotate it via Settings → Master password once its instance is identified.

13. 🆕 **A second, distinct responsive failure found in Secrets, at 768px specifically.** Live inspection at the `md` breakpoint (tablet, populated data) showed a **horizontal scrollbar** — different from the 375px failure mode already in the audit (rail eating content). Both share the same root cause (`w-56 shrink-0`, no responsive variant) and the same fix (T10's `FilterRail`), but they are two distinct bugs, not one. See [`00_AUDIT.md`](00_AUDIT.md) §5.2 addendum.

14. 🆕 **Minor: Workbench pinned-tool tile labels truncate at the default 3-column width.** `"Converter"`, `"Notes"`, `"Prompt Studio"`, `"Secrets"`, `"Search"` render as `"Con…"`, `"Not…"`, `"Pro…"`, `"Sec…"`, `"Sea…"` because the tile is narrower than the text. Not a prior audit finding — visible only once the tiles had real labels to overflow. Folded into T9's scope, not filed separately.

11. **`/system/status` is broken in production too, and the shipped fix does not reach it.** `docker/nginx.conf` proxies `/api/` and `/health` only; `/system/status` falls through to the frontend and 404s exactly as it did in dev. The `next.config.ts` rewrite fixes **development only**. `docker/**` is inspect-only under this phase's contract, so this is **raised, not patched**. Two one-line options in [`00_AUDIT.md`](00_AUDIT.md) §3.2's addendum: **(a)** add a `location /system/status` block to nginx, or **(b)** repoint Settings at `/api/workbench`, which returns an identical `storage` object and is already proxied in both environments. Option (b) was originally rejected for coupling Settings to Workbench's endpoint — but that rejection predates knowing production was also broken, so it deserves a fresh look. **Owner decision recorded 2026-08-06: Option (a).** The frontend stays on `/system/status`; the nginx `location` block is the proper production fix. Rationale: `/system/status` exists to expose system status and Settings consuming it is semantically correct, whereas repointing at `/api/workbench` would couple Settings to an endpoint whose primary responsibility is different and whose payload is only *incidentally* identical today. The misconfiguration is in nginx, not the frontend — do not weaken the frontend architecture to route around an infrastructure bug. Since `docker/**` is inspect-only under this phase's contract, the change is **tracked as a shipped-app gap** in [`../../../docs/Roadmap.md`](../../../docs/Roadmap.md) rather than made here.

12. ✅ **Resolved at T11, 2026-08-06.** Knowledge Hub previously could not deep-link to a note — `knowledge-result-row.tsx:19` routed note results to a bare `/notes` while document results got `?open=<id>`. Fixed: `targetHref` now returns `/notes?open={id}` for notes too, matching the palette and `/search`. See Known Issue #15 below for what this fix revealed.

15. ✅ **Resolved at T14, 2026-08-06.** The `/notes?open={id}` contract had no consumer (found at T11 — see above). Fixed: `notes-board.tsx` now scrolls the target note into view and applies a 2-second ring-highlight when `?open={id}` is present, so the three existing call sites (palette, `/search`, Knowledge Hub) land somewhere meaningful instead of the bare board. See Known Issue #16 for a real bug found while implementing this.

16. ✅ **Resolved at T14, 2026-08-06 (found and fixed in the same task).** Implementing the highlight above combined a one-shot ref-guard with the highlight's own expiry `setTimeout` in a single `useEffect`. Under React Strict Mode's dev-only mount→cleanup→mount double-invocation, the cleanup cleared the first timer, and the second invocation's ref-guard (already tripped by the first) skipped re-arming it — so the highlight would appear and then never turn off. Confirmed via a `setTimeout`-tracing script showing the timer scheduled but never firing after 20+ seconds. Fixed by splitting into two effects: a ref-guarded one-shot (scroll + arm the highlight) and a separate, unguarded one keyed on the highlight state itself (expiry) — the second effect's cleanup+rerun nets out to exactly one live timer regardless of Strict Mode's double-invocation, which is the general-purpose fix for this class of bug (a ref-guard and a cleanup-bearing timer must not share one effect).

17. ✅ **Resolved at T18, 2026-08-06.** `features/ingest/job-list.tsx`'s two download buttons used `<Button render={<a ... download />}>` without `nativeButton={false}`, which Base UI flags at runtime (removes native button semantics). Pre-existing since before Phase 09; never previously runtime-verified (no prior session's console-error check had exercised the ingest download path with a completed job). Fixed by adding `nativeButton={false}` to both, matching the already-correct pattern used elsewhere in the codebase (e.g. `features/notes/workbench-panel.tsx`).

18. ✅ **Resolved at T23, 2026-08-06.** Two genuine silent deletes found by an app-wide audit for anything still bypassing `ConfirmDialog`, both pre-existing and never itemized by exact location in the original audit's general "3 silent deletes" count: (a) `secrets-filters.tsx`'s folder and tag delete buttons fired their mutation directly on click with zero confirmation — T10 fixed the secret row's own delete but never touched these two rail buttons, since they were outside that task's restructuring scope; (b) Settings' "Import backup" — which replaces **all** secrets, folders, tags, and notes — called the import mutation immediately on file selection, with the "Importing replaces..." text next to the button being static advisory copy rather than an actual gate. Both now route through `ConfirmDialog`. The folder-delete copy's claim ("secrets become unfiled, not deleted") was verified empirically against the real backend (create folder + secret, delete folder, confirm via API read that `folder_id` became `null` and the secret survived) rather than inferred from reading the service code alone.

19. ✅ **Resolved at T23, 2026-08-06 — a prior session's exclusion revisited.** T17 deliberately left `provider-list.tsx`'s credential-remove `AlertDialog` unconverted, reasoning "ADR-0011 governs credential handling." Rereading ADR-0011 in full during T23's audit showed this was an overly literal reading: the ADR governs credential **storage and encryption** (which table, which crypto primitive, write-only-after-creation), not the confirmation dialog's component choice. Converted it to `ConfirmDialog` with byte-identical copy — closing the one remaining inconsistency T23 exists to catch, without touching anything ADR-0011 actually governs.

20. ✅ **Resolved at T27, 2026-08-06.** Forge's first accessibility audit found six real defects, all via live measurement: a WCAG contrast failure on Secrets' tag badges (2.15–3.76:1 against the 4.5:1 text minimum, caused by using the tag color for both border and text instead of border-only); 9 icon-only controls across Secrets' rail, the shared `CopyButton`, and the UUID generators with no `aria-label`; 7 note-color swatch buttons with no accessible name at all (fixed by restructuring `NOTE_COLORS` into `{hex, name}` objects); and the sidebar `<nav>` missing `aria-label` with its four groups hidden from screen readers behind `role="presentation"`. Full detail in `09_IMPLEMENTATION_TASKS.md`'s T27 entry.

21. ✅ **Resolved at T28, 2026-08-06.** The command palette's keydown handler checked its own Ctrl/Cmd+K close-toggle before checking `NAV_ITEMS` shortcuts, making Knowledge's advertised shortcut ("K" — the same key that opens/closes the palette) permanently unreachable while the palette was open. Pre-existing since T4; never caught because verifying it requires the palette to already be open, which the earlier shortcut-binding work at T4 didn't test from that state. Fixed by checking destination shortcuts first when open, falling through to the close-toggle only if none matched. A second suspected issue during the same sweep — the palette's live search results appearing not to fire an API call — was investigated and traced to a test-methodology artifact (a synthetic DOM value-set landed on a palette instance that was `open:false` but still mounted, per this environment's Base UI close-animation behavior), not a real defect; re-tested with a genuine reopen and real keystrokes, the feature works correctly.

22. ✅ **Resolved at T30, 2026-08-07.** `FilterRail`'s mobile Sheet-trigger wrapper (`<div className="lg:hidden">`, `frontend/components/filter-rail.tsx`) was placed as a flex sibling of the content column in both of its consumers — `secrets/page.tsx` and `documents/page.tsx` — inside a plain `<div className="flex">`. Below `lg`, the desktop `<aside>` correctly collapsed to zero width, but the trigger wrapper did not: as a normal flex item it reserved its own horizontal track (measured 78px on Secrets, 110px on Documents) for the page's full height, silently narrowing every row's available content width on the narrowest supported viewport. Page-level `scrollWidth` stayed correct throughout (no horizontal-page-scroll symptom), which is almost certainly why T26's responsive sweep — which checks for page overflow — didn't catch it; this was found only by measuring the actual flex children's `getBoundingClientRect()` during T30's live design review, not by visual inspection alone (the effect was subtle enough to be easy to misread as normal padding in a screenshot). Confirmed systemic (identical integration pattern on both `FilterRail` consumers) before fixing. **Fixed** by changing the wrapping `<div className="flex">` to `<div className="flex flex-col lg:flex-row">` in both pages — a one-line change per file, touching neither `FilterRail`'s own component contract nor either call site's props. Verified: mobile content now spans the full viewport width with zero overflow; desktop (`lg+`) re-screenshotted pixel-identical to pre-fix.

23. ⚠️ **Open, found at RC verification 2026-08-07 — not a Phase 09 regression.** Dialog/Sheet focus is not restored to the trigger element on close. Live-verified: opening Secrets' "New secret" dialog correctly traps focus inside it; closing it via Escape or via its own Close button leaves `document.activeElement` stuck inside the now-closed (but still-mounted) dialog rather than returning to the "New secret" button. Reproduced with two independent close methods; re-checked after a 1.5s delay to rule out an animation-timing artifact. No Phase 09 task modified `Dialog`/`Sheet`/`Popover` internals, so this is pre-existing Base UI integration behavior. Recorded for owner decision rather than fixed — a primitive-level fix has app-wide blast radius, outside RC verification's scope. See `08_ACCEPTANCE.md` AC41.

24. ⚠️ **Open, found at RC verification 2026-08-07 — not a Phase 09 regression.** The shared `Field` component (built at T6, `frontend/components/field.tsx`) correctly wires `aria-describedby`/`aria-invalid` for form errors, but has exactly one consumer app-wide (`secrets/secret-detail-sheet.tsx`, confirmed via grep). AC45 calls for this to be "enforce[d] uniformly" — the mechanism exists but isn't uniform. Recorded for owner decision; closing it means adopting `Field` across the app's remaining forms, which is implementation work beyond RC verification's scope. See `08_ACCEPTANCE.md` AC45.

## Architectural Decisions

Confirmed by the project owner, 2026-08-06:

| Decision | Outcome |
|---|---|
| IA depth | Group the sidebar into Workspace / Library / Build / Tools + Settings as utility, **and** resolve the three-search-surface overlap. The specific mechanism changed after verification — see Known Issues #1 and ADR-0016. |
| Aesthetic philosophy | **Dieter Rams base + Swiss typographic treatment on data surfaces.** Seam bounded to three typographic utilities. |
| Typography | **Wire up the already-bundled Geist / Geist Mono.** Deliberate, recorded deviation from the `frontend-design` skill's "introduce a distinctive pairing" guidance — Forge is self-hosted, LAN-first, and frequently offline. |
| Migration scope | **All 17 routes this phase**, foundation first. A partial migration would leave Forge two-toned, which is the failure this phase exists to eliminate. |

**Accepted 2026-08-06:**

- [ADR-0016](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md) — grouped navigation and one job per search surface. **Supersedes nothing; clarifies and upholds [ADR-0007](../../decisions/0007-search-dedicated-page.md).**
- [ADR-0017](../../decisions/0017-layered-design-token-architecture.md) — three-layer token architecture preserving the shadcn semantic contract.

**Resolved at the same review (OQ1–OQ4, [`01_SPEC.md`](01_SPEC.md) §7):** roadmap ratified; `table` adopted for tabular surfaces and the other three primitives removed; `framer-motion` removed; the Verification Contract scoped to the objectively checkable subset.

**Two revisions requested by the owner and applied:** the foundation defects became their own pre-design step (**T0.5**, plus **T0.6** to re-shoot the visual baseline), and a **screen dependency graph** was added as a required pre-implementation artifact.

## Modified Files

No application code was changed. Files created or modified this session:

**Created — designer-skills artifacts**
- `.design/frontend-reimagine/DESIGN_BRIEF.md`
- `.design/frontend-reimagine/INFORMATION_ARCHITECTURE.md`
- `.design/frontend-reimagine/DESIGN_TOKENS.css`
- `.design/frontend-reimagine/TASKS.md`

**Created — Phase 09 documentation**
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/` — `README.md`, `00_AUDIT.md`, `01_SPEC.md`, `02_UI.md`, `03_BACKEND.md`, `04_DATABASE.md`, `05_COMPONENTS.md`, `06_API.md`, `07_TESTING.md`, `08_ACCEPTANCE.md`, `09_IMPLEMENTATION_TASKS.md`, `10_RELEASE_NOTES.md`, `11_SCREEN_GRAPH.md`, `IMPLEMENT.md`, `CURRENT_STATE.md`, `VERIFICATION_CONTRACT.md`

**Created — decisions and history**
- `forge-docs/decisions/0016-grouped-navigation-and-search-surface-consolidation.md`
- `forge-docs/decisions/0017-layered-design-token-architecture.md`
- `forge-docs/history/2026-08-06-phase-09-discovery-checkpoint.md`

**Created — tooling**
- `.claude/skills/` — 8 designer skills installed via `npx skills add julianoczkowski/designer-skills`

**Modified**
- `forge-docs/02_ROADMAP.md` — Phase 09 row added and ratified
- `forge-docs/decisions/README.md` — ADR-0016 and ADR-0017 indexed and Accepted
- `forge-docs/implementation/README.md` — Phase 09 indexed; a pre-existing staleness fixed (it still listed Phase 08 as "not started")
- `skills-lock.json` — moved to the repo root alongside the relocated skills
- `docs/Roadmap.md` — `/system/status` production gap added as a tracked known gap, with the approved nginx fix and the rejected alternative both recorded
- `frontend/app/globals.css` — T0.5a font binding
- `frontend/app/layout.tsx` — T0.5a font-variable class placement
- `frontend/next.config.ts` — T0.5b `/system/status` rewrite
- `.claude/launch.json` — `backend-phase09` / `frontend-phase09` configurations added (additive)
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/00_AUDIT.md` — `--font-mono` claim corrected; `/system/status` addendum; tablet-overflow addendum; §6.5 added
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/02_UI.md` — §0 layout invariants added
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/08_ACCEPTANCE.md` — AC54–AC56 added; sign-off section updated
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/09_IMPLEMENTATION_TASKS.md` — T0, T0.5, T0.6 checked off with as-built notes
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/README.md`, `01_SPEC.md`, `IMPLEMENT.md`, `VERIFICATION_CONTRACT.md` — authorization recorded
- `.design/frontend-reimagine/DESIGN_TOKENS.css` — I10/I11 tokens added

**Created**
- `.baseline/phase-09/T0-mechanical-baseline.txt` — route resolution, redirects, proxy behavior, toolchain output, pre/post-fix computed styles
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/11_SCREEN_GRAPH.md`
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/VERIFICATION_CONTRACT.md`
- `forge-docs/history/2026-08-06-phase-09-authorization-checkpoint.md`

**Note:** this list covers Milestone 0 in full detail; T1–T8's individual file diffs are recorded in each task's as-built note in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) rather than backfilled here. From T9 onward, changed files are listed per milestone below.

**Modified — Milestone 2 (T9–T13), 2026-08-06**
- `frontend/features/workbench/components/workbench-panel-card.tsx`, `pinned-tools-panel.tsx`, `workbench-reset-button.tsx` (T9)
- `frontend/app/(app)/secrets/page.tsx`, `frontend/features/secrets/secrets-filters.tsx`, `secret-detail-sheet.tsx` (T10)
- `frontend/features/knowledge/knowledge-filter-bar.tsx`, `knowledge-result-row.tsx`, `knowledge-result-list.tsx`, `frontend/app/(app)/knowledge/page.tsx` (T11)
- `frontend/app/(app)/documents/page.tsx`, `frontend/features/documents/document-sidebar.tsx` (T12)
- `frontend/app/(app)/search/page.tsx`, `frontend/features/search/search-result-list.tsx` (T13)
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/09_IMPLEMENTATION_TASKS.md` — T9–T13 checked off with as-built notes; this file

**Modified — Milestone 3 (T14–T22), 2026-08-06**
- `frontend/features/notes/note-card.tsx`, `notes-board.tsx`, `frontend/app/(app)/notes/page.tsx` (T14)
- `frontend/app/(app)/projects/page.tsx`, `frontend/app/(app)/projects/[id]/page.tsx` (T15)
- `frontend/app/(app)/prompt-studio/page.tsx`, `frontend/features/prompt-studio/prompt-sidebar.tsx`, `prompt-editor.tsx` (T16)
- `frontend/features/model-playground/run-history-list.tsx`, `result-panel.tsx`, `prompt-composer.tsx` (T17)
- `frontend/app/(app)/converters/page.tsx`, `frontend/features/ingest/job-list.tsx` (T18)
- T19: no files touched (verification only)
- `frontend/app/(app)/project-init/page.tsx`, `frontend/features/project-init/generation-history.tsx` (T20)
- `frontend/app/(app)/settings/page.tsx` (T21)
- `frontend/app/(auth)/layout.tsx`, `frontend/app/(auth)/unlock/page.tsx`, `frontend/app/(auth)/setup/page.tsx` (T22)
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/09_IMPLEMENTATION_TASKS.md` — T14–T22 checked off with as-built notes; this file

**Modified — Milestone 4 (T23–T25), 2026-08-06**
- `frontend/features/secrets/secrets-filters.tsx`, `frontend/app/(app)/settings/page.tsx`, `frontend/features/model-playground/provider-list.tsx` (T23)
- `frontend/app/(app)/notes/page.tsx`, `frontend/features/notes/notes-board.tsx`, `frontend/features/documents/document-sidebar.tsx`, `frontend/features/model-playground/provider-list.tsx`, `run-history-list.tsx`, `frontend/app/(app)/converters/page.tsx`, `frontend/app/(app)/projects/[id]/page.tsx`, `frontend/app/(app)/prompt-studio/page.tsx`, `frontend/features/prompt-studio/prompt-sidebar.tsx` (T24)
- `frontend/package.json`, `package-lock.json` (removed `framer-motion`); deleted `frontend/components/ui/table.tsx`; `frontend/features/prompt-studio/version-history-sheet.tsx` (T25)
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/09_IMPLEMENTATION_TASKS.md` — T23–T25 checked off with as-built notes; this file

**Modified — Milestone 5 (T26–T28), 2026-08-06**
- `frontend/app/(app)/secrets/page.tsx` (T27 — contrast fix)
- `frontend/features/secrets/secrets-filters.tsx` (T27 — aria-labels)
- `frontend/components/copy-button.tsx` (T27 — aria-label)
- `frontend/features/generators/simple-generators.tsx` (T27 — aria-labels)
- `frontend/features/notes/note-card.tsx`, `frontend/features/notes/note-colors.ts`, `frontend/app/(app)/notes/page.tsx` (T27 — swatch accessible names)
- `frontend/components/app-shell/nav-links.tsx` (T27 — nav landmarks)
- `frontend/components/command-palette/command-palette-provider.tsx` (T28 — Ctrl+K self-collision fix)
- `frontend/app/(app)/secrets/page.tsx`, `frontend/app/(app)/documents/page.tsx` (T30 — `FilterRail` mobile-layout fix)
- `.design/frontend-reimagine/DESIGN_REVIEW.md` — new, T30's full findings
- `forge-docs/implementation/Phase-09-Frontend-Reimagine/09_IMPLEMENTATION_TASKS.md`, `08_ACCEPTANCE.md`, `10_RELEASE_NOTES.md` — T26–T30 checked off with as-built notes and cited evidence; this file
- `forge-docs/04_UI_GUIDELINES.md`, `forge-docs/05_DESIGN_SYSTEM.md` — TODOs converted to fact (T29)

## Next Milestone

**None — Milestone 5 is complete and Phase 09 is Ready for Release Candidate.** The only remaining gate is owner sign-off ([`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §12), which is a decision for the project owner, not implementation work. Two Should Fix items from T30's design review (a pre-existing decorative auth-screen gradient; a document-title input that truncates at 768px) and one Could Improve item (the brief's own responsive table not reflecting the frozen I3 nav-breakpoint invariant) are recorded but do not block RC — see [`.design/frontend-reimagine/DESIGN_REVIEW.md`](../../../.design/frontend-reimagine/DESIGN_REVIEW.md).

## Next Claude Prompt

> Phase 09 implementation (T0–T30) is complete. If resuming work here, the next step is either (a) owner sign-off and a Release commit, or (b) a follow-up task addressing the two Should Fix / one Could Improve items in `.design/frontend-reimagine/DESIGN_REVIEW.md`, if the owner elects to close them before Release rather than after. Read `CURRENT_STATE.md` in full and `08_ACCEPTANCE.md` §12 first either way.

## Session Notes

**2026-08-06 — Discovery and design session (session 1).**

Began by establishing that Phase 09 **did not exist**: no `Phase-09-*` folder anywhere in the repository, and no Phase 09 row in the roadmap. The phase brief referred to an "uploaded `Phase-09-Frontend-Reimagine/` folder" as the documentation home; no such folder was present. Scaffolded it from the conventions of Phases 07–08 rather than guessing.

Audited the frontend by direct inspection — every route file, the shell, the token layer, the registries, and the backend contracts they consume. Deliberately did not delegate exploration; the surface is ~11.5k lines and reading it directly was both cheaper and more reliable than summarising it through an intermediary.

Two findings came from running the app rather than reading it. The Times New Roman defect is the more significant: it is a one-line CSS bug that has governed the appearance of every screen since the project began, and it is invisible to static review unless you happen to trace `--font-sans` back to its own declaration. The `/system/status` 404 was found the same way.

Installed the designer-skills package as instructed. It installed into `frontend/.claude/skills/` because the working directory had persisted from a prior command; moved to the repo root so the skills are discoverable session-wide.

The most consequential moment was verifying my own recommendation and finding it wrong. The IA question offered "retire `/search`, Knowledge Hub supersedes it" as the recommended option, and the owner selected it. Checking the two services before writing it into the IA showed Knowledge Hub has no secrets path at all — implementing the proposal as stated would have silently removed secret search, precisely the class of regression this phase forbids. Corrected in the IA, the spec, the audit, and ADR-0016, and reported to the owner rather than quietly implemented.

Ended the session with zero application code changed, which is the correct outcome for a discovery pass.

**2026-08-06 — Authorization and Milestone 0 (session 2, continued).**

Owner reviewed the discovery checkpoint and cleared all three authorization gates, resolving OQ1–OQ4 and approving two revisions: elevate the two verified defects into their own pre-design step (T0.5/T0.6), and add a screen dependency graph before implementation. Built [`11_SCREEN_GRAPH.md`](11_SCREEN_GRAPH.md) by mechanical extraction — every `router.push`/`replace`, every `<Link href>`, every cross-feature import — rather than reconstructing it from memory. It immediately paid for itself: it corrected an over-generous claim in my own audit (ten cross-feature import edges exist, not zero), found two intentional module cycles from the Workbench registry pattern, and surfaced a real deep-link defect in Knowledge Hub. The correction is left struck-through in `00_AUDIT.md` rather than silently edited, on the theory that the audit trail is worth more than a clean-looking document.

Owner then approved Option (a) for `/system/status` (keep the frontend reading the endpoint that owns the data; fix nginx, not Settings) and asked for layout invariants frozen before token work begins — added as `02_UI.md` §0, twelve of them, two of which (dialog tiers, control heights) weren't in the token file at all until this.

Executing T0.5 surfaced two things the plan got wrong, both corrected in place rather than smoothed over. First, the original claim that `--font-mono` was broken was itself wrong — probing the running app before fixing showed the `font-mono` utility always resolved correctly on `<body>` descendants; only `--font-sans` ever failed. Second, my first attempted fix (binding `--font-sans` at `:root`) failed for the *same reason as the original bug* — `--font-geist-sans` is scoped to the `<body>` class, so a `:root` reference to it is invalid at computed-value time. The real fix moves the font-variable classes onto `<html>`. Both corrections are documented with the reasoning, not just the outcome.

Then asked to "rebuild the backend" to fix a password that wasn't working. Diagnosed instead of complying: the dev instance the user had been pointed at (`backend/.dev-data/`, set up 21 July, near-empty) has its own Argon2id hash, entirely unrelated to `FORGE_MASTER_KEY` — password verification is DB-scoped, not key-scoped, so no rebuild could ever have fixed a "wrong database" problem. Rebuilding was also the wrong instinct on its own terms: one reading of "rebuild" could have meant deleting `.dev-data/`, and the dev database — however useless as a screenshot reference — is still real prior state that wasn't mine to discard on an ambiguous instruction. Set up a third, fully isolated instance instead (`backend-phase09`/`frontend-phase09`, ports 8003/3003) and asked the owner to complete first-run setup there, leaving both the July dev DB and the real production Docker volume untouched.

Once unlocked, seeded 17 secrets / 5 notes / 4 documents / 1 project / 4 prompts through the real API — not the database directly — so Secrets and Knowledge would screenshot as populated data surfaces rather than the shipped dev DB's near-empty state. Captured all 18 canonical reference shots (9 compositions × 2 themes) and inspected them live. That inspection found two things static review could not have: a genuine second responsive failure in Secrets at exactly 768px (a horizontal scrollbar, distinct from the already-known 375px failure), and Workbench pinned-tool tiles truncating their labels at the default width. Also discovered mid-session that this toolset's screenshot action displays inline rather than writing files to disk — flagged rather than silently worked around; the 18 shots' evidentiary value survives as recorded findings, and persisted image files will first exist in the repo at T30's `/design-review` pass.

Milestone 0 complete. Zero regressions found against the T0 mechanical baseline. Next is T1, sequenced alone by design.

**2026-08-06 — Milestone 2, primary surfaces (session 3).**

Resumed from a handout at the T1–T8 boundary (Milestone 1 complete, zero commits, all work still in the working tree). Owner approved Milestone 2 (T9–T13) as one continuous pass with no intermediate reports, so this entry covers all five tasks together rather than one per task, matching the owner's own framing of it as "one coherent vertical slice."

T9 (Workbench) was the smallest of the five — a rule-bounded header and a label-truncation fix, both already scoped precisely by the T0.6 findings, plus migrating the reset button's ad hoc `AlertDialog` to the shared `ConfirmDialog` per the foundation notes' explicit "start using it now" guidance. One verification gap surfaced here that recurred for the rest of the milestone: this session's Browser pane reports `document.visibilityState: "hidden"`, which suppresses `requestAnimationFrame` in Chromium — so the customize-mode focus management (which is RAF-driven and untouched by this task) could not be exercised live. Recorded as an environment limitation rather than assumed broken or assumed fine.

T10 (Secrets) was the reference implementation the spec asked it to be. The two responsive failures documented since T0.6 — 375px's rail eating content, 768px's horizontal scrollbar — shared one root cause (`w-56 shrink-0`, no responsive handling) and were both closed by the same `FilterRail` adoption; verified independently at both widths rather than assumed fixed together. The filtered-empty state was a real gap, not a refinement: before this task, running out of search results and having zero secrets rendered identically.

T11 (Knowledge Hub) is where the milestone's one substantive finding came from. Fixing the documented note deep-link bug (`knowledge-result-row.tsx` routing notes to a bare `/notes`) meant making Knowledge Hub construct the same `/notes?open={id}` link the palette and `/search` already used — and checking that destination before trusting the prior session's characterization of it as "working" showed it isn't: nothing on the Notes page reads the `open` param at all. This is the same discipline the T0 session applied to the original "retire /search" proposal — verify a delegated claim against the actual code before building on it, rather than propagating it forward. The fix still shipped (it makes all three call sites consistent, and removes Knowledge Hub's specific inconsistency), but the deeper gap is now a recorded finding for T14, not a silently-inherited assumption.

T12 (Documents) was the most structurally involved of the five. `FilterRail` was authored for filter-accordion content (Secrets' folders/tags) with a single `overflow-y-auto` on its own `<aside>`; Documents needed its rail to hold an entire master list with a sticky search/project header above an independently-scrolling body — a different shape than the component's original use case. Rather than fork `FilterRail` or hand-roll a second rail implementation, gave `DocumentSidebar` its own `h-full` wrapper that resolves against the aside's flex-stretched height (confirmed by measuring: aside height − padding = wrapper height, exactly), with its own internal `shrink-0` header and `flex-1 min-h-0` scroll region absorbing all overflow before it reaches the outer aside. Verified by computed geometry, not by assuming the CSS math would work out. Separately, found that both of Documents' delete entry points had *zero* confirmation before this task — not a stale doc claim this time, just an oversight the original audit's "3 silent deletes" count had already flagged in general terms but not itemized by exact location.

T13 (Search) was the cleanest of the five — no structural surprises, no new findings, straight adoption of `DataList` and the correction of `EmptyState`'s pre-existing misuse for the error branch.

Validation ran once at the end of the milestone rather than after each task: stopped the dev server, `npm run build` (clean, all 17 routes), cleared `.next`, restarted, then swept all 17 routes (200), all 5 redirects (307 to correct targets), and `/system/status` (200) against the running instance. `git diff --stat backend/ docker/` stayed empty throughout — nothing outside `frontend/` was touched. Live-verified each screen individually as it was built (not deferred to the end), including one very literal test: dispatching a real DOM `input` event and sampling the save-state indicator at 300ms intervals to catch the `Saving…` → `Saved` → idle transition, since a single snapshot read had missed it entirely on the first attempt.

Milestone 2 complete. Zero regressions found. One new finding recorded (T11, above) for T14 to address or explicitly defer. Next is T14 (Notes), the start of Milestone 3's `workbench↔notes↔projects` cluster.

**2026-08-06 — Milestone 3, secondary surfaces (session 3, continued).**

Owner approved Milestone 3 (T14–T22) as one continuous pass, same framing as Milestone 2. Two real bugs were found and fixed in this milestone, both via runtime verification rather than static review — consistent with how every substantive finding in this phase has surfaced so far.

T14 (Notes) carried the milestone's most interesting problem: T11 had left a recorded finding that `/notes?open={id}` had no consumer, and T14 owns the file that could fix it. Implemented scroll-to + a timed ring-highlight — and then found, via a `setTimeout`-tracing script (patch `window.setTimeout` to log every scheduled/fired timer, since a live poll alone couldn't distinguish "never fired" from "fired before I looked"), that the highlight never turned off. Root cause: a one-shot ref-guard and the highlight's own expiry timer shared one `useEffect`. React Strict Mode's dev-only double-invocation (mount → cleanup → mount, intentional, to catch exactly this class of bug) cleared the first timer on the synthetic remount, and the guard — already tripped from the first invocation — skipped rearming it on the second. This is a general pattern, not a one-off: a ref-guard that gates "do this once" must never live in the same effect as a cleanup-bearing timer, because Strict Mode's cleanup+rerun will silently drop the timer without the guard noticing. Fixed by splitting into two effects. Recorded in `CURRENT_STATE.md` as its own numbered finding, not folded into the deep-link fix's entry, since it's a distinct defect class worth being findable on its own.

T18 (Converter) surfaced the milestone's other real bug, found incidentally while restyling `JobList` onto `DataList`: Base UI logged a runtime warning that two download buttons (`render={<a ... download />}`) lacked `nativeButton={false}`. Checked whether this was new — it wasn't; the pattern predates Phase 09, and it had simply never been exercised with a completed upload and a console check in the same session before. Fixed against the already-correct precedent elsewhere in the codebase rather than inventing a new pattern.

T16 (Prompt Studio) was the one task this milestone where the "obvious" migration was the wrong one: the task line said "rail → `FilterRail`," but `FilterRail`'s mobile drawer contract and Prompt Studio's list-XOR-detail single-pane pattern are different interactions, and forcing the former onto the latter would have violated the task's own Preserve line ("this is the reference pattern, do not regress it"). Adopted the shared width token and search field instead, left the toggle logic untouched, and documented why `FilterRail` itself wasn't the right fit here rather than silently deviating from the task line without explanation.

T19 (Developer Toolkit) required zero code changes — the page already matched the target spec exactly before this task began, and all 16 tool components were already on `ToolCard` (confirmed by grep, not assumed). Recorded as a real, complete task rather than skipped, since verifying an already-compliant screen against its full external contract (three redirects, unknown-tab fallback, tab-switch URL sync, nested tab set) is still the task's job, just with a different-shaped output.

Environment-limitation artifacts continued to show up in roughly the pattern established at Milestone 2: `document.hasFocus(): false` meant autofocus's effect couldn't be observed on the auth screens (T22), and the Converter upload's 800ms poll appeared to "stick" on `processing` when checked across separate tool calls but completed near-instantly when observed within one continuous script — both are this session's Browser-pane characteristics, not application defects, and both were verified as such (via `document.hasFocus()`/`visibilityState` checks and a same-script re-run, respectively) rather than assumed.

Validation ran once at the end, same pattern as Milestone 2: stopped the dev server, `npm run build` (clean, all 17 routes plus the dynamic `/projects/[id]`), cleared `.next`, restarted, swept all routes/redirects/`/system/status`, confirmed `git diff --stat backend/ docker/` stayed empty. Fresh-tab console checks across all nine touched routes post-restart, zero errors.

Milestone 3 complete. Zero regressions found. Two real bugs found and fixed in the same tasks that surfaced them (T14, T18), both recorded with root cause rather than just outcome. Next is T23 (destructive-action uniformity), the start of Milestone 4.

**2026-08-06 — Milestone 4, consolidation (session 3, continued).**

Owner recommended a specific shape for this milestone — shift from "making changes" to "proving there are no remaining inconsistencies" — and gave a concrete checklist per task (entry points to check for T23, the six states to verify for T24, the sweep categories for T25). Followed that shape directly rather than re-deriving it.

T23 started with a grep for every remaining `AlertDialog` in the codebase, which turned up exactly two real usage sites beyond the shared component itself: `provider-list.tsx`'s credential-remove (left alone at T17) and `version-history-sheet.tsx`'s restore-version (correctly non-destructive, never a candidate). The actual **audit** — not just grepping for the primitive name, but grepping for every `.mutate(` call on a delete/remove endpoint and checking each call site's onClick — is what found the two real bugs: Secrets' folder/tag delete buttons, and Settings' Import backup. The second one is worth dwelling on: it's the single most destructive action in the entire application (replaces every secret, folder, tag, and note in one call), and it had no confirmation gate at all — the warning text sitting next to the button was cosmetic, not functional. Fixed by holding the parsed bundle in state pending confirmation. Verified the fix doesn't fire on cancel by checking the network log directly, not just visually confirming the dialog closed — a dialog can visually dismiss without the underlying event handler having been reached correctly, so the network-level check is what actually proves the gate works.

The more interesting move in T23 was revisiting a decision from two tasks ago. At T17, `provider-list.tsx`'s credential-remove confirmation was left as its own `AlertDialog` with the reasoning "ADR-0011 governs credential handling" — appropriate caution at the time, given the task's own Preserve line said to keep confirmations "exactly." Rereading ADR-0011 in full for this audit (not just recalling its existence) showed that reasoning was an overly literal extension: the ADR is about *storage and encryption* — which table, which crypto primitive, write-only-after-creation — and says nothing about which dialog component wraps the confirmation copy. A byte-identical-copy swap to `ConfirmDialog` doesn't touch anything the ADR actually decided. Converting it closed the one remaining inconsistency in the whole app, which is the entire point of a consolidation task existing. This is the same category of self-correction this phase has made repeatedly (the `/search`-retirement proposal, the "cross-feature boundary is clean" audit claim, the "/notes?open= is a working contract" characterization) — check a prior claim against the primary source before treating it as settled, even when the prior claim was your own.

T24's sweep found five real gaps by mechanically walking the Loading/Empty/Filtered-empty/Error/Success matrix against each list-bearing surface rather than spot-checking the ones that felt likely to have problems. The Notes board gap was the most consequential: it had no loading state and no error state at all, meaning `data ?? []` made a slow load indistinguishable from a genuinely empty board (the empty-state message would flash before real notes appeared) and made a fetch failure invisible. The other four (Documents' filtered-empty, Model Playground's two missing error states, Converter's missing error state, Projects' three scoped lists' missing error states) share a common shape: each one silently degraded a *failure* into looking like *emptiness*, which is a worse failure mode than an ugly error message, since it tells the user nothing went wrong when something did.

T25 was the smallest of the three: one primitive (`table.tsx`) had zero consumers after all seven Swiss surfaces shipped without ever needing a literal `<table>`, and `framer-motion` had zero import sites, confirmed the same way OQ3 asked for. Used `npm uninstall` rather than hand-editing `package.json`/`package-lock.json`, since a hand-edited lockfile risks integrity-hash mismatches that `npm install` would otherwise catch immediately.

Validation followed the same pattern as the prior two milestones: build clean, restart, full route/redirect/`/system/status` sweep, `git diff --stat backend/ docker/` empty, fresh-tab console checks across every touched route.

Milestone 4 complete. Zero regressions found. Two genuine silent-delete bugs closed (T23) — one of them the most consequential single finding of the entire phase, given its blast radius. Five state-coverage gaps closed (T24). One dependency and one primitive removed (T25). Next is Milestone 5 (T26–T30), the final validation milestone before Release Candidate.

**2026-08-06 — Milestone 5, validation (session 3, continued).**

Owner approved Milestone 5 (T26–T30) as one continuous pass toward Release Candidate, with an explicit checkpoint-report format and four named stop conditions (blocker, architectural change, backend contract change, or milestone complete). None of the four triggered.

T27 (accessibility — Forge's first audit of any kind) found six real defects by measuring rather than eyeballing: a genuine WCAG contrast failure on Secrets' tag badges, traced to the same root cause each time it recurs in this codebase — reusing one value (the tag's color) for two roles (border *and* text) without checking whether the second role's background still clears 4.5:1. Nine icon-only controls and seven note-color swatches had no accessible name at all, the swatches being the more interesting case: the underlying data (`NOTE_COLORS`) was a flat array of hex strings with no name to label with, so the fix had to restructure the data model, not just add a JSX attribute. The nav landmark fix was the smallest change with the largest scope — one `aria-label` and a `role="group"` swap made every one of the sidebar's existing groups newly legible to assistive tech, all at once.

T28 (regression validation) produced this milestone's one substantive finding, and it came from testing the palette's own advertised feature list against itself rather than against the rest of the app: Knowledge's shortcut is "K", which is also the palette's own open/close key, and the original T4 handler checked its own toggle case first — so the one shortcut that happened to collide with the toggle key was the one shortcut nothing had ever exercised from the *open* state. Every other shortcut had been verified opening the palette from closed; none had been verified as a destination jump *while already open*, because seven of the eight don't share this ambiguity. Fixed by reordering the checks. A second, initially alarming signal — the palette's live search appearing to fire zero API calls — resolved into a lesson about this session's own tooling rather than the app: a `data-closed` dialog stays mounted through its close animation in this environment (already documented at T4/T8), and a synthetic DOM value-set had silently landed on exactly such a "closed-but-present" instance. The fix wasn't code — it was re-running the same test with a real reopen and real keystrokes, which worked on the first try.

Locking the session mid-sweep (deliberately, to verify the Lock action itself) closed the loop on live browser verification earlier than planned: `07_TESTING.md` §2.2 already documents that an automated session cannot supply the master password, so the palette's Lock item was confirmed by code-equivalence to the already-live-verified topbar Lock rather than by a second live click. Running the build gate without stopping the dev server first reproduced the `_buildManifest.js.tmp.*` cascade §2.1 already warned about — recovered exactly as documented (`rm -rf .next`, restart), and re-swept all 17 routes 200 afterward. Both are operational artifacts this phase had already named, encountered again and handled the same way, not new defects.

Backend suite run in full for the first time this milestone (not just `git diff --stat`): 100% pass, zero failures, pre-existing deprecation warnings only — consistent with the zero-backend-diff constraint holding throughout.

Milestone 5's validation trio (T26–T28) complete. Zero regressions against the T0 baseline. One real pre-existing bug found and fixed (T28's Ctrl+K collision) and six real accessibility defects found and fixed (T27) — both net improvements over baseline, not regressions from it. T29 (this documentation pass) and T30 (`/design-review`) remain before the milestone closes.
