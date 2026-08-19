# Phase 11 — Current State

> **Purpose:** Living snapshot of where this phase actually is.
> **Last Updated:** 2026-08-19

---

## 1. Lifecycle stage

**Implementation — Milestones 1–4 complete, checkpointed, and committed (`6854971`, `4cf1bd2`, Milestone 3's commit, and Milestone 4's commit). Milestone 5 explicitly NOT authorized — stays closed until the owner opens it.** Per `../../13_PHASE_LIFECYCLE.md`, the phase moved Specification → Authorized → Implementation on 2026-08-18.

Milestones 1–3's full history (authorization → implementation → Agentic Review → repair cycle where applicable → checkpoint/commit) is unchanged from before and is not repeated here — see `IMPLEMENT.md`'s gates 1–10 and §5 below for the abbreviated record, or the full checkpoints/reviews linked in §7.

The owner then instructed, in chat, on 2026-08-19: *"Start milestone 4 implementation"* — read as the separate, explicit authorization `IMPLEMENT.md`'s gate structure requires before any Milestone 4 task begins, matching the exact precedent Milestones 1–3 each required (gate 11 in `IMPLEMENT.md`). M4-T1 through M4-T5 were implemented; the full backend test suite (395/395) and Docker build were green (gate 12).

The independent Agentic Review's first pass reached **PASS WITH REQUIRED FIXES** (zero BLOCKER, one MAJOR, one MINOR). The MAJOR — `06_API.md` §5's resource table overclaiming enforced `forge:read` on the static `forge://projects` resource, when the resource structurally cannot enforce it (a genuine MCP SDK limitation, independently confirmed by reading the installed SDK's source) — was fixed with a footnote stating the true, current behavior. The MINOR (generic resource-error messages) was deliberately left as backlog, per the reviewer's own explicit non-blocking classification. The same reviewer independently re-verified the fix — re-reading the actual diff and re-running the backend suite fresh, not trusting the fix description — before returning a final verdict of **PASS** (gate 13). Full record: `reviews/AGENTIC_REVIEW_M4.md`.

The owner then instructed, in chat, on 2026-08-19: *"checkpoint and commit M4."* Checkpointed at `forge-docs/history/2026-08-19-phase-11-milestone-4-checkpoint.md` and committed (gate 14). **This session takes no further action on this phase without a new, explicit instruction** — in particular, no Milestone 5 task, however small, until the owner separately opens it.

## 2. What exists right now

**Planning package** (unchanged in structure since Specification; `01_SPEC.md`/`06_API.md`/`08_ACCEPTANCE.md` gained Milestone-3 corrections, in the same style as Milestone 2's corrections): `README.md`, `01_SPEC.md`, `03_BACKEND.md`, `04_DATABASE.md`, `06_API.md`, `07_TESTING.md`, `08_ACCEPTANCE.md`, `09_IMPLEMENTATION_TASKS.md`.

**Milestone 1 implementation** (committed at `6854971`): MCP transport/auth foundation. Full detail in `forge-docs/history/2026-08-18-phase-11-milestone-1-checkpoint.md`.

**Milestone 2 implementation** (checkpointed and committed): the 12 Knowledge CRUD tools (Notes/Documents/Projects). Full detail in `forge-docs/history/2026-08-18-phase-11-milestone-2-checkpoint.md`.

**Milestone 3 implementation** (new, 2026-08-19, Agentic Review PASS, checkpointed and committed):
- `backend/app/services/notes/service.py::search_notes`, `backend/app/services/documents/service.py::search_documents` — additive `project_id: str | None = None` keyword-only param, applied inside the FTS5 query before `LIMIT 50` (M3-T0a).
- `backend/app/services/knowledge/service.py::list_links_for_items` — new batch link-retrieval method, one query for the links themselves plus at most one query per referenced item type (note/document) for titles, regardless of item count (M3-T0b). `_tags_for` promoted to public `tags_for_items` (now has two real call sites: `list_knowledge` and the new `forge_context`).
- `backend/app/mcp/tools/search.py` (new) — `forge_search`, `forge_context`. Both call `notes_service.search_notes`/`documents_service.search_documents` directly (never `search_service.global_search`, which also returns Secrets). `forge_context`'s `links` output is filtered to edges between two matched items only (repair-cycle fix — see below).
- `backend/app/mcp/tools/knowledge.py` (new) — `forge_link_items`, `forge_unlink_items`, calling `knowledge_service` directly (the pre-anticipated, documented exception to "each tool calls its own domain's service" — linking is inherently cross-item). Both produce zero `ActivityLog` rows, a documented exception matching `update_note`/`update_document`'s existing precedent (repair-cycle finding — see below).
- `backend/app/mcp/tools/projects.py::_to_mcp_out` promoted to public `project_to_mcp_out` (reused by `search.py` for `forge_context`'s project field).
- `backend/app/mcp/server.py` — all 16 tools now registered (12 from Milestone 2 + 4 new). Every tool across all five modules now carries an explicit `description=` visible via `tools/list` (repair-cycle fix, verified live).
- `backend/tests/test_mcp_tools_search_context.py` (new, 13 tests), `backend/tests/test_mcp_tools_knowledge.py` (new, 7 tests), `backend/tests/test_knowledge_service.py` (+3 tests for `list_links_for_items`, including the AC13b query-count assertion), `backend/tests/test_mcp_server.py` (tool-list assertion updated to the real 16-tool set) — all green, alongside the full pre-existing backend suite (**377/377**, zero regressions) and FDK suite (**113/113**).
- `VERIFICATION_CONTRACT.md` updated in place for the Milestone 3 gate, including the repair-cycle findings and corrected AC18 status.
- Docker build check (`docker build ./backend`) succeeded.

**Milestone 3 repair cycle** (2026-08-19, in response to the Agentic Review's first-pass findings, all independently re-verified fixed in its second pass): three MAJOR findings — knowledge-graph link create/delete's undocumented lack of `ActivityLog` rows (resolved by documenting it as a deliberate exception, not by silently adding new logging behavior that would affect every REST caller too), all 16 MCP tools' empty `tools/list` descriptions (fixed by adding explicit `description=` to every tool, including restoring `06_API.md`'s already-required HTML-not-Markdown warning for `forge_create_document`/`forge_update_document`), `forge_context` emitting links to items outside its own matched set (fixed by filtering to intra-matched-set edges only) — and three MINOR findings: `forge_context`'s `topic` gained `forge_search`'s existing 200-char cap; the aggregate test now actually exercises tags; test counts corrected. Full detail in `reviews/AGENTIC_REVIEW_M3.md` §5.

**Milestone 4 implementation** (new, 2026-08-19, Agentic Review PASS — not yet checkpointed or committed):
- `backend/app/mcp/tools/memory.py` (new) — `forge_capture_decision`, `forge_capture_session`. Both call `notes_service.create_note` (`source="mcp"`) then `knowledge_service.add_tag` with a reserved tag name (`ai-decision`/`ai-session`) and a reserved color reusing the `Tag` model's own field default. Output is `NoteOut`'s fields plus a `tags` list — not a bare `NoteOut`, since `NoteOut` (`schemas/notes.py`) has no `tags` field at all, and `06_API.md` explicitly requires the applied tag be visible in the output (found by reading the schema before writing the handler, not assumed).
- `backend/app/mcp/resources.py` (new) — `forge://projects` (static, list), `forge://projects/{project_id}` (template, detail). The template resource enforces `forge:read` exactly like every tool (`current_scope`/`require_scope`). **The static resource cannot** — a real MCP SDK constraint (no per-request `Context` hook for a static resource's read function in this SDK version), documented in the module's own docstring and in `VERIFICATION_CONTRACT.md` §6. The Agentic Review independently confirmed this constraint is genuine (read the installed SDK's source directly, found no workaround) and judged the resulting security posture an acceptable narrow exception — but found `06_API.md` §5's own resource table still claimed `forge:read` was enforced, a real contract-accuracy gap; fixed with a footnote (see §5 below).
- `backend/app/mcp/server.py` — both new modules registered (18 tools total now: 16 from Milestones 2–3 + 2 new); `_INSTRUCTIONS` updated to mention the memory tools and resources.
- `backend/tests/test_mcp_tools_memory.py` (new, 10 tests), `backend/tests/test_mcp_resources.py` (new, 6 tests), `backend/tests/test_mcp_memory_continuity.py` (new, 2 tests — AC14, using a freshly-provisioned token and a fresh `initialize` handshake for the "later session" half), `backend/tests/test_mcp_server.py` (tool-list assertion updated to the real 18-tool set) — all green, alongside the full pre-existing backend suite (**395/395**, zero regressions).
- `docs/MCP_Usage.md` (new) — full tool/resource list, the `forge_context`-before-you-write workflow guidance M4-T4 asked for, a worked `forge_capture_decision` example, deletion/security notes.
- `docs/Deployment.md` — one stale sentence corrected (still described Milestone 1's "zero tools registered" state).
- `06_API.md` §5 — `forge://projects`'s Auth cell corrected from `forge:read` to "Connection-level bearer auth only — not scope-checked", with a footnote explaining the SDK limitation and the accepted-exception judgment (repair-cycle fix, Agentic Review MAJOR finding — see below).
- `VERIFICATION_CONTRACT.md` updated in place for the Milestone 4 gate, including the final findings list and fix-verification record.
- FDK suite: **103/113** — the 10 failures are pre-existing and environment-specific (a Windows/Git-Bash subprocess-invocation quirk in `BuildVerifier`/`TestVerifier`, root-caused by direct traceback inspection: `/bin/bash: ... python.exe: command not found`), not caused by anything this milestone touched (`git status --porcelain` confirms zero files under `tools/` changed). Same 113-test total as Milestone 3's "113/113".
- Docker build check (`docker build ./backend`) succeeded.

## 3. What does NOT exist yet (correctly, per Milestone 4's scope boundary)

- `02_UI.md`, `05_COMPONENTS.md` — still deliberately omitted.
- A token-management UI, the full authorization matrix test, production Docker/nginx verification, release artifacts — Milestone 5 scope, still unauthorized.
- `forge-docs/02_ROADMAP.md` update — still deliberately deferred to the Released/Frozen stage.
- No new Alembic migration this milestone — no new table/column was needed (`01_SPEC.md` §9's explicit "no new memory database" instruction; memory capture is Notes plus the pre-existing tags mechanism).

## 4. Immediate next step

**Milestone 4 is checkpointed and committed, per explicit owner instruction (*"checkpoint and commit M4."*). Stopped here — Milestone 5 is not authorized** and this session takes no further action on this phase without a new, explicit instruction.

**Next:** owner authorizes Milestone 5 (Production Hardening & Release) as a separate, explicit act whenever ready — not before.

## 5. Known findings from Milestone 4 (kept here as institutional memory, not just in the review artifact)

1. **`06_API.md` §5's resource table claimed `forge:read` was enforced on the static `forge://projects` resource, when it structurally cannot be — found by the Agentic Review, not the implementing session.** Three other places (`resources.py`'s docstring, `VERIFICATION_CONTRACT.md`, this file) had already documented the real limitation, but the phase's own authoritative contract document had not been corrected. Fixed with a footnote stating the true, current behavior; independently re-verified the correction is accurate in both directions (doesn't hide the gap, doesn't overstate it into a broken-auth claim).
2. **The `forge://projects` static-resource scope-enforcement gap is a genuine SDK constraint, confirmed by reading the installed MCP SDK's own source directly** (`mcp.server.mcpserver.server.MCPServer.resource`'s decorator explicitly raises `"Context injection for static resources is not supported"`; `FunctionResource.fn` is `Callable[[], Any]`, invoked with zero arguments on every read regardless of caller) — independently reconfirmed by the Agentic Review, which also searched the installed package for a `ContextVar`-based workaround and found none. `forge://projects/{project_id}` (a template resource) has no such limitation and enforces `forge:read` normally. Judged an **acceptable narrow exception** by the independent review, given the low sensitivity of the exposed fields and Forge's "one operator, one master key" threat model — not a BLOCKER.
3. **`06_API.md`'s Output row for the memory tools ("Full NoteOut of the created note, including the applied tag") doesn't match what `NoteOut` actually contains** — `schemas/notes.py::NoteOut` has no `tags` field, for any caller, ever. Same class of "plan describes desired behavior; the underlying type doesn't carry it" gap Milestone 2/3 found repeatedly (`update_note`'s audit logging, `forge_link_items`'s idempotency). Found by reading the schema before writing the handler this time, not discovered later by a review; independently confirmed correct and sufficient by the Agentic Review.
4. **Reserved-tag color (`#6366f1`) reuses the `Tag` model's own field default** (`models/secrets.py`) rather than inventing an unrelated "special" color — `01_SPEC.md` §9 left the exact value unspecified, so this was an implementation judgment call.
5. **AC14's "independent session" is built as a fresh persistent token AND a fresh `initialize` handshake**, not a second call on a reused connection. The Agentic Review independently reproduced this with an even stronger probe — a second, fully independently-constructed app/engine instance, not just a second token on the same app object — and cross-session continuity still held.
6. **One MINOR finding, deliberately left unfixed**: resource-read errors surface as a generic, unclassified SDK-level `-32603` error rather than a clean not-found message — traced to the MCP SDK's own blanket exception-wrapping, not this milestone's code. The Agentic Review classified this as backlog-appropriate and non-blocking; fixing it was deliberately out of scope for the repair cycle, which addressed only the one MAJOR finding the review actually required.

## 6. Recommended next prompt (for whoever picks this up)

"Milestone 4 is checkpointed and committed; Milestone 5 is explicitly not authorized and stays closed until the owner opens it. Review `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md` and `reviews/AGENTIC_REVIEW_M4.md`, then authorize Milestone 5 (Production Hardening & Release) explicitly when ready — not implied by anything above."

## 7. Cross-references

- [README.md](README.md)
- [IMPLEMENT.md](IMPLEMENT.md)
- [VERIFICATION_CONTRACT.md](VERIFICATION_CONTRACT.md)
- [reviews/AGENTIC_REVIEW_M1.md](reviews/AGENTIC_REVIEW_M1.md)
- [reviews/AGENTIC_REVIEW_M2.md](reviews/AGENTIC_REVIEW_M2.md)
- [reviews/AGENTIC_REVIEW_M3.md](reviews/AGENTIC_REVIEW_M3.md)
- [reviews/AGENTIC_REVIEW_M4.md](reviews/AGENTIC_REVIEW_M4.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [../../history/2026-08-18-phase-11-milestone-1-checkpoint.md](../../history/2026-08-18-phase-11-milestone-1-checkpoint.md)
- [../../history/2026-08-18-phase-11-milestone-2-checkpoint.md](../../history/2026-08-18-phase-11-milestone-2-checkpoint.md)
- [../../history/2026-08-19-phase-11-milestone-3-checkpoint.md](../../history/2026-08-19-phase-11-milestone-3-checkpoint.md)
- [../../history/2026-08-19-phase-11-milestone-4-checkpoint.md](../../history/2026-08-19-phase-11-milestone-4-checkpoint.md)
