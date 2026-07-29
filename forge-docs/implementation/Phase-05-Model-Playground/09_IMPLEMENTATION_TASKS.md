# Model Playground — Implementation Tasks

> **Purpose:** The ordered, checkable task list Claude Code executes against for this phase — the direct input to the checkpoint protocol's task-count trigger.
> **Scope:** This phase only. Tasks here must trace back to a requirement in 01_SPEC.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Complete — all 19 tasks done, phase implemented and verified.
> **Last Updated:** 2026-07-29

---


## 1. Task list

**Milestone 1 — Backend foundation**

- [x] T1 — Add `anthropic` to `backend/requirements.txt`; update [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md) §2/§5 to reflect it.
- [x] T2 — Add `backend/app/models/model_playground.py` (`ProviderCredential`, `PlaygroundRun`, `PlaygroundResult`) per [`04_DATABASE.md`](04_DATABASE.md) §1–§2.
- [x] T3 — Add Alembic migration `0006_model_playground.py` creating all three tables.
- [x] T4 — Add `backend/app/schemas/model_playground.py` per [`06_API.md`](06_API.md) §2.
- [x] T5 — Add `services/model_playground/providers/base.py` (`ProviderAdapter` protocol, `AdapterResult`) + `openai_adapter.py` + `anthropic_adapter.py` per [`03_BACKEND.md`](03_BACKEND.md) §2.
- [x] T6 — Add `services/model_playground/credentials.py` (list/create-or-replace/delete credential, provider availability) per [`03_BACKEND.md`](03_BACKEND.md) §2.
- [x] T7 — Add `services/model_playground/runs.py` (create/list/get/delete run, concurrent dispatch with per-target timeout + error isolation) per [`03_BACKEND.md`](03_BACKEND.md) §2.
- [x] T8 — Add `api/routes/model_playground.py` (all 8 endpoints per [`06_API.md`](06_API.md) §1), register the router in `app/api/routes/__init__.py`.
- [x] T9 — Backend unit tests: credential CRUD/encryption round-trip, provider-availability reporting, run orchestration success/error/timeout/partial-failure, cap/validation rejections — per [`07_TESTING.md`](07_TESTING.md) §1.
- [x] T10 — Backend integration tests: full router → service → test-db path for credentials and runs, auth-required check — per [`07_TESTING.md`](07_TESTING.md) §1.

> **Checkpoint at T10 (Milestone 1 complete)** — per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1.

**Milestone 2 — Frontend**

- [x] T11 — Add `frontend/features/model-playground/api.ts` per [`05_COMPONENTS.md`](05_COMPONENTS.md) §3–§4.
- [x] T12 — Add `provider-list.tsx` + `credential-form-dialog.tsx`.
- [x] T13 — Add `prompt-composer.tsx` + `result-panel.tsx`.
- [x] T14 — Add `run-view.tsx` + `run-history-list.tsx`.
- [x] T15 — Add `frontend/app/(app)/model-playground/page.tsx` composing the above; add the nav-registry entry per [`02_UI.md`](02_UI.md) §2.
- [x] T16 — All empty/loading/error/populated states implemented per [`02_UI.md`](02_UI.md) §3; keyboard/dark-mode/responsive pass per §4–§5.

> **Checkpoint at T16 (Milestone 2 complete)** — per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1.

**Milestone 3 — Verification & closeout**

- [x] T17 — Manual verification pass per [`07_TESTING.md`](07_TESTING.md) §3, in a running dev server (per this session's UI-verification workflow).
- [x] T18 — Check off every [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) criterion; fix anything that fails.
- [x] T19 — Update `CURRENT_STATE.md` to reflect reality; log the final checkpoint to [`../../history/`](../../history/README.md).

> **Checkpoint at T19 (Milestone 3 complete / phase done)** — per [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1.

> Reminder: 10–12 completed tasks is itself a checkpoint trigger, independent of milestone boundaries — see [`../../10_CHECKPOINT_PROTOCOL.md`](../../10_CHECKPOINT_PROTOCOL.md) §1. T10 and T16 already align with this given the task count above.

## 2. Task ordering notes

- T2 (models) must precede T3 (migration) must precede T4–T7 (schemas/services reference the models) must precede T8 (routes wire services to HTTP).
- T5 (provider adapters) has no dependency on T2–T4 and could be built in parallel with them if split across sessions, but is listed after them here for a single linear read.
- T9–T10 (tests) depend on T2–T8 all existing.
- T11 (api.ts) must precede T12–T14 (components consume its hooks) must precede T15 (page composes components).
- Milestone 2 (frontend) depends on Milestone 1 (backend) being functionally complete — the frontend calls real endpoints, not mocks, per [`07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md).

## 3. TODO

- [ ] Assign a phase owner.

## 4. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [CURRENT_STATE.md](CURRENT_STATE.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md)
