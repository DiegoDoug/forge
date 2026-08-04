# Knowledge Hub — IMPLEMENT

> **Purpose:** The execution contract for this phase — a Claude Code session must read this in full before writing any code for this phase.
> **Scope:** This phase only. Inherits from, and never overrides, the repo-wide rules in ../../09_CLAUDE_CODE_RULES.md.
> **Ownership:** Project owner (scope decisions confirmed 2026-08-04; §7's four open questions resolved 2026-08-04)
> **Status:** Not authorized — the specification is complete and `01_SPEC.md` §7's four open questions are resolved ([ADR-0015](../../decisions/0015-knowledge-hub-reuses-fts5.md) accepted; pagination, result cap, and tag semantics all ratified), but owner sign-off per `08_ACCEPTANCE.md` §5 is still outstanding — the sole remaining blocker
> **Last Updated:** 2026-08-04

---


## Role

You are implementing the **Knowledge Hub** phase of the Forge Development Kit, acting as the engineer of record for this phase. You are bound by [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) at all times; this document adds phase-specific detail only.

## Mission

Unify Notes, Documents, and Ingest output into a single searchable knowledge base with consistent tagging, linking, and full-text search.

**Unifies access to** the existing **Notes** and **Documents** (both FTS5-indexed, via `notes_fts` / `documents_fts`) and **Ingest** output — it does not rewrite them. "Consolidates" in the roadmap means one place to browse, search, tag, and link, not one merged data model. See [`01_SPEC.md`](01_SPEC.md) §6.1.

The existing **Search** feature (`/search`, `GET /api/search`, ⌘K) is **not** part of this phase's scope and must be left byte-for-byte unchanged, per [ADR-0007](../../decisions/0007-search-dedicated-page.md) and [`01_SPEC.md`](01_SPEC.md) FR21.

## Execution Rules

- [ ] Do not begin any task in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) until the remaining blocker in its §3 (owner sign-off per [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §5) is cleared. The specification is complete and all four §7 questions are resolved; authorization is not. This phase is **not yet authorized**.
- [ ] The four decisions in [`01_SPEC.md`](01_SPEC.md) §6.6–§6.8 (result cap = 100 fixed, no pagination, AND-only tag filter) and §6.4/[ADR-0015](../../decisions/0015-knowledge-hub-reuses-fts5.md) (extend FTS5) are **final, not implementation-time choices.** Do not reopen them, add an OR mode, add pagination, or make the cap configurable without a new decision record.
- [ ] Follow [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) exactly — thin routers, `api.ts` as the only endpoint-shape-aware file, no cross-feature imports.
- [ ] Update [`CURRENT_STATE.md`](CURRENT_STATE.md) as work progresses, not only at checkpoints.

## Autonomy Rules

Inherits [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3 in full. Phase-specific additions:

- [ ] **Ask before touching `/search`, `GET /api/search`, `services/search/`, or the command palette.** They are out of scope and protected by ADR-0007; any change is a new decision, not an implementation detail.
- [ ] **Ask before modifying `secret_tag_links` or any Secrets code.** This phase shares the `tags` table but must not alter Secrets' side of it ([`01_SPEC.md`](01_SPEC.md) FR13, §6.3).
- [ ] **Ask before adding any external dependency** — this phase is specified to need none (`05_COMPONENTS.md` §2, `03_BACKEND.md` §4). A dependency requirement means the design was wrong, which is a checkpoint, not a quiet `npm install`.
- [ ] **Ask before introducing a frontend test framework.** Its absence is a known, documented condition ([`07_TESTING.md`](07_TESTING.md) §0), and adopting one is cross-cutting infrastructure work outside this phase.
- [ ] **Never modify `tools/fdk_verification/`, `tools/tests/`, or any frozen phase folder** (Phase 01–06). This phase has no reason to touch them; `08_ACCEPTANCE.md` AC35–AC36 verify it did not.
- [ ] **Ask before adding pagination, a configurable `limit`, or an OR tag-filter mode.** All three were explicitly considered and rejected (`01_SPEC.md` §6.6–§6.8). "It would be a nicer UX" is not sufficient grounds to reopen a ratified decision mid-implementation.
- [ ] This phase makes **zero outbound network calls** and stores no credential material. Anything that would change that is a stop-and-ask.

## Quality Gates

Every task must clear [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) task-level checklist before being marked complete in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md).

## Testing Rules

Follow [`07_TESTING.md`](07_TESTING.md) in full. No task is complete with failing or skipped tests.

## Checkpoint Rules

Follow [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) exactly:

- [ ] Checkpoint after every 10–12 completed tasks.
- [ ] Checkpoint at ~70% context usage.
- [ ] Checkpoint at every milestone completion (see [`README.md`](README.md) Milestones).
- [ ] Checkpoint immediately on any blocking architectural decision — draft it with [`../../decisions/ADR_TEMPLATE.md`](../../decisions/ADR_TEMPLATE.md) and stop for approval.
- [ ] Log every checkpoint to [`../../history/`](../../history/README.md).

## Definition of Done

This phase is done when [`README.md`](README.md) §"Definition of Complete" is fully satisfied.

## Stop Criteria

Stop immediately and do not proceed on assumption when:

- [ ] A checkpoint trigger from [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1 is hit.
- [ ] A task has no corresponding filled-in spec section.
- [ ] A decision would violate a principle in [`../../01_PRODUCT_PRINCIPLES.md`](../../01_PRODUCT_PRINCIPLES.md) or an invariant in [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2.
- [ ] Any global session safety rule (destructive git ops, external communication, credentials) would otherwise be triggered.

## Resume Criteria

A fresh session may resume this phase once it has read, in order: [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md), this file, [`CURRENT_STATE.md`](CURRENT_STATE.md), and the most recent entry in [`../../history/README.md`](../../history/README.md) if one exists.

## Cross-references

- [README.md](README.md)
- [01_SPEC.md](01_SPEC.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
