# ADR-0009 — Phase Specification Freeze

> **Purpose:** Lock Phase 01's specification at the moment implementation is authorized, so the discipline that produced a stable spec (three review passes, an explicit scope freeze, ADR-0008 deliberately deferred) isn't undone by scope creep during implementation itself.
> **Scope:** Change-control policy for an authorized, in-progress phase. Applies to Phase 01 now; intended as the template for authorizing future phases too (see §6).
> **Ownership:** Project owner (approved 2026-07-20)
> **Status:** Accepted
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [../implementation/Phase-01-Workbench/README.md](../implementation/Phase-01-Workbench/README.md), [../implementation/Phase-01-Workbench/IMPLEMENT.md](../implementation/Phase-01-Workbench/IMPLEMENT.md)
> **Supersedes:** —

---

## 1. Context

Phase 01's specification went through three real review passes with the project owner — an initial spec, a rewrite around a panel architecture, and a scope-freeze pass that explicitly deferred the Capability Registry (ADR-0008) and a Projects interface rather than absorbing them into Phase 01. That discipline is worth protecting once implementation actually starts: without an explicit freeze, "while we're here" additions during implementation would erode exactly the scope boundary the project owner spent three passes establishing.

## 2. Decision

As of implementation authorization, Phase 01's specification (`01_SPEC.md` through `08_ACCEPTANCE.md`, `12_PANEL_INTERFACE.md`) is **locked**.

**Allowed without a new ADR or spec revision:**
- Bug fixes.
- Clarifications (a spec section is genuinely ambiguous or self-contradictory once implementation reveals the gap).
- Typos and cross-reference corrections.

**Deferred to the backlog (`forge-docs/research/future-features/` or `02_ROADMAP.md`), not implemented during Phase 01:**
- New features (an extra panel, an extra pinned tool, an extra Quick Action beyond the three specified).
- Architectural changes (any change to the Panel Registry's shape, the layout persistence model, or the API contract beyond what's already specified).
- Scope expansion of any kind — explicitly including the five items the project owner named directly: workflows, a command palette beyond the `/search` page, a capability registry, a Projects interface, a plugin system. Also explicitly included: AI-related additions of any kind not already in the accepted spec.

## 3. Exceptions

The freeze does not apply to:

- **Security bugs** — fix immediately, regardless of spec text.
- **Build failures** — the app must build cleanly; a spec detail that turns out to be unbuildable as written gets corrected, not worked around with a hack.
- **Specification errors** — a genuine contradiction between two spec documents, or a requirement that's impossible to satisfy as literally written, gets corrected (this is a "clarification" per §2, not a new decision — but if the correction changes behavior meaningfully rather than just fixing an internal inconsistency, treat it as scope-expansion-adjacent and flag it explicitly rather than quietly reinterpreting the spec).
- **Critical usability defects** — something that makes Phase 01 unusable, not merely "could be nicer" (that distinction matters: an unusable empty state is an exception; a nicer-looking empty state is scope expansion).

## 4. Consequences

- Makes it easier: a Claude Code session implementing Phase 01 has an unambiguous answer to "should I also add X while I'm in here" — no, unless X is a bug fix, clarification, typo, or one of the four named exceptions.
- Makes it harder: a genuinely good idea that surfaces mid-implementation (e.g. "this panel would be more useful with feature Y") must wait, even if it would be cheap to add right now. That's the point — cheap-right-now is exactly how scope creep happens, per the project owner's own framing ("every new concept increases the implementation surface and reduces the chance of a clean one-shot build").
- Any idea deferred under this ADR should still be captured, not lost — record it in [`../research/future-features/README.md`](../research/future-features/README.md) or as a candidate roadmap item, per the promotion path in [`../research/README.md`](../research/README.md) §3.

## 5. Priority order during implementation

Restated here because it's the operational complement to the freeze — see [`../implementation/Phase-01-Workbench/IMPLEMENT.md`](../implementation/Phase-01-Workbench/IMPLEMENT.md) "Priority Order" for the authoritative copy:

1. Correctness
2. Existing functionality (nothing already shipped regresses)
3. Stability
4. Performance
5. UX polish
6. New functionality

Never sacrifice a higher priority to improve a lower one — concretely, never break an existing feature (priority 2) in service of a Workbench polish detail (priority 5).

## 6. Future application

This ADR is written to generalize: any future phase's `README.md`/`IMPLEMENT.md` can reference this pattern (lock the spec at authorization, allow only bug-fix/clarification/typo changes, name explicit exceptions) rather than re-deriving it. TODO: once a second phase is authorized, decide whether to promote this into [`../09_CLAUDE_CODE_RULES.md`](../09_CLAUDE_CODE_RULES.md) as a standing rule rather than a per-phase ADR reference.

## 7. Cross-references

- [../implementation/Phase-01-Workbench/README.md](../implementation/Phase-01-Workbench/README.md)
- [../implementation/Phase-01-Workbench/IMPLEMENT.md](../implementation/Phase-01-Workbench/IMPLEMENT.md)
- [../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md](../implementation/Phase-01-Workbench/09_IMPLEMENTATION_TASKS.md)
- [../research/README.md](../research/README.md)
- [0008-capability-registry-direction.md](0008-capability-registry-direction.md)
