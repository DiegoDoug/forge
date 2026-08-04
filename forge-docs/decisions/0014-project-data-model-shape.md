# ADR-0014 — Project data model shape

> **Purpose:** Resolve where "Project" (Phase 06) lives in the data model, closing the open question tracked in [`../03_ARCHITECTURE.md`](../03_ARCHITECTURE.md) §4.
> **Scope:** The Project table's shape and its relationship to Secrets, Notes, Documents, and Model Playground runs. Not the full Phase 06 feature spec — that's [`../implementation/Phase-06-Projects/01_SPEC.md`](../implementation/Phase-06-Projects/01_SPEC.md).
> **Ownership:** Project owner (approved 2026-08-02)
> **Status:** Accepted
> **Version:** 0.1.0
> **Last Updated:** 2026-08-02
> **Depends On:** [ADR-0005](0005-projects-primary-organizational-unit.md), [ADR-0011](0011-model-playground-provider-credential-security.md), [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
> **Supersedes:** —

---

## 1. Context

ADR-0005 affirmed Projects as Forge's primary organizational unit — the concept every other feature (Notes, Documents, Secrets, later Prompt Studio and Model Playground) is expected to eventually scope into — but explicitly deferred the actual data model to Phase 06's own spec. `03_ARCHITECTURE.md` §4 has carried the open question since: "a new top-level table that Vault/Secrets/Notes/Documents gain an optional foreign key to, or a purely client-side grouping?" Phase 06 cannot start without an answer, and this is exactly the kind of schema/architecture decision [`09_CLAUDE_CODE_RULES.md`](../09_CLAUDE_CODE_RULES.md) §3 requires stopping for ("any schema change that isn't a straightforward additive migration").

The user has also confirmed Phase 06's scope includes a project-level default AI provider/model, building on the Phase 05 provider abstraction (`app.services.model_playground.providers.PROVIDER_REGISTRY`) rather than a new credential system.

## 2. Decision

**Project is a new top-level table** (`projects`), not a purely client-side grouping. `Secret`, `Note`, and `Document` each gain an additive, nullable `project_id` (FK to `projects.id`, indexed, no DB-level cascade). `PlaygroundRun` also gains a nullable `project_id`, so a project's AI runs can be listed without a join table.

Rationale for a real table over a client-side-only grouping: Secrets, Notes, and Documents are already server-persisted, queried, and filtered server-side (folders, search, archived flags); a client-only grouping would mean re-deriving project membership in every list endpoint from scratch client-side, duplicate the filtering logic three times, and provide no server-side integrity (an entity could silently reference a project that no longer exists). A real table lets every existing list endpoint gain a single optional `project_id` query filter, consistent with how `folder_id` already filters Secrets.

Deletion behavior: **unscope, never cascade-delete.** Deleting a project sets `project_id = NULL` on every Secret/Note/Document/PlaygroundRun that referenced it, then deletes the project row. Per [`01_PRODUCT_PRINCIPLES.md`](../01_PRODUCT_PRINCIPLES.md) honest-gaps-over-fake-completeness and the mission's explicit "do not destroy existing data" constraint, a Project is an organizational label, not an owner — secrets in particular must never be destroyed as a side effect of deleting a workspace grouping around them. This is enforced in the service layer (an explicit bulk `UPDATE ... SET project_id = NULL` before the delete), not relied on as a DB-level `ON DELETE SET NULL`, matching the existing codebase's pattern of declaring plain `foreign_key=` fields without DB-level cascade actions (see `Secret.folder_id`, `PlaygroundResult.run_id`) and doing lifecycle logic explicitly in `services/`.

AI configuration: `Project.default_provider: str | None` and `Project.default_model: str | None` store plain string references into `PROVIDER_REGISTRY` (same pattern as `PlaygroundResult.provider`/`.model` — a snapshot key, not a foreign key to `ProviderCredential`), validated the same way `model_playground` schemas already validate provider/model pairs. No API key or credential material is ever stored on `Project`; project-level "AI run" actions call directly into the existing `model_playground.runs.create_run()` service, reusing the existing credential lookup, adapter dispatch, and error handling rather than duplicating any of it.

## 3. Alternatives considered

- **Purely client-side grouping** (a client-persisted list of entity IDs per project, no server table) — rejected: no server-side filtering/integrity, triples the list-endpoint logic, and contradicts ADR-0005's framing of Projects as something every other feature "scopes into," which implies query-time membership, not a client-side view concern.
- **Join table** (`project_members(project_id, entity_type, entity_id)`) instead of per-table FK columns — rejected for this phase: more general (would support many-to-many or multi-project membership) but Phase 06's confirmed scope is one-project-per-entity, and a join table complicates every existing list query with a join instead of one indexed nullable column. Revisit only if a real multi-project-membership need emerges.
- **Cascade-delete children with a project** — rejected: destroys Vault secrets as a side effect of an organizational action, which is both a data-loss risk and inconsistent with Secrets' own "nothing is silently destroyed" posture (soft version history, no hard delete of versions).
- **New credential/provider system scoped to Project** — rejected per the mission's explicit constraint and ADR-0011/0012/0013: provider credentials remain centralized in Model Playground; Project only stores a reference (provider key + model string), and execution always goes through the existing `runs.create_run()` path.

## 4. Consequences

- Existing `Secret`, `Note`, `Document`, `PlaygroundRun` tables each need one additive nullable indexed column — a straightforward additive migration, no destructive schema change, no data loss.
- Every existing list endpoint for Secrets/Notes/Documents gains an optional `project_id` query filter, following the existing `folder_id`/`archived` filter pattern — no breaking change to existing callers (new field, new optional filter).
- Deleting a project is O(3) bulk updates + 1 delete, done inside the `projects` service, not via DB cascade — keeps the "never destroy Vault data" invariant enforceable and testable in one place.
- Project-level AI actions have zero new outbound-call code paths: they call the exact same `model_playground.runs.create_run()` used by Model Playground today, so ADR-0011's credential-security posture and ADR-0013's provider list apply unchanged.
- Forecloses (for now) multi-project membership per entity — acceptable per confirmed Phase 06 scope; would need a follow-up ADR to move to a join table later.

## 5. Cross-references

- [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
- [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
- [0005-projects-primary-organizational-unit.md](0005-projects-primary-organizational-unit.md)
- [0011-model-playground-provider-credential-security.md](0011-model-playground-provider-credential-security.md)
- [../implementation/Phase-06-Projects/01_SPEC.md](../implementation/Phase-06-Projects/01_SPEC.md)
- [../implementation/Phase-06-Projects/04_DATABASE.md](../implementation/Phase-06-Projects/04_DATABASE.md)
