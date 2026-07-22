# 12 — Bug Classification

> **Purpose:** A single triage matrix every phase uses to decide, without debate, whether a found issue blocks a merge or ships as tracked debt. Adopted after Phase 01's post-implementation audit surfaced 5 findings and needed a consistent way to decide which one actually mattered.
> **Scope:** Applies to every issue found during implementation, manual verification, automated scans, or a post-implementation audit, in every phase from Phase 01 onward.
> **Ownership:** TODO — assign an engineering owner.
> **Status:** Draft
> **Version:** 0.1.0
> **Last Updated:** 2026-07-21
> **Depends On:** [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md), [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md)
> **Supersedes:** —

---

## 1. Why this exists

Phase 01's own post-implementation audit found 5 issues after "Final Validation" had already passed. Deciding what to do with each one, one at a time, in conversation, is exactly the kind of decision that quietly drifts — a persuasive writeup or a tired reviewer can push a real blocker into "eh, ship it" or block a merge over something cosmetic. This document removes that judgment call for the common cases by classifying issues **before** anyone argues about a specific one.

## 2. The three tiers

### 🔴 BLOCKER — must fix before merge

An issue is a BLOCKER if it is **any** of:

- **Data loss or data corruption** — a user action (through the normal UI, not a crafted API call) causes previously-saved state to be silently deleted, overwritten incorrectly, or become inconsistent.
- **Security** — anything that exposes data, bypasses auth, or weakens the encryption/session model described in [`../docs/Security.md`](../docs/Security.md).
- **Build failure** — `tsc`, `eslint`, `next build`, the backend test suite, or `docker compose build` fails.
- **Acceptance-criteria failure** — a functional criterion in the phase's `08_ACCEPTANCE.md` §1 (not §4/§5's performance/accessibility criteria — see §4 below) is provably false against the running app, not just unverified.

A BLOCKER must be fixed, re-verified, and documented before the phase's branch merges to `master`. It is never left as "tracked debt."

### 🟡 MAJOR — project owner decides

An issue is MAJOR if it's a real, confirmed problem but doesn't meet any BLOCKER criterion above, and falls into:

- **Significant UX inconsistency** — e.g. some user actions get error feedback on failure and structurally similar ones silently don't.
- **Accessibility** — a real, confirmed a11y gap that isn't already covered by an automated scan's "no violations" pass.
- **Performance** — a measurable regression or a confirmed inefficiency (e.g. dead computation on a hot path) that doesn't rise to a build/acceptance failure.

MAJOR issues get a written issue file (see §3) and go to the project owner to decide: fix before merge, fix in a fast-follow, or accept and backlog. The default, absent an explicit owner decision, is **not** to block the merge — but the decision itself must be made, not skipped.

### 🟢 MINOR — backlog, ship anyway

An issue is MINOR if it is:

- **Cosmetic** — visual-only, no functional effect.
- **Cleanup** — dead code, an unused interface surface, a validation asymmetry with no real-world reachable failure mode.
- **Refactoring** — the code works correctly but could be structured better.
- **Nice-to-have** — a genuine improvement that was never a requirement.

MINOR issues get a written issue file, go straight to the backlog, and are never allowed to expand the current phase's scope. Do not keep iterating on a MINOR issue inside an already-implementation-complete phase — file it and move on.

## 3. Issue files

Every MAJOR or MINOR finding gets its own file under the phase's `implementation/Phase-NN-Name/BUGS/` folder (create it if it doesn't exist — same pattern as `QA/`), named `BUG-NNNN-short-slug.md`, containing at minimum: what the issue is, where it lives (file/line), why it's classified the way it is, and its current status (open / fixed / accepted-and-backlogged). BLOCKERs get the same file, but their status always ends at "fixed" before merge, never "accepted."

## 4. A performance/accessibility exception

`08_ACCEPTANCE.md` §4 (performance) and §5 (accessibility) criteria that are **unverified** because the verification environment structurally can't check them (e.g. no real device, no screen reader, an automated browser session that can't service animation frames) are not BLOCKERs, MAJORs, or MINORs — they're not "issues" at all, they're **unverified claims**. Track those as QA tickets (`QA/QA-NNNN-*.md`, per Phase 01's precedent) rather than bugs, and don't let "we couldn't verify this in an automated session" block a merge that every other criterion supports. A confirmed accessibility violation (e.g. a real axe-core finding, or a code-reviewed gap) is a different thing — that's a MAJOR or MINOR bug, classified per §2.

## 5. Release Candidates

A phase becomes mergeable through a Release Candidate cycle, not a single pass/fail moment:

```
RC1 → fix BLOCKER(s) found → RC2 → (repeat until no BLOCKERs remain) → Owner Sign-off → Tag → Merge → Freeze
```

Each RC is a snapshot: run Final Validation, run (or re-run) an independent audit if one hasn't been done, classify every finding per §2. If zero BLOCKERs remain, that RC is sign-off-ready. If any BLOCKER is found, fix it, and the next RC starts. MAJOR/MINOR findings don't gate the RC cycle — they're filed and carried forward regardless of which RC surfaces them.

## 6. Merge criteria

A phase merges to `master` when **all** of the following are true:

- [ ] Builds pass (`tsc`, `eslint`, frontend and backend test suites).
- [ ] `docker compose build` passes for every touched service.
- [ ] `08_ACCEPTANCE.md` §1–§3 (functional/UX/quality) criteria all pass.
- [ ] No scope violations (per that phase's own spec-freeze ADR, if one exists).
- [ ] No known data-loss bugs (no open BLOCKERs of any kind).
- [ ] No regressions in existing, previously-shipped functionality.
- [ ] QA tasks are documented (§4) even if not yet manually executed — pending QA doesn't block merge, undocumented QA does.
- [ ] Owner sign-off is recorded.

Only then: tag the release, merge, and freeze the phase's implementation directory (bug fixes only from that point forward; new features and architectural changes go to the next phase).

## 7. Cross-references

- [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md)
- [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md)
- [13_PHASE_LIFECYCLE.md](13_PHASE_LIFECYCLE.md) — where Release Candidate/QA/Sign-off/Frozen fit in the full phase lifecycle
- [implementation/Phase-01-Workbench/CURRENT_STATE.md](implementation/Phase-01-Workbench/CURRENT_STATE.md) — first phase this classification was applied to, retroactively; now released and frozen
- [history/Phase-01/BUGS/](history/Phase-01/BUGS/README.md) — first BUGS/ folder, precedent for the pattern; archived here once Phase 01 froze
- [history/Phase-01/QA/](history/Phase-01/QA/README.md) — first QA/ folder, precedent for the pattern; archived here once Phase 01 froze
