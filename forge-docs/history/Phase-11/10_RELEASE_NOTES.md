# Claude MCP / Second Brain — Release Notes

> **Purpose:** The release-facing summary of Phase 11 — what shipped, what to check before upgrading. Not a duplicate of `CURRENT_STATE.md` (the working log) — this is what a user or another engineer reads to understand what changed.
> **Scope:** This phase only.
> **Status:** 🔒 **Released & Frozen.** Committed to `master` at `8d8ddd8`, tagged `v0.11.0`, 2026-08-20. Owner authorized this release after completing the mandatory human review gate item by item in chat — architecture, auth model, scopes, tool surface, data exposure (including the `forge://projects` limitation below, reviewed verbatim), `confirm: true` for v1, Claude workflow (cross-session continuity independently live-verified), and deployment model — see [`../../implementation/Phase-11-Claude-MCP/IMPLEMENT.md`](../../implementation/Phase-11-Claude-MCP/IMPLEMENT.md)'s "mandatory human review gate" section for the full record. Per [`../../13_PHASE_LIFECYCLE.md`](../../13_PHASE_LIFECYCLE.md) §4, this phase now accepts bug fixes only — no new features, no architectural changes; further MCP work begins as a new phase.
> **Version:** `v0.11.0`
> **Last Updated:** 2026-08-20
> **Depends On:** [`../../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md`](../../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md), [`../../implementation/Phase-11-Claude-MCP/08_ACCEPTANCE.md`](../../implementation/Phase-11-Claude-MCP/08_ACCEPTANCE.md)

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
- **`forge://projects` (a static MCP resource) cannot enforce its documented `forge:read` scope — accepted, intentional technical debt, reviewed and explicitly signed off on by the owner, not a defect this release papers over.** A genuine limitation of the installed MCP SDK version (no per-request auth context is available to a static, non-templated resource's read function), independently confirmed twice — by Milestone 4's Agentic Review and again by Milestone 5's whole-phase RC review, both by reading the SDK's own source directly. Any validly-authenticated MCP token can read this resource (project name/description/color/counts — no secrets) regardless of its granted scopes; `forge://projects/{id}` and every tool enforce scope normally. Documented in `06_API.md` §5's footnote, `docs/Security.md`, and `app/mcp/resources.py`'s own docstring. **This item is deliberately kept visible here, in the permanent release record, rather than left to fade into implementation history** — revisit if this MCP SDK ever adds per-request context for static resources, or if Forge's threat model changes from "one operator, one master key."
- **A small number of write tools produce no audit-log row**, matching pre-existing REST behavior exactly rather than introducing new logging as a side effect of adding MCP: `forge_update_note`/`forge_update_document` (Note/Document PATCH has never logged, for any caller), `forge_link_items`/`forge_unlink_items` (knowledge-graph link mutations have never logged, for any caller). Every create and delete does log, with `source="mcp"`.
- **Process note, not a product change**: preparing this milestone's Docker verification, the implementing session nearly deleted a local dev database before catching itself. No data was lost, but the reasoning behind the near-miss was unsound, not merely lucky — the owner required it be converted into a permanent safeguard as a condition of release sign-off. Added: `../../09_CLAUDE_CODE_RULES.md` §3/§3.1, a repo-wide rule (not scoped to this phase) against deleting/resetting local DB or Docker-volume state a session did not itself create for that verification run.

## Bug Fixes

None user-facing — this phase adds new capability; it does not modify existing behavior. One internal fix worth recording for transparency: Milestone 5's whole-phase RC review found that a Milestone-3-era regression test (`test_forge_search_never_returns_secret_data`) never actually created a `Secret`, despite its docstring and several documents describing it as adversarial proof that `forge_search` can't leak Secrets. The live product was never vulnerable — the reviewer independently proved this with a real Secret before flagging the test — and the test itself was fixed and re-verified before this release. (Other milestone-internal bugs found and fixed during each milestone's own Agentic Review repair cycle — a `confirm` boolean-coercion bypass, a raw exception leak on a bad `project_id`, empty tool descriptions, a dangling-link reference in `forge_context`'s output, a stale API-contract claim — are implementation-detail history, not user-facing fixes to prior releases; see each milestone's `reviews/AGENTIC_REVIEW_M*.md` for the full record.)

## Known Issues

- No automated frontend test suite exists in this repository (pre-existing, Phase 09 Known Issue) — the new Settings-page token UI's regression safety rests on `tsc`/`eslint`/production build plus live manual verification, not automated tests.
- Resource-read errors (`forge://projects`, `forge://projects/{id}`, on an unknown ID) surface as a generic, unclassified MCP protocol error rather than a clean "not found" message — a Milestone 4 finding, classified non-blocking, left as backlog. The equivalent tools (`forge_get_project`, etc.) already give clean messages.
- The FDK verification tooling's own self-test suite (`tools/tests/`) showed 10 environment-specific failures (a Windows/Git-Bash subprocess-invocation quoting issue, unrelated to any Forge/Phase-11 code) during Milestone 4 and part of Milestone 5; by the whole-phase RC review it was fully green (113/113) with the underlying environment condition no longer present, not further root-caused. Not a Phase 11 regression either way.

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

- [`../../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md`](../../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md)
- [`../../implementation/Phase-11-Claude-MCP/08_ACCEPTANCE.md`](../../implementation/Phase-11-Claude-MCP/08_ACCEPTANCE.md)
- [`../../implementation/Phase-11-Claude-MCP/01_SPEC.md`](../../implementation/Phase-11-Claude-MCP/01_SPEC.md)
- [`../../implementation/Phase-11-Claude-MCP/06_API.md`](../../implementation/Phase-11-Claude-MCP/06_API.md)
- [`../../implementation/Phase-11-Claude-MCP/IMPLEMENT.md`](../../implementation/Phase-11-Claude-MCP/IMPLEMENT.md) — the human review gate's full record
- [`../../implementation/Phase-11-Claude-MCP/reviews/`](../../implementation/Phase-11-Claude-MCP/reviews/) — `AGENTIC_REVIEW_M1.md` through `M5.md`
- [`../../../docs/MCP_Usage.md`](../../../docs/MCP_Usage.md)
- [`../../../docs/Security.md`](../../../docs/Security.md)
- [`../../../docs/Deployment.md`](../../../docs/Deployment.md)
- [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) — §3.1, the dev-state safeguard added this milestone
