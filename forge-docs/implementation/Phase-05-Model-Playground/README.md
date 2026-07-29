# Model Playground — README

> **Purpose:** Entry point for the Model Playground phase — objective, scope, deliverables, and completion criteria.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Release Candidate — Owner Sign-off recorded (APPROVED) 2026-07-29; PR pending. Not yet Released/Frozen — see [`../../13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md).
> **Last Updated:** 2026-07-29

---


## Objective

Provide a UI for testing and comparing LLM provider/model outputs side by side, with configurable API keys per provider.

## Scope

**In scope:**
- [x] UI-configurable, encrypted, per-provider API key storage (OpenAI, Anthropic) — [ADR-0011](../../decisions/0011-model-playground-provider-credential-security.md).
- [x] Sending one prompt to multiple selected provider/model combinations and viewing results side by side, each panel independent (success/error/timeout isolated per target).
- [x] Persisted run history (indefinite retention, manual delete) — reopen and re-view a past comparison.
- [x] `docs/Security.md` outbound-network-calls addendum.

**Out of scope (see [`01_SPEC.md`](01_SPEC.md) §5 for full list and rationale):**
- Multi-turn chat / conversation history within a run.
- Streaming (SSE) responses.
- Revealing a stored credential's raw key after creation.
- Cost estimation/billing tracking beyond echoing provider-reported token usage.
- Any provider beyond OpenAI/Anthropic, including a generic "Custom / OpenAI-compatible" pseudo-provider — deferred per [ADR-0012](../../decisions/0012-model-playground-provider-sdk-selection.md) §2.3; candidate for a future roadmap item, not this phase.
- Prompt template management/versioning (Prompt Studio's territory, not shared with this phase).

## Relationship to the shipped application

New capability — the first Forge feature with first-class outbound LLM provider calls as its core purpose (Ingest's vision-LLM path is optional/secondary by comparison).

- Related frontend: new `frontend/features/model-playground/` + `frontend/app/(app)/model-playground/page.tsx`.
- Related backend: new `backend/app/services/model_playground/`, `backend/app/models/model_playground.py`, `backend/app/schemas/model_playground.py`, `backend/app/api/routes/model_playground.py`, migration `0006_model_playground.py`.

## Deliverables

- [x] `ProviderCredential`, `PlaygroundRun`, `PlaygroundResult` tables + Alembic migration `0006_model_playground.py`.
- [x] `services/model_playground/` (credentials CRUD, run orchestration, OpenAI + Anthropic provider adapters).
- [x] `/api/model-playground/*` routes (providers, credentials, runs) per [`06_API.md`](06_API.md).
- [x] `/model-playground` page + `features/model-playground/` frontend, reachable from sidebar and command palette.
- [x] `docs/Security.md` outbound-network-calls section.
- [x] `anthropic` dependency added to `backend/requirements.txt` and [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md).
- [x] Backend unit + integration tests per [`07_TESTING.md`](07_TESTING.md) — 27 new tests, full suite passing.

## Dependencies

Outbound network calls and provider API-key storage are resolved: [ADR-0011](../../decisions/0011-model-playground-provider-credential-security.md) (credential storage & security posture) and [ADR-0012](../../decisions/0012-model-playground-provider-sdk-selection.md) (provider/SDK selection), both **Accepted 2026-07-29**. No other phase dependency blocks this one — Phase 05 has no upstream phase prerequisite per [`../../02_ROADMAP.md`](../../02_ROADMAP.md) §4.

## Milestones

- [x] **Milestone 1 — Backend foundation:** models, migration, credential CRUD service, provider availability endpoint, both provider adapters, run orchestration service (with concurrent dispatch, per-target timeout/error isolation), all routes, backend tests passing.
- [x] **Milestone 2 — Frontend:** `features/model-playground/` (api.ts + components), `/model-playground` page, nav-registry entry, all UI states (empty/loading/error/populated) per [`02_UI.md`](02_UI.md).
- [x] **Milestone 3 — Verification & closeout:** manual verification pass (per [`07_TESTING.md`](07_TESTING.md) §3) in a running dev server, `08_ACCEPTANCE.md` fully checked off (see one partial item noted there), `CURRENT_STATE.md` reflects reality, final checkpoint produced.

> Each milestone completion is a checkpoint trigger — see [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1.

## Risks

- **Technical:** concurrent outbound calls with independent timeouts is more orchestration complexity than any existing Forge feature has needed — mitigated by keeping the adapter interface minimal and testing failure-isolation explicitly (per `07_TESTING.md` §1).
- **Technical:** provider SDKs (`openai`, `anthropic`) evolve independently of Forge's release cycle — a breaking SDK upgrade could surface here first among Forge's dependencies. No mitigation beyond normal dependency-update vigilance; not a blocking risk for v1.
- **Product/UX:** two providers is a thin "comparison" experience — acceptable for v1 per ADR-0012, but the value proposition weakens if a user expects more providers immediately. Tracked as a future roadmap item, not a v1 blocker.
- **Security:** this is Forge's first UI-configurable outbound-credential feature — mitigated by ADR-0011's write-only, encrypted-at-rest, decrypt-only-at-call-time design, matching Secrets' existing encryption guarantee.
- **Existing features:** none touched beyond an additive `nav-registry.ts` entry — no consolidation risk (unlike Phase 04/07/08).

## Definition of Complete

- [x] All deliverables above are shipped and meet [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md).
- [x] [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criteria are checked off (one item, AC18, is honestly flagged as a QA ticket rather than falsely marked done — see [`QA/QA-0001-keyboard-activation-audit.md`](QA/QA-0001-keyboard-activation-audit.md)).
- [x] [`CURRENT_STATE.md`](CURRENT_STATE.md) reflects reality with no stale "In Progress" items.
- [x] A final checkpoint has been produced per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md).
- [x] Release Candidate audit complete, zero BLOCKERs (per [`../../12_BUG_CLASSIFICATION.md`](../../12_BUG_CLASSIFICATION.md)) — see [`POST_IMPLEMENTATION_REVIEW.md`](POST_IMPLEMENTATION_REVIEW.md).
- [x] Owner sign-off recorded — see [`CURRENT_STATE.md`](CURRENT_STATE.md).
- [ ] PR opened, reviewed, and merged to `master`; release tagged; implementation directory frozen — the remaining steps in [`../../13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md), not part of this checkpoint.

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [01_SPEC.md](01_SPEC.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
