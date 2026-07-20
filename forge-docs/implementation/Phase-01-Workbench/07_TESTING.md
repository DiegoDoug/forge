# Workbench — Testing

> **Purpose:** Test plan for this phase — what must be covered before it can be marked done.
> **Scope:** Test strategy and enumeration. Pass/fail criteria live in 08_ACCEPTANCE.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Draft — second full pass (panel architecture + performance/accessibility targets), pending confirmation
> **Version:** 0.3.0
> **Last Updated:** 2026-07-20
> **Depends On:** [01_SPEC.md](01_SPEC.md), [12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md), [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md), [../../decisions/0006-vault-renamed-to-secrets.md](../../decisions/0006-vault-renamed-to-secrets.md)
> **Supersedes:** v0.2.0 of this document (rename regression risk didn't yet cover alias verification)

---

## 1. Backend tests

Following the existing `backend/tests/` pytest convention:

- `test_workbench.py` — unit tests for `services/workbench.py`:
  - `get_layout()` creates the default row on first access (get-or-create).
  - `update_layout()` accepts any structurally valid `panels` list — **including an unrecognized `type` value** (e.g. `"recent_projects"`), per [`06_API.md`](06_API.md) §2's note that panel types are not enum-validated. This is a load-bearing test: it proves the backend doesn't accidentally reintroduce the coupling [ADR-0002](../../decisions/0002-workbench-panel-architecture.md) removed.
  - `update_layout()` rejects a `panels` list with a duplicate `type` or a missing field.
  - `update_layout()` rejects a `pinned_tools` key not present in `WORKBENCH_TOOL_KEYS`, and accepts one marked `available: False` (e.g. `"prompt_studio"`).
  - `reset_layout()` restores the exact `DEFAULT_LAYOUT` constant (five panels, six pinned tools, per `03_BACKEND.md` §2).
  - `get_workbench()` returns data identical in shape/content to the former `get_dashboard()` for storage/activity/notes, and confirms **no `recent_secrets` key is present** in the response — a direct regression check for the removal decision.
- Integration tests for `routes/workbench.py`:
  - `GET /api/workbench` without a session → 401; with a session → 200 with the full `WorkbenchOut` shape, including `tool_catalog`.
  - `PUT /api/workbench/layout` valid payload → 200, reflected on subsequent `GET`.
  - `PUT /api/workbench/layout` with an unknown pinned-tool key → 422; with an unrecognized panel `type` → 200 (not rejected — confirms the §2 behavior above at the route level, not just the service level).
  - `POST /api/workbench/layout/reset` → 200 with the default layout, confirmed via a subsequent `GET`.

## 2. Frontend tests

No frontend test tooling exists in this stack yet (per [`../../06_TECH_STACK.md`](../../06_TECH_STACK.md) §5). Unchanged from v0.1.0 — frontend coverage relies on §3 manual verification.

## 3. Manual verification

**Functional:**

- Pin a tool, confirm it appears in the Pinned Tools panel in pinned order, reload, confirm it persists.
- Pin `prompt_studio` (or `universal_converter`), confirm it renders as a disabled "Coming soon" tile, not a dead link.
- Unpin a tool, confirm immediate removal and persistence after reload.
- Reorder panels via drag in customize mode; confirm the new order persists after reload.
- Reorder panels via the keyboard-only fallback; confirm parity with drag reordering.
- Hide a panel, confirm it disappears from view mode and reappears (dimmed) in customize mode.
- Hide every panel, confirm the all-hidden empty state renders instead of a blank page.
- Trigger "Reset to default layout," confirm the confirmation step appears and the default (5 panels, 6 pinned tools) is restored exactly.
- Navigate to `/search` directly and via the Pinned Tools panel's Search tile; confirm results match what the command palette shows for the same query.
- Confirm the former `/api/dashboard`/Dashboard UI no longer exists anywhere reachable in the app.
- Verify dark mode and mobile-width (single-column) rendering for every panel, the pin picker, and `/search`.

**Performance** (targets set in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §4):

- Measure initial Workbench render time on a local Docker Compose deployment (cold load, `GET /api/workbench` through fully painted grid) using browser devtools' Performance/Network panel.
- Record frame rate during a drag-reorder interaction (devtools' Performance panel, or the FPS meter) — confirm no visible jank.
- Measure `PUT /api/workbench/layout` round-trip time (Network panel) for a typical payload.
- Use the React DevTools Profiler during a drag interaction to confirm only the dragged panel and its immediate neighbors re-render, not the full grid.

**Accessibility** (targets set in [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §5):

- Full keyboard walkthrough: reach and operate every control in view mode, customize mode, and the pin picker using Tab/Shift+Tab/Enter/Space/Arrow keys alone, no mouse.
- Confirm keyboard-only drag-and-drop reordering (per [`02_UI.md`](02_UI.md) §3.3) using the dnd-kit keyboard sensor.
- Confirm focus lands on a sensible element when entering/exiting customize mode and opening/closing the pin picker, and returns to the triggering control on close.
- Confirm every icon-only control has an accessible name (screen-reader spot check with VoiceOver/NVDA, or an automated pass — see §5's tooling TODO).
- Run an automated accessibility scan (axe or equivalent) against Workbench in both modes and `/search` — first real use of the audit [`../../04_UI_GUIDELINES.md`](../../04_UI_GUIDELINES.md) §4 has flagged as outstanding.

## 4. Regression risk

- **`frontend/features/dashboard/`** is removed as part of this phase — every piece of data it rendered must have a verified equivalent in Workbench (minus Recent Secrets, removed by decision) before its removal.
- **Sidebar and command palette** entries pointing at `/` must continue to resolve correctly, now labeled "Workbench."
- **Existing `ActivityLog` and `Note` queries** are reused unmodified.
- **Vault → Secrets compatibility migration** ([ADR-0006](../../decisions/0006-vault-renamed-to-secrets.md)) carries its own regression risk to the Vault/Secrets feature itself. Minimum coverage: the Secrets pinned-tool tile and the Quick Actions "new secret" action both resolve correctly post-rename; **and** the old `/vault` route and `/api/vault` endpoint still work as aliases (not 404s) — the whole point of the compatibility-migration approach is that nothing that worked before the rename breaks during it.
- **Command palette search** must continue to work exactly as before — the new `/search` page is additive, not a replacement for palette search.

## 5. TODO

- [ ] TODO: Write `test_workbench.py` once [`03_BACKEND.md`](03_BACKEND.md) is confirmed.
- [ ] TODO: Decide the automated accessibility scan tool (axe-core via a manual browser extension pass vs. a scripted check) — no frontend test runner exists yet to wire it into CI (see §2).
- [ ] TODO: Revisit §2 once a frontend test tooling decision is made at the project level.

## 6. Cross-references

- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [12_PANEL_INTERFACE.md](12_PANEL_INTERFACE.md)
- [../../07_CODING_STANDARDS.md](../../07_CODING_STANDARDS.md)
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
