# Knowledge Hub — Post-Implementation Review

> **Purpose:** A retrospective on how Phase 07 actually went — not a restatement of what was built (see `CURRENT_STATE.md`/`08_ACCEPTANCE.md` for that), but what the process revealed.
> **Scope:** This phase's full arc: specification, ADR-0015, implementation, the first real use of the FDK Verification Framework against a real phase, framework hardening, evidence reconciliation, and release.
> **Status:** Final — Phase 07 Released & Frozen as `v0.7.0-knowledge-hub` (commit `b445b09`).
> **Last Updated:** 2026-08-05
> **Depends On:** [CURRENT_STATE.md](../../implementation/Phase-07-Knowledge-Hub/CURRENT_STATE.md), [08_ACCEPTANCE.md](../../implementation/Phase-07-Knowledge-Hub/08_ACCEPTANCE.md)

---

## What Went Well

- **This phase was the first real end-to-end dry run of the FDK Verification Framework (Milestone 4A) against an actual implemented phase**, exactly the precondition Milestone 4B has been gated on. The framework caught real, non-obvious problems it was designed to catch — a Windows shell-dispatch bug, a self-referential Architecture check against its own persisted reports, and a genuine repository-state issue (uncommitted framework work sharing a tree with phase work) — without ever needing to be weakened to get there.
- **Every RC FAIL across all three runs was correctly triaged into implementation defect vs. framework defect vs. repository-state issue vs. evidence gap, and none were ever collapsed into another to manufacture a PASS.** The first run's six FAILs were all contract-evidence-sync or framework/environment issues, not Knowledge Hub defects. The second run's single FAIL was a real, accurate repository-state finding, not a false positive — it was resolved by committing the already-completed work correctly, not by touching the verifier.
- **The checkpoint-scope tension (a phase's own required checkpoint artifact living under a path the phase declares out-of-scope) was treated as a genuine open governance question, not silently resolved.** The eventual fix — commit checkpoints before RC — was chosen explicitly as the least invasive option, and the tension itself was left open rather than closed by inventing a verifier exemption.
- **Evidence discipline held across the whole phase.** An earlier draft of `CURRENT_STATE.md` claimed "all 41 acceptance criteria verified"; that claim was caught as inaccurate under scrutiny and corrected rather than left standing. AC34/AC39 and three regression targets were left honestly unchecked until real evidence existed for them, rather than assumed from "the implementation is believed complete."

## What Didn't

- **No formal, contemporaneous checkpoint-log entry was produced during the T1–T16 implementation session**, despite crossing the 10–12 task checkpoint trigger partway through. The entry that exists (`2026-08-04-phase-07-implementation-checkpoint.md`) was authored retroactively during evidence reconciliation, which its own "Known Risks" section discloses — it satisfies the letter of `10_CHECKPOINT_PROTOCOL.md` §3 (an artifact now exists) but not its original real-time-recoverability intent. This is the direct cause of two follow-on costs: AC34/AC39 required an explicit interpretive call rather than a clean checkbox, and the second RC run failed purely because that retroactive artifact was still uncommitted at RC time.
- **The framework-hardening work and the phase's own checkpoint artifact were left uncommitted in the same working tree as Phase 07's implementation for longer than they should have been**, which is exactly what caused the second RC run's Architecture FAIL. Neither was a defect in either body of work — the fix was ordinary commit hygiene (`be5b227`, `36d2ffa`), but the RC run cost that could have been avoided by committing incrementally is a real process cost, not just a one-line footnote.
- **This phase, like Phase 06, has no feature-branch/PR record** — Phase 07 was implemented and committed directly to `master`, continuing rather than reversing that precedent. Worth naming again here, as Phase 06's own review did, so the audit trail stays honest about which phases have a PR record and which don't.

## Unexpected Problems

- **`tools/fdk_verification/verifiers/_shell.py`'s `subprocess.run(shell=True)` silently resolved to `cmd.exe` on native Windows**, which does not resolve forward-slash-led relative executable paths (`backend/.venv/Scripts/python.exe`) the way Git Bash does — a platform-execution gap invisible until a real Windows RC run actually hit it. Fixed by explicit Git Bash dispatch on Windows, not by rewriting the contract-authoring convention that assumed POSIX-shell semantics.
- **The Architecture Verifier's report-persistence step wrote into the exact `forge-docs/history/` path every phase's contract declares out-of-scope**, so any second RC run in the same session would always flag its own prior report — a self-referential bug invisible until the pipeline was actually run twice against the same repository state. Fixed narrowly: a filename-pattern exemption recognizing only the pipeline's own generated report/escalation names, leaving out-of-scope protection for everything else under `forge-docs/history/` fully intact (verified by a dedicated test proving a hand-written history file still fails correctly).
- **Code Quality's TODO/FIXME detection was a bare substring match**, so any prose containing the literal word "TODO" (a section heading, template boilerplate) produced a false-positive warning. Fixed by requiring the conventional marker form (`TODO:`, `TODO(name):`). Never blocked anything (Code Quality is warnings-only by design), but was real noise that would have compounded on every future phase's RC run if left unfixed.

## Architecture Changes

None beyond what ADR-0015 and this phase's own spec called for. Specifically confirmed:

- No new search index or content table — `services/knowledge/service.py` composes the existing `notes_service.search_notes()`/`documents_service.search_documents()` rather than issuing its own FTS SQL.
- No cross-feature import between `notes`/`documents` — the delete-hook purge is implemented at the route layer (`api/routes/notes.py`/`documents.py`), specifically because the services-layer alternative was a literal circular import with `services/knowledge/service.py` already importing both services at module level.
- `forge-docs/03_ARCHITECTURE.md` §4's Knowledge Hub search-index question, open since that document's creation, is now closed by ADR-0015.
- Three purely additive tables (`note_tag_links`, `document_tag_links`, `knowledge_links`); no existing table or column altered. `knowledge_links` is polymorphic with no real cross-table foreign key possible — orphan prevention is service-enforced (`purge_links_for`), the one deliberate integrity trade-off this phase's schema makes, documented in `docs/Database.md`.

## Recommendations for Phase 08

- **Commit checkpoint-log entries at the moment they're triggered, not retroactively.** This phase's single largest process cost traced back to one missing contemporaneous checkpoint — both the AC34/AC39 interpretive call and the second RC run's failure were downstream of that one gap.
- **If a phase's implementation and any framework-level work happen to overlap in the same session, commit them separately and promptly**, rather than letting them accumulate together in one working tree — Phase 07's second RC run exists entirely because two already-good bodies of work shared a tree for too long.
- **The FDK Verification Framework is now dry-run-proven against a real phase.** Milestone 4B (autonomous progression) remains explicitly out of scope and unimplemented — this review does not recommend starting it, only notes that its stated precondition has now genuinely been met, for whoever makes that call.

## Cross-references

- [CURRENT_STATE.md](../../implementation/Phase-07-Knowledge-Hub/CURRENT_STATE.md)
- [08_ACCEPTANCE.md](../../implementation/Phase-07-Knowledge-Hub/08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](../../implementation/Phase-07-Knowledge-Hub/09_IMPLEMENTATION_TASKS.md)
- [10_RELEASE_NOTES.md](10_RELEASE_NOTES.md)
- [../../decisions/0015-knowledge-hub-reuses-fts5.md](../../decisions/0015-knowledge-hub-reuses-fts5.md)
- [Phase-06/POST_IMPLEMENTATION_REVIEW.md](../Phase-06/POST_IMPLEMENTATION_REVIEW.md)
