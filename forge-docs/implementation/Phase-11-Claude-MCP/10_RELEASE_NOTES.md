# Claude MCP / Second Brain — Release Notes

> **Purpose:** The release-facing summary of Phase 11 — what shipped, what to check before upgrading. Not a duplicate of `CURRENT_STATE.md` (the working log) — this is what a user or another engineer reads to understand what changed.
> **Scope:** This phase only.
> **Status:** 📝 **Draft — not yet released.** All five milestones are complete and independently gated PASS (Milestone 5's Agentic RC Review result recorded in `VERIFICATION_CONTRACT.md`/`reviews/AGENTIC_REVIEW_M5.md`), and the mandatory human review gate (`IMPLEMENT.md`'s checklist) is now complete — the owner reviewed and approved the phase item by item in chat, 2026-08-20. Phase 11 is clear for release; this phase still does not self-release. This file will be finalized, dated, and archived to `../../history/Phase-11/` only as part of the owner's own explicit release action.
> **Version:** Not yet tagged.
> **Last Updated:** 2026-08-20
> **Depends On:** [`CURRENT_STATE.md`](CURRENT_STATE.md), [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md)

---

## New Features

- **MCP server for Claude / Claude Code**, mounted in-process inside the existing FastAPI backend at `/mcp` (Streamable HTTP transport), reachable through the same nginx reverse proxy as the REST API. Off by default (`FORGE_MCP_ENABLED=false`).
- **18 MCP tools** across five domains:
  - Notes/Documents/Projects CRUD (`forge_get/create/update/delete_note`, the same four for documents, `forge_list/get/create/update_project` — no project delete).
  - Retrieval (`forge_search`, `forge_context` — a Claude-oriented aggregate: project + matched items + tags + links, in one call).
  - Knowledge graph (`forge_link_items`, `forge_unlink_items`).
  - Memory (`forge_capture_decision`, `forge_capture_session` — thin wrappers over `forge_create_note` with a reserved-tag convention; proven end-to-end across genuinely independent MCP sessions, not just within one connection).
- **2 MCP resources**: `forge://projects` (list, auto-discoverable) and `forge://projects/{id}` (detail).
- **Scoped, revocable bearer-token authentication**, independent of the browser session cookie — `forge:read`/`forge:write`/`forge:delete` scopes, individually issued and revoked, hashed at rest, shown exactly once at creation.
- **Settings → Claude / MCP access**: a new UI panel to issue and revoke MCP tokens without leaving the browser — list active/revoked tokens, create with a scope picker, one-time reveal-and-copy dialog, named-confirm revoke.
- **`docs/MCP_Usage.md`**: a Claude-oriented guide to the tool surface, the `forge_context`-before-you-write workflow, and a worked memory-capture example.

## Breaking Changes

None. Every existing REST endpoint, service function signature (beyond additive, default-preserving keyword parameters), and frontend page behaves exactly as before. `ActivityLog` gained one additive column (`source`, default `"ui"`) — every pre-existing row and caller is unaffected.

## Migrations

One additive migration: `mcp_tokens` table (new), `activity_log.source` column (new, nullable-safe default). Verified up/down/up in Milestone 1; no further schema changes through Milestone 5.

## Security Notes

