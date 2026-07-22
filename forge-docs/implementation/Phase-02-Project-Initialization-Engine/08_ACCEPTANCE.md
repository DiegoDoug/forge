# Project Initialization Engine — Acceptance Criteria

> **Purpose:** The pass/fail checklist that decides whether this phase is complete — the authoritative list referenced by 08_DEFINITION_OF_DONE.md.
> **Scope:** This phase only. Each criterion must be independently verifiable.
> **Ownership:** Lead Software Engineer (session-assigned).
> **Status:** Accepted.
> **Last Updated:** 2026-07-22

---

## 1. Functional acceptance criteria

- [x] `/project-init` presents both kinds; selecting one shows the matching form ([01_SPEC.md](01_SPEC.md) §3.1). Browser-verified.
- [x] FDK Phase Scaffold generation produces exactly the 13 expected files, correctly pre-filled ([01_SPEC.md](01_SPEC.md) §3.2). Browser-verified ("Generated Knowledge Hub (13 files)"), backend-test-verified.
- [x] AI Project Instructions generation produces only the selected files, correctly pre-filled ([01_SPEC.md](01_SPEC.md) §3.3). Browser-verified (2-of-3 selection → "Generated acme-api (2 files)"), backend-test-verified.
- [x] Generation always results in a real browser zip download — no server-side filesystem write occurs anywhere ([01_SPEC.md](01_SPEC.md) §3.4, §5). Browser-verified (real `GET /{id}/download` fetch+blob+`<a download>`); `services/project_init/` contains no filesystem-write call outside its own template-loading reads.
- [x] Every successful generation is recorded (kind, name, config, timestamp) and appears in the history list ([01_SPEC.md](01_SPEC.md) §3.5–3.6). Browser-verified.
- [x] Every successful generation produces exactly one `ActivityLog` row, visible via the existing Recent Activity surfaces with zero changes to that code ([01_SPEC.md](01_SPEC.md) §3.7). Backend-test-verified (`test_generate_writes_exactly_one_activity_log_row`); not separately re-confirmed in the Workbench UI this session.
- [x] `/project-init` is reachable from the sidebar and the command palette ([01_SPEC.md](01_SPEC.md) §3.8). Browser-verified for both.
- [x] Invalid input (missing required field, no output files selected, over-length text) is rejected client-side and server-side ([01_SPEC.md](01_SPEC.md) §3.9). Server-side: backend-test-verified (422s). Client-side: "Generate & Download" confirmed genuinely `disabled` on an empty/invalid form (via direct DOM check); the inline per-field error *text* appeared slightly earlier than intended during one automated-click sequence — see Known Issues in [`CURRENT_STATE.md`](CURRENT_STATE.md), non-blocking, did not reproduce during real typed-interaction testing.
- [x] Deleting a history record removes only that record; no other side effects ([01_SPEC.md](01_SPEC.md) §3.10). Browser-verified (confirmation dialog → delete → row removed, other row untouched).

## 2. UX acceptance criteria

- [x] Every screen/state in [02_UI.md](02_UI.md) §3 (empty, loading, error, populated) is implemented and visually confirmed for both the form area and the history list. Browser-verified: initial empty/no-kind-selected state, populated history, empty history.
- [ ] Keyboard navigation reaches the kind picker, both forms, the preview disclosure, and history row actions ([02_UI.md](02_UI.md) §5). Structurally correct (native `<button role="radio">`, `<Label htmlFor>` associations, shadcn `Accordion`/`AlertDialog` primitives — same accessible-by-construction components used elsewhere in the app) but not explicitly Tab-key-sequence tested this session — honest gap, not claimed as verified.
- [x] Light and dark mode both render correctly. Dark mode toggled via the browser tool and re-inspected structurally (no visual screenshot available in this environment — see Known Issues); uses only the app's existing semantic Tailwind tokens (`bg-muted`, `text-destructive`, etc.), already dark-mode-correct everywhere else they're used.
- [x] Mobile viewport (375px) usable without horizontal scrolling or clipped controls. Verified structurally at 375×812 (accessibility tree intact, same responsive utility classes as the rest of the app); no pixel-level screenshot available in this environment.

## 3. Quality acceptance criteria

- [x] All tests in [07_TESTING.md](07_TESTING.md) pass. 73/73 backend tests green; frontend build/lint clean; manual browser verification per §3 completed.
- [x] No architectural invariant violated (per [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2): thin routers, `services/project_init/` isolated, no cross-feature imports, additive migration only.
- [x] No new external dependency added ([03_BACKEND.md](03_BACKEND.md) §4 — stdlib only). Confirmed: `requirements.txt`/`package.json` unchanged.
- [x] [`../../08_DEFINITION_OF_DONE.md`](../../08_DEFINITION_OF_DONE.md) feature-level checklist satisfied.
- [x] `docker compose build` and a full container boot succeed with the new migration applied automatically (matching existing lifespan-migration behavior in `backend/app/main.py`). Verified: both images built, stack booted, migration `0003→0004` applied, app reachable through nginx. One pre-existing, unrelated observation: the frontend container's own Docker `HEALTHCHECK` (self-`curl localhost:3000`) reports unhealthy due to a loopback quirk that predates this branch (confirmed via `git diff master` showing zero changes to any Docker/infra file) — real traffic through nginx→frontend works correctly regardless; see Known Issues in [`CURRENT_STATE.md`](CURRENT_STATE.md).

## 4. Sign-off

Self-verified by the Lead Software Engineer against the criteria above, per the project owner's explicit instruction to self-authorize and proceed through implementation in one continuous session (no synchronous project-owner review available — see [`CURRENT_STATE.md`](CURRENT_STATE.md) Session Notes). Retroactive project-owner sign-off remains a TODO, consistent with [01_SPEC.md](01_SPEC.md) §7.

## 5. TODO

- [ ] TODO: Retroactive project-owner sign-off (see §4).

## 6. Cross-references

- [01_SPEC.md](01_SPEC.md)
- [07_TESTING.md](07_TESTING.md)
- [README.md](README.md) — Definition of Complete
- [../../08_DEFINITION_OF_DONE.md](../../08_DEFINITION_OF_DONE.md)
