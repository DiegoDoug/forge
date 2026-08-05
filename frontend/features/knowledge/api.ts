import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export type KnowledgeItemType = "note" | "document";

export interface KnowledgeTag {
  id: string;
  name: string;
  color: string;
}

export interface KnowledgeItem {
  type: KnowledgeItemType;
  id: string;
  title: string;
  excerpt: string;
  tags: KnowledgeTag[];
  project_id: string | null;
  updated_at: string;
}

export interface KnowledgeList {
  items: KnowledgeItem[];
  total: number;
  truncated: boolean;
}

export interface KnowledgeTagWithCount extends KnowledgeTag {
  count: number;
}

export interface KnowledgeLinkOther {
  type: KnowledgeItemType;
  id: string;
  title: string;
}

export interface KnowledgeLink {
  link_id: string;
  other: KnowledgeLinkOther;
  created_at: string;
}

export interface KnowledgeFilters {
  q?: string;
  type?: "all" | KnowledgeItemType;
  tagIds?: string[];
  projectId?: string | null;
}

// GET /api/knowledge supports exactly q / type / tag_id (repeatable) /
// project_id - deliberately NO page/offset/cursor/limit parameter anywhere
// (01_SPEC.md SS6.6/SS6.7). The 100-item cap is a fixed server constant.
function buildKnowledgeQuery(filters: KnowledgeFilters): string {
  const search = new URLSearchParams();
  if (filters.q) search.set("q", filters.q);
  if (filters.type && filters.type !== "all") search.set("type", filters.type);
  if (filters.projectId) search.set("project_id", filters.projectId);
  for (const tagId of filters.tagIds ?? []) search.append("tag_id", tagId);
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export const knowledgeApi = {
  list: (filters: KnowledgeFilters) => api.get<KnowledgeList>(`/api/knowledge${buildKnowledgeQuery(filters)}`),
  listTags: () => api.get<KnowledgeTagWithCount[]>("/api/knowledge/tags"),
  addTag: (itemType: KnowledgeItemType, itemId: string, input: { tag_id: string } | { name: string; color?: string }) =>
    api.post<KnowledgeTag[]>(`/api/knowledge/${itemType}/${itemId}/tags`, input),
  removeTag: (itemType: KnowledgeItemType, itemId: string, tagId: string) =>
    api.delete<void>(`/api/knowledge/${itemType}/${itemId}/tags/${tagId}`),
  listLinks: (itemType: KnowledgeItemType, itemId: string) =>
    api.get<KnowledgeLink[]>(`/api/knowledge/${itemType}/${itemId}/links`),
  createLink: (itemType: KnowledgeItemType, itemId: string, targetType: KnowledgeItemType, targetId: string) =>
    api.post<KnowledgeLink>(`/api/knowledge/${itemType}/${itemId}/links`, { target_type: targetType, target_id: targetId }),
  removeLink: (linkId: string) => api.delete<void>(`/api/knowledge/links/${linkId}`),
};

export function useKnowledgeList(filters: KnowledgeFilters) {
  return useQuery({
    queryKey: ["knowledge", filters],
    queryFn: () => knowledgeApi.list(filters),
  });
}

export function useKnowledgeTags() {
  return useQuery({
    queryKey: ["knowledge", "tags"],
    queryFn: () => knowledgeApi.listTags(),
  });
}

export function useKnowledgeLinks(itemType: KnowledgeItemType | null, itemId: string | null) {
  return useQuery({
    queryKey: ["knowledge", "links", itemType, itemId],
    queryFn: () => knowledgeApi.listLinks(itemType as KnowledgeItemType, itemId as string),
    enabled: !!itemType && !!itemId,
  });
}

export function useKnowledgeTagMutations(itemType: KnowledgeItemType, itemId: string | null) {
  const qc = useQueryClient();
  // Tag mutations invalidate both the item list (excerpt/tags shown per
  // row) and the tag list (counts change) - 05_COMPONENTS.md SS4.
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["knowledge"] });
  };

  return {
    addTag: useMutation({
      mutationFn: (input: { tag_id: string } | { name: string; color?: string }) =>
        knowledgeApi.addTag(itemType, itemId as string, input),
      onSuccess: invalidate,
    }),
    removeTag: useMutation({
      mutationFn: (tagId: string) => knowledgeApi.removeTag(itemType, itemId as string, tagId),
      onSuccess: invalidate,
    }),
  };
}

export function useKnowledgeLinkMutations(itemType: KnowledgeItemType, itemId: string | null) {
  const qc = useQueryClient();
  // A link is visible from both endpoints (01_SPEC.md FR15) - invalidating
  // just this item's own links query would leave the OTHER item's cached
  // link list stale, so invalidate every knowledge "links" query rather
  // than only this item's key.
  const invalidateLinks = () => {
    qc.invalidateQueries({ queryKey: ["knowledge", "links"] });
    qc.invalidateQueries({ queryKey: ["knowledge"], exact: false, predicate: (q) => q.queryKey[0] === "knowledge" });
  };

  return {
    createLink: useMutation({
      mutationFn: ({ targetType, targetId }: { targetType: KnowledgeItemType; targetId: string }) =>
        knowledgeApi.createLink(itemType, itemId as string, targetType, targetId),
      onSuccess: invalidateLinks,
    }),
    removeLink: useMutation({
      mutationFn: (linkId: string) => knowledgeApi.removeLink(linkId),
      onSuccess: invalidateLinks,
    }),
  };
}
