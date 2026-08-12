# UX Elevation — Specification / Design Record

> **Purpose:** The design record for Phase 10 — reproduces the actual planning-session plan that governed implementation, and records where implementation confirmed, modified, or rejected each hypothesis against the live application. This is a **design record written from an already-approved lightweight plan**, not a pre-implementation spec that went through this repo's roadmap-ratification/spec-approval gates — see [`README.md`](README.md)'s process note.
> **Scope:** This phase only.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Complete — reflects implementation as shipped, not as originally proposed.
> **Version:** 1.0.0
> **Last Updated:** 2026-08-12
> **Depends On:** [`../Phase-09-Frontend-Reimagine/README.md`](../Phase-09-Frontend-Reimagine/README.md)

---

## 1. Governing principle

Every "target model" in the source plan was written as a hypothesis to validate against the live, running screen — never a predetermined answer to implement mechanically. The plan's own wording, preserved here because it was the operative instruction during implementation:

> A hypothesis may be confirmed, modified, or rejected. Do not implement a proposed redesign merely because it appears in this document. If the current composition is actually stronger than the proposed target, preserve it and explain why. If you discover a materially better composition, implement the better composition even when it differs from the hypothesis.

Screen tiers set going in, to bound scope:
- **Major redesign candidates:** Workbench, Notes, Projects, Documents, Model Playground.
- **Focused redesign:** Knowledge, Prompt Studio.
- **Reference / verify-only:** Secrets, Search, Converters, Developer Toolkit, Settings, Project Init, Unlock, Setup.

## 2. Ground rules (held throughout)

