# Architecture Decision Records (ADRs)

> **Purpose:** Durable record of every architectural exception, blocking decision, or cross-cutting choice made during FDK-driven development — the things [09_CLAUDE_CODE_RULES.md](../09_CLAUDE_CODE_RULES.md) requires stopping for.
> **Scope:** Decisions that affect architecture, principles, or cross-phase behavior. Day-to-day implementation choices belong in a phase's own docs, not here.
> **Ownership:** TODO — assign an owner (recommended: whoever owns [03_ARCHITECTURE.md](../03_ARCHITECTURE.md)).
> **Status:** Empty — no decisions recorded yet
> **Last Updated:** 2026-07-20

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
| _(none yet)_ | | | |

> No decisions have been recorded yet — this repository has not diverged from the principles and architecture set out in [`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) and [`../03_ARCHITECTURE.md`](../03_ARCHITECTURE.md).

## 4. TODO

- [ ] TODO: Record the first ADR when Phase 01 or 02 surfaces its first blocking decision (candidates already flagged in [`../03_ARCHITECTURE.md`](../03_ARCHITECTURE.md) §4 — e.g. where "Project" data lives).

## 5. Cross-references

- [ADR_TEMPLATE.md](ADR_TEMPLATE.md)
- [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
- [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
- [../09_CLAUDE_CODE_RULES.md](../09_CLAUDE_CODE_RULES.md)
- [../../docs/DecisionLog.md](../../docs/DecisionLog.md) — the equivalent log for decisions already made in the shipped application
