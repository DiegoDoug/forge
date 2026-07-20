# Universal Converter — README

> **Purpose:** Entry point for the Universal Converter phase — objective, scope, deliverables, and completion criteria.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — template scaffold, not yet filled in
> **Last Updated:** 2026-07-20

---


## Objective

Unify the existing Converters and Ingest feature areas into one universal format-conversion surface spanning text formats (JSON/YAML/XML/CSV/Markdown) and document formats (Office/PDF/images).

## Scope

**In scope:**
- [ ] TODO: enumerate the concrete capabilities this phase delivers.

**Out of scope:**
- [ ] TODO: enumerate explicitly excluded capabilities (link them to a future phase or `../../02_ROADMAP.md` if deferred rather than dropped).

## Relationship to the shipped application

Consolidates the existing **Converters** (`frontend/features/converters`, `backend/app/converters`) and **Ingest** (`frontend/features/ingest`, `backend/app/ingest`) feature areas.

> **TODO:** This relationship is the Lead Architect's proposal, not a ratified decision — confirm before [`01_SPEC.md`](01_SPEC.md) is finalized.

- Related frontend: `frontend/features/converters/, frontend/features/ingest/`
- Related backend: `backend/app/converters/, backend/app/ingest/`

## Deliverables

- [ ] TODO: list concrete deliverables (a shipped page, an API surface, a migration, etc.)

## Dependencies

None hard — a consolidation of shipped features, can proceed independently.

- [ ] TODO: confirm dependency status before authorizing `IMPLEMENT.md` for this phase (see [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3).

## Milestones

- [ ] Milestone 1 — TODO: name and define
- [ ] Milestone 2 — TODO: name and define
- [ ] Milestone 3 — TODO: name and define

> Each milestone completion is a checkpoint trigger — see [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1.

## Risks

- [ ] TODO: enumerate technical risks
- [ ] TODO: enumerate product/UX risks
- [ ] TODO: enumerate risks to existing features this phase touches or consolidates

## Definition of Complete

- [ ] All deliverables above are shipped and meet [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md).
- [ ] [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criteria are fully checked off.
- [ ] [`CURRENT_STATE.md`](CURRENT_STATE.md) reflects reality with no stale "In Progress" items.
- [ ] A final checkpoint has been produced per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md).

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [01_SPEC.md](01_SPEC.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
