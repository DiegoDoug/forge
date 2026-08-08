import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

// Owns the shell's layout geometry so no page ever recomputes it. `main` is
// the only scroll container in the app: it is sized by flex (topbar shrink-0,
// main flex-1 min-h-0), never by a page-invented viewport-height expression.
// Pages needing a full-height split pane (Documents, Prompt Studio, Notes)
// set their own root to `h-full` and manage their own nested overflow inside
// that fixed box — see Phase 09 T2 / 02_UI.md §1.
export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-dvh overflow-hidden bg-background">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="min-h-0 flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
