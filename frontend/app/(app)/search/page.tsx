"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Search as SearchIcon } from "lucide-react";

import { DataListSkeleton } from "@/components/data-list";
import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/error-state";
import { PageHeader } from "@/components/page-header";
import { SearchField } from "@/components/search-field";
import { searchApi } from "@/features/search/api";
import { SearchResultList } from "@/features/search/search-result-list";

export default function SearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [query, setQuery] = useState(() => searchParams.get("q") ?? "");

  const trimmed = query.trim();

  useEffect(() => {
    const params = new URLSearchParams();
    if (trimmed) params.set("q", trimmed);
    const qs = params.toString();
    router.replace(qs ? `/search?${qs}` : "/search", { scroll: false });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trimmed]);

  const resultsQuery = useQuery({
    queryKey: ["search", "page", trimmed],
    queryFn: () => searchApi.search(trimmed),
    enabled: trimmed.length > 1,
  });

  return (
    <div>
      <PageHeader title="Search" description="Search secrets, notes, and documents" />

      <div className="p-4 md:p-6">
        <SearchField
          value={query}
          onChange={setQuery}
          placeholder="Search secrets, notes, documents…"
          autoFocus
          className="mb-6 max-w-md"
        />

        {trimmed.length <= 1 ? (
          <EmptyState
            icon={SearchIcon}
            title="Search Forge"
            description="Type at least two characters to search secrets, notes, and documents."
          />
        ) : resultsQuery.isLoading ? (
          <DataListSkeleton rows={4} />
        ) : resultsQuery.isError ? (
          <ErrorState
            description={resultsQuery.error instanceof Error ? resultsQuery.error.message : "Something went wrong."}
            onRetry={() => resultsQuery.refetch()}
          />
        ) : resultsQuery.data ? (
          <SearchResultList results={resultsQuery.data} query={trimmed} />
        ) : null}
      </div>
    </div>
  );
}