- No backend/API/data-model changes. No new product capabilities.
- Preserve every navigation edge documented in [`../Phase-09-Frontend-Reimagine/11_SCREEN_GRAPH.md`](../Phase-09-Frontend-Reimagine/11_SCREEN_GRAPH.md) unless a redesign explicitly changed one (none did).
- Preserve the Workbench panel-registry contract and the `workbench ↔ notes ↔ projects` module cycles (ADR-0002) — intended architecture, not accidental coupling.
- Reuse existing Phase 09 shared components wherever they fit; only introduce a new presentation primitive when the existing vocabulary genuinely couldn't express the right UX, confirmed against the live screen first.
- Respect prior deliberate decisions (e.g. Prompt Studio's documented Phase 09 choice not to use `FilterRail`) unless hands-on work showed they demonstrably failed the new bar.
- No decorative additions: no gradients, glassmorphism, new shadows/animation, or generic SaaS dashboard patterns.

## 3. Per-screen record: hypothesis vs. outcome

For each screen: what the plan proposed, what live inspection found, and what was actually built.

### Workbench — major redesign, hypothesis confirmed

- **Plan hypothesis:** uniform 3-column grid gave every panel (Pinned Tools, Recent Activity, Quick Actions, System Status, Recent Notes, Recent Projects) equal visual weight regardless of information value; Quick Actions duplicated Pinned Tools' function. Target: weighted primary/rail composition — primary column for panels the user jumps into, rail for lower-frequency-glance panels.
- **Live inspection:** confirmed. Screenshot at 1440px showed exactly the described flat grid, with Quick Actions occupying a full card for 3 buttons and Recent Activity squeezed into an equal-width column despite being the most information-dense panel.
- **Alternatives considered:** an activity-feed-dominant composition (Recent Activity as the primary column) was considered and rejected — Workbench's job is "jump fast," not "read a log," so panels the user acts on (Pinned Tools, Recent Notes, Recent Projects) were given primary weight instead; Recent Activity moved to the rail alongside Quick Actions (collapsed to a compact row) and System Status.
- **Built:** additive `column?: "primary" | "rail"` field on `WorkbenchPanelMetadata` (`panel-types.ts`); `WorkbenchGrid` renders two tracks (`lg:w-2/3` primary, `lg:w-1/3` rail), each with its own `DndContext` so drag-reorder is scoped within a column — the primary/rail split itself is fixed by panel metadata, not draggable. Pinned Tools spans the primary column's full row width to avoid an unbalanced 2-column gap next to Recent Notes/Recent Projects.
- **Must-not-break, verified:** panel-registry contract (`getRegisteredPanels`/`register-all.ts` ordering) intact; `useWorkbenchQuery`/`useUpdateLayoutMutation` payload shape unchanged; all Workbench-sourced nav edges (3 quick actions, 7 pinned-tool targets, 2 panel deep links) replayed and confirmed.

### Notes — major redesign, hypothesis confirmed (user-approved before build)

- **Plan hypothesis:** search/project filter swapped the note set (list-filtering vocabulary) rather than preserving spatial context, defeating the "spatial position is information" property of a free-positioned canvas. Target: filtering dims/fades non-matching notes in place instead of removing them.
- **Live inspection:** confirmed via direct read of `notes-board.tsx` — `notes` prop was populated from either the full board query or a separate `/notes/search` result set, a straight swap.
- **Built:** `NotesPage` now always sources the board from `notesQuery` (respecting archived/project scope); a separate `matchIds` set is derived from the search query and passed to `NotesBoard`, which applies `opacity-30 saturate-50` to non-matching `NoteCard`s rather than omitting them. A non-blocking inline banner appears when a search has zero matches among the currently-displayed notes, rather than replacing the canvas with an empty state. The `?open={id}` scroll-and-highlight effect (Phase 09, Strict-Mode-safe) was preserved unmodified.
- **Verified live:** dimming confirmed via computed `opacity` on rendered `NoteCard` elements (0.3 for non-matches, 1 for the match) with all three notes retaining their real canvas positions; deep-link highlight re-verified working after the change.

### Model Playground — major redesign, one hypothesis confirmed, one rejected on inspection

- **Plan hypothesis A (confirmed):** `ProviderList` (setup/configuration) was always fully expanded above `RunView`, pushing the actual run/comparison workspace down — collapse it into a compact summary.
- **Plan hypothesis B (rejected):** the plan speculated that the side-by-side multi-provider comparison view might not exist yet and could require a new "comparison grid" primitive. **Live inspection found this wrong** — `RunView` already rendered `ResultPanel`s in a `grid md:grid-cols-2 lg:grid-cols-3`, i.e. side-by-side comparison already worked. No new primitive was built; the hypothesis was explicitly discarded rather than implemented anyway.
- **Built:** new `ProviderListSummary` component wraps `ProviderList`, collapsed by default once at least one provider is configured (a one-line "N of M configured" row), forced open when zero providers are configured (since that blocks the primary task entirely). `ProviderList` itself lost its own `Card` wrapper so it renders correctly nested inside the summary's card when expanded.
- **Verified live:** seeded a real credential via the backend API, confirmed the summary collapses correctly; created a real two-target comparison run (`gpt-4o-mini` + `gpt-4o`) and confirmed both results render side-by-side, proving the existing grid does what the screen's own tagline ("Compare LLM provider outputs side by side") claims.
- **Must-not-break, verified:** `ResultPanel` is reused in Project Detail's AI quick-run panel — not modified, so no re-verification risk there.

### Prompt Studio — focused redesign, hypothesis confirmed after direct inspection

- **Plan position going in:** the list-XOR-detail pattern and the documented Phase 09 decision not to use `FilterRail` were expected to be correct and were **not** targeted for structural change.
- **Plan hypothesis (flagged as "observe in source, validate live"):** `VariablesPanel` and `PreviewPanel` both render fully expanded, stacked around the body editor — the actual composition surface — pushing it down and competing for space with setup/checking chrome not always needed.
- **Live inspection:** confirmed. Opened a real prompt with 3 variables ("Bug Triage") at 1440px — Variables occupied roughly the top third of the visible editor, Body was pushed toward the bottom of the fold, and Preview (with its own variable-value inputs) would have been entirely below the fold.
- **Built:** reordered so Body renders first and is always visible; Variables and Preview moved into a `Tabs` strip below the body (reusing the existing shared `Tabs` primitive — no new component). Redundant "Variables"/"Preview" headings inside each panel removed since the tab labels now carry that role.
- **Verified live:** desktop and mobile (375px) both confirmed — Body visible immediately on load, tab switch between Variables/Preview working, variable count shown on the tab trigger.

### Knowledge — focused redesign, hypothesis confirmed

- **Plan hypothesis:** flat, undifferentiated result list makes scanning "just documents" or "just notes" require reading every row's type badge; the note deep-link (`/notes?open={id}`) needed fixing.
- **Live inspection:** the note deep-link fix from Phase 09 T11 was already present in source (confirmed via code comment) — that part of the hypothesis was already resolved before this phase began.
- **Built:** results now group into "Documents"/"Notes" sections with `SectionHeading` labels and counts, but only when the current filter is unfiltered-by-type and both types are actually present in the result set — a single-type filter renders as a flat list, matching the plan's own caution against adding a redundant heading over an already-homogenous list.
- **Verified live:** seeded mixed data (2 documents, 3 notes), confirmed grouping renders correctly; confirmed the note deep-link resolves to `/notes?open={id}` and lands with the scroll-and-highlight behavior intact.

### Projects — major redesign, hypothesis partially confirmed, partially already-shipped

- **Plan hypothesis:** `ProjectCard` needed enriching with per-project content signals (counts, recency), contingent on the API already returning that data (explicitly: no API change permitted).
- **Live inspection:** the `secret_count`/`note_count`/`document_count`/`updated_at` fields **already existed** on `ProjectSummary` and were already rendered — that part of the hypothesis was wrong; no API check was needed, the data was already there.
- **Built:** cards now distinguish empty projects ("Nothing here yet") from active ones, and show relative-time recency (`formatRelativeTime(project.updated_at)`) — the actual remaining gap once the existing count-rendering was accounted for. Separately, Project Detail's `ScopedList` rows (secrets/notes/documents) were found to render as inert non-clickable rows — fixed by adding real `?open={id}` deep links to each row, using the same contract Secrets/Notes/Documents already honor elsewhere.
- **Verified live:** confirmed via the seeded backend API that `secret_count` etc. are returned without any endpoint change; clicked through a Project Detail scoped-list row into a real secret's detail sheet to confirm the new deep link resolves correctly.

### Documents — hypothesis rejected; one real bug found and fixed instead

- **Plan hypothesis:** `FilterRail` (built for filtering-heavy surfaces like Secrets) was semantically mismatched for an authoring screen's document switcher; proposed replacing it with a purpose-built list-only sidebar and moving tag/link controls into an on-demand contextual panel.
- **Live inspection:** rejected. `DocumentSidebar`'s actual content inside `FilterRail` was already list-only (search + project picker + grouped pinned/history list, no filter chrome); the tag/knowledge-link controls were already behind a `Popover`, i.e. already contextual. The screen already achieved the "editorial workspace" composition the plan was proposing to build. Per the plan's own governing principle, the hypothesis was explicitly discarded rather than implemented, since rebuilding `FilterRail`'s already-correct rail/drawer responsive contract in parallel would have been pure duplication for no material gain.
- **Real gap found instead:** the mobile empty-state copy read "pick one from the history on the left," which is meaningless once the list lives behind a drawer trigger below `lg` — there is no "left" on that viewport. Fixed by changing the copy to "pick one from your document list."
- **Verified live:** confirmed at 375px that the corrected copy renders; confirmed (via a control test on the unmodified Secrets screen, which showed the same environment-level Sheet-open timeout) that the drawer-open interaction itself was unaffected by this change.

### Secrets, Search, Converters, Developer Toolkit, Settings, Project Init, Unlock, Setup — verify-only, no redesign

Each was inspected live at 1440px (and, for Secrets/Search, with populated seeded data) against its stated target interaction model. All eight already matched: Secrets is the Phase 09 reference data-surface; Search already groups results by type and its real gap is a navigation/discoverability question already tracked in ADR-0016, not a layout problem; Converters and Developer Toolkit are already dense, scannable instrument grids; Settings is already grouped into reference vs. consequential sections (Phase 09 T21); Project Init is already a clear two-template picker; Unlock and Setup are already correctly minimal single-focus security gates. No changes made to any of the eight — restraint per the plan's own tiering, not a shortfall.

## 4. Cross-cutting fix found outside the original plan

During the final audit pass, a user-reported UI defect (overlapping header icons on the Secrets detail sheet) traced to `SheetContent`'s built-in absolute-positioned close button (`top-3 right-3`, `icon-sm`) colliding with any custom header action row placed in the same corner. All 6 `SheetContent` consumers and all 10 `DialogContent` consumers in the frontend were audited; the same collision existed in exactly one other place (`features/ingest/preview-sheet.tsx`). Both fixed by reserving `pr-12` on the affected header's action row rather than modifying the shared `Sheet`/`Dialog` primitives themselves — a call-site fix, not a primitive-level change, to avoid the app-wide re-verification blast radius a primitive change would require (the same reasoning Phase 09 applied when it left the Dialog/Sheet focus-restore gap as an owner decision rather than touching the primitive — see [`../Phase-09-Frontend-Reimagine/CURRENT_STATE.md`](../Phase-09-Frontend-Reimagine/CURRENT_STATE.md) Known Issue #23).

## 5. What this phase deliberately did not touch

- Phase 09's design tokens, shared component library (`DataList`, `FilterRail`, `Toolbar`, etc.), app shell, or responsive/accessibility baseline.
- The `workbench ↔ notes ↔ projects` panel-registry module cycles (ADR-0002) — extended additively (`column` field), not restructured.
- Any backend route, schema, or API contract.
- The `Sheet`/`Dialog` shared primitives themselves (fixed at the call site, per §4).
