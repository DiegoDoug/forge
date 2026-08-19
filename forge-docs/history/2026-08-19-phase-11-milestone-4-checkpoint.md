# Checkpoint — Claude MCP / Second Brain (Phase 11) — 2026-08-19 (Milestone 4)

> **Trigger:** Milestone completion. Milestone 4 (Claude Memory Workflows) of [Phase-11-Claude-MCP](../implementation/Phase-11-Claude-MCP/README.md) reached a passing Agentic Review gate. Per [`../10_CHECKPOINT_PROTOCOL.md`](../10_CHECKPOINT_PROTOCOL.md) §1.
> **Phase:** [Phase-11-Claude-MCP](../implementation/Phase-11-Claude-MCP/README.md)
> **Last Updated:** 2026-08-19

---

```
Phase 11
Milestone 4 — PASS
Mechanical verification: 7/7 applicable verifiers
Agentic Review: PASS (after one narrow repair cycle)
Findings: 0 BLOCKER, 1 MAJOR, 1 MINOR — MAJOR fixed and independently re-verified; MINOR left as backlog
Regression tests added: yes (3 new files, 18 tests)
M5: NOT AUTHORIZED
Phase 11: NOT RELEASED
Phase 11: NOT FROZEN
```

This is a **milestone checkpoint, not a release and not a freeze.** Milestones 1–3 are already committed (`6854971`, `4cf1bd2`, and Milestone 3's commit); this checkpoint covers Milestone 4's work only. Phase 11 remains in **Implementation**, four of five milestones complete, per [`../13_PHASE_LIFECYCLE.md`](../13_PHASE_LIFECYCLE.md).

## Completed Tasks

All five Milestone 4 tasks from [`09_IMPLEMENTATION_TASKS.md`](../implementation/Phase-11-Claude-MCP/09_IMPLEMENTATION_TASKS.md):

- **M4-T1** — `app/mcp/tools/memory.py` — `forge_capture_decision`, `forge_capture_session` (reserved-tag convention: `ai-decision`/`ai-session`, thin wrappers over `notes_service.create_note`/`knowledge_service.add_tag`)
- **M4-T2** — `app/mcp/resources.py` — `forge://projects` (static, list), `forge://projects/{id}` (template, detail)
- **M4-T3** — Cross-session continuity test (AC14) — `backend/tests/test_mcp_memory_continuity.py`, using a freshly-provisioned token and a fresh `initialize` handshake for the "later session" half
- **M4-T4** — Claude-oriented usage documentation — `docs/MCP_Usage.md` (new)
- **M4-T5** — `VERIFICATION_CONTRACT.md` updated in place for the Milestone 4 gate

Plus the gate itself: full mechanical verification (7/7 applicable verifiers) and an independent Agentic Review, including **one narrow repair cycle addressing 1 MAJOR finding, independently re-verified by the same reviewer** — see Known Risks.

## Modified Files

**Created**
- `backend/app/mcp/tools/memory.py`, `backend/app/mcp/resources.py`
- `backend/tests/test_mcp_tools_memory.py` (10 tests), `test_mcp_resources.py` (6 tests), `test_mcp_memory_continuity.py` (2 tests)
- `docs/MCP_Usage.md`
- `forge-docs/implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M4.md`
- `forge-docs/history/2026-08-19-phase-11-milestone-4-checkpoint.md` (this file)

**Modified**
- `backend/app/mcp/server.py` (registration — `memory_tools.register(server)`, `resources_module.register(server)`; `_INSTRUCTIONS` updated to mention the memory tools and resources)
- `backend/tests/test_mcp_server.py` (tool-list assertion updated: 16 → 18 tools, `forge_capture_decision`/`forge_capture_session` added)
- `docs/Deployment.md` (one stale sentence corrected — no longer describes Milestone 1's "zero tools registered" state)
- `forge-docs/implementation/Phase-11-Claude-MCP/06_API.md` (§5's `forge://projects` Auth cell corrected from `forge:read` to the true, current behavior, with a footnote — repair-cycle fix, Agentic Review MAJOR finding)
- `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md`, `IMPLEMENT.md`, `VERIFICATION_CONTRACT.md`

**Untouched, confirmed by `git diff --stat` and the Agentic Review independently**: `backend/app/services/secrets/`, `crypto/`, `settings/`; `backend/app/api/deps.py` (`AuthDep`/`require_auth`); `backend/app/mcp/auth.py` (`McpBearerAuthMiddleware`, the token/scope model); `backend/app/mcp/tools/notes.py`, `documents.py`, `projects.py`, `search.py`, `knowledge.py` (all five pre-existing tool modules); `backend/alembic/` (no new migration — no new table/column needed); `frontend/`.

## Current State

Claude can now persist memory across sessions — a decision or session summary captured via `forge_capture_decision`/`forge_capture_session` in one Claude session is retrievable via `forge_search`/`forge_context` in a later, independent one, proven end to end (AC14):

```
Claude
  ↓
forge_capture_decision / forge_capture_session          forge://projects / forge://projects/{id}
  ↓                                                        ↓
require_scope (forge:write)                              (template only) require_scope (forge:read)
  ↓                                                        ↓
notes_service.create_note (source="mcp")                 projects_service.list_projects / get_project
  + knowledge_service.add_tag (ai-decision / ai-session)    ↓
  ↓                                                        SQLite
SQLite
```

Both memory tools are thin wrappers, not a new persistence mechanism — no new table, model, or migration. A captured item is an ordinary Note, tagged, discoverable through the exact same `forge_search`/`forge_context` path every other note goes through. `forge://projects/{id}` enforces `forge:read` exactly like every tool; `forge://projects` (a static resource, no URI variable) structurally cannot, in this MCP SDK version — a genuine, independently-confirmed constraint, documented as an accepted narrow exception (project metadata only, no secrets, connection-level bearer auth still required) rather than silently built around or silently accepted without documentation.

**Gate result:** mechanical verification 7/7 applicable verifiers. Agentic Review: PASS, after one narrow repair cycle — see Known Risks.

## Remaining Work

Milestone 5 of [`09_IMPLEMENTATION_TASKS.md`](../implementation/Phase-11-Claude-MCP/09_IMPLEMENTATION_TASKS.md), **not authorized**:

- **Milestone 5 — Production Hardening & Release.** Token lifecycle (the token-management-UI open question), full authorization matrix test, audit completeness pass, Docker/nginx production-path verification, full regression + security suite, release artifacts. Needs its own scoping/review discipline, same as Milestones 2–4 — not implied by this checkpoint.
- The mandatory human review gate (`IMPLEMENT.md`'s own §"The mandatory human review gate") remains after Milestone 5's PASS, not before — unchanged.

## Recommended Next Prompt

> Milestone 4 is checkpointed and committed. Milestone 5 (Production Hardening & Release) is not authorized. When ready, review `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md` and `reviews/AGENTIC_REVIEW_M4.md`, then authorize Milestone 5 explicitly as its own act — not implied by this checkpoint.

## Known Risks

1. **The Agentic Review's first pass was not a clean PASS, and the finding was real.** One MAJOR: `06_API.md` §5's resource contract table claimed `forge:read` was enforced on the static `forge://projects` resource, when this MCP SDK version (`mcp` 2.0.0) has no per-request `Context` hook for a static resource's read function — a genuine constraint, independently confirmed by the reviewer reading the installed SDK's source directly (`MCPServer.resource()`'s decorator; `FunctionResource.fn`'s zero-argument signature), with no `ContextVar`-based workaround found anywhere in the package. Three other places (`resources.py`'s docstring, `VERIFICATION_CONTRACT.md`, `CURRENT_STATE.md`) had already documented this correctly during implementation; `06_API.md` itself, the phase's authoritative contract document, had not been corrected. Fixed with a footnote stating the true, current behavior; the same reviewer independently re-verified the fix by re-reading the actual diff (not the fix description) and re-running the full backend suite, before returning PASS.
2. **The underlying security trade-off (any authenticated token can read `forge://projects` regardless of scope) was independently judged an acceptable narrow exception, not a BLOCKER** — given the low sensitivity of the exposed fields (project name/description/color/counts; `secret_count` already excluded) and Forge's own "one operator, one master key" threat model. `forge://projects/{id}` has no such limitation and enforces `forge:read` normally, matching every tool.
3. **One MINOR finding, deliberately left unfixed**: resource-read errors (an unknown project ID on either resource) surface as a generic, unclassified SDK-level `-32603` error rather than the clean "Project not found" message the equivalent tool gives — traced to the MCP SDK's own blanket exception-wrapping in `read_resource()`, not introduced by this milestone's code. Classified by the Agentic Review as backlog-appropriate; the repair cycle deliberately addressed only the one MAJOR finding the review actually required, not this too, to avoid unrequested scope expansion.
4. **The independent-review process itself hit an infrastructure snag worth recording**: the first re-verification attempt (of the `06_API.md` fix) crashed mid-write after the reviewing agent hit a session/rate limit, leaving the review artifact briefly in a self-inconsistent state (a "PASS" verdict line pointing at a re-verification section that didn't exist yet). This was caught before being trusted — the file was re-read, the inconsistency identified, and the same reviewer agent was resumed to actually complete the re-verification (re-reading the real diff, re-running the test suite) before the PASS verdict was accepted as genuine. No shortcut was taken to paper over the interruption.
5. **`06_API.md`'s "Full NoteOut... including the applied tag" output claim for the memory tools didn't match what `NoteOut` actually contains** (`schemas/notes.py::NoteOut` has no `tags` field) — found by reading the schema before writing the tool handler this time, not discovered later by a review (unlike the analogous Milestone 2/3 gaps). Resolved by returning `NoteOut`'s fields plus a `tags` list from `add_tag`'s own return value; independently confirmed correct and sufficient by the Agentic Review.
6. **No frontend surface for MCP token management** — unchanged from Milestone 1, still an open question for Milestone 5.
7. **The knowledge-link no-audit-logging open question from Milestone 3** (`08_ACCEPTANCE.md` §6) is unaffected by and unrelated to this milestone's tools.

## Blocking decisions requiring approval

**None currently.** The owner's standing instruction is explicit and procedural: Milestone 5 remains unauthorized until the owner opens it — not inferred from this checkpoint, not rushed on the strength of four consecutive PASS gates.

## Cross-references

- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md](../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md)
- [../implementation/Phase-11-Claude-MCP/IMPLEMENT.md](../implementation/Phase-11-Claude-MCP/IMPLEMENT.md)
- [../implementation/Phase-11-Claude-MCP/VERIFICATION_CONTRACT.md](../implementation/Phase-11-Claude-MCP/VERIFICATION_CONTRACT.md)
- [../implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M4.md](../implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M4.md)
- [2026-08-19-phase-11-milestone-3-checkpoint.md](2026-08-19-phase-11-milestone-3-checkpoint.md)
- [2026-08-18-phase-11-milestone-2-checkpoint.md](2026-08-18-phase-11-milestone-2-checkpoint.md)
- [2026-08-18-phase-11-milestone-1-checkpoint.md](2026-08-18-phase-11-milestone-1-checkpoint.md)
