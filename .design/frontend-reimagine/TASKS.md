# Build Tasks: Forge Frontend Reimagine

Generated from: `.design/frontend-reimagine/DESIGN_BRIEF.md`
Also reads: `INFORMATION_ARCHITECTURE.md`, `DESIGN_TOKENS.css`
Date: 2026-08-06
Produced by the `brief-to-tasks` skill (julianoczkowski/designer-skills)

> **This list is the design-side view.** Its FDK counterpart —
> `forge-docs/implementation/Phase-09-Frontend-Reimagine/09_IMPLEMENTATION_TASKS.md`
> — carries the same T-numbers plus per-task acceptance criteria and the
> preserve-this-behavior contract each task must not break. The two are kept
> in sync; where they disagree, the FDK document wins.
>
> **Nothing here is authorized to start.** Phase 09 is at *Specification* in the
> lifecycle. See `IMPLEMENT.md`.

Ordering follows the skill's three rules: dependencies first (tokens and shell
before any screen), visual priority early (the shell and one data surface land
before the long tail, so the direction can be judged on real screens), and risk
first — **T1 is both the riskiest and the most foundational**, because it is a
global CSS change that touches all 40 primitives at once.

---

## Foundation — Milestone 1

- [ ] **T1 · Design tokens + typography fix**: Merge `DESIGN_TOKENS.css` into `frontend/app/globals.css` as the three-layer system, preserving every existing shadcn token name. Fixes the self-referential `--font-sans` and the class-scoped `--font-mono` so the app renders in Geist instead of Times New Roman. Adds the type ramp, spacing scale, status roles, motion tokens, elevation, shell/density constants, and the `prefers-reduced-motion` block. **Establishes the Rams + Swiss direction — this is the task that sets the aesthetic.** _Modifies: `app/globals.css`, `app/layout.tsx`. Reuses: the entire existing shadcn semantic layer._
- [ ] **T2 · Application shell**: Turn the three loose components composed inline in `app/(app)/layout.tsx` into a real shell owning the layout grid, `--shell-topbar-h`, and scroll containment. Retires both `h-[calc(100dvh-3.5rem)]` hacks and the `calc(100dvh - 7.5rem)` in the Notes board. _New component: `components/app-shell/app-shell.tsx`. Modifies: `app/(app)/layout.tsx`._
- [ ] **T3 · Grouped navigation**: Add group metadata to `lib/nav-registry.ts` (Workspace / Library / Build / Tools, plus Settings as pinned utility) and render sidebar and mobile drawer from that one source, ending the duplicated render loop with divergent active-state classes. _Modifies: `lib/nav-registry.ts`, `components/app-shell/sidebar.tsx`, `components/app-shell/mobile-nav.tsx`._
- [ ] **T4 · Command palette**: Implement the `NAV_ITEMS[].shortcut` letters that are displayed today but wired to nothing. Add the "View all results" affordance into `/search?q=`. Restyle to tokens. _Modifies: `components/command-palette/command-palette-provider.tsx`. Preserves: the `?open=<id>` deep-link contract exactly._
- [ ] **T5 · Primitive retune**: Bring the 40 `components/ui/*` primitives onto the type ramp, spacing scale, radius, focus ring, and elevation rules. **Every export name and prop signature is preserved** — this is a visual retune, not an API change. Decide `table` / `avatar` / `context-menu` / `alert` (currently installed and unused): adopt `table` for data surfaces or remove all four. _Modifies: `components/ui/*`._
- [ ] **T6 · Shared app components**: `PageHeader` v2 (breadcrumb slot, sticky, overflow-menu action collapse), `EmptyState` retune, and new `ErrorState`, `SearchField`, `ConfirmDialog`, `Toolbar`, `SectionHeading`, `StatusBadge`, `Field`, `KeyValueRow`. Each replaces a pattern the audit found duplicated 4–7 times. _New + modifies: `components/`._
- [ ] **T7 · Data surface components**: `DataList` / `DataListRow` — the Swiss-register component that replaces seven independent `rounded-xl border border-border` + hand-rolled-row implementations. Plus `FilterRail`, owning the rail-at-`lg` / drawer-below contract that Secrets' `w-56` and Documents' `w-72` rails lack entirely. Covers: default, hover, focus, selected, loading, empty, error rows. _New components._
- [ ] **T8 · Feedback system**: One skeleton vocabulary that matches the shape of what it replaces (no layout shift), one toast treatment, and `panel-error-boundary` generalized so a failed region never blanks the page around it. _Modifies: `components/ui/skeleton.tsx`, `components/ui/sonner.tsx`, `features/workbench/components/panel-error-boundary.tsx`._

## Core UI — Milestone 2 (primary surfaces)

Chosen by audit evidence, not assumption: the Workbench is the landing route, Secrets is the largest feature by endpoint count (13) and the densest list, Knowledge Hub is the newest and most data-dense, Documents is the most structurally broken at mobile.

