# Checkpoint — Claude MCP / Second Brain (Phase 11) — 2026-08-19 (Milestone 3)

> **Trigger:** Milestone completion. Milestone 3 (Search, Context & Knowledge Graph) of [Phase-11-Claude-MCP](../implementation/Phase-11-Claude-MCP/README.md) reached a passing Agentic Review gate. Per [`../10_CHECKPOINT_PROTOCOL.md`](../10_CHECKPOINT_PROTOCOL.md) §1.
> **Phase:** [Phase-11-Claude-MCP](../implementation/Phase-11-Claude-MCP/README.md)
> **Last Updated:** 2026-08-19

---

```
Phase 11
Milestone 3 — PASS
Mechanical verification: 6/6 applicable verifiers
Agentic Review: PASS (after one repair cycle)
Findings: 0 BLOCKER, 3 MAJOR, 3 MINOR — all fixed and independently re-verified
Regression tests added: yes (2 new files, 20 tests; 2 existing tests strengthened)
M4: NOT AUTHORIZED
Phase 11: NOT RELEASED
Phase 11: NOT FROZEN
```

This is a **milestone checkpoint, not a release and not a freeze.** Milestones 1 and 2 are already committed (`6854971`, `4cf1bd2`); this checkpoint covers Milestone 3's work only. Phase 11 remains in **Implementation**, three of five milestones complete, per [`../13_PHASE_LIFECYCLE.md`](../13_PHASE_LIFECYCLE.md).

## Completed Tasks

All seven Milestone 3 tasks from [`09_IMPLEMENTATION_TASKS.md`](../implementation/Phase-11-Claude-MCP/09_IMPLEMENTATION_TASKS.md):

- **M3-T0a** — `project_id: str | None = None` added to `notes_service.search_notes`/`documents_service.search_documents`, applied inside the FTS5 query before `LIMIT 50`
- **M3-T0b** — `knowledge_service.list_links_for_items(session, items)` — batch link retrieval, one query for the links plus at most one per referenced item type for titles, regardless of item count
- **M3-T1** — `app/mcp/tools/search.py` — `forge_search` (calls `notes_service.search_notes`/`documents_service.search_documents` directly, never `search_service.global_search`)
- **M3-T2** — `forge_context` composition — uses `list_links_for_items`, not one `list_links` call per matched item
- **M3-T3** — `app/mcp/tools/knowledge.py` — `forge_link_items`, `forge_unlink_items`
- **M3-T4** — Tool registry wiring for all 4 new tools — 16 tools total now registered
- **M3-T5** — `VERIFICATION_CONTRACT.md` updated in place for the Milestone 3 gate

Plus the gate itself: full mechanical verification (6/6 applicable verifiers) and an independent Agentic Review, including **one repair cycle addressing 3 MAJOR and 3 MINOR findings, independently re-verified by the same reviewer** — see Known Risks.

## Modified Files

**Created**
- `backend/app/mcp/tools/search.py`, `knowledge.py`
- `backend/tests/test_mcp_tools_search_context.py` (13 tests), `test_mcp_tools_knowledge.py` (7 tests)
- `forge-docs/implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M3.md`
- `forge-docs/history/2026-08-19-phase-11-milestone-3-checkpoint.md` (this file)

**Modified**
- `backend/app/mcp/server.py` (tool registration — all 16 tools wired in)
- `backend/app/services/notes/service.py`, `documents/service.py` (`project_id` param on search functions)
- `backend/app/services/knowledge/service.py` (`list_links_for_items` added; `_tags_for` → `tags_for_items`, made public)
- `backend/app/mcp/tools/projects.py` (`_to_mcp_out` → `project_to_mcp_out`, made public; tool descriptions added in the repair cycle)
- `backend/app/mcp/tools/notes.py`, `documents.py` (repair-cycle addition, not original scope: tool descriptions added — a description-string-only change, no logic touched)
- `backend/tests/test_knowledge_service.py` (+3 tests for `list_links_for_items`, including the AC13b query-count assertion), `test_mcp_server.py` (Milestone-2-era 12-tool assertion updated to the real, current 16-tool set)
- `forge-docs/implementation/Phase-11-Claude-MCP/01_SPEC.md`, `06_API.md`, `08_ACCEPTANCE.md` (corrected against verified implementation findings — see Known Risks)
- `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md`, `IMPLEMENT.md`, `VERIFICATION_CONTRACT.md`

