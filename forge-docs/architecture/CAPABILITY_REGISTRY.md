# Capability Registry (proposed direction)

> **Purpose:** Sketch the shape of a unified Capability Registry — the idea that panels, pages, commands, workflow nodes, converters, and prompt/project assets could all register with one system instead of each growing its own. Written to capture the idea while it's fresh, not to authorize building it.
> **Scope:** Cross-cutting design sketch only. No phase currently implements this — Phase 01 uses the narrower, already-accepted Panel Registry ([ADR-0002](../decisions/0002-workbench-panel-architecture.md), [`../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md`](../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md)) instead.
> **Ownership:** TODO — assign an owner.
> **Status:** Proposed — a sketch backing [ADR-0008](../decisions/0008-capability-registry-direction.md), which is itself `Proposed`, not `Accepted`. Do not treat anything below as a build contract.
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md](../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md), [ADR-0008](../decisions/0008-capability-registry-direction.md)
> **Supersedes:** —

---

## 0. Read this first

This document exists because writing an idea down well is cheap and having it later is valuable — not because the idea is ready to build. Per [ADR-0008](../decisions/0008-capability-registry-direction.md) §2, this generalization is deliberately deferred until a **second real registry-shaped need** exists alongside Phase 01's Panel Registry, so the design below is validated against two concrete cases instead of guessed from one. Everything in this document should be read as "here's roughly the shape, if and when we build it" — not "here's the spec."

## 1. Registry philosophy

The observation: a panel (Workbench content), a command (palette action), a workflow node (a step in a future visual workflow builder), and a converter (a format transformation) all share the same underlying pattern — something with an identity, some metadata describing it, and a way to be invoked or rendered, registered once and discovered by whatever host needs it (Workbench, the command palette, a workflow canvas, a converter picker).

A Capability Registry would be the single place any of these register, so:

- Workbench, Search/command-palette, Projects, and a future Workflow builder all **consume** the same registry instead of each maintaining its own list.
- A feature that wants to be reachable from more than one of those surfaces (e.g. "Generate password" as both a Workbench quick action and a command-palette command) registers once, not once per surface.
- The registry itself stays generic — it has no more knowledge of what a "capability" does than Phase 01's Panel Registry has of what a panel renders (see [`12_PANEL_INTERFACE.md`](../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md) §1 for the precedent this generalizes).

This is explicitly an evolution of, not a replacement for, the reasoning in [ADR-0002](../decisions/0002-workbench-panel-architecture.md) — same philosophy, wider scope.

## 2. Registration lifecycle

Sketch, following the Panel Registry's proven shape:

1. **Registration** — a feature calls `registerCapability({...})` once, at module load, from its own feature folder. No central file lists every capability by name.
2. **Bootstrap** — one bootstrap module imports every capability-registering feature's registration file, same pattern as `12_PANEL_INTERFACE.md` §4's `register-all.ts`.
3. **Discovery** — a host (Workbench, command palette, …) queries the registry for capabilities matching a shape it knows how to render (e.g. "give me everything with a `panel` facet").
4. **Invocation/render** — the host renders the capability's `panel` component, or executes its `command` handler, or renders its `page`, etc. — whichever facet it asked for.
5. **Unregistration** — not expected in normal operation (this is a compile-time registry, not a dynamic plugin system — see §9); a capability disappears only when its owning feature is removed from the build.

## 3. Metadata schema

Sketch, generalizing [`12_PANEL_INTERFACE.md`](../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md) §2's `WorkbenchPanelMetadata`:

```ts
interface Capability {
  id: string;                    // stable, unique — e.g. "prompt-studio"
  title: string;
  description: string;
  icon: LucideIcon;

  // Facets — a capability implements zero or more of these.
  // Optionality matters: "Generate password" might have a `command` and
  // no `page`; "Prompt Studio" might have a `page`, a `panel`, and a
  // `command` ("Open Prompt Studio") but no `workflowNode` until later.
  page?: { route: string; component: React.ComponentType };
  panel?: WorkbenchPanelDefinition;   // reuses the Phase 01 shape as-is
  command?: { run: (context: CapabilityContext) => void | Promise<void> };
  workflowNode?: { /* shape TBD when Workflows is actually designed */ };
}
```

The key design question this sketch does **not** resolve: whether facets are optional fields on one `Capability` object (as above) or the registry indexes several smaller, separately-registered records that share an `id`. Both have precedent in similar systems (VS Code's contribution points lean toward the latter). Left open deliberately — resolving it well requires the second real use case ADR-0008 is waiting for, not a guess now.

## 4. Discovery

Hosts query by facet, not by knowing every `id` in advance — e.g. `getCapabilitiesWithFacet("panel")` for Workbench, `getCapabilitiesWithFacet("command")` for the command palette. This mirrors `getRegisteredPanels()` in [`12_PANEL_INTERFACE.md`](../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md) §4, generalized to filter by facet instead of returning everything.

## 5. Lazy loading

Not addressed by the Panel Registry (Phase 01's five panels are cheap enough to bundle eagerly). A general registry with many more capabilities (converters, workflow nodes, prompt assets) may need registration metadata to be cheap/eager while the actual component/handler is `React.lazy`-loaded on first use. Sketch only — needs real measurement once there's enough registered capability volume to matter.

## 6. Permissions

Same non-RBAC meaning as [`12_PANEL_INTERFACE.md`](../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md) §8: preconditions for meaningful use (e.g. a Model Playground command requiring a configured provider), not user roles — Forge remains single-tenant ([`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) §1.1). A capability with an unmet precondition should degrade honestly (disabled, "needs setup"), never silently disappear.

## 7. Feature flags

Not present anywhere in Forge today (no flag system exists per [`../06_TECH_STACK.md`](../06_TECH_STACK.md)). If the registry grows large enough that shipping-but-hiding a capability becomes a real need (distinct from the "not yet available" pattern Phase 01 already uses for Prompt Studio/Universal Converter pins), that's a separate system to design when it's actually needed — not assumed here.

## 8. Dependency injection

Sketch only: a `command.run(context)` handler likely needs access to things like the router, the query client, or a toast function — a `CapabilityContext` passed at invocation time (not baked into registration) keeps registration itself framework-agnostic and testable. Exact shape TBD against a real command implementation.

## 9. Future plugin support

Explicitly **not** a goal, for the same reason [ADR-0002](../decisions/0002-workbench-panel-architecture.md) §3 rejected dynamic plugin loading for the Panel Registry: Forge is a single-operator, self-hosted tool, and a runtime plugin-loading system is a materially larger security and complexity surface than this project's actual needs justify. "Future plugin support" here means: don't design the registry in a way that makes a *future, separately-decided* plugin system harder than necessary (e.g. keep capability metadata serializable) — not that this document is building toward one.

## 10. TODO

- [ ] TODO: Resolve the open question in §3 once a second real registration need exists.
- [ ] TODO: Revisit this entire document's status per [ADR-0008](../decisions/0008-capability-registry-direction.md) §2's trigger condition before treating any part of it as authoritative.

## 11. Cross-references

- [../decisions/0008-capability-registry-direction.md](../decisions/0008-capability-registry-direction.md)
- [../decisions/0002-workbench-panel-architecture.md](../decisions/0002-workbench-panel-architecture.md)
- [../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md](../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md)
- [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
