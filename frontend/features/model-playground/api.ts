import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export interface ProviderAvailability {
  provider: string;
  display_name: string;
  configured: boolean;
  models: string[];
}

export interface ProviderCredential {
  id: string;
  provider: string;
  label: string;
  created_at: string;
  updated_at: string;
}

export interface ProviderCredentialInput {
  provider: string;
  label?: string | null;
  api_key: string;
}

export interface RunTarget {
  provider: string;
  model: string;
}

export type PlaygroundResultStatus = "success" | "error" | "timeout";

export interface PlaygroundResult {
  id: string;
  provider: string;
  model: string;
  status: PlaygroundResultStatus;
  response_text: string | null;
  error_message: string | null;
  latency_ms: number | null;
  prompt_tokens: number | null;
  completion_tokens: number | null;
}

export interface PlaygroundRun {
  id: string;
  prompt: string;
  created_at: string;
  results: PlaygroundResult[];
}

export interface PlaygroundRunListItem {
  id: string;
  prompt_excerpt: string;
  providers: string[];
  created_at: string;
}

export const MAX_TARGETS_PER_RUN = 6;

function buildQuery(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) search.set(key, String(value));
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export const modelPlaygroundApi = {
  listProviders: () => api.get<ProviderAvailability[]>("/api/model-playground/providers"),
  listCredentials: () => api.get<{ items: ProviderCredential[] }>("/api/model-playground/credentials"),
  createCredential: (input: ProviderCredentialInput) =>
    api.post<ProviderCredential>("/api/model-playground/credentials", input),
  deleteCredential: (id: string) => api.delete<void>(`/api/model-playground/credentials/${id}`),
  createRun: (input: { prompt: string; targets: RunTarget[] }) =>
    api.post<PlaygroundRun>("/api/model-playground/runs", input),
  listRuns: (limit?: number, offset?: number) =>
    api.get<{ items: PlaygroundRunListItem[] }>(`/api/model-playground/runs${buildQuery({ limit, offset })}`),
  getRun: (id: string) => api.get<PlaygroundRun>(`/api/model-playground/runs/${id}`),
  deleteRun: (id: string) => api.delete<void>(`/api/model-playground/runs/${id}`),
};

export function useProviders() {
  return useQuery({
    queryKey: ["model-playground", "providers"],
    queryFn: modelPlaygroundApi.listProviders,
  });
}

export function useCredentials() {
  return useQuery({
    queryKey: ["model-playground", "credentials"],
    queryFn: modelPlaygroundApi.listCredentials,
  });
}

export function useCredentialMutations() {
  const qc = useQueryClient();
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["model-playground", "providers"] });
    qc.invalidateQueries({ queryKey: ["model-playground", "credentials"] });
  };

  return {
    create: useMutation({ mutationFn: modelPlaygroundApi.createCredential, onSuccess: invalidate }),
    remove: useMutation({ mutationFn: modelPlaygroundApi.deleteCredential, onSuccess: invalidate }),
  };
}

export function useRuns(limit?: number, offset?: number) {
  return useQuery({
    queryKey: ["model-playground", "runs", limit ?? null, offset ?? null],
    queryFn: () => modelPlaygroundApi.listRuns(limit, offset),
  });
}

export function useRun(id: string | null) {
  return useQuery({
    queryKey: ["model-playground", "run", id],
    queryFn: () => modelPlaygroundApi.getRun(id as string),
    enabled: !!id,
  });
}

export function useRunMutations() {
  const qc = useQueryClient();
  const invalidateRuns = () => qc.invalidateQueries({ queryKey: ["model-playground", "runs"] });

  return {
    create: useMutation({
      mutationFn: modelPlaygroundApi.createRun,
      onSuccess: (run) => {
        invalidateRuns();
        qc.setQueryData(["model-playground", "run", run.id], run);
      },
    }),
    remove: useMutation({
      mutationFn: modelPlaygroundApi.deleteRun,
      onSuccess: (_data, id) => {
        invalidateRuns();
        qc.removeQueries({ queryKey: ["model-playground", "run", id] });
      },
    }),
  };
}
