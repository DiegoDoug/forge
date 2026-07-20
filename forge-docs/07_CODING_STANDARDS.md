# 07 — Coding Standards

> **Purpose:** Encode the conventions that keep the modular monolith's internal boundaries real, so any Claude Code session (or human) produces code indistinguishable in style from the rest of the codebase.
> **Scope:** Code-level conventions for both frontend and backend. Product-level judgment calls live in [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md).
> **Ownership:** TODO — assign an engineering standards owner.
> **Status:** Draft — derived from existing codebase conventions in [`../docs/FolderStructure.md`](../docs/FolderStructure.md) and [`../docs/Contributing.md`](../docs/Contributing.md)
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** [03_ARCHITECTURE.md](03_ARCHITECTURE.md)
> **Supersedes:** —

---

## 1. Hard rules (violating these requires an ADR, not just a preference)

- [ ] **Features don't import from each other.** `features/vault` never imports from `features/notes`. Shared code goes in `lib/` or `components/`.
- [ ] **`api.ts` is the only file in a feature that knows its backend endpoint shapes.** Pages/components consume hooks it exports; no ad hoc `fetch` calls elsewhere.
- [ ] **Backend routers stay thin.** Validation lives in Pydantic schemas; business logic lives in `services/`; routers wire the two together and shape the HTTP response.
- [ ] **Models are the schema source of truth.** Every schema change is an explicit Alembic migration (except the historical initial migration built from `SQLModel.metadata`).
- [ ] **Never expose ORM objects directly** — always shape responses through `schemas/`.

## 2. Naming conventions

- [ ] TODO: Confirm and document file naming (kebab-case vs. camelCase) per directory — currently consistent by convention, not written down.
- [ ] TODO: Document component naming (PascalCase files for components, confirmed already in use).
- [ ] Backend: `snake_case` for Python modules/functions, `PascalCase` for SQLModel/Pydantic classes.

## 3. Typing & validation

- [ ] All backend request/response shapes go through Pydantic schemas — no raw `dict` payloads.
- [ ] All frontend forms validate through `zod` schemas paired with `react-hook-form`.
- [ ] TypeScript `strict` mode — TODO: confirm `tsconfig.json` setting matches this and document any exceptions.

## 4. Testing expectations

- [ ] New backend service logic gets unit tests under `backend/tests/`.
- [ ] New API routes get at least one integration test exercising the real router → service → (test) database path.
- [ ] Frontend: TODO — confirm current test tooling/coverage expectations (none observed in the current stack table; see [06_TECH_STACK.md](06_TECH_STACK.md) — a testing library has not yet been added for the frontend).
- [ ] See [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md) for the gate this feeds into, and each phase's `07_TESTING.md`.

## 5. Documentation-in-code

- Comments explain *why*, not *what* — a comment restating the code is noise.
- Non-obvious workarounds (see the session-cookie `Secure` flag precedent in [`../docs/DecisionLog.md`](../docs/DecisionLog.md)) must be commented with a pointer to the decision record, not silently reproduced.

## 6. Git & review conventions

- [ ] TODO: Document commit message conventions (currently observed: short imperative subject, e.g. "Add Documents tab...", "Fix notes pin/archive/delete buttons...").
- [ ] TODO: Document branch naming / PR size expectations.
- See [`../docs/Contributing.md`](../docs/Contributing.md) for existing contributor-facing guidance.

## 7. TODO

- [ ] TODO: Add a linting/formatting section once ESLint/Prettier/Ruff/Black configs are audited and documented here explicitly (ESLint config exists at `frontend/eslint.config.mjs`; Python side not yet documented).
- [ ] TODO: Confirm whether a pre-commit hook framework is (or should be) in use.

## 8. Cross-references

- [../docs/FolderStructure.md](../docs/FolderStructure.md)
- [../docs/Contributing.md](../docs/Contributing.md)
- [03_ARCHITECTURE.md](03_ARCHITECTURE.md)
- [08_DEFINITION_OF_DONE.md](08_DEFINITION_OF_DONE.md)
- [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md)