- [ ] **T9 · Workbench** `/`: Panel grid, panel cards, customize mode, pinned tools, quick actions, recent activity, system status. Preserves drag-reorder, keyboard reorder, the optimistic layout mutation, and the unregistered-panel-type survival rule. _Depends on: T2, T5, T7, T8._
- [ ] **T10 · Secrets** `/secrets`: List → `DataList`; folder/tag rail → `FilterRail`; detail sheet and form dialog retuned. **The reference implementation of the Swiss data surface** — judge the direction here. Covers: loading, empty, populated, error, filtered-empty. _Depends on: T6, T7._
- [ ] **T11 · Knowledge Hub** `/knowledge`: Filter bar, result rows with type/tags/project legible without hover, truncation notice as a first-class element. Copy clarified so `?q=` reads as a filter within the Hub, not global search. Preserves all four URL filters. _Depends on: T6, T7._
- [ ] **T12 · Documents** `/documents`: Adopt `PageHeader`, convert the fixed `w-72` rail to `FilterRail`, implement the master–detail responsive pattern (Prompt Studio is the reference), group the toolbar by consequence. Preserves debounced autosave, export, pin, tags, and links. _Depends on: T2, T6, T7._
- [ ] **T13 · Search results** `/search`: Bring onto `DataList`; add palette linkage; keep the full secrets + notes + documents scope. Includes the `next.config.ts` rewrite for `/system/status`, which currently 404s. _Depends on: T4, T7._

## Core UI — Milestone 3 (secondary surfaces)

- [ ] **T14 · Notes** `/notes`: Board, note card, drag/resize, Markdown rendering, color picker. Board keeps horizontal pan at mobile rather than reflowing. Preserves `@dnd-kit` keyboard fallbacks. _Depends on: T6._
- [ ] **T15 · Projects** `/projects` + `/projects/[id]`: Project cards, scoped lists → `DataList`, AI config + quick run column, breadcrumb in the topbar. Preserves archive/unarchive and unscope-on-delete. _Depends on: T6, T7._
- [ ] **T16 · Prompt Studio** `/prompt-studio`: Rail → `FilterRail`, adopt `PageHeader`, retune editor/variables/preview/version-history. Its existing responsive behavior is the pattern others adopt — preserve it. _Depends on: T6, T7._
- [ ] **T17 · Model Playground** `/model-playground`: Provider list, credential dialog, prompt composer, result panel, run history → `DataList`. Preserves credential handling exactly (ADR-0011). _Depends on: T6, T7._
- [ ] **T18 · Converter** `/converters`: Nine tool cards + document dropzone + job list. Section structure made legible. Preserves the polling `refetchInterval` and the `/ingest` redirect. _Depends on: T6, T7._
- [ ] **T19 · Developer Toolkit** `/developer-toolkit`: 16 tools across three tabs plus nested crypto tabs. Preserves the `?tab=` external contract that three retired routes redirect into. _Depends on: T6._
- [ ] **T20 · Project Init** `/project-init`: Kind picker, the two forms, file preview, generation history → `DataList` with confirmation on delete. _Depends on: T6, T7._
- [ ] **T21 · Settings** `/settings`: Four cards regrouped by consequence, master-password and destructive-import treatments separated. Verifies the T13 `/system/status` fix end to end. _Depends on: T6._
- [ ] **T22 · Auth screens** `/setup`, `/unlock`: The only unauthenticated surfaces and the first thing a new user sees. Restyle to tokens; `AuthGate` redirect logic untouched. _Depends on: T1, T5._

## Interactions & States — Milestone 4 (consolidation)

- [ ] **T23 · Destructive-action uniformity**: Route every delete in the app through `ConfirmDialog`. Closes the audit finding that Documents, Notes, and Project-Init generations delete silently while Secrets, Prompts, Providers, and Runs confirm. Covers: trigger, confirm, cancel, in-flight, success, failure. _Depends on: T6, and every screen task._
- [ ] **T24 · State-coverage sweep**: Verify every list-bearing surface has a real loading, empty, filtered-empty, error, and populated state, per `04_UI_GUIDELINES.md §5`. Fill the gaps found. _Depends on: Milestones 2–3._
- [ ] **T25 · Dead-code removal**: Remove superseded layouts, duplicated inline patterns, and any primitive left unused after T5. Resolve `framer-motion` — a declared dependency with **zero import sites** — by adopting it for the minimal motion this philosophy permits, or removing it. Nothing new is installed either way. _Depends on: Milestones 2–3._

## Responsive & Polish — Milestone 5 (validation)

- [ ] **T26 · Responsive validation**: All 15 routes at **375 / 768 / 1024 / 1440**. Confirm the behavior changes, not just size changes: rails become drawers, master–detail becomes single-pane, header actions become overflow menus, touch targets reach 44px. _Breakpoints: all four._
- [ ] **T27 · Accessibility pass**: Contrast measured against the budget in `DESIGN_TOKENS.css` in **both** themes; accessible names on all 38 icon-only buttons (only 3 have one today); focus order and restoration in every dialog, sheet, and drawer; landmarks and heading order; `prefers-reduced-motion` verified; keyboard reachability of the Notes board and Workbench reorder.
- [ ] **T28 · Regression validation**: Every route resolves; all five compatibility redirects still land correctly; deep links (`?open=`, `?tab=`, `?q=`, `?project_id=`, `?new=`) behave identically to the pre-phase baseline; `npx tsc --noEmit`, `npm run lint`, and `npm run build` all pass; backend test suite unchanged and green.
- [ ] **T29 · Documentation finalization**: Bring `CURRENT_STATE.md`, `10_RELEASE_NOTES.md`, and `08_ACCEPTANCE.md` to match what actually shipped. Update `forge-docs/04_UI_GUIDELINES.md` and `05_DESIGN_SYSTEM.md`, whose token/contrast/motion sections this phase converts from TODO into fact.

## Review

- [ ] **T30 · Design review**: Run `/design-review` against `DESIGN_BRIEF.md` at all four breakpoints in both themes. Specifically hunt the brief's anti-references — visual drift, one-off styles, excessive cards, decorative rounding, gradients, "AI-generated UI" repetition — and iterate on findings.
