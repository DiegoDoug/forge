// Bootstrap module — imported once from the app shell so every panel-owning
// feature's registration module runs exactly once, deterministically,
// regardless of what else has loaded (per 12_PANEL_INTERFACE.md §4).
// Workbench's own code never lists panels by name; each panel-owning feature
// contributes one import line here instead.
import "./components/pinned-tools-panel";
import "./components/recent-activity-panel";
import "./components/quick-actions-panel";
import "./components/system-status-panel";
import "@/features/notes/workbench-panel";
