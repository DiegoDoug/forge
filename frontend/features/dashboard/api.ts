import { api } from "@/lib/api-client";

export interface ActivityEntry {
  id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  summary: string;
  created_at: string;
}

export interface DashboardNote {
  id: string;
  title: string;
  color: string;
  updated_at: string;
}

export interface DashboardSecret {
  id: string;
  name: string;
  type: string;
  updated_at: string;
}

export interface DashboardData {
  version: string;
  storage: {
    database_bytes: number;
    disk_total_bytes: number;
    disk_used_bytes: number;
    disk_free_bytes: number;
  };
  recent_activity: ActivityEntry[];
  recent_notes: DashboardNote[];
  recent_secrets: DashboardSecret[];
}

export const dashboardApi = {
  get: () => api.get<DashboardData>("/api/dashboard"),
};
