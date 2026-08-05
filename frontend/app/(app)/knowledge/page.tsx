"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useMemo } from "react";

import { PageHeader } from "@/components/page-header";
import { useKnowledgeList } from "@/features/knowledge/api";
import type { KnowledgeFilters } from "@/features/knowledge/api";
import { KnowledgeFilterBar } from "@/features/knowledge/knowledge-filter-bar";
import { KnowledgeResultList } from "@/features/knowledge/knowledge-result-list";

function filtersFromParams(params: URLSearchParams): KnowledgeFilters {
  const tagIds = params.getAll("tag_id");
  return {
    q: params.get("q") || undefined,
    type: (params.get("type") as KnowledgeFilters["type"]) || "all",
    tagIds: tagIds.length ? tagIds : undefined,
    projectId: params.get("project_id") || undefined,
  };
}

function paramsFromFilters(filters: KnowledgeFilters): string {
  // Exactly the four documented filters - never a page/offset parameter,
  // because none exists (01_SPEC.md SS6.6/SS6.7, 08_ACCEPTANCE.md AC25).
  const search = new URLSearchParams();
  if (filters.q) search.set("q", filters.q);
  if (filters.type && filters.type !== "all") search.set("type", filters.type);
  if (filters.projectId) search.set("project_id", filters.projectId);
  for (const tagId of filters.tagIds ?? []) search.append("tag_id", tagId);
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export default function KnowledgeHubPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const filters = useMemo(() => filtersFromParams(searchParams), [searchParams]);
  const listQuery = useKnowledgeList(filters);

  function setFilters(next: KnowledgeFilters) {
    router.replace(`/knowledge${paramsFromFilters(next)}`);
  }

  const total = listQuery.data?.total ?? 0;
  const shown = listQuery.data?.items.length ?? 0;

  return (
    <div className="flex flex-col">
      <PageHeader
        title="Knowledge Hub"
        description={
          listQuery.data
            ? listQuery.data.truncated
              ? `${shown} of ${total} items shown`
              : `${total} item${total === 1 ? "" : "s"}`
            : "Search, tag & link your notes and documents"
        }
      />
      <KnowledgeFilterBar filters={filters} onChange={setFilters} />
      <KnowledgeResultList
        filters={filters}
        data={listQuery.data}
        isLoading={listQuery.isLoading}
        isError={listQuery.isError}
        onRetry={() => listQuery.refetch()}
        onClearFilters={() => setFilters({})}
      />
    </div>
  );
}