**Untouched, confirmed by `git diff --stat` and the Agentic Review independently**: `backend/app/services/secrets/`, `crypto/`, `settings/`; `backend/app/api/deps.py` (`AuthDep`/`require_auth`); `backend/app/mcp/auth.py` (`McpBearerAuthMiddleware`, the token/scope model); `backend/alembic/` (no new migration — no new table/column needed); `frontend/`.

## Current State

Claude can now search across Notes and Documents, retrieve a topic-scoped aggregate (project + matched items + tags + links) in one call, and shape the knowledge graph directly — the first milestone where Claude *retrieves* Forge's knowledge as a composed view rather than one item at a time:

```
Claude
  ↓
forge_search / forge_context                    forge_link_items / forge_unlink_items
  ↓                                                ↓
require_scope (forge:read)                       require_scope (forge:write)
  ↓                                                ↓
services/notes, services/documents,              services/knowledge
services/knowledge (tags, links)                   ↓
  ↓                                               SQLite
SQLite
```

`project_id` scoping is applied inside the FTS5 query itself, before the 50-per-type cap — not as a post-filter, which could otherwise silently drop relevant results for a project with many matches. `forge_context`'s link lookup is a single batch query (plus at most one per item type for titles), never one query per matched item, and its `links` output only includes edges between two items already present in the response (no dangling references). `forge_link_items`/`forge_unlink_items` produce no `ActivityLog` row, a documented exception matching the pre-existing `update_note`/`update_document` asymmetry rather than newly-introduced, undocumented behavior. All 16 MCP tools now carry real, non-empty descriptions visible to any MCP client. Zero MCP code path reaches Secrets, Crypto, or Settings — confirmed by the same recursive static check Milestone 2 built, unmodified and re-passing against the two new files.

**Gate result:** mechanical verification 6/6 applicable verifiers. Agentic Review: PASS, after one repair cycle — see Known Risks.

## Remaining Work

Milestones 4–5 of [`09_IMPLEMENTATION_TASKS.md`](../implementation/Phase-11-Claude-MCP/09_IMPLEMENTATION_TASKS.md), **neither authorized**:

- **Milestone 4 — Claude Memory Workflows.** `forge_capture_session`, `forge_capture_decision`, resource exposure (`forge://projects`), multi-session continuity proof. Needs its own scoping/review discipline, same as Milestones 2 and 3 — not implied by this checkpoint. **Explicitly, per the owner's own instruction, remains unauthorized until the owner opens it.**
- Milestone 5 (Production Hardening & Release) unchanged, downstream of Milestone 4.

## Recommended Next Prompt

> Milestone 3 is checkpointed and committed; Milestone 4 is not authorized and remains explicitly closed until the owner opens it. When ready, review `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md` and `reviews/AGENTIC_REVIEW_M3.md`, then authorize Milestone 4 explicitly as its own act — not implied by this checkpoint. On authorization, update `IMPLEMENT.md`'s Status line to record it as a separate, dated gate (matching how Milestones 1–3's authorizations are recorded there), then begin `09_IMPLEMENTATION_TASKS.md`'s Milestone 4 task table.

## Known Risks

