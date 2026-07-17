"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useTheme } from "next-themes";
import { useRef, useState } from "react";
import { Download, Moon, Sun, Upload } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/page-header";
import { ToolCard } from "@/components/tool-card";
import { formatBytes } from "@/lib/format";
import { authApi } from "@/features/auth/api";
import { settingsApi, type BackupBundle } from "@/features/settings/api";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const aboutQuery = useQuery({ queryKey: ["settings", "about"], queryFn: settingsApi.about });
  const statusQuery = useQuery({
    queryKey: ["settings", "system-status"],
    queryFn: () => fetch("/system/status").then((r) => r.json()),
  });

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const themeMutation = useMutation({ mutationFn: settingsApi.updateTheme });
  const passwordMutation = useMutation({
    mutationFn: () => authApi.changePassword(currentPassword, newPassword),
    onSuccess: () => {
      toast.success("Master password updated");
      setCurrentPassword("");
      setNewPassword("");
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed to change password"),
  });

  const importMutation = useMutation({
    mutationFn: settingsApi.importBackup,
    onSuccess: (result) => toast.success(`Imported ${result.secrets} secrets, ${result.notes} notes`),
    onError: (err) => toast.error(err instanceof Error ? err.message : "Import failed"),
  });

  function setThemeAndSync(next: string) {
    setTheme(next);
    themeMutation.mutate(next);
  }

  async function handleExport() {
    const bundle = await settingsApi.exportBackup();
    const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `forge-backup-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function handleImportFile(file: File) {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const bundle = JSON.parse(reader.result as string) as BackupBundle;
        importMutation.mutate(bundle);
      } catch {
        toast.error("Invalid backup file");
      }
    };
    reader.readAsText(file);
  }

  return (
    <div>
      <PageHeader title="Settings" description="Theme, master password, backups, and system info" />

      <div className="grid gap-4 p-4 md:grid-cols-2 md:p-6">
        <ToolCard title="Appearance" description="Dark mode by default">
          <div className="flex gap-2">
            <Button variant={theme === "dark" ? "default" : "outline"} size="sm" onClick={() => setThemeAndSync("dark")}>
              <Moon className="h-3.5 w-3.5" />
              Dark
            </Button>
            <Button variant={theme === "light" ? "default" : "outline"} size="sm" onClick={() => setThemeAndSync("light")}>
              <Sun className="h-3.5 w-3.5" />
              Light
            </Button>
            <Button variant={theme === "system" ? "default" : "outline"} size="sm" onClick={() => setThemeAndSync("system")}>
              System
            </Button>
          </div>
        </ToolCard>

        <ToolCard title="Master password" description="Changes take effect immediately for new sessions">
          <div className="flex flex-col gap-2">
            <div>
              <Label htmlFor="current-pw" className="text-xs text-muted-foreground">
                Current password
              </Label>
              <Input id="current-pw" type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} />
            </div>
            <div>
              <Label htmlFor="new-pw" className="text-xs text-muted-foreground">
                New password
              </Label>
              <Input id="new-pw" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
            </div>
            <Button
              size="sm"
              className="w-fit"
              onClick={() => passwordMutation.mutate()}
              disabled={!currentPassword || newPassword.length < 8 || passwordMutation.isPending}
            >
              Update password
            </Button>
          </div>
        </ToolCard>

        <ToolCard title="Backup" description="Vault values stay encrypted inside the export — it's only useful with your master key">
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="h-3.5 w-3.5" />
              Export backup
            </Button>
            <Button variant="outline" size="sm" onClick={() => fileInputRef.current?.click()} disabled={importMutation.isPending}>
              <Upload className="h-3.5 w-3.5" />
              Import backup
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              accept="application/json"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleImportFile(e.target.files[0])}
            />
          </div>
          <p className="text-xs text-muted-foreground">Importing replaces all current vault secrets, folders, tags, and notes.</p>
        </ToolCard>

        <ToolCard title="About" description="System information">
          <div className="flex flex-col gap-1 text-xs text-muted-foreground">
            <span>Forge v{aboutQuery.data?.version ?? "…"}</span>
            <span>Environment: {aboutQuery.data?.environment ?? "…"}</span>
            {statusQuery.data ? (
              <span>
                Storage: {formatBytes(statusQuery.data.storage.database_bytes)} database ·{" "}
                {formatBytes(statusQuery.data.storage.disk_free_bytes)} free
              </span>
            ) : null}
          </div>
        </ToolCard>
      </div>
    </div>
  );
}
