# Universal Converter — README

> **Purpose:** Entry point for the Universal Converter phase — objective, scope, deliverables, and completion criteria.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** TODO — assign a phase owner.
> **Status:** **Implementation complete — all seven milestones done.** RC audit (Milestone 7) passed with zero open BLOCKERs. Awaiting the project owner's formal Sign-off decision (see [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §5) before this phase moves to Released/Frozen per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md).
> **Last Updated:** 2026-07-25

---


## Objective

Unify the existing Converters and Ingest feature areas into one universal format-conversion surface — one page, one nav entry, one backend provider abstraction — without changing any existing conversion's behavior and without adding any new conversion direction in this phase. See [`01_SPEC.md`](01_SPEC.md) §1 for the full scope decision record.

## Scope

**In scope:**
- [x] One unified page at `/converters` with a "Text & Data" section (today's nine client-side tools, unmodified) and a "Documents" section (today's Ingest upload/job/preview workflow, unmodified).
- [x] One nav-registry entry replacing the current two ("Converters", "Ingest").
- [x] A redirect from `/ingest` to `/converters` so existing bookmarks/links keep working.
- [x] A new `ConverterProvider` interface + registry in `backend/app/services/converters/providers/`, with the existing MarkItDown/vision pipeline registered as the first provider — additive scaffolding for future extensibility, not a new user-facing capability.
- [x] A new additive `GET /api/converters/providers` endpoint.

**Out of scope:**
- [ ] Any new conversion direction (Markdown→DOCX/PDF, server-side JSON↔YAML↔XML, etc.) — deferred to a future fast-follow phase that registers a second provider. See [`01_SPEC.md`](01_SPEC.md) §5.
- [ ] Moving the client-side text converters to the backend — they stay client-side.
- [ ] Any new database persistence (conversion history/presets) — see [`04_DATABASE.md`](04_DATABASE.md).
- [ ] The Documents feature's rich-text export pipeline (`services/documents/export.py`) — that's Phase 07 (Knowledge Hub) territory, not touched here.

## Relationship to the shipped application

Consolidates the existing **Converters** (`frontend/features/converters`, `backend/app/services/converters`) and **Ingest** (`frontend/features/ingest`, `backend/app/services/ingest`) feature areas, at the presentation and backend-organization layer only. Neither feature's underlying logic is rewritten — see [`03_BACKEND.md`](03_BACKEND.md) §1 for why this is a wrap-not-rewrite design.

- Related frontend: `frontend/features/converters/, frontend/features/ingest/`
- Related backend: `backend/app/services/converters/, backend/app/services/ingest/`

## Deliverables

- [x] Unified `/converters` page (Text & Data + Documents sections) — see [`02_UI.md`](02_UI.md).
- [x] `/ingest` → `/converters` redirect.
- [x] Single consolidated `nav-registry.ts` entry.
- [x] `ConverterProvider` protocol + registry + `MarkItDownProvider` adapter — see [`03_BACKEND.md`](03_BACKEND.md).
- [x] `GET /api/converters/providers` endpoint — see [`06_API.md`](06_API.md).
- [x] Zero regressions to any existing Converters or Ingest capability — verified against every criterion in `08_ACCEPTANCE.md`, including a Docker Compose clean-room build and a fresh-checkout reproducibility check (Milestone 7).

## Dependencies

None hard — a consolidation of shipped features, can proceed independently.

- [x] Dependency status confirmed: both Converters and Ingest are shipped, stable foundation features (per [`../../02_ROADMAP.md`](../../02_ROADMAP.md) §2) — no blocking phase dependency.

## Milestones

