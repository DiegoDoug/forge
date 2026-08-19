# Using Forge from Claude / Claude Code

Forge's MCP server (off by default — see [Deployment.md](Deployment.md#mcp-server-for-claude--claude-code-optional)
for enabling it and provisioning a token) turns Forge into Claude's
persistent knowledge substrate: a place Claude can search, retrieve,
organize, and remember across conversations, scoped by a bearer token you
control.

## Tools at a glance

| Category | Tools | Scope |
|---|---|---|
| Retrieval | `forge_search`, `forge_context`, `forge_get_note`, `forge_get_document`, `forge_list_projects`, `forge_get_project` | `forge:read` |
| Notes/Documents/Projects CRUD | `forge_create/update_note`, `forge_create/update_document`, `forge_create/update_project` | `forge:write` |
| Deletion | `forge_delete_note`, `forge_delete_document` | `forge:delete` |
| Knowledge graph | `forge_link_items`, `forge_unlink_items` | `forge:write` |
| Memory | `forge_capture_decision`, `forge_capture_session` | `forge:write` |

Full contract for every tool (input/output/error shape) is
[`06_API.md`](../forge-docs/implementation/Phase-11-Claude-MCP/06_API.md).
Two resources are also exposed for orientation: `forge://projects` (list)
and `forge://projects/{id}` (detail) — a client that auto-discovers
resources gets a project overview without an explicit tool call.

## The core workflow: `forge_context` before you write

Before creating or changing anything, call `forge_context` with the topic
you're about to work on:

```
forge_context(topic="Phase 11 MCP auth")
```

This returns, in one call: the matching project (if `project_id` was
given), the Notes and Documents whose content matches the topic (with their
tags), and the links already drawn between them. It exists specifically so
you don't have to chain `forge_search` → `forge_get_note` → `forge_get_note`
→ ... to build the same picture — one call gives you the aggregate, and you
only reach for `forge_get_note`/`forge_get_document` afterward for the full
body of something `forge_context`'s summary told you is worth reading in
full.

Use `forge_search` instead of `forge_context` when you have a specific
query and don't need the aggregate framing (project + tags + links) —
e.g. "does a note about X already exist" before creating a duplicate.

## Persisting memory: `forge_capture_decision` / `forge_capture_session`

These exist so something you learn or decide in this conversation is still
there the next time a Claude session (this one or a different one) opens
Forge. Both are thin wrappers over `forge_create_note` — a captured item
*is* an ordinary Note, tagged `ai-decision` or `ai-session`, discoverable
through `forge_search`/`forge_context` exactly like anything a human wrote
in the Notes board. There is no separate memory store to fall out of sync
with the rest of Forge.

**When to use which:**

- `forge_capture_decision(summary, detail?, project_id?)` — an architectural
  or product decision worth remembering *why*, not just *what*. `summary`
  becomes the note's title (`Decision: <summary>`); put the reasoning in
  `detail`, not the summary — `forge_context`'s output shows summaries as
  snippets, so the reasoning is what a later session actually needs to see.
- `forge_capture_session(summary, detail?, project_id?)` — a summary of what
  this conversation accomplished, for a later session to pick up the
  thread. Title becomes `Session <YYYY-MM-DD>: <summary>`.

**Worked example** — a session that redesigns Forge's auth model, then a
later session that needs to know why:

```
# Session 1, after the redesign is agreed:
forge_capture_decision(
    summary: "MCP tokens use bearer auth, not OAuth",
    detail: "OAuth needs a standing authorization server, disproportionate "
            "for a single-tenant instance. Static, revocable bearer tokens "
            "fit the existing 'one operator, one master key' trust model. "
            "Revisit if multi-user support is ever added.",
    project_id: "<forge-project-id>",
)

# Session 2, days later, a different conversation:
forge_context(topic: "MCP auth", project_id: "<forge-project-id>")
# -> notes[] includes "Decision: MCP tokens use bearer auth, not OAuth",
#    tagged ai-decision, with the reasoning in its snippet/content.
```

`summary` is capped at 180 characters (leaves room for the prefix within
the Notes title limit) — put anything longer in `detail`.

## What Claude cannot reach through this server

Secrets, Settings, and Crypto are structurally excluded — no MCP tool or
resource in any milestone imports those service modules (enforced by a
static check in the backend test suite, not just a documented convention).
If you need to work with a Secret, do it through the Forge UI directly.

## Deletion is permanent

`forge_delete_note`/`forge_delete_document` require `confirm: true` as a
literal boolean in the structured tool call — never inferred from
conversation ("yes, delete it" in chat does not satisfy this). There is no
trash; a deleted item is gone. Prefer `forge_update_note`/
`forge_update_document` with `archived: true` if you want to hide something
reversibly instead.
