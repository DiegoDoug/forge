# Prompt Studio — Testing

> **Purpose:** Test plan for this phase — what must be covered before it can be marked done.
> **Scope:** Test strategy and enumeration. Pass/fail criteria live in 08_ACCEPTANCE.md.
> **Ownership:** Lead Software Engineer (phase-assigned).
> **Status:** Accepted — approved alongside [`01_SPEC.md`](01_SPEC.md) 2026-07-22.
> **Last Updated:** 2026-07-22

---

## 1. Backend tests

**Unit tests** (`backend/tests/test_prompt_studio_service.py` and `test_prompt_studio_templating.py` — flat under `backend/tests/`, matching the existing `test_project_init_service.py`/`test_project_init_renderer.py` naming convention, in-memory SQLite per [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) §4):

- `templating.py`: `extract_placeholders` finds every `${name}` in a body; ignores an escaped `$$`; returns an empty set for a body with no placeholders; a body referencing the same name twice yields one entry (a set, not a list).
- `create()`: happy path creates a `Prompt` at version 1 with exactly one `PromptVersion` (note `"Initial version"`); a body referencing an undeclared variable is rejected before any row is written (schema-level, but verified end-to-end through the service call); an `ActivityLog` row is written with `action=created, entity_type="prompt"`.
- `update_metadata()`: changes `name`/`description`/`tags` without incrementing `version_number` and without creating a new `PromptVersion` row (the key invariant distinguishing it from `update_content`); partial payload (only `name` supplied) leaves `description`/`tags` untouched.
- `update_content()`: increments `version_number`; creates exactly one new `PromptVersion` snapshotting the **pre-update** body/variables (not the post-update ones — this is the easiest place to introduce an off-by-one direction bug); rejects an undeclared-placeholder body the same way `create()` does; writes an `ActivityLog` row with the new version number in its summary.
- `delete()`: cascades — deleting a `Prompt` with N versions leaves zero `PromptVersion` rows for that `prompt_id`; the `ActivityLog` summary captures the prompt's name (verifying it's captured before the row is gone, per [`03_BACKEND.md`](03_BACKEND.md) §2).
- `duplicate()`: the new prompt has its own id, starts at version 1 with exactly one `PromptVersion`, copies `body`/`variables`/`tags` from the source, and does not share any row (versions, id) with the source; deleting the source afterward does not affect the duplicate.
- `list_versions()` / `get_version()`: newest-first ordering; `get_version()` raises `NotFoundError` when the version id exists but belongs to a *different* prompt's `prompt_id` (the cross-prompt-lookup case explicitly called out in [`06_API.md`](06_API.md) §3).
- `restore_version()`: restoring version N snapshots the prompt's pre-restore current content as a new version **before** applying N's content; the resulting `version_number` is `current + 1` (never re-uses or decrements to `N`); restoring, then restoring again to a different earlier version, still preserves every version created along the way (no version is ever overwritten or deleted by a restore).
- Idempotence/edge cases per the playbook's testing checklist: update A then update A again (two sequential `update_content` calls produce two new versions, not one); delete then re-fetch (404, not a stale read); restore to the *current* version_number itself (a no-op-ish case — still creates a new version per the stated rule, since the rule is unconditional, not "only if different" — confirm this is the desired behavior during implementation-review, not assumed silently).

**Integration tests** (`backend/tests/test_prompt_studio_api.py` — flat, matching `test_project_init_api.py`, FastAPI `TestClient`, per [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) §4):

- Every endpoint in [`06_API.md`](06_API.md) §1: happy path → expected status/shape; missing required field → `422`; not-found id → `404`; unauthenticated request → `401` (via the existing `AuthDep`, unmodified).
- `PUT .../content` with a body referencing an undeclared variable → `422`, and confirms zero new `PromptVersion` rows were created (the rejection happens before any write, not as a partial/rolled-back write).
- Full lifecycle test: create → update content (v2) → update content again (v3) → list versions (3 entries) → restore v1 (v4, content matches v1) → duplicate (new id, version 1) → delete original (204, then `GET` on it is `404`) — mirrors the golden path in [`02_UI.md`](02_UI.md) and doubles as the basis for §3's manual browser script below.

