# Implementation Phases

> **Purpose:** Index of every FDK implementation phase — the buildable work that realizes the roadmap in [`../02_ROADMAP.md`](../02_ROADMAP.md).
> **Scope:** Index only. Each phase owns its own full spec in its own folder.
> **Ownership:** TODO — assign an owner.
> **Status:** Draft — Phase 01 🔒 released & frozen (v0.1.0-workbench); Phase 02 current; Phases 03–08 still template scaffolds
> **Version:** 0.3.0
> **Last Updated:** 2026-07-20
> **Depends On:** [../02_ROADMAP.md](../02_ROADMAP.md)
> **Supersedes:** —

---

## 1. Phases

| # | Phase | Status |
|---|-------|--------|
| 01 | [Workbench](Phase-01-Workbench/README.md) | 🔒 Released & frozen — `v0.1.0-workbench`, bug fixes only from here |
| 02 | [Project Initialization Engine](Phase-02-Project-Initialization-Engine/README.md) | Current phase — not yet started |
| 03 | [Prompt Studio](Phase-03-Prompt-Studio/README.md) | Not started — spec placeholder |
| 04 | [Universal Converter](Phase-04-Universal-Converter/README.md) | Not started — spec placeholder |
| 05 | [Model Playground](Phase-05-Model-Playground/README.md) | Not started — spec placeholder |
| 06 | [Projects](Phase-06-Projects/README.md) | Not started — spec placeholder |
| 07 | [Knowledge Hub](Phase-07-Knowledge-Hub/README.md) | Not started — spec placeholder |
| 08 | [Developer Toolkit](Phase-08-Developer-Toolkit/README.md) | Not started — spec placeholder |

## 2. Shape of every phase folder

Each `Phase-XX-Name/` starts, at spec-authoring time, with the same 12 files:

`README.md`, `CURRENT_STATE.md`, `01_SPEC.md`, `02_UI.md`, `03_BACKEND.md`, `04_DATABASE.md`, `05_COMPONENTS.md`, `06_API.md`, `07_TESTING.md`, `08_ACCEPTANCE.md`, `09_IMPLEMENTATION_TASKS.md`, `IMPLEMENT.md`.

A phase may add extra numbered docs beyond this base 12 when its design introduces a contract that doesn't fit an existing file — e.g. Phase 01 (Workbench) adds `12_PANEL_INTERFACE.md` to specify the `WorkbenchPanel` contract (per [ADR-0002](../decisions/0002-workbench-panel-architecture.md)). This is the exception, not the norm — don't add a numbered doc speculatively; only when a phase's own spec work surfaces a real need for one.

### 2.1 End-of-phase additions (from Phase 02 onward)

As a phase approaches RC/sign-off, it accumulates a few more standard artifacts — not written upfront, only once there's something real to put in them:

- **`10_RELEASE_NOTES.md`** — the release-facing summary (New Features / Breaking Changes / Migrations / Bug Fixes / Known Issues / Upgrade Notes / Deferred Work). Copy [`RELEASE_NOTES_TEMPLATE.md`](RELEASE_NOTES_TEMPLATE.md) into the phase folder and fill it in at RC, finalize at sign-off. Adopted starting with Phase 01 (retroactively, since the practice didn't exist when Phase 01 began) — write it from the start for Phase 02 onward.
- **`QA/`** — QA tickets for acceptance criteria that couldn't be verified by an automated session (a real device/browser/screen-reader requirement), ruled explicitly non-blocking for merge. See [`../history/Phase-01/QA/README.md`](../history/Phase-01/QA/README.md) for the pattern.
- **`BUGS/`** — one issue file per finding from manual verification or a post-implementation audit, classified BLOCKER/MAJOR/MINOR per [`../12_BUG_CLASSIFICATION.md`](../12_BUG_CLASSIFICATION.md). See [`../history/Phase-01/BUGS/README.md`](../history/Phase-01/BUGS/README.md) for the pattern.
- **`POST_IMPLEMENTATION_REVIEW.md`** — the retrospective (What Went Well / What Didn't / Unexpected Problems / Architecture Changes / Performance Notes / Accessibility Notes / Lessons Learned / Recommendations for the next phase). See [`../history/Phase-01/POST_IMPLEMENTATION_REVIEW.md`](../history/Phase-01/POST_IMPLEMENTATION_REVIEW.md) for the pattern.

None of these four block a phase from starting — they're end-state artifacts, not upfront scaffolding. All four move to [`../history/Phase-NN/`](../history/) once the phase freezes (per [`../13_PHASE_LIFECYCLE.md`](../13_PHASE_LIFECYCLE.md) §5) — the links above point at Phase 01's already-archived copies, since Phase 01 is the only phase to have reached that point so far.

See [`../11_PROJECT_STRUCTURE.md`](../11_PROJECT_STRUCTURE.md) §5 for how this maps onto the repository as a whole.

## 3. Before starting a phase

A phase is not authorized for implementation until its `01_SPEC.md` and `08_ACCEPTANCE.md` are filled in (not template placeholders) — see [`../09_CLAUDE_CODE_RULES.md`](../09_CLAUDE_CODE_RULES.md) §1.

## 4. TODO

- [ ] TODO: Update the Status column as each phase moves from spec placeholder → authorized → in progress → complete.

## 5. Cross-references

- [../02_ROADMAP.md](../02_ROADMAP.md)
- [../09_CLAUDE_CODE_RULES.md](../09_CLAUDE_CODE_RULES.md)
- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../12_BUG_CLASSIFICATION.md](../12_BUG_CLASSIFICATION.md)
- [../13_PHASE_LIFECYCLE.md](../13_PHASE_LIFECYCLE.md)
- [../history/](../history/) — where a phase's end-of-phase artifacts land once it freezes
