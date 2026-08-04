"use client";

import { Library, SearchX } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
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
      <div className="flex flex-col gap-2 p-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full" />
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center gap-2 py-16 text-center">
        <p className="text-sm text-muted-foreground">Couldn&apos;t load the Knowledge Hub.</p>
        <Button size="sm" variant="outline" onClick={onRetry}>
          Retry
        </Button>
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
    <div className="flex flex-col">
      {/* Announces result-count/truncation changes to assistive tech
          (02_UI.md SS3/SS5). */}
      <div aria-live="polite" className="sr-only">
        {data?.truncated
          ? `Showing the first ${RESULT_CAP} of ${data.total} results`
          : `${items.length} result${items.length === 1 ? "" : "s"}`}
      </div>

      <div className="flex flex-col gap-0.5 p-2">
        {items.map((item) => (
          <KnowledgeResultRow key={`${item.type}-${item.id}`} item={item} />
        ))}
      </div>

      {data?.truncated ? (
        <p className="border-t border-border px-4 py-2.5 text-center text-xs text-muted-foreground">
          Showing the first {RESULT_CAP} of {data.total} — narrow your filters to see more.
        </p>
      ) : null}
    </div>
  );
}