- **Secrets, Settings, and `services/crypto/` are structurally unreachable through MCP** — enforced by a recursive static import-boundary check across `app/mcp/**` in the backend test suite (not just a documented convention), re-confirmed at every milestone including this one.
- **Deletes are permanent and require `confirm: true`** as a literal, structurally-validated boolean — never inferred from conversation context.
- **`forge://projects` (a static MCP resource) cannot enforce its documented `forge:read` scope** — a genuine limitation of the installed MCP SDK version (no per-request auth context is available to a static, non-templated resource's read function), independently confirmed by Milestone 4's Agentic Review by reading the SDK's own source. Any validly-authenticated MCP token can read this resource (project name/description/color/counts — no secrets) regardless of its granted scopes; `forge://projects/{id}` and every tool enforce scope normally. Documented in `06_API.md` §5, `docs/Security.md`, and `app/mcp/resources.py`'s own docstring — judged an acceptable narrow exception given the low sensitivity of the data and this phase's single-operator threat model, not silently built around.
- **A small number of write tools produce no audit-log row**, matching pre-existing REST behavior exactly rather than introducing new logging as a side effect of adding MCP: `forge_update_note`/`forge_update_document` (Note/Document PATCH has never logged, for any caller), `forge_link_items`/`forge_unlink_items` (knowledge-graph link mutations have never logged, for any caller). Every create and delete does log, with `source="mcp"`.

## Bug Fixes

None — this phase adds new capability; it does not modify existing behavior. (Milestone-internal bugs found and fixed during each milestone's own Agentic Review repair cycle — a `confirm` boolean-coercion bypass, a raw exception leak on a bad `project_id`, empty tool descriptions, a dangling-link reference in `forge_context`'s output, a stale API-contract claim — are implementation-detail history, not user-facing fixes to prior releases; see each milestone's `reviews/AGENTIC_REVIEW_M*.md` for the full record.)

## Known Issues

- No automated frontend test suite exists in this repository (pre-existing, Phase 09 Known Issue) — the new Settings-page token UI's regression safety rests on `tsc`/`eslint`/production build plus live manual verification, not automated tests.
- Resource-read errors (`forge://projects`, `forge://projects/{id}`, on an unknown ID) surface as a generic, unclassified MCP protocol error rather than a clean "not found" message — a Milestone 4 finding, classified non-blocking, left as backlog. The equivalent tools (`forge_get_project`, etc.) already give clean messages.
- The FDK verification tooling's own self-test suite (`tools/tests/`) has 10 pre-existing, environment-specific failures on this Windows/Git-Bash development machine (a subprocess-invocation quoting issue unrelated to any Forge/Phase-11 code) — not a Phase 11 regression, and out of this phase's scope to fix.

## Upgrade Notes

MCP is off by default — existing deployments are unaffected until an operator explicitly sets `FORGE_MCP_ENABLED=true`. To enable:

1. Set `FORGE_MCP_ENABLED=true` and a high-entropy `FORGE_MCP_BOOTSTRAP_TOKEN`, redeploy.
2. Provision a persistent token — via `curl` (see `docs/Deployment.md`) or, once the UI is running, **Settings → Claude / MCP access → Create token**.
3. Point Claude Code at it: `claude mcp add --transport http forge <your-forge-url>/mcp --header "Authorization: Bearer <token>"`.
4. Set `FORGE_MCP_BOOTSTRAP_ENABLED=false` and redeploy — closes provisioning entirely without affecting already-issued tokens.

No new required environment variables for instances that leave MCP disabled.

## Deferred Work

- **Token rotation ergonomics beyond revoke-and-reissue** — no in-place rotation exists; recorded as acceptable for this phase's scope, not revisited.
- **OAuth 2.0 for MCP auth** — the static bearer-token model is judged sufficient for a single-tenant, self-hosted instance; OAuth remains a possible future hardening step (`08_ACCEPTANCE.md` §6).
- **Whether Note/Document-update and knowledge-link-mutation logging should be added** (closing the audit asymmetry with Notes/Documents create/delete and Project update) — a genuine, still-open product question, not resolved by this phase; changing it would alter existing REST-facing behavior for every caller, not just MCP ones.
- **Whether AI-driven reads (`forge_search`, `forge_context`, `forge_get_*`) should be logged** at all, given the UI has never logged `viewed` actions either — same open-question status.
- **`forge_delete_project`** — deliberately not built (Projects unscope, not delete, their children today); whether to add it, and what a "confirm cascade" pattern would need, is left to a future phase.

## Cross-references

- [`CURRENT_STATE.md`](CURRENT_STATE.md)
- [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md)
- [`01_SPEC.md`](01_SPEC.md)
- [`06_API.md`](06_API.md)
- [`../../../docs/MCP_Usage.md`](../../../docs/MCP_Usage.md)
- [`../../../docs/Security.md`](../../../docs/Security.md)
- [`../../../docs/Deployment.md`](../../../docs/Deployment.md)
