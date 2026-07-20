# ADR-0005 — Projects become the primary organizational unit

> **Purpose:** Record Projects' long-term status as Forge's primary organizational concept, and how Workbench's panel architecture accommodates a "Recent Projects" panel before Projects (Phase 06) exists.
> **Scope:** The Projects concept's priority and how Phase 01 defers to it without pulling Phase 06 forward. Not the Projects data model itself — that's Phase 06's own `01_SPEC.md`/`04_DATABASE.md` when written.
> **Ownership:** Project owner (approved 2026-07-20)
> **Status:** Accepted
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [ADR-0002](0002-workbench-panel-architecture.md), [../02_ROADMAP.md](../02_ROADMAP.md)
> **Supersedes:** —

---

## 1. Context

`02_ROADMAP.md` currently sequences Phase 06 (Projects) after Workbench (01) and Project Initialization Engine (02), and `03_ARCHITECTURE.md` §4 has an open question about where "Project" lives in the data model. Separately, Workbench's default panel set was directed to include "Recent Projects" in place of "Recent Secrets" — before Projects exists in any form.

## 2. Decision

Projects are affirmed as Forge's primary organizational unit going forward — the concept every other feature (Notes, Documents, Secrets, future Prompt Studio prompts, Model Playground sessions) is expected to eventually scope into. Workbench's panel architecture (ADR-0002) accommodates this now without requiring Projects to exist yet: a `RecentProjectsPanel` type is defined in the panel catalog (`12_PANEL_INTERFACE.md`, `01_SPEC.md`) but ships **inactive/unregistered** until Phase 06 implements the real Project model and registers the panel — proving the "add a panel, no Workbench changes" extensibility promise on day one of Phase 06 rather than asserting it untested.

## 3. Alternatives considered

- Pull Phase 06 (Projects) earlier, or build a minimal Project table now just to back this panel — rejected for this phase: this drags a later phase's data-model scope into an earlier phase's timeline, the reverse of the dependency discipline [`../09_CLAUDE_CODE_RULES.md`](../09_CLAUDE_CODE_RULES.md) §3 already applies in the other direction ("starting a phase whose dependencies aren't marked complete").
- Ship "Recent Projects" now against fake/stub data — rejected: honest-gaps-over-fake-completeness ([`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) §1.3). A panel showing fabricated projects is exactly the "convincing-looking stub" that principle rules out.

## 4. Consequences

- The Recent Secrets panel is removed from the Phase 01 default catalog now; Recent Projects is documented but not shipped active until Phase 06.
- `02_ROADMAP.md`'s sequencing rationale (§4) should be revisited to confirm Projects' priority reflects this "primary organizational unit" status once Phase 01/02 land — tracked as a TODO there.

## 5. Cross-references

- [../02_ROADMAP.md](../02_ROADMAP.md)
- [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
- [../implementation/Phase-01-Workbench/01_SPEC.md](../implementation/Phase-01-Workbench/01_SPEC.md)
- [../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md](../implementation/Phase-01-Workbench/12_PANEL_INTERFACE.md)
