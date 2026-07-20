# 04 — UI Guidelines

> **Purpose:** Define how Forge should look, behave, and feel from a user's perspective, independent of visual token values (see [05_DESIGN_SYSTEM.md](05_DESIGN_SYSTEM.md) for those).
> **Scope:** Interaction patterns, layout conventions, accessibility, and responsive behavior across the app shell and all features.
> **Ownership:** TODO — assign a UI/UX owner.
> **Status:** Draft
> **Last Updated:** 2026-07-20

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

- [ ] Every feature must be usable at mobile widths (mobile nav exists for this reason) — TODO: define the minimum supported viewport width.
- [ ] Data-dense views (Vault tables, future Knowledge Hub search results) need an explicit mobile layout, not just a squeezed desktop table.

## 4. Accessibility

- [ ] Keyboard navigation must reach every interactive element, including the command palette and drag-and-drop board.
- [ ] Color is never the only signal (e.g. status badges pair color with text/icon).
- [ ] TODO: Run and document a baseline accessibility audit (axe or equivalent) — none exists yet.
- [ ] TODO: Define a minimum contrast standard (WCAG AA vs AA+) explicitly rather than by convention.

## 5. Empty, loading, and error states

Every list-based feature (Vault, Notes, future Knowledge Hub, Model Playground history) must define, explicitly, in its phase's `02_UI.md`:

- [ ] What the zero-items empty state looks like (with a clear first action, not just blank space).
- [ ] What the loading skeleton looks like (TanStack Query `isLoading` state).
- [ ] What an error state looks like, and whether it's retryable inline.

## 6. TODO

- [ ] TODO: Produce a written interaction-pattern reference with real screenshots once Phase 01 (Workbench) lands.
- [ ] TODO: Decide on a motion/animation policy (Framer Motion is a dependency already — when is animation appropriate vs. gratuitous?).

## 7. Cross-references

- [05_DESIGN_SYSTEM.md](05_DESIGN_SYSTEM.md) — tokens, color, typography
- [06_TECH_STACK.md](06_TECH_STACK.md) — frontend dependency list
- [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md) — UI review gate before a feature is "done"
- [implementation/](implementation/) — each phase's `02_UI.md`
