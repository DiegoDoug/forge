# QA-0001 — Verify keyboard activation of the shared `Tabs` primitive with a real keyboard

> **Purpose:** Close out the keyboard-navigation criterion in [`08_ACCEPTANCE.md`](../../../implementation/Phase-08-Developer-Toolkit/08_ACCEPTANCE.md) §2 that the T8 automated browser session could not answer conclusively.
> **Status:** Open — not yet run
> **Owner:** TODO — assign a QA owner
> **Type:** Manual Browser Session (not automatable in this repo's current toolchain — no frontend test runner exists per [`07_TESTING.md`](../../../implementation/Phase-08-Developer-Toolkit/07_TESTING.md) §2)
> **Blocks Phase 08 sign-off:** No — and, critically, the behavior in question is **pre-existing, not introduced by Phase 08** (see below). Tracked here so it is neither silently dropped nor falsely checked off, per [`../../../13_PHASE_LIFECYCLE.md`](../../../13_PHASE_LIFECYCLE.md) §3.

---

## What was observed

During Phase 08's T8 verification, against the real running instance:

- `Tab`/focus reaches the top-level `Generators` / `Crypto` / `Utilities` tabs. ✅
- The tabs carry correct ARIA semantics — `role="tablist"` wrapping three `role="tab"` buttons, each with a matching `role="tabpanel"`. ✅
- `ArrowRight` **moves focus** from `Generators` to `Crypto`. ✅
- But neither `Enter` nor `Space` on the focused tab **activated** it — the active tab stayed `Generators`. ❓

## Why this is not a Phase 08 regression

This was checked before filing, rather than assumed. The identical behavior occurs on the **nested Crypto tab set** (`Encode & Hash` / `AES` / `JWT` / `RSA & ECC`), which is:

- rendered from the same `components/ui/tabs.tsx` primitive;
- **uncontrolled** (`defaultValue="encode"`), unlike Phase 08's outer tabs which are controlled (`value` + `onValueChange`);
- byte-for-byte the same JSX as the pre-Phase-08 standalone `/crypto` page, which Phase 08 did not modify (confirmed against `git show 5a47d1a:"frontend/app/(app)/crypto/page.tsx"`).

Since the unmodified, uncontrolled, pre-existing tab set behaves exactly the same way as the new controlled one, the behavior belongs to the shared primitive (or to the test harness — see below), not to anything Phase 08 introduced. Phase 08's controlled wiring was the obvious suspect and was specifically ruled out by this comparison.

## The open question

Two explanations remain, and the automated session cannot distinguish them:

1. **Harness artifact.** The synthetic key events dispatched by the automation tool may not carry whatever properties Base UI's `TabsTab` handler requires (it consults pointer/press state — see `isPressingRef` and `activateOnFocus` in `@base-ui/react/tabs/tab/TabsTab.js`). Real hardware key events may activate the tab correctly, in which case there is nothing to fix.
2. **A genuine accessibility gap in the shared primitive**, affecting every `Tabs` consumer in the app — today that is the Developer Toolkit page and `features/ingest/preview-sheet.tsx`.

Mouse activation works correctly in both cases, verified repeatedly during T8, so this affects keyboard-only users specifically.

## How to run it

1. Open `http://localhost:8585/developer-toolkit` in a real browser tab (not an automation-driven one).
2. Press `Tab` until the `Generators` tab has visible focus.
3. Press `ArrowRight` — confirm focus moves to `Crypto`.
4. Press `Enter`, then (on a fresh load) `Space` — confirm whether the Crypto panel actually becomes active.
5. Repeat inside the nested Crypto tab set (`Encode & Hash` → `AES`).
6. Confirm the same result on `features/ingest/preview-sheet.tsx`'s tabs, reachable from `/converters` after running a document conversion.

## Acceptance criteria

- [ ] A keyboard-only user can both focus **and activate** every top-level tab on `/developer-toolkit`.
- [ ] The same holds for the nested Crypto tab set.
- [ ] If explanation 1 (harness artifact) is confirmed, close this ticket and note that `08_ACCEPTANCE.md` §2's keyboard criterion is genuinely met.
- [ ] If explanation 2 (real gap) is confirmed, this becomes a bug against `frontend/components/ui/tabs.tsx` — a **shared, cross-feature primitive**, so it belongs in its own scoped fix affecting every consumer, **not** in Phase 08's directory. Phase 08 is explicitly barred from redesigning shared UI it did not introduce ([`01_SPEC.md`](../../../implementation/Phase-08-Developer-Toolkit/01_SPEC.md) §5, [`IMPLEMENT.md`](../../../implementation/Phase-08-Developer-Toolkit/IMPLEMENT.md) scope lock).

## Cross-references

- [../../implementation/Phase-08-Developer-Toolkit/08_ACCEPTANCE.md](../../implementation/Phase-08-Developer-Toolkit/08_ACCEPTANCE.md) §2 — the keyboard criterion this defers
- [../../implementation/Phase-08-Developer-Toolkit/02_UI.md](../../implementation/Phase-08-Developer-Toolkit/02_UI.md) §5 — the accessibility position this phase took (reuse the existing primitive, introduce no new pattern)
- [../../implementation/Phase-08-Developer-Toolkit/07_TESTING.md](../../implementation/Phase-08-Developer-Toolkit/07_TESTING.md) §2 — why no automated frontend test can close this
- [../../../13_PHASE_LIFECYCLE.md](../../../13_PHASE_LIFECYCLE.md) §3 — why a QA ticket does not block sign-off
