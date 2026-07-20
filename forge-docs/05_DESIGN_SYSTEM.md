# 05 — Design System

> **Purpose:** Single source of truth for visual tokens — color, typography, spacing, iconography — beneath the interaction guidelines in [04_UI_GUIDELINES.md](04_UI_GUIDELINES.md).
> **Scope:** Token values and their source files. Component-level API documentation lives in each phase's `05_COMPONENTS.md`.
> **Ownership:** TODO — assign a design system owner.
> **Status:** Draft — captures current configuration; full token audit still TODO
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
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
- [ ] TODO: Define semantic color roles (success/warning/danger/info) explicitly — confirm current usage is consistent across Vault, Notes, and Documents status badges.

## 3. Typography

- [ ] TODO: Document the font family/scale in use.
- [ ] TODO: Define heading hierarchy conventions for in-app content vs. documentation (this FDK's own Markdown heading hierarchy is specified in [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md), which is separate from in-app typography).

## 4. Spacing & layout

- [ ] TODO: Document the spacing scale (Tailwind default vs. customized).
- [ ] TODO: Document the app shell's grid/breakpoint system.

## 5. Iconography

- Icon library: `lucide-react`.
- [ ] TODO: Document icon sizing conventions (sidebar vs. inline vs. button icons).

## 6. Component primitives

Base UI + shadcn/ui primitives live in `frontend/components/ui/`. This design system document should track:

- [ ] TODO: Which shadcn primitives are in use vs. available-but-unused.
- [ ] TODO: Any primitives customized beyond the shadcn default (and why).

## 7. Motion

- Dependency: `framer-motion`.
- [ ] TODO: Document standard transition durations/easings (currently ad hoc per component, e.g. the Notes drag animation fix).

## 8. TODO

- [ ] TODO: This document is currently a stub with real configuration facts but no full token table — treat filling it in as a Phase 01 (Workbench) prerequisite since Workbench will be the first surface to stress-test shared layout tokens.

## 9. Cross-references

- [04_UI_GUIDELINES.md](04_UI_GUIDELINES.md)
- [06_TECH_STACK.md](06_TECH_STACK.md)
- [../frontend/components.json](../frontend/components.json)
- [implementation/](implementation/) — each phase's `05_COMPONENTS.md`
