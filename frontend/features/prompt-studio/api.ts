import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export type PromptVariableType = "string" | "number" | "boolean";

export interface PromptVariable {
  name: string;
  type: PromptVariableType;
  required: boolean;
  default?: string | number | boolean | null;
  description?: string | null;
}

export interface Prompt {
  id: string;
  name: string;
  description: string | null;
  body: string;
  variables: PromptVariable[];
  tags: string[];
  version_number: number;
  created_at: string;
  updated_at: string;
}

export interface PromptListItem {
  id: string;
  name: string;
  description: string | null;
  tags: string[];
  version_number: number;
  updated_at: string;
}

export interface PromptVersion {
  id: string;
  version_number: number;
  body: string;
  variables: PromptVariable[];
  note: string | null;
  created_at: string;
}

export interface PromptVersionListItem {
  id: string;
  version_number: number;
  note: string | null;
  created_at: string;
}

export interface PromptCreateInput {
  name: string;
  description?: string | null;
  body: string;
  variables?: PromptVariable[];
  tags?: string[];
}

export interface PromptUpdateMetaInput {
  name?: string;
  description?: string | null;
  tags?: string[];
}

export interface PromptUpdateContentInput {
  body: string;
  variables: PromptVariable[];
}

function buildQuery(params: Record<string, string | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value) search.set(key, value);
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export const promptStudioApi = {
  list: (search?: string, tag?: string) =>
    api.get<{ items: PromptListItem[] }>(`/api/prompts${buildQuery({ search, tag })}`),
  get: (id: string) => api.get<Prompt>(`/api/prompts/${id}`),
  create: (input: PromptCreateInput) => api.post<Prompt>("/api/prompts", input),
  updateMeta: (id: string, input: PromptUpdateMetaInput) => api.patch<Prompt>(`/api/prompts/${id}`, input),
  updateContent: (id: string, input: PromptUpdateContentInput) => api.put<Prompt>(`/api/prompts/${id}/content`, input),
  remove: (id: string) => api.delete<void>(`/api/prompts/${id}`),
  duplicate: (id: string) => api.post<Prompt>(`/api/prompts/${id}/duplicate`),
  listVersions: (id: string) => api.get<{ items: PromptVersionListItem[] }>(`/api/prompts/${id}/versions`),
  getVersion: (id: string, versionId: string) => api.get<PromptVersion>(`/api/prompts/${id}/versions/${versionId}`),
  restoreVersion: (id: string, versionId: string) =>
    api.post<Prompt>(`/api/prompts/${id}/versions/${versionId}/restore`),
};

export function usePrompts(search?: string, tag?: string) {
  return useQuery({
    queryKey: ["prompt-studio", "list", search ?? "", tag ?? ""],
    queryFn: () => promptStudioApi.list(search, tag),
  });
}

export function usePrompt(id: string | null) {
  return useQuery({
    queryKey: ["prompt-studio", "detail", id],
    queryFn: () => promptStudioApi.get(id as string),
    enabled: !!id,
  });
}

export function usePromptVersions(id: string | null) {
  return useQuery({
    queryKey: ["prompt-studio", "versions", id],
    queryFn: () => promptStudioApi.listVersions(id as string),
    enabled: !!id,
  });
}

export function usePromptVersion(id: string | null, versionId: string | null) {
  return useQuery({
    queryKey: ["prompt-studio", "version", id, versionId],
    queryFn: () => promptStudioApi.getVersion(id as string, versionId as string),
    enabled: !!id && !!versionId,
  });
}

export function usePromptStudioMutations() {
  const qc = useQueryClient();
  const invalidateList = () => qc.invalidateQueries({ queryKey: ["prompt-studio", "list"] });
  const invalidateVersions = (id: string) => qc.invalidateQueries({ queryKey: ["prompt-studio", "versions", id] });

  return {
    create: useMutation({ mutationFn: promptStudioApi.create, onSuccess: invalidateList }),
    updateMeta: useMutation({
      mutationFn: ({ id, input }: { id: string; input: PromptUpdateMetaInput }) => promptStudioApi.updateMeta(id, input),
      onSuccess: (prompt) => {
        invalidateList();
        qc.setQueryData(["prompt-studio", "detail", prompt.id], prompt);
      },
    }),
    updateContent: useMutation({
      mutationFn: ({ id, input }: { id: string; input: PromptUpdateContentInput }) =>
        promptStudioApi.updateContent(id, input),
      onSuccess: (prompt) => {
        invalidateList();
        invalidateVersions(prompt.id);
        qc.setQueryData(["prompt-studio", "detail", prompt.id], prompt);
      },
    }),
    remove: useMutation({
      mutationFn: promptStudioApi.remove,
      onSuccess: (_data, id) => {
        invalidateList();
        qc.removeQueries({ queryKey: ["prompt-studio", "detail", id] });
        qc.removeQueries({ queryKey: ["prompt-studio", "versions", id] });
      },
    }),
    duplicate: useMutation({ mutationFn: promptStudioApi.duplicate, onSuccess: invalidateList }),
    restoreVersion: useMutation({
      mutationFn: ({ id, versionId }: { id: string; versionId: string }) => promptStudioApi.restoreVersion(id, versionId),
      onSuccess: (prompt) => {
        invalidateList();
        invalidateVersions(prompt.id);
        qc.setQueryData(["prompt-studio", "detail", prompt.id], prompt);
      },
    }),
  };
}
