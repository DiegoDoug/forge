"use client";

import { Library, SearchX } from "lucide-react";

import { DataList, DataListRow, DataListSkeleton } from "@/components/data-list";
import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/error-state";
import { Button } from "@/components/ui/button";
import type { KnowledgeFilters, KnowledgeList } from "./api";
import { KnowledgeResultRow } from "./knowledge-result-row";

const RESULT_CAP = 100;

function hasActiveFilters(filters: KnowledgeFilters): boolean {
  return Boolean(filters.q || (filters.type && filters.type !== "all") || filters.tagIds?.length || filters.projectId);
}

export function KnowledgeResultList({
  filters,
  data,
  isLoading,
  isError,
  onRetry,
  onClearFilters,
}: {
  filters: KnowledgeFilters;
  data: KnowledgeList | undefined;
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  onClearFilters: () => void;
}) {
  if (isLoading) {
    return (
      <div className="p-3">
        <DataListSkeleton rows={6} />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-3">
        <ErrorState description="Couldn't load the Knowledge Hub." onRetry={onRetry} />
      </div>
    );
  }

  const items = data?.items ?? [];

  if (items.length === 0 && !hasActiveFilters(filters)) {
    return (
      <EmptyState
        icon={Library}
        title="No notes or documents yet"
        description="Create a note or a document to see it here, tag it, and link it to other things you know."
      />
    );
  }

  if (items.length === 0) {
    return (
      <EmptyState
        icon={SearchX}
        title="No items match these filters"
        description="Try a different search term, or clear your filters to see everything."
        action={
          <Button size="sm" variant="outline" onClick={onClearFilters}>
            Clear filters
          </Button>
        }
      />
    );
  }

  return (
    <div className="p-3">
      {/* Announces result-count/truncation changes to assistive tech
          (02_UI.md SS3/SS5). */}
      <div aria-live="polite" className="sr-only">
        {data?.truncated
          ? `Showing the first ${RESULT_CAP} of ${data.total} results`
          : `${items.length} result${items.length === 1 ? "" : "s"}`}
      </div>

      <DataList>
        {items.map((item) => (
          <KnowledgeResultRow key={`${item.type}-${item.id}`} item={item} />
        ))}
        {data?.truncated ? (
          <DataListRow className="justify-center hover:bg-transparent">
            <span className="data-meta text-center">
              Showing the first {RESULT_CAP} of {data.total} — narrow your filters to see more.
            </span>
          </DataListRow>
        ) : null}
      </DataList>
    </div>
  );
}
