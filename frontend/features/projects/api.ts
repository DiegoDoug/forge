import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api-client";
import type { PlaygroundRun, PlaygroundRunListItem } from "@/features/model-playground/api";

export interface Project {
  id: string;
  name: string;
  description: string;
  color: string;
  archived: boolean;
  default_provider: string | null;
  default_model: string | null;
  secret_count: number;
  note_count: number;
  document_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectSummary {
  id: string;
  name: string;
  color: string;
  archived: boolean;
  secret_count: number;
  note_count: number;
  document_count: number;
  updated_at: string;
}

export interface ProjectCreateInput {
  name: string;
  description?: string;
  color?: string;
  default_provider?: string | null;
  default_model?: string | null;
}

export interface ProjectUpdateInput {
  name?: string;
  description?: string;
  color?: string;
  archived?: boolean;
  default_provider?: string | null;
  default_model?: string | null;
  clear_default_ai?: boolean;
}

function buildQuery(params: Record<string, string | number | boolean | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) search.set(key, String(value));
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export const projectsApi = {
  list: (archived = false) => api.get<ProjectSummary[]>(`/api/projects${buildQuery({ archived })}`),
  get: (id: string) => api.get<Project>(`/api/projects/${id}`),
  create: (input: ProjectCreateInput) => api.post<Project>("/api/projects", input),
  update: (id: string, input: ProjectUpdateInput) => api.patch<Project>(`/api/projects/${id}`, input),
  remove: (id: string) => api.delete<void>(`/api/projects/${id}`),
  runAi: (id: string, prompt: string) => api.post<PlaygroundRun>(`/api/projects/${id}/ai/run`, { prompt }),
  listAiRuns: (id: string, limit?: number) =>
    api.get<{ items: PlaygroundRunListItem[] }>(`/api/projects/${id}/ai/runs${buildQuery({ limit })}`),
};

export function useProjects(archived = false) {
  return useQuery({ queryKey: ["projects", { archived }], queryFn: () => projectsApi.list(archived) });
}

export function useProject(id: string | null) {
  return useQuery({
    queryKey: ["projects", "project", id],
    queryFn: () => projectsApi.get(id as string),
    enabled: !!id,
  });
}

export function useProjectAiRuns(id: string | null) {
  return useQuery({
    queryKey: ["projects", "project", id, "ai-runs"],
    queryFn: () => projectsApi.listAiRuns(id as string),
    enabled: !!id,
  });
}

export function useProjectMutations() {
  const qc = useQueryClient();
  const invalidateList = () => qc.invalidateQueries({ queryKey: ["projects"] });

  return {
    create: useMutation({ mutationFn: projectsApi.create, onSuccess: invalidateList }),
    update: useMutation({
      mutationFn: ({ id, input }: { id: string; input: ProjectUpdateInput }) => projectsApi.update(id, input),
      onSuccess: (project) => {
        invalidateList();
        qc.setQueryData(["projects", "project", project.id], project);
      },
    }),
    remove: useMutation({
      mutationFn: projectsApi.remove,
      onSuccess: (_data, id) => {
        invalidateList();
        qc.removeQueries({ queryKey: ["projects", "project", id] });
      },
    }),
  };
}

export function useProjectAiRun(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (prompt: string) => projectsApi.runAi(id, prompt),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects", "project", id, "ai-runs"] });
      qc.invalidateQueries({ queryKey: ["model-playground", "runs"] });
    },
  });
}
