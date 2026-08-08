# Frontend Reimagine — Specification

> **Purpose:** What Phase 09 delivers, stated as testable requirements.
> **Scope:** This phase only.
> **Ownership:** TODO — assign a phase owner.
> **Status:** **Approved 2026-08-06** (see [`IMPLEMENT.md`](IMPLEMENT.md)); **fully implemented and RC-verified 2026-08-07** — see [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) for criterion-by-criterion evidence.
> **Version:** 0.2.0
> **Last Updated:** 2026-08-07
> **Depends On:** [00_AUDIT.md](00_AUDIT.md)

---

## 1. Summary

Forge has eight phases of shipped, working functionality presented through an interface that never received a system pass. The audit found a coherent color palette and a sound data architecture sitting underneath: no type scale, no spacing scale, no motion or status tokens, seven copies of the same list container, six copies of the same search input, three surfaces that delete without asking, two rails that are unusable below 1024px, one orphaned route, eight advertised keyboard shortcuts bound to nothing — and, verified at runtime, **an application that renders entirely in Times New Roman** because `--font-sans` was declared as a self-reference.

Phase 09 fixes the presentation layer, in place, without touching what the product does.

## 2. User stories

- As a developer opening Forge for the first time, I can tell within seconds what kind of tool this is and where my content lives versus where my tools live.
- As a returning user, I find every capability exactly where I left it — no route moved, no feature disappeared, no bookmark broke.
- As someone managing dozens of secrets, I can scan a list quickly because rows have real typographic hierarchy, not because they have more padding.
- As someone reaching for search, there is one obvious way to do it, and it finds secrets as well as notes and documents.
- As a keyboard user, the shortcuts the interface advertises actually work, and I can reach every action without a pointer.
- As a phone user, Secrets and Documents are usable, not a 90-pixel sliver next to a rail that will not collapse.
- As anyone about to delete something, Forge asks — and it asks the same way every time.
- As a user with reduced-motion or contrast needs, the interface respects both, in either theme.

## 3. Functional requirements

Each is testable and traced to an acceptance criterion in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md).

**FR1 — Token system.** A three-layer token system (foundation → semantic → structural) exists in `frontend/app/globals.css` per [ADR-0017](../../decisions/0017-layered-design-token-architecture.md). Every shadcn token name currently in `globals.css` is preserved verbatim. New categories are added: type ramp, spacing scale, status roles, motion, elevation, shell and density constants.

**FR2 — Typography renders.** `--font-sans` and `--font-mono` resolve to the bundled Geist and Geist Mono families. Verified by computed style on `<html>` and `<body>`, not by inspection. No new font dependency is added.

**FR3 — Application shell.** One shell component owns the layout grid, the topbar height (`--shell-topbar-h`), and scroll containment. No page recomputes shell geometry; all three hardcoded viewport calcs are removed.

**FR4 — Grouped navigation.** The sidebar presents four labelled groups — Workspace, Library, Build, Tools — with Settings pinned below a divider as utility navigation. Rail and mobile drawer render from the same source. `NAV_ITEMS` gains group metadata **additively**; no existing field is removed or renamed.

**FR5 — Search model.** Each of the three search surfaces has one stated job, per [ADR-0016](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md). `/search` gains a command-palette entry and a "View all results" path from the palette. **`/search` retains its full secrets + notes + documents scope; Knowledge Hub retains its notes + documents scope.** Neither surface's backend query changes.

**FR6 — Keyboard accelerators.** The eight `NAV_ITEMS[].shortcut` letters already rendered by the palette are bound as palette-scoped accelerators. ⌘K/Ctrl-K continues to toggle the palette from any route.

**FR7 — Primitive retune.** All 40 `components/ui/*` primitives consume the token system. Every export name and prop signature is unchanged — a consumer must not need editing because a primitive was retuned.

**FR8 — Shared component set.** The patterns the audit found duplicated 4–7 times exist once: `DataList`/`DataListRow`, `FilterRail`, `SearchField`, `ErrorState`, `ConfirmDialog`, `Toolbar`, `SectionHeading`, `StatusBadge`, `Field`, `KeyValueRow`, plus `PageHeader` v2 and a retuned `EmptyState`.

