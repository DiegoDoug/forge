# 04 — UI Guidelines

> **Purpose:** Define how Forge should look, behave, and feel from a user's perspective, independent of visual token values (see [05_DESIGN_SYSTEM.md](05_DESIGN_SYSTEM.md) for those).
> **Scope:** Interaction patterns, layout conventions, accessibility, and responsive behavior across the app shell and all features.
> **Ownership:** TODO — assign a UI/UX owner.
> **Status:** Draft
> **Version:** 0.2.0
> **Last Updated:** 2026-08-06 (Phase 09 converted three TODOs into fact — see §3–4)
> **Depends On:** [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md)
> **Supersedes:** —

---

## 1. Current UI foundation

- **Framework:** Next.js App Router, React 19, TypeScript.
- **Component base:** shadcn/ui on Base UI primitives (`components.json` style: `base-nova`, base color `neutral`, icon library `lucide`).
- **Theming:** `next-themes` — light/dark mode must be supported by every new surface.
- **Global navigation:** persistent app shell (sidebar + topbar + mobile nav) plus a command palette (`cmdk`, ⌘K) that must be able to reach every feature and, ideally, deep-link into specific tool states.
- **Layout areas:** `app/(auth)/` (no shell, unauthenticated) vs. `app/(app)/` (full shell, behind `AuthGate`).

## 2. Interaction principles

- [ ] Every feature page is reachable from the sidebar **and** the command palette.
- [ ] Destructive actions (delete secret, delete note, purge history) require a confirmation step — no silent deletes.
- [ ] Long-running operations (Ingest conversion, future Model Playground calls) show progress, not a frozen UI.
- [ ] Forms use `react-hook-form` + `zod` validation with inline error messages, not alert dialogs.
- [ ] Drag interactions (Notes board) use `@dnd-kit` with keyboard-accessible fallbacks — never mouse-only.
- [ ] Copy-to-clipboard actions (secrets, generated values, hashes) give explicit visual confirmation.

## 3. Responsive behavior

- [x] Every feature must be usable at mobile widths (mobile nav exists for this reason). **Minimum supported viewport width: 375px** — frozen as a layout invariant in Phase 09 ([`implementation/Phase-09-Frontend-Reimagine/02_UI.md`](implementation/Phase-09-Frontend-Reimagine/02_UI.md) §0, I-invariants) and verified across all 17 routes, both themes ([`implementation/Phase-09-Frontend-Reimagine/09_IMPLEMENTATION_TASKS.md`](implementation/Phase-09-Frontend-Reimagine/09_IMPLEMENTATION_TASKS.md) T26).
- [ ] Data-dense views (Vault tables, future Knowledge Hub search results) need an explicit mobile layout, not just a squeezed desktop table.

## 4. Accessibility

- [ ] Keyboard navigation must reach every interactive element, including the command palette and drag-and-drop board.
- [ ] Color is never the only signal (e.g. status badges pair color with text/icon).
- [x] **Baseline accessibility audit run: Phase 09, T27** ([`implementation/Phase-09-Frontend-Reimagine/09_IMPLEMENTATION_TASKS.md`](implementation/Phase-09-Frontend-Reimagine/09_IMPLEMENTATION_TASKS.md) T27) — Forge's first. Found and fixed one WCAG contrast failure, 16 icon-only/swatch controls with no accessible name, and a sidebar landmark/grouping gap. **Caveat, carried forward as a TODO rather than closed:** no automated `axe`-core (or equivalent) tool exists in this project's toolchain yet; T27 substituted live-measured contrast checking plus a manual `aria-label`/landmark sweep. TODO: adopt an actual `axe` integration once a frontend test framework exists (see [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md) and Phase 09's `CURRENT_STATE.md` Known Issue #2).
- [x] **Minimum contrast standard defined: WCAG 2.1 AA** (4.5:1 normal text, 3:1 large text/≥18px or ≥14px bold), both themes — set and measured against in Phase 09 T27.

## 5. Empty, loading, and error states

Every list-based feature (Vault, Notes, future Knowledge Hub, Model Playground history) must define, explicitly, in its phase's `02_UI.md`:

- [ ] What the zero-items empty state looks like (with a clear first action, not just blank space).
- [ ] What the loading skeleton looks like (TanStack Query `isLoading` state).
- [ ] What an error state looks like, and whether it's retryable inline.

## 6. TODO

- [ ] TODO: Produce a written interaction-pattern reference with real screenshots once Phase 01 (Workbench) lands.
- [ ] TODO: Decide on a motion/animation policy. **Correction (Phase 09, T25):** Framer Motion is no longer a dependency — it had zero import sites and was removed. All current motion (dialog/sheet open-close, hover, drag) runs on Base UI's built-in CSS-animation state attributes and Tailwind transition utilities, driven by the token layer's motion tokens ([`implementation/Phase-09-Frontend-Reimagine/09_IMPLEMENTATION_TASKS.md`](implementation/Phase-09-Frontend-Reimagine/09_IMPLEMENTATION_TASKS.md) T1/T25). The policy question itself (when animation is appropriate vs. gratuitous) remains open.

## 7. Cross-references

- [05_DESIGN_SYSTEM.md](05_DESIGN_SYSTEM.md) — tokens, color, typography
- [06_TECH_STACK.md](06_TECH_STACK.md) — frontend dependency list
- [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md) — UI review gate before a feature is "done"
- [implementation/](implementation/) — each phase's `02_UI.md`
