# 05 — Design System

> **Purpose:** Single source of truth for visual tokens — color, typography, spacing, iconography — beneath the interaction guidelines in [04_UI_GUIDELINES.md](04_UI_GUIDELINES.md).
> **Scope:** Token values and their source files. Component-level API documentation lives in each phase's `05_COMPONENTS.md`.
> **Ownership:** TODO — assign a design system owner.
> **Status:** Draft — captures current configuration. Phase 09 (2026-08-06) converted several long-standing TODOs into fact (typography, spacing/breakpoints, primitive inventory, motion) — see §3–4, §6–7. A full color-palette table (§2) remains outstanding.
> **Version:** 0.2.0
> **Last Updated:** 2026-08-06
> **Depends On:** [04_UI_GUIDELINES.md](04_UI_GUIDELINES.md)
> **Supersedes:** —

---

## 1. Current configuration

Source of truth: [`frontend/components.json`](../frontend/components.json) and [`frontend/app/globals.css`](../frontend/app/globals.css).

| Token | Current value |
|---|---|
| shadcn/ui style | `base-nova` |
| Base color | `neutral` |
| CSS variables | enabled |
| Icon library | `lucide` |
| RTL support | disabled |
| Tailwind version | v4 (`@tailwindcss/postcss`) |

## 2. Color

- [ ] TODO: Document the full light/dark palette (CSS custom properties in `globals.css`) as a table here — currently only living in CSS.
- [x] **Semantic color roles defined and consistent: Phase 09, T1/T5.** `frontend/app/globals.css` now implements a three-layer token architecture (Foundation → Semantic → Structural, [ADR-0017](decisions/0017-layered-design-token-architecture.md)) with explicit status roles, used consistently via the shared `StatusBadge` component (T6) across every list-bearing surface (Secrets, Notes, Documents, Model Playground, Converter, Project Init). **Minimum contrast standard:** WCAG 2.1 AA in both themes, measured and enforced in Phase 09 T27 (see [04_UI_GUIDELINES.md](04_UI_GUIDELINES.md) §4).

## 3. Typography

- [x] **Font family/scale documented: Phase 09, T0.5a/T1/T5.** Typeface is **Geist Sans** (body/UI) and **Geist Mono** (code/monospace values), both already bundled pre-phase — fixed to actually apply (a self-referential `--font-sans` had resolved empty since the project began, rendering everything in Times New Roman) and wired into Tailwind's `text-xs`–`text-4xl` utility scale via `@theme inline` in `frontend/app/globals.css` (previously the scale existed as CSS variables but was never connected to the utilities that reference it). Three Swiss-influenced typographic utilities layer on top for data-dense surfaces: `.label-structural`, `.data-primary`, `.data-meta` ([`implementation/Phase-09-Frontend-Reimagine/02_UI.md`](implementation/Phase-09-Frontend-Reimagine/02_UI.md)).
- [ ] TODO: Define heading hierarchy conventions for in-app content vs. documentation (this FDK's own Markdown heading hierarchy is specified in [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md), which is separate from in-app typography).

## 4. Spacing & layout

- [x] **Spacing scale and app-shell grid/breakpoints documented: Phase 09.** Twelve layout invariants frozen in [`implementation/Phase-09-Frontend-Reimagine/02_UI.md`](implementation/Phase-09-Frontend-Reimagine/02_UI.md) §0: spacing steps, the four responsive breakpoints (375/768/1024/1440px), the three rail widths, topbar height, row heights (40px desktop / 48px touch), touch targets (≥44×44px below `md`), prose measure, form width, the four dialog tiers, the three control heights, and a no-shadows-outside-overlays rule. One `AppShell` (T2) owns the layout grid and `--shell-topbar-h`; all three prior hardcoded `calc(100dvh...)` viewport hacks were removed.

## 5. Iconography

- Icon library: `lucide-react`.
- [ ] TODO: Document icon sizing conventions (sidebar vs. inline vs. button icons).

## 6. Component primitives

Base UI + shadcn/ui primitives live in `frontend/components/ui/`. This design system document should track:

- [x] **Primitive inventory current as of Phase 09, T25.** `table`, `avatar`, `context-menu`, and `alert` were installed but unused; `table` was adopted for the app's genuinely tabular surfaces (see below), and the other three were removed after confirming zero consumers via a scripted sweep. Every remaining primitive in `frontend/components/ui/` is in active use.
- [x] **Primitives customized beyond the shadcn default: Phase 09, T5.** All primitive shadows now route through the token layer's `--elevation-2`/`--elevation-3` (5 overlay primitives affected); sizing/spacing use the wired `--font-size-*`/spacing tokens rather than component-local values. No `components/ui/*` export name or prop signature changed — customization was internal styling only ([`implementation/Phase-09-Frontend-Reimagine/05_COMPONENTS.md`](implementation/Phase-09-Frontend-Reimagine/05_COMPONENTS.md) has the full per-primitive record). Eight new shared *app-level* components (not shadcn primitives, but sitting at the same layer conceptually) were added on top: `DataList`/`DataListRow`, `FilterRail`, `ConfirmDialog`, `ErrorState`, `SearchField`, `StatusBadge`, `SectionHeading`, `Toolbar`, `Field`, `KeyValueRow`.

## 7. Motion

- ~~Dependency: `framer-motion`~~ **Removed, Phase 09 T25** — zero import sites existed anywhere in the codebase; confirmed via a scripted sweep before removal. All current motion (dialog/sheet open-close, hover states, drag) runs on Base UI's built-in `data-open`/`data-closed` CSS-animation state attributes and Tailwind transition utilities.
- [ ] TODO: Document standard transition durations/easings. Motion tokens exist in the Phase 09 token layer (`globals.css`), but a durations/easings reference table has not been written here.

## 8. TODO

- [x] ~~This document is currently a stub... treat filling it in as a Phase 01 (Workbench) prerequisite~~ — stale; Phase 01 shipped long ago. Phase 09 (2026-08-06) converted most of the remaining structural TODOs into fact (§3–4, §6–7). What's left: the full color-palette table (§2), heading-hierarchy conventions (§3), icon-sizing conventions (§5), and a transition-durations/easings reference (§7) — all documentation-transcription tasks, not implementation gaps.

## 9. Cross-references

- [04_UI_GUIDELINES.md](04_UI_GUIDELINES.md)
- [06_TECH_STACK.md](06_TECH_STACK.md)
- [../frontend/components.json](../frontend/components.json)
- [implementation/](implementation/) — each phase's `05_COMPONENTS.md`