**FR9 — Route coverage.** All 17 routes are migrated. Each defines and implements loading, empty, filtered-empty, populated, and error states where applicable, per [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §5.

**FR10 — Behavior preservation.** Every route, route parameter, redirect, deep link, mutation, optimistic update, polling interval, autosave debounce, and redirect-on-auth behavior is identical to the pre-phase baseline. The full contract list is enumerated in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §3.

**FR11 — Responsive behavior.** All 17 routes are usable at 375, 768, 1024, and 1440px. Filter rails become drawers below `lg`; master–detail becomes single-pane below `lg`; page-header actions collapse past two; touch targets reach 44px at mobile. This is behavior change, not scaling.

**FR12 — Destructive-action uniformity.** Every delete in the application routes through one confirmation treatment that names the object and states what is lost. Closes the three silent deletes in Documents, Notes, and Project Init.

**FR13 — Accessibility baseline.** WCAG 2.1 AA contrast in both themes, measured against the budget in `DESIGN_TOKENS.css`. Every icon-only control has an accessible name. Focus is visible, trapped in overlays, and restored to the trigger. A `prefers-reduced-motion` block exists. Landmarks and heading order are correct.

**FR14 — `/system/status` reachable.** A `next.config.ts` rewrite makes the existing endpoint reachable so the Settings storage readout renders. **No backend change.**

**FR15 — Consolidation.** No superseded layout, duplicated inline pattern, unused primitive, or unused dependency remains at phase end without a documented reason.

## 4. Non-functional requirements

- **NFR1** — `npx tsc --noEmit`, `npm run lint`, and `npm run build` pass at every checkpoint, not only at phase end.
- **NFR2** — No new runtime dependency is added. `framer-motion` is either used or removed.
- **NFR3** — No parallel frontend. No second shell, second router, duplicate API client, or parallel page directory. Any temporary parallel implementation must be documented with its removal boundary at the moment it is created.
- **NFR4** — No temporary or fake data is introduced to make a screen look complete.
- **NFR5** — Bundle size does not regress materially; the font fix must not add a network request (Geist is already downloaded).

## 5. Explicitly out of scope

Restating [`README.md`](README.md)'s out-of-scope list as spec text, because this is the section a future session will check when tempted:

- Backend code, endpoints, schemas, migrations, and the database.
- New product capabilities, screens, panels, or tools.
- Route deletion. `/search` is **not** retired — see §6.1.
- The auth/session model, the query layer, and the `api.ts` boundary.
- Pagination.
- A frontend test framework.
- New dependencies.
- Reopening frozen phase specifications.

Anything discovered in these areas becomes a documented finding in `CURRENT_STATE.md` → Known Issues, not an in-flight edit.

## 6. Resolved questions

### 6.1 Is `/search` superseded by Knowledge Hub? — **No. Verified.**

The Phase 09 brief proposed retiring `/search` by redirecting it into Knowledge Hub. Direct inspection settled it against the proposal:

- `backend/app/services/search/service.py` → `secrets_service.list_secrets` + `notes_service.search_notes` + `documents_service.search_documents`.
- `backend/app/services/knowledge/service.py` → `notes_service.search_notes` + `documents_service.search_documents` only, per [ADR-0015](../../decisions/0015-knowledge-hub-reuses-fts5.md).

Knowledge Hub covers strictly less. Redirecting would have removed secret search — a user-visible functionality regression. **Rejected.** The adopted resolution gives each surface one job without changing any scope: [ADR-0016](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md).

### 6.2 Which aesthetic philosophy? — **Dieter Rams base + Swiss on data surfaces.**

Confirmed by the project owner, 2026-08-06. Rams governs shell, forms, dialogs, and tool cards; Swiss typographic treatment governs the seven data-dense surfaces. The seam is bounded to two typographic registers defined in `DESIGN_TOKENS.css` so it cannot spread into a second design system. Rationale in [`DESIGN_BRIEF.md`](../../../.design/frontend-reimagine/DESIGN_BRIEF.md).

### 6.3 New typeface, or fix the existing one? — **Fix the existing one.**

Confirmed by the project owner, 2026-08-06. The `frontend-design` skill recommends introducing a distinctive display/body pairing; Forge deviates deliberately because it is self-hosted, LAN-first, and frequently offline, and because Geist/Geist Mono are already bundled and self-hosted by `next/font`. The deviation is recorded in `DESIGN_BRIEF.md` and `DESIGN_TOKENS.css`.

### 6.4 How much of the surface migrates this phase? — **All 17 routes.**

Confirmed by the project owner, 2026-08-06. A partial migration would leave Forge visibly two-toned, which is the exact failure mode this phase exists to eliminate.

### 6.5 Do the two verified defects belong to this phase? — **Yes, both.**

The typography defect (🔴) and the `/system/status` 404 (🟡) both live in shipped-foundation frontend code. Per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) §4 a frozen phase's directory still accepts BLOCKER fixes, and neither defect sits in a frozen phase's directory — `globals.css` and `next.config.ts` are shared frontend infrastructure. Both fixes are frontend-only. Fixing typography is inseparable from the token task.

