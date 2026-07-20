# Workbench — Acceptance Criteria

> **Purpose:** The pass/fail checklist that decides whether this phase is complete — the authoritative list referenced by 08_DEFINITION_OF_DONE.md.
> **Scope:** This phase only. Each criterion must be independently verifiable.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — second full pass (panel architecture + performance/accessibility/extensibility), pending confirmation
> **Version:** 0.3.0
> **Last Updated:** 2026-07-20
> **Depends On:** [01_SPEC.md](01_SPEC.md), [02_UI.md](02_UI.md), [07_TESTING.md](07_TESTING.md), [12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md), [../../decisions/0006-vault-renamed-to-secrets.md](../../decisions/0006-vault-renamed-to-secrets.md), [../../decisions/0008-capability-registry-direction.md](../../decisions/0008-capability-registry-direction.md)
> **Supersedes:** v0.2.0 of this document (no explicit scope-freeze guard against ADR-0008/Projects/Workflows creeping into the implementation)

---

## 1. Functional acceptance criteria

One criterion per functional requirement in [`01_SPEC.md`](01_SPEC.md) §3:

- [ ] The home route (`/`) renders the Workbench panel grid; "Dashboard" does not exist anywhere in the app. (FR1, FR12)
- [ ] Workbench renders any registered + visible panel with no fixed enum inside Workbench's own code. (FR2)
- [ ] Five active panels ship (Pinned Tools, Recent Activity, Quick Actions, Storage & System, Recent Notes); Recent Projects is defined but renders nothing (no active panel registered); Recent Secrets does not exist in any form. (FR3)
- [ ] Each registered panel can be independently shown/hidden, and the change persists. (FR4)
- [ ] Visible panels can be reordered, and the order persists. (FR5)
- [ ] Any tool from `nav-registry.ts`, plus the forward-looking `prompt_studio`/`universal_converter` entries, can be pinned/unpinned and reordered. (FR6)
- [ ] Panel visibility, panel order, and pinned tools all persist server-side and survive reload, logout/unlock, and access from a different browser. (FR7)
- [ ] "Reset to default layout" restores the shipped default in one action. (FR8)
- [ ] A fresh instance renders the shipped default: 5 panels visible in order, 6 pinned tools (Ingest, Notes, Prompt Studio, Universal Converter, Secrets, Search), with Prompt Studio/Universal Converter shown disabled. (FR9)
- [ ] Recent Activity, Storage & System, and Recent Notes panels show data identical in content/shape to the former Dashboard's equivalents. (FR10)
- [ ] Quick Actions offers working shortcuts for: new note, new secret, generate password. (FR11)
- [ ] The "Secrets" pinned tool resolves to a real, working `/secrets` route, **and** the legacy `/vault` route/`/api/vault` endpoint still resolve as working aliases rather than 404ing (i.e. the Vault → Secrets compatibility migration has landed, per [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md)). (FR13)
- [ ] The "Search" pinned tool resolves to a real, working `/search` page showing the same results the command palette shows. (FR14)
- [ ] A test panel can be added by a developer using only: a new component + a `registerWorkbenchPanel()` call + a bootstrap import — with zero other file changes inside `frontend/features/workbench/`. (FR15 — see also §6 Extensibility.)

## 2. UX acceptance criteria

Derived from [`02_UI.md`](02_UI.md):

- [ ] Every active panel defines and correctly renders its empty, loading, and error states.
- [ ] The all-panels-hidden empty state renders instead of a blank page.
- [ ] Customize mode's drag reordering has a working keyboard-only fallback.
- [ ] The reset action requires an explicit confirmation step.
- [ ] Pin/unpin failures roll back optimistically with a toast.
- [ ] Disabled ("coming soon") pinned tools are visually distinct and inert — no dead-link click-through to a 404.
- [ ] Desktop grid and mobile single-column layouts both work correctly, including `/search`.
- [ ] Light and dark mode both render correctly for every panel, the pin picker, and `/search`.

