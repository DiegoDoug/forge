# Frontend Reimagine — Backend

> **Purpose:** State this phase's backend impact.
> **Scope:** This phase only.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Approved 2026-08-06; holds as implemented — zero backend diff confirmed throughout and re-verified at RC 2026-08-07.
> **Version:** 0.1.0
> **Last Updated:** 2026-08-06
> **Depends On:** [01_SPEC.md](01_SPEC.md)

---

## 1. Backend impact: none

**No file under `backend/` is created, modified, or deleted by this phase.**

Phase 09 is a presentation-layer phase. Every one of the 112 endpoints across 18 route modules keeps its path, method, request shape, response shape, status codes, and error contract. No service is added or extended. No router is touched. No `WORKBENCH_TOOL_KEYS` entry changes.

This is stated explicitly rather than left as an unfilled template so that a future session does not have to re-derive it — and so that any backend diff appearing on this phase's branch is immediately identifiable as out of contract.

## 2. The one server-adjacent change, and why it is not a backend change

[`00_AUDIT.md`](00_AUDIT.md) §3.2 records a 🟡 MAJOR defect: `app/(app)/settings/page.tsx` calls `fetch("/system/status")`, which 404s.

The endpoint is **not** missing. `backend/app/api/routes/health.py:23` serves `GET /system/status` and returns exactly the payload Settings expects. It is mounted at the application root, without the `/api` prefix.

The break is in the frontend proxy configuration. `frontend/next.config.ts` rewrites only:

```ts
{ source: "/api/:path*", destination: `${backendUrl}/api/:path*` },
{ source: "/health",     destination: `${backendUrl}/health` },
```

`/system/status` matches neither, so the browser request is served by Next.js, which has no such route, and `.json()` then rejects on an HTML 404 body.

**Fix (task T13):** add one rewrite to `frontend/next.config.ts`.

```ts
{ source: "/system/status", destination: `${backendUrl}/system/status` },
```

This is a frontend build-configuration change. It adds no endpoint, alters no handler, and changes no contract — it makes an already-shipped endpoint reachable through the same proxy layer that already carries `/health`.

### 2.1 The alternative, and why it was not chosen

Settings could instead read `GET /api/workbench`, which already returns an identical `storage` object and is already proxied. That would also work with no config change.

It was rejected because it makes the Settings page depend on the Workbench feature's endpoint for system information, coupling two unrelated features to save one line of config. The rewrite keeps each surface reading the endpoint that semantically owns its data.

### 2.2 Production parity

In production, Nginx (`docker/nginx.conf`) proxies in front of both services rather than Next.js, so the rewrite is inert there — exactly as the existing `/api/*` and `/health` rewrites are. **T13 must verify that `docker/nginx.conf` already routes `/system/status` to the backend**; if it does not, that is a genuine production gap and a finding to raise, not a change to make silently.

## 3. Boundaries this phase upholds

From [`../../03_ARCHITECTURE.md`](../../03_ARCHITECTURE.md) §2 and [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md):

- Endpoint-shape knowledge stays inside `features/*/api.ts`. Phase 09 **reduces** violations of this from one to zero by removing the raw `fetch` in Settings.
- No component gains direct backend coupling.
- Routers stay thin — trivially satisfied, since no router is touched.
- Models remain the schema source of truth — no schema is touched.

## 4. If a backend change turns out to be necessary

Per [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) §6 and Phase 09's own charter: **stop, do not implement, and raise it as a blocking architectural decision** with a drafted ADR. Do not modify backend behavior to make a frontend layout easier. A frontend that cannot be built without a backend change is a finding about the specification, not a licence to edit the backend.

## 5. Cross-references

- [00_AUDIT.md](00_AUDIT.md) §3.2 · [01_SPEC.md](01_SPEC.md) FR14 · [04_DATABASE.md](04_DATABASE.md) · [06_API.md](06_API.md)
- [../../03_ARCHITECTURE.md](../../03_ARCHITECTURE.md) · [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
