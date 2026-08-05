# BUG-0001 — Retiring a Workbench tool key 500s the entire Workbench for anyone who had it pinned

> **Classification:** 🔴 BLOCKER — a core, always-visible surface is completely unusable, per [`../../../12_BUG_CLASSIFICATION.md`](../../../12_BUG_CLASSIFICATION.md) §2
> **Status:** ✅ Fixed and verified
> **Found:** Phase 08 manual verification (T8), 2026-08-05 — against a real instance with real pre-existing user data
> **Fixed:** Same day
> **File:** `backend/app/services/workbench.py` (`serialize_layout`)

---

## The bug

`serialize_layout()` built each pinned tool's entry with a direct, unguarded dictionary index:

```python
"pinned_tools": [
    {"key": key, "available": WORKBENCH_TOOL_KEYS[key]["available"]} for key in pinned_tool_keys
],
```

`pinned_tool_keys` is **user data**, read from the persisted `workbench_layout.pinned_tools` JSON column. It was written against whatever tool catalog existed at the time the user last customized their Workbench. `WORKBENCH_TOOL_KEYS` is **current code**.

When those two disagree — specifically, when a key exists in the saved layout but no longer exists in the catalog — the index raises `KeyError`, which surfaces as **`GET /api/workbench` → 500**. That endpoint backs the entire Workbench page, so the result is not a missing tile; it is the whole home screen replaced by "Couldn't load your Workbench layout."

Phase 08 is what made the two disagree: [`01_SPEC.md`](../../../implementation/Phase-08-Developer-Toolkit/01_SPEC.md) §3 requirement 4 retires the `"generators"`, `"crypto"`, and `"utilities"` keys in favor of a single `"developer_toolkit"`.

## How it was found

Not by a test — by actually loading the Workbench during the T8 manual pass, against a real instance whose persisted layout was:

```json
["notes", "generators", "documents", "secrets", "utilities", "converters"]
```

Two retired keys, `generators` and `utilities`. The Workbench was dead on arrival.

Worth recording plainly: the code comment written alongside the catalog merge asserted that a user who had pinned a retired tool "simply loses that pin." That was an assumption about behavior that had never been verified, and it was wrong. The automated gates all passed — 292 backend tests, typecheck, lint, production build, Docker build — because none of them exercises a layout containing a stale key. Only real data did.

## Why this is a BLOCKER

The Workbench is Forge's home screen ([ADR-0001](../../../decisions/0001-workbench-replaces-dashboard.md) made it the replacement for the Dashboard outright). A phase that renders it permanently unloadable for a subset of real users, on upgrade, with no user action able to recover it, is not a MINOR or MAJOR nit — the affected user cannot reach the Workbench at all, and cannot un-pin the offending tool precisely because the page that would let them do so is the page that is broken.

## Scope note — was fixing this in scope for Phase 08?

Yes, and deliberately checked against [`IMPLEMENT.md`](../../../implementation/Phase-08-Developer-Toolkit/IMPLEMENT.md)'s scope lock rather than assumed. The defect is *caused by* Phase 08's own catalog merge; [`08_ACCEPTANCE.md`](../../../implementation/Phase-08-Developer-Toolkit/08_ACCEPTANCE.md) §4 requires that no other Workbench panel regresses, and FR4 requires the merge itself. Leaving it would mean shipping a phase that breaks the application's home screen. Per the kickoff prompt's finding procedure, this is a true dependency of the approved work, so it takes the smallest justified change — a guard in the existing function — rather than a redesign.

## Pre-existing latency

This fragility predates Phase 08. Phase 04 (Universal Converter) retired the `"ingest"` and `"universal_converter"` keys the same way and had the identical unguarded lookup; it simply never triggered, because no layout in play at the time happened to pin `ingest`. Phase 08 is the first phase to retire a key that real saved data actually referenced. The fix is written to cover the general case, not just this phase's three keys.

## The fix

Skip pinned keys that are no longer in the catalog, rather than indexing blindly:

```python
"pinned_tools": [
    {"key": key, "available": WORKBENCH_TOOL_KEYS[key]["available"]}
    for key in pinned_tool_keys
    if key in WORKBENCH_TOOL_KEYS
],
```

Dropping the stale pin (rather than rendering it as unavailable) is the correct behavior here: the retired tool has no `tool-metadata.ts` entry either, so there is no title, icon, or href to render a tile from — an "unavailable" entry would just move the failure to the frontend.

Read-only: nothing rewrites the persisted layout. The stale key stays in storage, inert, and disappears from the payload; the next time the user saves a layout it is written out without it. `update_layout`'s existing `_validate_pinned_tools` still rejects an unknown key on write, so a stale key cannot be newly introduced.

## Verification

- New regression test `test_serialize_layout_skips_pins_for_retired_tool_keys` in `backend/tests/test_workbench.py`, asserting a layout pinning both live and retired keys serializes to the live ones only, and that the retired keys are absent from the catalog while `developer_toolkit` is present.
- **The test was confirmed to actually catch the bug**: with the guard temporarily removed it fails with `KeyError: 'generators'`; with the guard restored it passes. A regression test that passes either way would have been worthless here.
- Full backend suite re-run after the fix.
- Live re-verification against the same real instance and the same real persisted layout that exhibited the 500.

## Cross-references

- [../../implementation/Phase-08-Developer-Toolkit/01_SPEC.md](../../implementation/Phase-08-Developer-Toolkit/01_SPEC.md) §3 requirement 4 — the catalog merge that triggered this
- [../../implementation/Phase-08-Developer-Toolkit/08_ACCEPTANCE.md](../../implementation/Phase-08-Developer-Toolkit/08_ACCEPTANCE.md) §4 — the regression criterion this was caught by
- [../../implementation/Phase-08-Developer-Toolkit/07_TESTING.md](../../implementation/Phase-08-Developer-Toolkit/07_TESTING.md) §4 — Workbench listed as a regression risk area
- [../../../12_BUG_CLASSIFICATION.md](../../../12_BUG_CLASSIFICATION.md) §2
- [../../implementation/Phase-04-Universal-Converter/01_SPEC.md](../../implementation/Phase-04-Universal-Converter/01_SPEC.md) — the earlier key retirement that shared this latent fragility