## 3. Quality acceptance criteria

- [ ] All tests in [`07_TESTING.md`](07_TESTING.md) pass, including the panel-type-not-enum-validated test and the `recent_secrets`-absence regression check.
- [ ] No architectural invariant violated (per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2).
- [ ] `frontend/features/dashboard/` is fully removed with no dangling references.
- [ ] [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) feature-level checklist satisfied.

## 4. Performance acceptance criteria

- [ ] Initial Workbench render completes in **under 1 second** on a local Docker Compose deployment (cold load through fully painted panel grid).
- [ ] Drag-reorder interaction sustains **60 FPS** with no visible jank (measured per [`07_TESTING.md`](07_TESTING.md) §3).
- [ ] `PUT /api/workbench/layout` round-trips in **under 200 ms** on a local deployment.
- [ ] No unnecessary re-renders occur during a drag interaction — the React DevTools Profiler shows only the dragged panel and its immediate neighbors re-rendering, not the full grid, not unrelated panels' own data-fetching hooks re-firing.

## 5. Accessibility acceptance criteria

- [ ] Full keyboard navigation reaches and operates every interactive element in view mode, customize mode, and the pin picker.
- [ ] Keyboard-only drag-and-drop reordering works (arrow-key reorder while a panel is focused).
- [ ] Focus management is correct: entering/exiting customize mode and opening/closing the pin picker moves focus to a sensible element and returns it to the trigger on close.
- [ ] Every icon-only or ambiguous control has a correct ARIA label (visibility toggle, drag handle, reset button, pin/unpin toggle).
- [ ] Screen-reader pass (VoiceOver or NVDA spot check, or an equivalent automated tool) confirms panel titles, states ("Hidden," "Coming soon," loading/error states), and controls are announced correctly.
- [ ] An automated accessibility scan (axe or equivalent) against Workbench (both modes) and `/search` reports no critical/serious violations.

## 6. Extensibility acceptance criteria

- [ ] A developer can add a new panel to Workbench by: (1) creating a component implementing `WorkbenchPanelProps`, (2) registering it with `registerWorkbenchPanel(...)` and its metadata, (3) adding one import line to the bootstrap list — **and nothing else**. No file inside `frontend/features/workbench/` beyond the bootstrap import list changes; no backend change is required unless the new panel needs its own new data (which is the owning feature's concern, not Workbench's).
- [ ] This is demonstrated concretely before the phase is marked complete — e.g. by implementing one of the five active panels genuinely through the registry (not special-cased in `WorkbenchGrid`), which every panel in §1 already requires by construction.

## 7. ADR acceptance criteria

- [ ] ADR-0001 through ADR-0007 (`../../decisions/0001-*.md` through `0007-*.md`) are all `Status: Accepted`.
- [ ] ADR-0008 (Capability Registry) remains `Status: Proposed` — the implementation introduces **no** generalized capability registry, no `ProjectProvider`/`ProjectContext`, and no Workflow-related code. If any of these appear in the implementation, that's a scope violation of the project owner's explicit freeze, not a bonus.
- [ ] Every ADR's "Consequences" section that names a required prerequisite task (notably ADR-0006's Vault → Secrets compatibility migration) has a corresponding entry in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) before implementation begins.

## 8. Sign-off

- [ ] TODO: who signs off on this phase being complete? (Recommendation: whoever is assigned phase ownership in [`README.md`](README.md), once assigned.)

## 9. TODO

- [ ] TODO: Re-check this list against [`01_SPEC.md`](01_SPEC.md) §6's open questions once resolved.
- [ ] TODO: Confirm the exact axe/accessibility tooling referenced in §5 before implementation, since no frontend test runner exists yet to automate it in CI.

## 10. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [07_TESTING.md](07_TESTING.md)
- [12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md)
- [README.md](README.md) — Definition of Complete / Exit Criteria
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
- [../../decisions/README.md](../../decisions/README.md)