1. **The Agentic Review's first pass was not a clean PASS, and the findings were real.** Three MAJOR findings: (a) `forge_link_items`/`forge_unlink_items` produced zero `ActivityLog` rows with no documentation anywhere — resolved by documenting it as a deliberate REST-parity exception (matching the `update_note`/`update_document` precedent) rather than silently adding new logging behavior that would have changed existing REST callers' behavior too; (b) all 16 MCP tools had empty `tools/list` descriptions, including a direct violation of an already-written `06_API.md` requirement (`forge_create_document`'s HTML-not-Markdown warning, specified but never surfaced to a caller) — fixed across all five tool modules, verified live; (c) `forge_context`'s `links` output could reference items outside its own matched set, a dangling reference with no accompanying context — fixed by filtering to intra-matched-set edges only. The same reviewer independently re-verified all three by reproducing the exact original failing scenarios, not by trusting the fix descriptions, before returning PASS. Worth remembering going into Milestone 4: an Agentic Review that finds nothing on a complex milestone is more suspicious than one that finds real things and they get fixed.
2. **Three MINOR findings, all fixed**: `forge_context`'s `topic` parameter had no length cap unlike `forge_search`'s `query`, despite both feeding the identical FTS phrase-prefix construction the cap exists to guard against; the `forge_context` aggregate test never actually exercised tags (a coverage gap, not a live bug — verified live before the test was strengthened); and `CURRENT_STATE.md`'s self-reported test counts were inaccurate.
3. **A secondary staleness finding, caught mid-re-verification by the same reviewer**: after the repair cycle, `VERIFICATION_CONTRACT.md` §3/§5/§10 still contained pre-repair-cycle text (an inaccurate "AC18 unchanged" claim, a stale test count, an incomplete findings list). Corrected before the final PASS was recorded — the review process caught its own documentation lagging behind the code fix, not just the code fix itself.
4. **`06_API.md`'s `forge_link_items` idempotency claim didn't match `create_link`'s actual behavior** (the service raises a 409 on an exact re-link rather than returning the existing row) — found by re-reading the actual service code during implementation, not by the Agentic Review. Same class of gap as Milestone 2's `update_note` audit-logging finding: a planning document describing desired behavior is not the same as the underlying function already producing it. Fixed with an explicit catch-and-translate at the tool layer.
5. **Two private service helpers promoted to public, not duplicated**: `knowledge_service._tags_for` → `tags_for_items`, `app/mcp/tools/projects.py::_to_mcp_out` → `project_to_mcp_out`. Both now have two real call sites; independently confirmed by the Agentic Review as genuine reuse, not an unjustified public-surface expansion.
6. **No frontend surface for MCP token management** — unchanged from Milestone 1, still an open question for Milestone 5.
7. **New open question added this milestone** (`08_ACCEPTANCE.md` §6): should `knowledge_service.create_link`/`delete_link` gain `ActivityLog` logging in a future phase, given knowledge-graph mutations arguably have more product value for audit visibility than the pre-existing `update_note`/`update_document` asymmetry? Not decided by this implementation session.

## Blocking decisions requiring approval

**None currently.** The owner's standing instruction is explicit and procedural: Milestone 4 remains unauthorized until the owner opens it — not inferred from this checkpoint, not rushed on the strength of three consecutive PASS gates.

## Cross-references

- [../10_CHECKPOINT_PROTOCOL.md](../10_CHECKPOINT_PROTOCOL.md)
- [../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md](../implementation/Phase-11-Claude-MCP/CURRENT_STATE.md)
- [../implementation/Phase-11-Claude-MCP/IMPLEMENT.md](../implementation/Phase-11-Claude-MCP/IMPLEMENT.md)
- [../implementation/Phase-11-Claude-MCP/VERIFICATION_CONTRACT.md](../implementation/Phase-11-Claude-MCP/VERIFICATION_CONTRACT.md)
- [../implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M3.md](../implementation/Phase-11-Claude-MCP/reviews/AGENTIC_REVIEW_M3.md)
- [2026-08-18-phase-11-milestone-2-checkpoint.md](2026-08-18-phase-11-milestone-2-checkpoint.md)
- [2026-08-18-phase-11-milestone-1-checkpoint.md](2026-08-18-phase-11-milestone-1-checkpoint.md)
