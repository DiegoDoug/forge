# ADR-0002 — Workbench uses a panel architecture

> **Purpose:** Record that Workbench renders panels conforming to a shared interface, not a fixed enum of hardcoded widget types.
> **Scope:** The extensibility model for Workbench content. The interface itself is specified in 12_PANEL_INTERFACE.md.
> **Ownership:** Project owner (approved 2026-07-20)
> **Status:** Accepted
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [ADR-0001](0001-workbench-replaces-dashboard.md)
> **Supersedes:** The `WidgetType` fixed-enum model in the original Phase 01 draft

---

## 1. Context

The initial Phase 01 draft modeled Workbench content as a fixed `WidgetType` enum (six hardcoded values), with backend validation and frontend rendering both switching on that enum. This does not scale: every future phase that wants Workbench presence (Prompt Studio, Model Playground, Projects, Knowledge Hub) would need to extend Workbench's own enum, validation list, and rendering switch — coupling Workbench's code to every future phase's implementation timeline, the opposite of feature isolation ([`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) §1.5).

## 2. Decision

Workbench is a runtime that renders **panels**. A panel is any component implementing the `WorkbenchPanel` interface (defined in `12_PANEL_INTERFACE.md`) and registered with a panel registry. Workbench itself has no knowledge of what a panel is *for* — it only knows how to lay out, persist visibility/order for, and render anything conforming to the interface. Adding a new panel never requires a change inside the Workbench runtime.

## 3. Alternatives considered

- Keep the fixed-enum widget model, extending it per phase as needed — rejected: couples Workbench's code to every future phase; violates [`../07_CODING_STANDARDS.md`](../07_CODING_STANDARDS.md) §1's feature-isolation rule in spirit even though Workbench itself isn't a "feature" in the strictest sense.
- A dynamic plugin/marketplace-style loading system — rejected as over-engineering for a single-operator, single-deployment app. A compile-time registry (panels imported and registered once, at build time) gives the same extensibility without runtime plugin-loading complexity or its security surface.

## 4. Consequences

- Makes it easier: future phases (03, 05, 06, 07) add Workbench presence by implementing the interface and registering a panel — no Workbench runtime change, satisfying the extensibility acceptance criterion in `08_ACCEPTANCE.md`.
- Makes it harder: panel behavior must fit one common contract. A panel with fundamentally unusual needs (e.g. a full-bleed canvas) may strain the interface — this is a documented design constraint in `12_PANEL_INTERFACE.md`, not an escape hatch to bypass it.
- Touches every Phase 01 doc: `01_SPEC.md`, `02_UI.md`, `03_BACKEND.md`, `04_DATABASE.md`, `05_COMPONENTS.md`, `06_API.md` — "widget" terminology and the `WidgetType` enum are replaced with the panel registry model throughout.

## 5. Cross-references

- [../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md](../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md)
- [../implementation/Phase-01-Workbench/05_COMPONENTS.md](../implementation/Phase-01-Workbench/05_COMPONENTS.md)
- [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
