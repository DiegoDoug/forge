# Workbench — Current State

> **Purpose:** Live snapshot of where this phase actually stands, updated at every checkpoint.
> **Scope:** This phase only — updated continuously, never left stale.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Authorized, not yet started
> **Version:** 0.2.0
> **Last Updated:** 2026-07-20
> **Depends On:** [README.md](README.md), [IMPLEMENT.md](IMPLEMENT.md)
> **Supersedes:** v0.1.0 of this document (pre-authorization)

---


## Current Status

**Authorized, not yet started.** Specification is locked ([ADR-0009](../../decisions/0009-phase-specification-freeze.md)); no implementation code has been written. The next session should begin Milestone 1 (Foundation, T1–T4) per [`IMPLEMENT.md`](IMPLEMENT.md)'s Milestone Plan.

## Completed

- [ ] TODO: nothing completed yet — populate as work lands.

## In Progress

- [ ] TODO: nothing in progress yet.

## Remaining

- [ ] Everything in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) — all 16 tasks across 4 milestones, starting with Milestone 1 / T1 (Vault → Secrets compatibility migration).

## Known Issues

- [ ] TODO: none yet — this section must never be left stale once work begins.

## Architectural Decisions

- [ADR-0001](../../decisions/0001-workbench-replaces-dashboard.md) — Workbench replaces Dashboard.
- [ADR-0002](../../decisions/0002-workbench-panel-architecture.md) — Workbench uses a panel architecture.
- [ADR-0003](../../decisions/0003-workbench-single-row-layout.md) — Single-row persisted layout.
- [ADR-0004](../../decisions/0004-interactive-workflows-not-automation.md) — Interactive workflows, not automation.
- [ADR-0005](../../decisions/0005-projects-primary-organizational-unit.md) — Projects become the primary organizational unit.
- [ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md) — Vault renamed to Secrets.
- [ADR-0007](../../decisions/0007-search-dedicated-page.md) — Search becomes a dedicated Workbench-reachable page.

- [ADR-0009](../../decisions/0009-phase-specification-freeze.md) — Phase Specification Freeze.

All eight are `Status: Accepted` as of 2026-07-20. [ADR-0008](../../decisions/0008-capability-registry-direction.md) (Capability Registry) was also proposed during this phase's planning and deliberately left `Status: Proposed` — not a Phase 01 dependency, revisit later per its own trigger condition. No code has been written against any ADR yet.

## Modified Files

- [ ] TODO: none yet — list every file touched once implementation begins.

## Next Milestone

Milestone 1 — Foundation (T1–T4): Secrets compatibility migration, `/search` page, `workbench_layout` migration, the panel contract. See [`IMPLEMENT.md`](IMPLEMENT.md) "Milestone Plan" and [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md).

## Next Claude Prompt

```
You are working in the Forge repository as a Claude Code session.

Read, in order:
1. forge-docs/09_CLAUDE_CODE_RULES.md
2. forge-docs/implementation/Phase-01-Workbench/README.md
3. forge-docs/implementation/Phase-01-Workbench/CURRENT_STATE.md
4. forge-docs/implementation/Phase-01-Workbench/IMPLEMENT.md

Then begin work on: T1 in 09_IMPLEMENTATION_TASKS.md (Vault → Secrets
compatibility migration), the first task of Milestone 1 — Foundation.

Follow the checkpoint protocol in forge-docs/10_CHECKPOINT_PROTOCOL.md exactly,
plus the milestone checkpoints in IMPLEMENT.md — stop after T4 (end of
Milestone 1) even if the 10-12 task threshold hasn't been hit yet.

The specification is locked per forge-docs/decisions/0009-phase-specification-freeze.md.
Only bug fixes, clarifications, and typo corrections are in scope beyond the
documented tasks — anything else (extra panels, workflows, a command palette,
a capability registry, a Projects interface, a plugin system, AI additions)
gets flagged and deferred, not built.
```

## Session Notes

- 2026-07-20 — Phase scaffold created by the Lead Architect FDK setup. No implementation work has occurred.
- 2026-07-20 — Full spec pass: `01_SPEC.md` through `08_ACCEPTANCE.md` and new `12_PANEL_INTERFACE.md` drafted; ADR-0001 through ADR-0007 recorded and accepted; `README.md` Exit Criteria added. Still no implementation work — every exit-criteria item needs project-owner confirmation before `IMPLEMENT.md` is authorized.
- 2026-07-20 — Scope-freeze pass: Secrets rename refined to a compatibility migration (ADR-0006 v0.2.0); Search's scope confirmed as page-only, with a future command-palette direction recorded but deferred (ADR-0007 §6); Capability Registry direction recorded as ADR-0008, deliberately `Proposed` not `Accepted`; Projects interface confirmed deferred to Phase 06 (ADR-0005 unchanged); Workflows explicitly excluded from this phase. All nine Exit Criteria documents are now content-complete. `09_IMPLEMENTATION_TASKS.md` populated with an ordered 16-task breakdown. `IMPLEMENT.md` remains "Not authorized" pending the project owner's explicit go-ahead.
- 2026-07-20 — **Authorized.** ADR-0009 (Phase Specification Freeze) recorded and accepted. `09_IMPLEMENTATION_TASKS.md` regrouped into 4 content-coherent milestones (Foundation/Backend/Frontend/Integration). `IMPLEMENT.md` updated with the milestone checkpoint plan and the immutable Priority Order rule (Correctness > Existing functionality > Stability > Performance > UX polish > New functionality). `README.md` now carries a Definition of Success and a formal Authorization record. Specification is locked; implementation is approved to begin at T1.

## Cross-references

- [README.md](README.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
- [../../history/README.md](../../history/README.md)
