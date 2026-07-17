import { api } from "@/lib/api-client";

export interface AboutInfo {
  name: string;
  version: string;
  environment: string;
}

export interface BackupBundle {
  version: number;
  exported_at: string;
  folders: unknown[];
  tags: unknown[];
  secrets: unknown[];
  notes: unknown[];
}

export const settingsApi = {
  about: () => api.get<AboutInfo>("/api/settings/about"),
  updateTheme: (theme: string) => api.put<{ theme: string }>("/api/settings/theme", { theme }),
  exportBackup: () => api.get<BackupBundle>("/api/settings/backup"),
  importBackup: (bundle: BackupBundle) => api.post<Record<string, number>>("/api/settings/backup/import", bundle),
};