Seven milestones (per the project owner's Stage 4 ordering, 2026-07-23), each independently reviewable, independently testable, reversible on its own, and small enough to isolate a regression quickly. Full detail — objective, scope, files, dependencies, acceptance criteria, tests, rollback, complexity — is in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md).

- [x] Milestone 1 — Baseline characterization tests (closes the zero-coverage gap found in [`07_TESTING.md`](07_TESTING.md) §0; no production code changes). **Complete, approved by the project owner 2026-07-25** — 27 new tests, full suite 138 → 165 passed, 0 regressions.
- [x] Milestone 2 — Provider interface and registry (`ConverterProvider` protocol, proven against a fake provider only). **Complete, approved by the project owner 2026-07-25** — full suite 165 → 172 passed, 0 regressions.
- [x] Milestone 3 — Ingest provider integration (`MarkItDownProvider` adapter, `GET /api/converters/providers`). **Complete, approved by the project owner 2026-07-25** — full suite 172 → 183 passed, 0 regressions, `services/ingest/` confirmed byte-for-byte unmodified.
- [x] Milestone 4 — Browser provider abstraction (a declarative manifest for the nine client-side tools; no execution-location change). **Complete, approved by the project owner 2026-07-25** — zero existing tool files touched; verified live in browser (identical render, working Minify/Cron interactions) via a throwaway page, deleted afterward.
- [x] Milestone 5 — Unified Converter UI and routing (the single `/converters` page, nav consolidation, `/ingest` redirect). **Complete, approved by the project owner 2026-07-25** — plus an unplanned but necessary fix to Workbench's own pinned-tools mapping (the dead `"ingest"` key and a redundant `"universal_converter"` placeholder, both retired in favor of `"converters"`), verified by the Workbench panel correctly showing a "Converter" tile post-fix. Full backend suite 183 passed, `tsc`/`lint`/`build` clean.
- [x] Milestone 6 — Cleanup, documentation, and regression hardening (full acceptance-criteria sweep, shipped-app docs updated). **Complete, approved by the project owner 2026-07-25** — every `08_ACCEPTANCE.md` §1–§4 criterion now checked with cited evidence; `docs/Architecture.md`, `docs/API.md`, `docs/FolderStructure.md`, root `README.md`, and `forge-docs/02_ROADMAP.md` updated; dead-code sweep found nothing left over.
- [x] Milestone 7 — Release candidate audit (independent verification pass, Docker clean-room check, sign-off readiness). **Complete** — plus a fresh-checkout reproducibility check added at the project owner's request (T20a), a dependency review (zero new dependencies, T20c), a repository-cleanliness check (T20d), and a drafted [`10_RELEASE_NOTES.md`](10_RELEASE_NOTES.md) (T20e). Zero open BLOCKERs. Awaiting the project owner's Sign-off decision.

> Each milestone completion is a checkpoint trigger — see [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1.

## Risks

- **Technical:** Regressing an existing conversion behavior while moving components/wrapping the pipeline — mitigated by the "wrap, don't rewrite" design in [`03_BACKEND.md`](03_BACKEND.md) §1 and an explicit RC verification pass (Milestone 3) that re-checks every capability listed in [`01_SPEC.md`](01_SPEC.md) §3.
- **Product/UX:** Users with `/ingest` or old Converters deep-links — mitigated by the redirect requirement in [`01_SPEC.md`](01_SPEC.md) §3.
- **Scope creep:** Temptation to add "just one" new conversion direction while already touching this code — explicitly guarded against in [`01_SPEC.md`](01_SPEC.md) §5; any such addition requires a new spec pass, not an in-flight scope change.
- **Abstraction risk:** The `ConverterProvider` interface is introduced with only one provider registered — flagged as a trade-off requiring explicit owner sign-off in [`03_BACKEND.md`](03_BACKEND.md) §2, not assumed acceptable by default.

## Definition of Complete

- [x] All deliverables above are shipped and meet [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md).
- [x] [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criteria are fully checked off.
- [x] [`CURRENT_STATE.md`](CURRENT_STATE.md) reflects reality with no stale "In Progress" items.
- [x] A final checkpoint has been produced per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md).

Implementation is complete. Per [`13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md), the remaining stages (Owner Sign-off → Released → Frozen) are the project owner's decisions to make, not this document's to declare.

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [01_SPEC.md](01_SPEC.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [10_RELEASE_NOTES.md](10_RELEASE_NOTES.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
