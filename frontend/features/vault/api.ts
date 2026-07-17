import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export type SecretType =
  | "password"
  | "api_key"
  | "ssh_key"
  | "jwt_secret"
  | "oauth_secret"
  | "env_var"
  | "note"
  | "other";

export interface Tag {
  id: string;
  name: string;
  color: string;
}

export interface Folder {
  id: string;
  name: string;
  parent_id: string | null;
  created_at: string;
}

export interface SecretMetadata {
  username: string | null;
  url: string | null;
  notes: string | null;
}

export interface SecretSummary {
  id: string;
  name: string;
  type: SecretType;
  folder_id: string | null;
  tags: Tag[];
  favorite: boolean;
  created_at: string;
  updated_at: string;
}

export interface SecretDetail extends SecretSummary {
  value: string | null;
  metadata: SecretMetadata;
}

export interface SecretVersion {
  id: string;
  created_at: string;
}

export interface SecretCreateInput {
  name: string;
  type: SecretType;
  value: string;
  folder_id?: string | null;
  tag_ids?: string[];
  metadata?: Partial<SecretMetadata>;
  favorite?: boolean;
}

export interface SecretUpdateInput {
  name?: string;
  type?: SecretType;
  value?: string;
  folder_id?: string | null;
  tag_ids?: string[];
  metadata?: Partial<SecretMetadata>;
  favorite?: boolean;
}

export const vaultApi = {
  listSecrets: (params?: { folder_id?: string; tag_id?: string; q?: string }) => {
    const search = new URLSearchParams();
    if (params?.folder_id) search.set("folder_id", params.folder_id);
    if (params?.tag_id) search.set("tag_id", params.tag_id);
    if (params?.q) search.set("q", params.q);
    const qs = search.toString();
    return api.get<SecretSummary[]>(`/api/vault/secrets${qs ? `?${qs}` : ""}`);
  },
  getSecret: (id: string, reveal = false) =>
    api.get<SecretDetail>(`/api/vault/secrets/${id}${reveal ? "?reveal=true" : ""}`),
  createSecret: (input: SecretCreateInput) => api.post<SecretDetail>("/api/vault/secrets", input),
  updateSecret: (id: string, input: SecretUpdateInput) => api.patch<SecretDetail>(`/api/vault/secrets/${id}`, input),
  deleteSecret: (id: string) => api.delete<void>(`/api/vault/secrets/${id}`),
  listVersions: (id: string) => api.get<SecretVersion[]>(`/api/vault/secrets/${id}/versions`),
  revealVersion: (id: string, versionId: string) =>
    api.get<{ id: string; value: string; created_at: string }>(`/api/vault/secrets/${id}/versions/${versionId}`),

  listFolders: () => api.get<Folder[]>("/api/vault/folders"),
  createFolder: (name: string, parentId?: string | null) =>
    api.post<Folder>("/api/vault/folders", { name, parent_id: parentId ?? null }),
  deleteFolder: (id: string) => api.delete<void>(`/api/vault/folders/${id}`),

  listTags: () => api.get<Tag[]>("/api/vault/tags"),
  createTag: (name: string, color?: string) => api.post<Tag>("/api/vault/tags", { name, color }),
  deleteTag: (id: string) => api.delete<void>(`/api/vault/tags/${id}`),
};

export function useSecrets(params?: { folder_id?: string; tag_id?: string; q?: string }) {
  return useQuery({ queryKey: ["vault", "secrets", params], queryFn: () => vaultApi.listSecrets(params) });
}

export function useFolders() {
  return useQuery({ queryKey: ["vault", "folders"], queryFn: vaultApi.listFolders });
}

export function useTags() {
  return useQuery({ queryKey: ["vault", "tags"], queryFn: vaultApi.listTags });
}

export function useVaultMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ["vault"] });

  return {
    createSecret: useMutation({ mutationFn: vaultApi.createSecret, onSuccess: invalidate }),
    updateSecret: useMutation({
      mutationFn: ({ id, input }: { id: string; input: SecretUpdateInput }) => vaultApi.updateSecret(id, input),
      onSuccess: invalidate,
    }),
    deleteSecret: useMutation({ mutationFn: vaultApi.deleteSecret, onSuccess: invalidate }),
    createFolder: useMutation({
      mutationFn: ({ name, parentId }: { name: string; parentId?: string | null }) =>
        vaultApi.createFolder(name, parentId),
      onSuccess: invalidate,
    }),
    deleteFolder: useMutation({ mutationFn: vaultApi.deleteFolder, onSuccess: invalidate }),
    createTag: useMutation({
      mutationFn: ({ name, color }: { name: string; color?: string }) => vaultApi.createTag(name, color),
      onSuccess: invalidate,
    }),
    deleteTag: useMutation({ mutationFn: vaultApi.deleteTag, onSuccess: invalidate }),
  };
}
