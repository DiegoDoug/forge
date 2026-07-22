# 13 — Phase Lifecycle

> **Purpose:** The one lifecycle every phase moves through, in the same order, so "what state is this phase in" is never a judgment call. Adopted after Phase 01 became the first phase to actually traverse the whole thing — this document generalizes what Phase 01 did into a repeatable standard.
> **Scope:** Every phase, from the moment its folder is scaffolded to the moment (if ever) it's archived.
> **Ownership:** TODO — assign an owner.
> **Status:** Draft
> **Version:** 0.1.0
> **Last Updated:** 2026-07-21
> **Depends On:** [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md), [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md), [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md)
> **Supersedes:** —

---

## 1. The lifecycle

```
Draft → Specification → Authorized → Implementation → Release Candidate → QA → Owner Sign-off → Released → Frozen → Maintenance → Archived
```

Every phase passes through these stages **in this order**. A phase can sit at any stage indefinitely (most of Phases 02–08 sit at "Draft" today), but it cannot skip a stage or move backward without an explicit decision to do so (e.g. a rejected sign-off sends a phase back to Release Candidate, not to Draft).

## 2. Stage definitions

| Stage | Meaning | Exit condition |
|---|---|---|
| **Draft** | The phase folder exists as a scaffold; `01_SPEC.md` through `IMPLEMENT.md` are placeholders, not real content. | A real spec pass begins. |
| **Specification** | `01_SPEC.md` through `08_ACCEPTANCE.md` (and any extra numbered docs the phase needs) are being actively drafted and reviewed with the project owner. | Every exit-criteria document in the phase's `README.md` is content-complete. |
| **Authorized** | The specification is locked (per an ADR like [ADR-0009](decisions/0009-phase-specification-freeze.md) for Phase 01), and the project owner has explicitly approved implementation to begin. | `IMPLEMENT.md` says "Approved to begin" and the first implementation task starts. |
| **Implementation** | Tasks in `09_IMPLEMENTATION_TASKS.md` are being executed, milestone by milestone, per [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md). | Every task is checked off and `08_ACCEPTANCE.md` has had a first full pass. |
| **Release Candidate** | Implementation is done. An independent verification/audit pass (manual and/or a dedicated code-review pass, per Phase 01's precedent) runs against the spec. Findings are classified per [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md) §2. Any 🔴 BLOCKER is fixed and the phase re-enters Release Candidate (RC1 → RC2 → ... until zero BLOCKERs remain). | Zero known BLOCKERs remain. |
| **QA** | Acceptance criteria that need a real device/browser/screen-reader session (not verifiable by an automated Claude Code session) are tracked as tickets in the phase's `QA/` folder. QA does not block progression to sign-off — see §3. | QA tickets exist and are documented (not necessarily *run* — see §3). |
| **Owner Sign-off** | The project owner reviews the Release Candidate's merge criteria (per [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md) §6) and records an explicit decision. | Sign-off is recorded as APPROVED (or the phase returns to Release Candidate with specific fixes required). |
| **Released** | The phase's branch is tagged (`vX.Y.Z-phase-name`) and merged to the main branch. `10_RELEASE_NOTES.md` is finalized. | Tag and merge are both pushed. |
| **Frozen** | The phase's implementation directory accepts bug fixes only — no new features, no architectural changes, no scope expansion. Specification is locked permanently (not just for the duration of implementation). | Never exits on its own — a phase stays frozen through Maintenance. |
| **Maintenance** | The frozen phase continues to receive bug fixes as needed, indefinitely. Each fix is a normal, small, scoped change against already-shipped code. | N/A — ongoing. |
| **Archived** | (Reserved for a future point — not yet exercised by any phase.) If a phase's functionality is eventually superseded or removed entirely, its implementation folder and history are marked archived rather than deleted, preserving the record. | N/A — not yet defined in detail; revisit when the first phase actually reaches this point. |

## 3. Why QA and Owner Sign-off don't block each other the way they sound like they should

QA existing as its own stage does **not** mean sign-off waits for QA to finish. Phase 01 established the precedent: two acceptance criteria (drag-reorder FPS/Profiler, a live screen-reader pass) structurally cannot be verified by an automated Claude Code session — no real device, no real screen reader. Blocking sign-off on those would mean the phase could never close. Instead:

- Genuinely unverifiable-by-automation criteria become QA tickets, explicitly ruled non-blocking by the project owner.
- Sign-off means: every criterion the environment *could* verify, was verified — and the ones it structurally couldn't are tracked, not silently dropped or falsely checked off.
- QA tickets remain open after Released/Frozen and get closed out whenever a human with the right hardware/software actually runs them — this can happen well after the phase is otherwise done.

## 4. What "Frozen" actually permits

Per [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md) §2's BLOCKER/MAJOR/MINOR matrix — a frozen phase's directory can still receive:

- 🔴 BLOCKER fixes (should never have shipped this way, fix immediately regardless of freeze).
- 🟡 MAJOR fixes, if a project-owner decision approves them (per the phase's own `BUGS/` tracker).
- 🟢 MINOR fixes, at any time, since they're explicitly backlog-safe.

What a frozen phase's directory does **not** accept: new panels/features/endpoints, architectural changes, or anything that would require re-opening `01_SPEC.md`. That belongs in a new phase (or, if it's small enough to not warrant a whole phase, a clearly-scoped follow-up tracked in the roadmap).

## 5. End-of-phase artifacts and the archive step

As a phase reaches Release Candidate and beyond, it accumulates `10_RELEASE_NOTES.md`, `POST_IMPLEMENTATION_REVIEW.md`, `QA/`, and `BUGS/` (see [`implementation/README.md`](implementation/README.md) §2.1 for what each contains). Once a phase reaches **Frozen**, these four are moved to `history/Phase-NN/` — not deleted, not left in the active implementation folder — so the active folder stays focused on the specification (`01_SPEC.md` through `09_IMPLEMENTATION_TASKS.md`) and its living `CURRENT_STATE.md`, while the full historical record of how the phase actually went stays discoverable under `history/`.

## 6. Phase 01 as the worked example

Phase 01 (Workbench) is the first phase to traverse this entire lifecycle, and its own documents are the reference implementation of every stage above:

- Draft → Specification → Authorized: [`implementation/Phase-01-Workbench/README.md`](implementation/Phase-01-Workbench/README.md) "Authorization" section, and the Session Notes history in `CURRENT_STATE.md`.
- Implementation: `09_IMPLEMENTATION_TASKS.md`, T1–T16, four milestones.
- Release Candidate: the post-T16 independent audit, `BUG-0001` found and fixed, RC1 → RC2 — see [`history/Phase-01/BUGS/`](history/Phase-01/BUGS/README.md).
- QA: [`history/Phase-01/QA/`](history/Phase-01/QA/README.md).
- Owner Sign-off: recorded 2026-07-21, "APPROVED, Accepted for Release."
- Released: tagged `v0.1.0-workbench`, merged via [#14](https://github.com/DiegoDoug/forge/pull/14).
- Frozen: `implementation/Phase-01-Workbench/README.md` and `CURRENT_STATE.md` both record the frozen status explicitly.
- Maintenance: ongoing — see `BUGS/BUG-0002` through `BUG-0005` for the open backlog items that may get picked up here.

## 7. TODO

- [ ] TODO: Define the Archived stage in real detail once a phase actually reaches end-of-life (likely years out for this project).
- [ ] TODO: Decide whether a phase can be skipped from Draft straight to Archived if it's abandoned before implementation (e.g. deprioritized in the roadmap) — not yet needed, but a real question once more phases exist.

## 8. Cross-references

- [12_BUG_CLASSIFICATION.md](12_BUG_CLASSIFICATION.md)
- [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md)
- [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md)
- [02_ROADMAP.md](02_ROADMAP.md)
- [implementation/README.md](implementation/README.md)
- [implementation/Phase-01-Workbench/](implementation/Phase-01-Workbench/README.md) — the worked example
- [history/Phase-01/](history/Phase-01/) — Phase 01's archived end-of-phase artifacts