## 2. Frontend tests

No frontend test framework exists yet in this codebase (per [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md) §5 and [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) §4 — both explicitly note this is a TODO, not yet chosen). Per Phase 02's precedent, this phase does not introduce a new frontend test framework unilaterally (that would be a new dependency decision per [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md) §4, requiring the same "ask first" treatment as any other new dependency) — frontend correctness is covered by build/lint/typecheck plus manual browser verification (§3), matching every prior phase.

- [x] `npm run build` and `npm run lint` clean.
- [x] `tsc --noEmit` passes.

## 3. Manual verification

Golden path, run in a real browser against the running app (not just `TestClient`), per [`../../14_IMPLEMENTATION_PLAYBOOK.md`](../../14_IMPLEMENTATION_PLAYBOOK.md) §5:

1. Navigate to Prompt Studio via the sidebar; confirm it's also reachable via ⌘K.
2. Empty state: with zero prompts, confirm the "No prompts yet" CTA (not blank space).
3. Create a prompt with two variables (one required `string`, one optional `number` with a default); confirm the body editor highlights both `${name}` tokens as declared.
4. Type an undeclared `${typo}` into the body and attempt to save; confirm an inline error, not a silent failure or a generic crash.
5. Fill the Preview panel's inputs; confirm the rendered output updates live and the required-but-blank case highlights the unresolved token distinctly (not just blank).
6. Copy the rendered output; confirm the existing copy-confirmation UX (matching Secrets/Generators' copy pattern).
7. Edit the body and save; confirm the version badge increments and a new entry appears in History.
8. Open History, diff v1 vs. v2; confirm additions/removals are marked with text, not color alone.
9. Restore v1; confirm the confirmation dialog appears, and after confirming, the body reverts and a new version (v3) appears in history (v1 and v2 are still present, not overwritten).
10. Duplicate the prompt; confirm a new list entry appears with `(copy)` suffixed and its own independent version 1.
11. Delete the duplicate; confirm the confirmation dialog, then confirm it disappears from the list.
12. Open the existing Activity/Recent Activity view; confirm create, update (both saves), restore, duplicate, and delete all appear with sensible summaries.
13. Search by name and filter by tag; confirm both narrow the list, and confirm the "no results" state is distinct from the true-empty state.
14. Resize to 375px width; confirm the list/editor collapse to single-pane stack navigation with a working back affordance (per [`02_UI.md`](02_UI.md) §4).
15. Toggle dark mode; confirm the editor, diff view, and all panels render correctly in both themes.
16. Tab through the entire editor (metadata, variables, body editor, preview, toolbar) using only the keyboard; confirm every action is reachable (per [`02_UI.md`](02_UI.md) §5).

## 4. Regression risk

None — this is a wholly new, isolated feature (`services/prompt_studio/`, `features/prompt-studio/`, two new tables). It does not touch Secrets, Notes, Documents, Generators, Crypto, Converters, Utilities, Ingest, Workbench, Search, Project Init, or Settings. The only shared surface touched at all is `frontend/lib/nav-registry.ts` (a new array entry, no structural change) and `backend/app/api/router.py` (a new router included, no existing router modified) — both additive, low-risk changes with an established, twice-repeated precedent (Phase 01, Phase 02).

As a spot-check regardless (per [`../../14_IMPLEMENTATION_PLAYBOOK.md`](../../14_IMPLEMENTATION_PLAYBOOK.md) §6's audit guidance), confirm during Milestone 3 integration testing that: the sidebar and command palette still list every pre-existing item correctly, and the full existing backend test suite (`pytest backend/tests/ -v`) still passes alongside the new tests.

## 5. TODO

- [ ] None — this document is filled in for the specification review pass.

## 6. Cross-references

- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
