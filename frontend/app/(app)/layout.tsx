import { AuthGate } from "@/features/auth/auth-gate";
import { CommandPaletteProvider } from "@/components/command-palette/command-palette-provider";
import { AppShell } from "@/components/app-shell/app-shell";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGate>
      <CommandPaletteProvider>
        <AppShell>{children}</AppShell>
      </CommandPaletteProvider>
    </AuthGate>
  );
}
