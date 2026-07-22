# [Phase Name] — Release Notes

> **Purpose:** The release-facing summary of this phase — what shipped, what broke on purpose, what to do before upgrading. Written once the phase reaches RC and updated through sign-off; not a duplicate of `CURRENT_STATE.md` (the day-to-day working log) or `POST_IMPLEMENTATION_REVIEW.md` (the retrospective) — this is the document a user or another engineer reads to understand what changed, not how it was built.
> **Scope:** This phase only.
> **Status:** Draft — fill in at RC, finalize at sign-off.
> **Version:** [tag this phase ships as, e.g. v0.2.0-project-init]
> **Last Updated:** [date]
> **Depends On:** [../../implementation/Phase-NN-Name/CURRENT_STATE.md](../../implementation/Phase-NN-Name/CURRENT_STATE.md), [../../implementation/Phase-NN-Name/08_ACCEPTANCE.md](../../implementation/Phase-NN-Name/08_ACCEPTANCE.md), [POST_IMPLEMENTATION_REVIEW.md](POST_IMPLEMENTATION_REVIEW.md)

---

## New Features

- [What a user or another engineer can now do that they couldn't before. One bullet per real capability, not per file changed.]

## Breaking Changes

- [Anything that changes existing behavior in a way that could surprise someone relying on the old behavior. If none, say "None" explicitly — don't omit the section.]

## Migrations

- [Database migrations, data transformations, or one-time setup steps required to move from the previous state to this one. Reference the actual Alembic revision(s) by name. If none, say "None" explicitly.]

## Bug Fixes

- [Real bugs found and fixed during this phase — including ones found in already-shipped functionality while building this phase, not just new-code bugs. Reference the phase's `BUGS/` tracker for full detail per issue.]

## Known Issues

- [What's shipping with a known gap, and why that's an acceptable trade-off rather than an oversight — per [`../01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) §1.3's "honest gaps" principle. Reference `BUGS/` (MAJOR/MINOR findings not fixed this phase) and `QA/` (criteria not yet verified) if either exists for this phase.]

## Upgrade Notes

- [Anything an operator running an existing Forge instance needs to know or do before/after pulling this version. If genuinely nothing beyond a normal deploy, say so explicitly.]

## Deferred Work

- [What was deliberately scoped out of this phase and pushed to a later one — cite the ADR or spec section that made that call, so "why isn't X here" has a documented answer.]

## Cross-references

- [../../implementation/Phase-NN-Name/CURRENT_STATE.md](../../implementation/Phase-NN-Name/CURRENT_STATE.md)
- [../../implementation/Phase-NN-Name/08_ACCEPTANCE.md](../../implementation/Phase-NN-Name/08_ACCEPTANCE.md)
- [POST_IMPLEMENTATION_REVIEW.md](POST_IMPLEMENTATION_REVIEW.md)
- [BUGS/README.md](BUGS/README.md) — if this phase has one
- [QA/README.md](QA/README.md) — if this phase has one
- [../../12_BUG_CLASSIFICATION.md](../../12_BUG_CLASSIFICATION.md)
