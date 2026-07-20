# Architecture (forward-looking sketches)

> **Purpose:** Home for architecture-level design sketches that are one step more developed than a research idea but not yet an accepted ADR or a phase's own contract — a place to think out loud about system shape without implying it's authorized.
> **Scope:** Cross-cutting architectural direction, not tied to a single phase. Ratified, current architecture lives in [`../03_ARCHITECTURE.md`](../03_ARCHITECTURE.md); a specific phase's own technical design lives in its `implementation/Phase-XX-*/03_BACKEND.md` etc.
> **Ownership:** TODO — assign an owner.
> **Status:** Active
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
> **Supersedes:** —

---

## 1. Why this folder exists, and how it differs from `research/`

[`../research/`](../research/README.md) holds raw ideas and evidence-gathering (competitors, benchmarks, unscoped ideas). This folder holds documents one step further along: a specific proposed architecture, written in enough detail that a future phase could pick it up and build from it — but explicitly not yet accepted or authorized. The signal that separates a document here from a document in `../03_ARCHITECTURE.md` is the same signal an ADR uses: `Status: Proposed` means "designed, not decided"; `Status: Accepted` (which promotes it out of this folder, or into `../03_ARCHITECTURE.md` proper) means a phase can build against it.

**Never build implementation against a `Proposed` document in this folder.** If a phase's spec needs to depend on one, that dependency itself is a signal the underlying ADR needs to move to `Accepted` first — see [`../decisions/README.md`](../decisions/README.md).

## 2. Contents

| Document | Status | Backing ADR |
|---|---|---|
| [CAPABILITY_REGISTRY.md](CAPABILITY_REGISTRY.md) | Proposed | [ADR-0008](../decisions/0008-capability-registry-direction.md) |

## 3. TODO

- [ ] TODO: When a document here is promoted (its backing ADR moves to `Accepted`), decide whether it stays in this folder or graduates into a numbered root doc / phase doc — case by case, not a fixed rule yet.

## 4. Cross-references

- [../README.md](../README.md)
- [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
- [../decisions/README.md](../decisions/README.md)
- [../research/README.md](../research/README.md)
