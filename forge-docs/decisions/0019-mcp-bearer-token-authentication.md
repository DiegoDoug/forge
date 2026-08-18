# ADR-0019 — MCP authentication is a second, independent bearer-token scheme

> **Purpose:** Record the decision that Claude's MCP connection authenticates via a new, scoped, revocable bearer token — never the browser session cookie, never OAuth in this phase — and reconcile that with ADR-0004's "interactive workflows, not automation" default.
> **Scope:** MCP authentication/authorization model only. Not the full Phase 11 spec — that's [`../implementation/Phase-11-Claude-MCP/01_SPEC.md`](../implementation/Phase-11-Claude-MCP/01_SPEC.md) §4.
> **Ownership:** Project owner (approved 2026-08-18, with amendments — see §3; Milestone 1 authorized 2026-08-18)
> **Status:** Accepted
> **Version:** 1.0.0
> **Last Updated:** 2026-08-18
> **Depends On:** [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md), [0004-interactive-workflows-not-automation.md](0004-interactive-workflows-not-automation.md), [0018-mcp-server-integrated-not-separate-process.md](0018-mcp-server-integrated-not-separate-process.md)
> **Supersedes:** —

---

## 1. Context

Forge's only existing authentication is a browser session: a stateless HMAC token (`app/core/security.py`), delivered via an `httponly` `Set-Cookie`, verified by `require_auth`/`AuthDep` on nearly every REST route. It carries no identity or scope beyond a validity window, and is revoked only by rotating the master password (which invalidates every session at once). An MCP client is not a browser — it sends an `Authorization` header, not a cookie, and a persistent MCP connection is expected to stay valid across many Claude sessions over weeks, independent of whether the browser UI is open. Phase 11 also requires excluding Secrets/Settings/Crypto from what Claude can reach, which the existing all-or-nothing session token cannot express.

## 2. Decision

A new `Authorization: Bearer <token>` scheme, checked by request-level auth logic in `backend/app/mcp/` (ASGI middleware wrapping the mounted `/mcp` app — see implementation note in §4), entirely separate from `AuthDep`. Tokens are individually issued, scoped (`forge:read`/`forge:write`/`forge:delete`/`forge:secrets` — the last reserved, implemented by nothing in this phase), and revocable, backed by a new `mcp_tokens` table (`McpToken`) — the first individually-revocable credential in this codebase.

**Two credential tiers, never conflated:**
- A **bootstrap token** (`FORGE_MCP_BOOTSTRAP_TOKEN`/`_FILE`, gated by `mcp_bootstrap_enabled`) authenticates exactly one thing: `POST /api/mcp/tokens`, a REST route (not an MCP tool) that provisions a persistent token. It is never accepted by `/mcp` itself.
- A **persistent token**, provisioned through that route and shown once, is what Claude actually connects with. It can be revoked (`DELETE /api/mcp/tokens/{id}`) without touching the bootstrap credential or the master password.

**OAuth 2.0 is explicitly not built in this phase.** Claude Code supports OAuth for remote MCP servers, but standing up an authorization server is disproportionate for a single-tenant, self-hosted instance whose entire security model is already "one operator, one master key." A static, revocable bearer token fits that existing trust model; OAuth remains a documented option for a future hardening phase if Forge's deployment model changes (e.g. multi-user).

## 2.1 Reconciliation with ADR-0004 ("interactive workflows, not automation")

ADR-0004 establishes that Forge defaults against unattended automation acting on a user's behalf. Phase 11 is, by nature, about an external agent (Claude) acting inside Forge outside a human's direct click-by-click interaction — this is exactly the shape of thing ADR-0004 defaults against, so it is addressed here explicitly rather than silently treated as an exception.

This is judged different from the automation ADR-0004 guards against, on four grounds, all structural rather than aspirational:
1. **Every MCP write is scoped** — a token without `forge:write`/`forge:delete` cannot perform one, and scope is checked per-tool, not once at connection time.
2. **Every MCP write is token-gated and individually revocable** — unlike a cron job or webhook running under implicit standing permission, an MCP connection can be cut off without affecting anything else, immediately.
3. **Every MCP write is audited** — `ActivityLog` gets a `source="mcp"` entry indistinguishable in kind from a UI-originated one, so nothing happens invisibly.
4. **Every MCP session is initiated by a human's own Claude conversation** — there is no scheduled/triggered/webhook-driven path in this phase; a Claude session that calls an MCP tool does so because a person is, in that moment, talking to Claude and asking for something. This is closer to "a human using a different client than the browser" than to "an unattended process acting alone," which is the category ADR-0004 is actually about.

