# Developer Toolkit — README

> **Purpose:** Entry point for the Developer Toolkit phase — objective, scope, deliverables, and completion criteria.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Specification — **approved in principle by the project owner 2026-08-05**, all [`01_SPEC.md`](01_SPEC.md) §7 open questions resolved and three requested corrections applied. **Not yet authorized for implementation** — explicit authorization is a separate step, see [`IMPLEMENT.md`](IMPLEMENT.md).
> **Last Updated:** 2026-08-05

---


## Objective

Consolidate Generators, Crypto, and Utilities under one unified Developer Toolkit page and navigation entry, without changing any of their underlying service logic.

## Scope

**In scope:**
- [ ] One unified page at `/developer-toolkit` (slug confirmed 2026-08-05) with three tabs — Generators, Crypto, Utilities — each rendering today's existing page content unmodified.
- [ ] One nav-registry entry replacing the current three ("Generators", "Crypto", "Utilities").
- [ ] Redirects from `/generators`, `/crypto`, `/utilities` to `/developer-toolkit?tab=<name>` so existing bookmarks/links keep working.
- [ ] A merge of `backend/app/services/workbench.py`'s three existing `WORKBENCH_TOOL_KEYS` entries into one, and the matching frontend `tool-metadata.ts` update.

**Out of scope:**
- [ ] Any change to Generators or Crypto service/route/schema logic (see [`03_BACKEND.md`](03_BACKEND.md)).
- [ ] A new Utilities backend service — investigated directly; none is needed (see [`01_SPEC.md`](01_SPEC.md) §6).
- [ ] Any new backend abstraction analogous to Universal Converter's `ConverterProvider` — no forward-looking need for one exists here (see [`01_SPEC.md`](01_SPEC.md) §1).
- [ ] Any database migration (see [`04_DATABASE.md`](04_DATABASE.md)).
- [ ] Command-palette deep-linking into a specific tool's pre-filled state, and a standalone "Hash Compare" tool — both are real, already-tracked gaps in [`../../../docs/Roadmap.md`](../../../docs/Roadmap.md), deferred to a future phase, not delivered here.

## Relationship to the shipped application

Consolidates the existing **Generators**, **Crypto**, and **Utilities** feature areas, at the presentation and navigation layer only. Neither feature's underlying logic is rewritten.

- Related frontend: `frontend/features/generators/`, `frontend/features/crypto/`, `frontend/features/utilities/`
- Related backend: `backend/app/services/generators/`, `backend/app/services/crypto/` (Utilities has no backend component — confirmed by direct inspection, see [`01_SPEC.md`](01_SPEC.md) §6)

## Deliverables

- [ ] Unified `/developer-toolkit` page (Generators / Crypto / Utilities tabs) — see [`02_UI.md`](02_UI.md).
- [ ] `/generators`, `/crypto`, `/utilities` → `/developer-toolkit?tab=<name>` redirects.
- [ ] Single consolidated `nav-registry.ts` entry.
- [ ] `WORKBENCH_TOOL_KEYS` / `tool-metadata.ts` catalog merge.
- [ ] Zero regressions to any existing Generators, Crypto, or Utilities capability — verified against every criterion in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md).

## Dependencies

None hard — a consolidation of shipped, stable foundation features (all released in Phase 01, per [`../../02_ROADMAP.md`](../../02_ROADMAP.md) §2), can proceed independently.

- [x] Dependency status confirmed during this specification session: Generators, Crypto, and Utilities are all shipped and stable — no blocking phase dependency.

## Milestones

One milestone (approved in principle 2026-08-05) — see [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) §2 for why this phase's shape (no backend/database work) doesn't warrant Universal Converter's seven-milestone breakdown.

- [ ] Milestone 1 — Unified page, redirects, nav/workbench catalog merge, verification, and documentation (T1–T10 in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md)).

> Each milestone completion is a checkpoint trigger — see [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1.

## Risks

- **Technical:** A copy/relocation error while moving components onto the new unified page (wrong import, dropped prop) — the realistic failure mode for a consolidation phase, not a logic bug. Mitigated by the "import, not copy" execution rule in [`IMPLEMENT.md`](IMPLEMENT.md) and the full manual verification pass in [`07_TESTING.md`](07_TESTING.md) §3.
- **Product/UX:** Users with `/generators`, `/crypto`, or `/utilities` deep-links — mitigated by the redirect requirement in [`01_SPEC.md`](01_SPEC.md) §3.
- **Scope creep:** Temptation to add the near-term command-palette deep-linking gap or a new Utilities tool "while already touching this code" — explicitly guarded against in [`01_SPEC.md`](01_SPEC.md) §5; either requires a new spec pass, not an in-flight scope change.
- ~~**Naming/layout risk:**~~ Retired 2026-08-05 — the route slug, nav label, icon/shortcut, and tabs-vs-stacked-sections layout that T1/T3/T4 depend on were all confirmed by the project owner before implementation was scheduled to start. See [`01_SPEC.md`](01_SPEC.md) §7.

## Definition of Complete

- [ ] All deliverables above are shipped and meet [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md).
- [ ] [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criteria are fully checked off.
- [ ] [`CURRENT_STATE.md`](CURRENT_STATE.md) reflects reality with no stale "In Progress" items.
- [ ] A final checkpoint has been produced per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md).

**Not yet authorized.** This phase is at the **Specification** stage (per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) §1). The specification is content-complete and approved in principle, which satisfies the Specification stage's exit condition — but the move to **Authorized** requires the project owner's explicit approval for implementation to begin, and that has not been given. See [`CURRENT_STATE.md`](CURRENT_STATE.md) "Remaining".

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [01_SPEC.md](01_SPEC.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
