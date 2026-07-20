# ADR-0008 — Everything is a Capability (direction, not yet adopted)

> **Purpose:** Record the long-term direction of generalizing the Panel Registry (ADR-0002) into a unified Capability Registry that panels, pages, commands, workflow nodes, converters, and prompt/project assets all register with — and record, equally deliberately, that this is **not** Phase 01 scope.
> **Scope:** Direction and rationale only. No design in this document is authorized for implementation by any phase yet — see §6.
> **Ownership:** Project owner (proposed 2026-07-20)
> **Status:** Proposed — explicitly not Accepted; do not build against this document
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [ADR-0002](0002-workbench-panel-architecture.md)
> **Supersedes:** —

---

## 1. Context

While reviewing Phase 01's panel architecture ([ADR-0002](0002-workbench-panel-architecture.md)), the project owner observed that Workbench panels, a future command palette ([ADR-0007](0007-search-dedicated-page.md) §6), future workflow nodes, and future project/prompt assets all share the same underlying shape: something registers itself with metadata and becomes discoverable by a host system. Rather than building a separate registry per concern (panel registry, command registry, workflow-node registry, …), the proposal is one **Capability Registry** that all of them register with and consume from.

In the same review, the project owner also asked to freeze Phase 01's scope and stop adding concepts, on the grounds that "every new concept increases the implementation surface and reduces the chance of a clean one-shot build." Building the generalized Capability Registry now — before Phase 01 ships even the narrower Panel Registry, and before any of Pages, Commands, Workflow Nodes, or Project Assets exist to validate the generalization against — would directly contradict that same discipline. This ADR resolves the tension by recording the direction now, while explicitly not authorizing it for Phase 01.

## 2. Decision

The Capability Registry is a **recorded architectural direction**, not a current commitment:

- Phase 01 ships the narrower Panel Registry exactly as specified in [ADR-0002](0002-workbench-panel-architecture.md) and [`../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md`](../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md) — unchanged by this ADR.
- The Capability Registry generalization is revisited once there is a **second real registry-shaped need** actually being built (a strong candidate: whatever backs the command-palette direction noted in [ADR-0007](0007-search-dedicated-page.md) §6, or Phase 02's Project Initialization Engine template registration). Generalizing from one concrete implementation (Panels) plus one more real one is a sound basis for an abstraction; generalizing from zero is speculation.
- When that second need arrives, the phase that needs it drafts a follow-up ADR (or promotes this one to Accepted, revised against real evidence) and a corresponding `forge-docs/architecture/CAPABILITY_REGISTRY.md` design — a first draft of that document exists now (see §5) to capture the shape of the idea, but it is explicitly a **forward-looking sketch**, not a build contract.

## 3. Alternatives considered

- Accept this ADR now and rebuild Phase 01's Panel Registry as a `type: "panel"` capability inside a general registry — rejected for Phase 01: this is exactly the premature abstraction the project owner's own "freeze scope" instruction warns against. `01_PRODUCT_PRINCIPLES.md` (this session's broader engineering guidance, consistent with it) explicitly counsels against designing for hypothetical future requirements over three similar concrete cases.
- Reject the direction outright and keep every future registry (commands, workflow nodes, …) fully separate forever — rejected: the underlying observation (these are structurally the same shape) is sound, and worth capturing now while the insight is fresh, even if execution waits.

## 4. Consequences

- Makes it easier: Phase 01 stays exactly as scoped and specified across `01_SPEC.md` through `08_ACCEPTANCE.md` — no rework of already-accepted `ADR-0002` or `12_PANEL_INTERFACE.md`.
- Makes it easier (later): when a second registry-shaped need arrives, there's already a recorded direction and a sketch document to start from instead of a blank page.
- Makes it harder: nothing yet — this ADR authorizes no implementation work, so it carries no immediate execution cost.
- Risk being tracked: generalizing too early is exactly as costly as generalizing too late is inconvenient; §2's "wait for a second real need" rule is the guardrail against the former.

## 5. What exists today

A first-draft sketch of the registry's shape — philosophy, registration lifecycle, metadata schema, discovery, lazy loading, permissions, feature flags, dependency injection, and future plugin support — lives at [`../architecture/CAPABILITY_REGISTRY.md`](../architecture/CAPABILITY_REGISTRY.md). It is marked `Status: Proposed` for the same reason this ADR is: useful to have written down, not to be treated as ratified.

## 6. TODO

- [ ] TODO: Do not reference this ADR as justification for adding a capability-registry dependency to any phase's `03_BACKEND.md` or `05_COMPONENTS.md` until it is promoted to `Accepted`.
- [ ] TODO: Revisit after Phase 01 ships and Phase 02 (or the command-palette direction in [ADR-0007](0007-search-dedicated-page.md) §6) is being actively designed — that's the trigger condition in §2, not a fixed date.

## 7. Cross-references

- [0002-workbench-panel-architecture.md](0002-workbench-panel-architecture.md)
- [0007-search-dedicated-page.md](0007-search-dedicated-page.md)
- [../architecture/CAPABILITY_REGISTRY.md](../architecture/CAPABILITY_REGISTRY.md)
- [../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md](../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md)
