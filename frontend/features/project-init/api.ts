import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export type TemplateKind = "fdk_phase" | "ai_instructions";

export interface FieldSpec {
  name: string;
  type: string;
  required: boolean;
  max_length?: number | null;
  min?: number | null;
  max_items?: number | null;
  min_items?: number | null;
  enum?: string[] | null;
}

export interface TemplateKindInfo {
  kind: TemplateKind;
  label: string;
  description: string;
  fields: FieldSpec[];
  output_files: string[] | null;
}

export interface TemplateCatalog {
  kinds: TemplateKindInfo[];
}

export interface FdkPhaseConfig {
  phase_number: number;
  phase_name: string;
  objective: string;
}

export const AI_INSTRUCTIONS_FILES = ["CLAUDE.md", "AGENTS.md", "instructions.md"] as const;
export type AiInstructionsFile = (typeof AI_INSTRUCTIONS_FILES)[number];

export interface AiInstructionsConfig {
  project_name: string;
  description: string;
  tech_stack: string[];
  conventions: string;
  output_files: AiInstructionsFile[];
}

export type GenerateConfig = FdkPhaseConfig | AiInstructionsConfig;

export interface GenerationOut {
  id: string;
  kind: TemplateKind;
  name: string;
  created_at: string;
  file_count: number;
}

export interface GenerationListItem {
  id: string;
  kind: TemplateKind;
  name: string;
  created_at: string;
}

export const projectInitApi = {
  catalog: () => api.get<TemplateCatalog>("/api/project-init/catalog"),
  history: (limit = 20) => api.get<{ items: GenerationListItem[] }>(`/api/project-init/history?limit=${limit}`),
  generate: (kind: TemplateKind, config: GenerateConfig) =>
    api.post<GenerationOut>("/api/project-init/generate", { kind, config }),
  remove: (id: string) => api.delete<void>(`/api/project-init/${id}`),
  downloadUrl: (id: string) => `/api/project-init/${id}/download`,
};

export function useProjectInitCatalog() {
  return useQuery({
    queryKey: ["project-init", "catalog"],
    queryFn: projectInitApi.catalog,
    staleTime: Infinity,
  });
}

export function useProjectInitHistory(limit = 20) {
  return useQuery({
    queryKey: ["project-init", "history", limit],
    queryFn: () => projectInitApi.history(limit),
  });
}

export function useProjectInitMutations() {
  const qc = useQueryClient();
  const invalidateHistory = () => qc.invalidateQueries({ queryKey: ["project-init", "history"] });

  return {
    generate: useMutation({
      mutationFn: ({ kind, config }: { kind: TemplateKind; config: GenerateConfig }) =>
        projectInitApi.generate(kind, config),
      onSuccess: invalidateHistory,
    }),
    remove: useMutation({ mutationFn: projectInitApi.remove, onSuccess: invalidateHistory }),
  };
}

/** Downloads a generation's zip by fetching it as a blob (so the session
 * cookie goes along with the request), same pattern as
 * features/documents/api.ts's downloadDocumentExport. */
export async function downloadGeneration(id: string, fallbackName: string) {
  const res = await fetch(projectInitApi.downloadUrl(id), { credentials: "include" });
  if (!res.ok) {
    throw new Error(`Download failed (${res.status})`);
  }
  const blob = await res.blob();
  const disposition = res.headers.get("content-disposition") ?? "";
  const match = /filename="([^"]+)"/.exec(disposition);
  const filename = match?.[1] ?? `${fallbackName}.zip`;

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
