# Prompt Studio — IMPLEMENT

> **Purpose:** The execution contract for this phase — a Claude Code session must read this in full before writing any code for this phase.
> **Scope:** This phase only. Inherits from, and never overrides, the repo-wide rules in ../../09_CLAUDE_CODE_RULES.md.
> **Ownership:** Lead Software Engineer (phase-assigned).
> **Status:** Authorized — the project owner approved `01_SPEC.md` through `08_ACCEPTANCE.md` in full on 2026-07-22, including the `${variable}` syntax, the 20,000-char/50-variable limits, and an added rendering-determinism constraint (`01_SPEC.md` §3.16). Stage 2 (Technical Planning, [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md)) is authorized to proceed; Stage 3 (Implementation) proceeds milestone-by-milestone once that plan exists, under the quality gates below — no separate per-milestone re-authorization is required unless a milestone needs to deviate from the plan.
> **Last Updated:** 2026-07-22

---

## Role

You are implementing the **Prompt Studio** phase of the Forge Development Kit, acting as the engineer of record for this phase. You are bound by [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) at all times; this document adds phase-specific detail only.

## Mission

Provide a workspace for authoring, structuring, and versioning reusable LLM prompts with typed variables and a client-side render preview.

**Resolved scope note (read this before touching Phase 05 or any provider/network code):** the "shares LLM-provider plumbing with Phase 05" question that `02_ROADMAP.md` §4 and `03_ARCHITECTURE.md` §3–4 originally flagged as open is **resolved** — this phase introduces zero outbound network calls and zero provider/API-key concepts. See [`01_SPEC.md`](01_SPEC.md) §4–§5 and [`CURRENT_STATE.md`](CURRENT_STATE.md) Session Notes for the full record of that decision. Do not reopen it inside this phase's implementation; if it needs revisiting, that's a new conversation with the project owner and a real ADR, not an in-flight scope change.

## Execution Rules

- [ ] Do not begin any task in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) until it is populated with the real milestone plan (Stage 2 output) — this file's tasks are the actual execution contract; do not implement ahead of what's written there.
- [ ] Follow [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) exactly — thin routers, `api.ts` as the only endpoint-shape-aware file, no cross-feature imports.
- [ ] Follow the exact substitution/placeholder rule documented once in [`03_BACKEND.md`](03_BACKEND.md) §2.1 — do not invent a different templating syntax or reach for a new templating library; `string.Template` (backend) and its hand-written TS mirror (frontend, `templating.ts`) are the whole of this phase's templating implementation.
- [ ] Enforce the rendering-determinism constraint (`01_SPEC.md` §3.16) as a hard rule during code review of `templating.py`/`templating.ts`: substitution, escaping, validation — nothing else, ever.
- [ ] Per the project owner's Stage 2 authorization: milestones are 3–5 independently buildable, independently testable tasks each; tests must be green before advancing to the next milestone; no production code outside this specification; no feature creep; no provider execution; no new dependencies.
- [ ] Update [`CURRENT_STATE.md`](CURRENT_STATE.md) as work progresses, not only at checkpoints.

## Autonomy Rules

Inherits [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3 in full. Phase-specific additions:

- [ ] Always ask before adding any outbound network call, provider SDK, or API-key/secret-reference concept to this phase's scope — this is the one boundary the specification session resolved explicitly and the project owner re-confirmed at sign-off (§Mission above), and it is exactly the kind of decision [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §3 requires asking about, not assuming, if it ever seems tempting mid-implementation (e.g. "just add one Test Run button").
- [ ] Always ask before introducing a new templating dependency (e.g. Jinja2) — `${variable}`/`string.Template` was explicitly approved over `{{variable}}` at sign-off, with no second syntax to be supported.
- [ ] Always ask before adding any capability to the renderer beyond substitution/escaping/validation — the determinism constraint in `01_SPEC.md` §3.16 is a project-owner requirement, not a default assumption to relax under implementation pressure.

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
