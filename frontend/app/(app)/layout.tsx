import { AuthGate } from "@/features/auth/auth-gate";
import { CommandPaletteProvider } from "@/components/command-palette/command-palette-provider";
import { Sidebar } from "@/components/app-shell/sidebar";
import { Topbar } from "@/components/app-shell/topbar";
import "@/features/workbench/register-all";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGate>
      <CommandPaletteProvider>
        <div className="flex h-dvh overflow-hidden bg-background">
          <Sidebar />
          <div className="flex min-w-0 flex-1 flex-col">
            <Topbar />
            <main className="flex-1 overflow-y-auto">{children}</main>
          </div>
        </div>
      </CommandPaletteProvider>
    </AuthGate>
  );
}