This ADR does not amend or narrow ADR-0004's scope for anything else — Forge's default posture against unattended automation is otherwise unchanged. If a future phase wants Claude (or anything else) to act on a schedule or trigger with no human-initiated session behind it, that is new territory requiring its own decision, not something this ADR pre-authorizes.

## 3. Amendments from initial draft (owner review, 2026-08-18)

The originally circulated draft of this decision left the bootstrap/persistent-token relationship underspecified — it risked the bootstrap token becoming a permanent, undifferentiated credential sitting in deployment config, which would have undermined the entire point of a scoped, revocable model. Resolved before Milestone 1 authorization:
- Bootstrap token authenticates provisioning only, never `/mcp` itself (§2).
- `mcp_bootstrap_enabled` is a true kill switch, checked before any token comparison.
- `last_used_at` is write-throttled (updated at most once per 5-minute window per token) rather than written on every request, to avoid putting a write on the hot path of every MCP call under SQLite's single-writer model.
- Resource authorization remains a service-layer property, not a scope property: a token's scope answers "what kind of operation," never "which specific record" — every MCP tool handler reaches data through an existing service function that performs its own existence check, never a raw ORM query trusting a client-supplied ID.

Full detail: [`01_SPEC.md`](../implementation/Phase-11-Claude-MCP/01_SPEC.md) §4.

## 4. Implementation note (recorded here since it affects the auth boundary directly)

The MCP Python SDK's `MCPServer.streamable_http_app()` returns a plain Starlette ASGI application with no FastAPI dependency-injection surface of its own — tool handlers are plain Python functions, not FastAPI routes, so `Depends(require_scope(...))`-shaped enforcement (as originally sketched in `03_BACKEND.md` §3) cannot attach at the tool level via FastAPI's DI. Milestone 1 implements the connection-level check (equivalent to `require_mcp_auth`) as ASGI middleware wrapping the mounted app, and provides `require_scope(ctx, scope)` as a plain function for Milestone 2's tool handlers to call explicitly at the top of each handler body. The enforcement guarantee is unchanged (every `/mcp` request is authenticated before any MCP protocol processing occurs, every tool call will be scope-checked before performing its operation); only the FastAPI-`Depends` shape originally sketched changes to match what the mounted SDK app actually is.

## 5. Alternatives considered

- **Reuse the browser session cookie for MCP.** Rejected: would require exposing raw session tokens outside the browser's cookie jar, and since the existing token carries no scope, it would give MCP the same blanket access as the browser with no way to exclude Secrets — directly conflicting with `01_SPEC.md` §2's structural exclusion requirement.
- **OAuth 2.0 from the start.** Rejected for this phase — see §2. Not foreclosed for the future.
- **One long-lived token with no distinct bootstrap tier** (the original draft). Rejected per §3 — collapses "provisioning credential" and "Claude's daily-use credential" into one, which is the permanent-root-credential risk this ADR exists to avoid.

## 6. Consequences

- Forge gains its first per-credential revocation mechanism, and the pattern (hashed-at-rest, shown-once, individually revocable) is available as precedent for any future credential type.
- `AuthDep`/`require_auth` and the browser session model are completely unmodified by this phase.
- A compromised or leaked persistent MCP token is scoped and revocable without rotating the master password (which would log out the browser session too) — a strict improvement over the alternative of reusing session tokens.
- Adds one new REST route family (`/api/mcp/tokens`) and one new table (`mcp_tokens`) to maintain.

## 7. Cross-references

- [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
- [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
- [0004-interactive-workflows-not-automation.md](0004-interactive-workflows-not-automation.md)
- [0018-mcp-server-integrated-not-separate-process.md](0018-mcp-server-integrated-not-separate-process.md)
- [../implementation/Phase-11-Claude-MCP/01_SPEC.md](../implementation/Phase-11-Claude-MCP/01_SPEC.md)
- [../implementation/Phase-11-Claude-MCP/03_BACKEND.md](../implementation/Phase-11-Claude-MCP/03_BACKEND.md)
