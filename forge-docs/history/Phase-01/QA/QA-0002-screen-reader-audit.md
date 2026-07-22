# QA-0002 — Screen reader audit

> **Purpose:** Close out the one accessibility criterion in [`../../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md`](../../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md) §5 that T16 could not perform — a live assistive-technology pass.
> **Status:** Open — not yet run
> **Owner:** TODO — assign a QA owner
> **Type:** Manual audit — NVDA, VoiceOver, keyboard-only
> **Blocks Phase 01 sign-off:** No — tracked here specifically so it does not block. See [`../../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md`](../../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md) §5 and [`../../../implementation/Phase-01-Workbench/CURRENT_STATE.md`](../../../implementation/Phase-01-Workbench/CURRENT_STATE.md) for why.

---

## Why this is a QA task, not an implementation task

T16 substituted an automated `axe-core` scan (zero violations in Workbench's own view mode, customize mode, the pin picker, and `/search`) plus direct accessibility-tree inspection (every control's accessible name, every "Hidden"/"Coming soon" state) for a live screen-reader pass. That substitution covers a meaningful fraction of what NVDA/VoiceOver would catch, but not all of it — axe cannot tell you whether announcements are *coherent* in the order and phrasing a real screen-reader user experiences them, only whether the underlying markup is structurally valid. A live pass needs a real screen reader and a real listener, which is a QA activity.

## Scope

- Workbench, view mode (`/`)
- Workbench, customize mode (drag handles, visibility switches, "Manage pinned tools", "Reset to default")
- The Pin Picker dialog
- `/search`

## Acceptance criteria (from `08_ACCEPTANCE.md` §5)

- [ ] **NVDA** (Windows) pass: panel titles, "Hidden" state, "Coming soon" badges, loading/error states, and every control (drag handle, visibility switch, pin/unpin switch, Reset, Manage pinned tools) are announced correctly and in a sensible order.
- [ ] **VoiceOver** (macOS/iOS) pass: same coverage as above.
- [ ] **Keyboard-only** pass (no mouse, real hardware — not a scripted key-dispatch): Tab/Shift+Tab/Enter/Space/Arrow keys alone reach and operate every control in view mode, customize mode, and the pin picker; the dnd-kit keyboard-sensor reorder (Space to pick up, arrows to move, Space to drop, Escape to cancel) works correctly; focus lands on a sensible element and returns to the trigger when entering/exiting customize mode and opening/closing the pin picker.

## How to run it

1. NVDA: use a real Windows machine with NVDA running, navigate through the scope above with the screen reader active, note anything mis-announced, silent, or confusingly ordered.
2. VoiceOver: same, on macOS (Cmd+F5) or iOS.
3. Keyboard-only: unplug/ignore the mouse, walk the same scope with a real keyboard, including the drag-and-drop reorder flows.

## Result

_Not yet run. Fill in with findings and a pass/fail once done._

## Cross-references

- [../../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md](../../../implementation/Phase-01-Workbench/08_ACCEPTANCE.md) §5
- [../../../implementation/Phase-01-Workbench/07_TESTING.md](../../../implementation/Phase-01-Workbench/07_TESTING.md) §3
- [../../../implementation/Phase-01-Workbench/CURRENT_STATE.md](../../../implementation/Phase-01-Workbench/CURRENT_STATE.md)