### 6.6 Does grouping the sidebar break the Workbench tool catalog? — **Not if done additively.**

`features/workbench/tool-metadata.ts` derives from `NAV_ITEMS` via a manually-synced `NAV_KEY_BY_HREF` map, and the backend keeps its own `WORKBENCH_TOOL_KEYS`. This seam caused Phase 08's BLOCKER (`BUG-0001`). T3 therefore adds a `group` field **additively** and changes no `href`, `title`, or `icon` on which the map depends; T3's acceptance criterion re-verifies the Workbench catalog explicitly.

## 7. Open questions — all resolved 2026-08-06

All four were resolved in the project owner's discovery-checkpoint review, in favour of the recommended answers.

- [x] **OQ1 — Roadmap ratification. → Ratified.** Phase 09's row in [`../../02_ROADMAP.md`](../../02_ROADMAP.md) §3 is confirmed.
- [x] **OQ2 — `table` primitive. → Adopt for tabular surfaces; remove the other three.** `DataList` is built on semantic `<table>` markup for the genuinely tabular surfaces (Secrets, run history, generation history) and on `<ul>` for the non-tabular ones (Knowledge results, project scoped lists). `avatar`, `context-menu`, and `alert` are removed in T25.
- [x] **OQ3 — `framer-motion`. → Remove it.** A declared dependency with zero import sites. Under a philosophy permitting motion only on state change, CSS transitions plus `tw-animate-css` are sufficient. Removed in T25.
- [x] **OQ4 — `VERIFICATION_CONTRACT.md`. → Scope it to the objectively checkable subset.** Typecheck, lint, build, route resolution, redirect behavior, deep-link parameters, the 48 navigation edges in [`11_SCREEN_GRAPH.md`](11_SCREEN_GRAPH.md) §7, and computed-style assertions for the font fix. Visual and accessibility criteria route to `/design-review` and QA tickets instead, rather than being asserted by a verifier that cannot actually see them.

### 7.1 Revisions requested at the same review, and applied

- **The two verified defects were elevated into their own pre-design step (T0.5).** The owner's reasoning, which is sharper than the original plan's: every spacing, density, truncation, and sizing judgement in Forge's history was made while the app rendered in the wrong typeface, so the correct type metrics must be in place *before* any design decision is taken — not merged in alongside the token work. **T0.6** was added as a consequence: T0's screenshots are in Times New Roman and are a historical record, not a reference to design against.
- **A screen dependency graph was added** as a required pre-implementation artifact: [`11_SCREEN_GRAPH.md`](11_SCREEN_GRAPH.md). It changed three conclusions — it corrected an over-generous claim in [`00_AUDIT.md`](00_AUDIT.md) §8 about cross-feature isolation, surfaced two module cycles that constrain migration order, and found a new 🟢 MINOR defect (Knowledge Hub cannot deep-link to a note). It also raised T28's regression surface from 17 routes to 48 navigation edges.

## 8. Cross-references

- [00_AUDIT.md](00_AUDIT.md) · [02_UI.md](02_UI.md) · [05_COMPONENTS.md](05_COMPONENTS.md) · [08_ACCEPTANCE.md](08_ACCEPTANCE.md) · [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md](../../decisions/0016-grouped-navigation-and-search-surface-consolidation.md)
- [../../decisions/0017-layered-design-token-architecture.md](../../decisions/0017-layered-design-token-architecture.md)
- [`.design/frontend-reimagine/DESIGN_BRIEF.md`](../../../.design/frontend-reimagine/DESIGN_BRIEF.md)
