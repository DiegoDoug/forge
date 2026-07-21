import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export interface WorkbenchPanelState {
  type: string;
  visible: boolean;
}

export interface PinnedTool {
  key: string;
  available: boolean;
}

export interface ToolCatalogEntry {
  key: string;
  available: boolean;
}

export interface WorkbenchLayout {
  panels: WorkbenchPanelState[];
  pinned_tools: PinnedTool[];
  tool_catalog: ToolCatalogEntry[];
}

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

export interface WorkbenchData {
  version: string;
  storage: {
    database_bytes: number;
    disk_total_bytes: number;
    disk_used_bytes: number;
    disk_free_bytes: number;
  };
  recent_activity: ActivityEntry[];
  recent_notes: DashboardNote[];
}

export interface WorkbenchOut {
  layout: WorkbenchLayout;
  data: WorkbenchData;
}

export interface WorkbenchLayoutUpdate {
  panels: WorkbenchPanelState[];
  pinned_tools: string[];
}

export const workbenchApi = {
  get: () => api.get<WorkbenchOut>("/api/workbench"),
  updateLayout: (input: WorkbenchLayoutUpdate) => api.put<WorkbenchLayout>("/api/workbench/layout", input),
  resetLayout: () => api.post<WorkbenchLayout>("/api/workbench/layout/reset"),
};

const WORKBENCH_KEY = ["workbench"];

export function useWorkbenchQuery() {
  return useQuery({ queryKey: WORKBENCH_KEY, queryFn: workbenchApi.get });
}

export function useUpdateLayoutMutation() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: workbenchApi.updateLayout,
    onMutate: async (input) => {
      await qc.cancelQueries({ queryKey: WORKBENCH_KEY });
      const previous = qc.getQueryData<WorkbenchOut>(WORKBENCH_KEY);
      if (previous) {
        qc.setQueryData<WorkbenchOut>(WORKBENCH_KEY, {
          ...previous,
          layout: {
            ...previous.layout,
            panels: input.panels,
            pinned_tools: input.pinned_tools.map((key) => {
              const existing = previous.layout.pinned_tools.find((t) => t.key === key);
              const catalogEntry = previous.layout.tool_catalog.find((t) => t.key === key);
              return { key, available: existing?.available ?? catalogEntry?.available ?? false };
            }),
          },
        });
      }
      return { previous };
    },
    onError: (_err, _input, context) => {
      if (context?.previous) qc.setQueryData(WORKBENCH_KEY, context.previous);
    },
    onSettled: () => qc.invalidateQueries({ queryKey: WORKBENCH_KEY }),
  });
}

export function useResetLayoutMutation() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: workbenchApi.resetLayout,
    onSuccess: () => qc.invalidateQueries({ queryKey: WORKBENCH_KEY }),
  });
}
