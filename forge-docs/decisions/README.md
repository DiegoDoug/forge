# Architecture Decision Records (ADRs)

> **Purpose:** Durable record of every architectural exception, blocking decision, or cross-cutting choice made during FDK-driven development — the things [09_CLAUDE_CODE_RULES.md](../09_CLAUDE_CODE_RULES.md) requires stopping for.
> **Scope:** Decisions that affect architecture, principles, or cross-phase behavior. Day-to-day implementation choices belong in a phase's own docs, not here.
> **Ownership:** TODO — assign an owner (recommended: whoever owns [03_ARCHITECTURE.md](../03_ARCHITECTURE.md)).
> **Status:** Active — 9 decisions recorded (8 accepted, 1 proposed)
> **Version:** 0.4.0
> **Last Updated:** 2026-07-20
> **Depends On:** [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md), [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
> **Supersedes:** —

---

## 1. When to add an ADR

Add one whenever:

- A choice violates or extends a principle in [`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md).
- A choice changes an architectural invariant in [`../03_ARCHITECTURE.md`](../03_ARCHITECTURE.md) §2.
- [09_CLAUDE_CODE_RULES.md](../09_CLAUDE_CODE_RULES.md) §6 triggers a "blocking architectural decision requires approval" checkpoint.
- A new external dependency category is introduced (per [`../06_TECH_STACK.md`](../06_TECH_STACK.md) §4).

## 2. How to add one

1. Copy [`ADR_TEMPLATE.md`](ADR_TEMPLATE.md) to `NNNN-short-title.md` in this folder, where `NNNN` is the next zero-padded sequence number (start at `0001`).
2. Fill it in completely — an ADR with unresolved TODOs is not yet decided.
3. Link it from the phase or root doc that prompted it.
4. Add a row to the index table below.

## 3. Index

| # | Title | Status | Date |
|---|-------|--------|------|
| [0001](0001-workbench-replaces-dashboard.md) | Workbench replaces Dashboard | Accepted | 2026-07-20 |
| [0002](0002-workbench-panel-architecture.md) | Workbench uses a panel architecture | Accepted | 2026-07-20 |
| [0003](0003-workbench-single-row-layout.md) | Single-row persisted layout | Accepted | 2026-07-20 |
| [0004](0004-interactive-workflows-not-automation.md) | Interactive workflows, not automation | Accepted | 2026-07-20 |
| [0005](0005-projects-primary-organizational-unit.md) | Projects become the primary organizational unit | Accepted | 2026-07-20 |
| [0006](0006-vault-renamed-to-secrets.md) | Vault renamed to Secrets, as a compatibility migration | Accepted | 2026-07-20 |
| [0007](0007-search-dedicated-page.md) | Search becomes a dedicated Workbench-reachable page | Accepted | 2026-07-20 |
| [0008](0008-capability-registry-direction.md) | Everything is a Capability (direction, not yet adopted) | **Proposed** | 2026-07-20 |
| [0009](0009-phase-specification-freeze.md) | Phase Specification Freeze | Accepted | 2026-07-20 |

## 4. TODO

- [ ] TODO: ADR-0006 (Vault → Secrets) and ADR-0004 (interactive workflows) record decisions whose consequences reach beyond Phase 01 — fold ADR-0004 into [`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) as a numbered principle, and confirm ADR-0006's actual code rename is tracked in [`../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md`](../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md) before Phase 01 implementation begins.
- [ ] TODO: ADR-0008 is intentionally left `Proposed`, not `Accepted` — do not promote it without a phase that actually needs a second registry to generalize against (see ADR-0008 §2 for the trigger condition). No Phase 01 document should depend on it being accepted.

## 5. Cross-references

- [ADR_TEMPLATE.md](ADR_TEMPLATE.md)
- [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
- [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
- [../09_CLAUDE_CODE_RULES.md](../09_CLAUDE_CODE_RULES.md)
- [../../docs/DecisionLog.md](../../docs/DecisionLog.md) — the equivalent log for decisions already made in the shipped application
