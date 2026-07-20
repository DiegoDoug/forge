"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { RotateCw, Search as SearchIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/empty-state";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/page-header";
import { Skeleton } from "@/components/ui/skeleton";
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
        <div className="relative mb-6 max-w-md">
          <SearchIcon className="pointer-events-none absolute top-1/2 left-2.5 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search secrets, notes, documents…"
            className="pl-8"
            autoFocus
          />
        </div>

        {trimmed.length <= 1 ? (
          <EmptyState
            icon={SearchIcon}
            title="Search Forge"
            description="Type at least two characters to search secrets, notes, and documents."
          />
        ) : resultsQuery.isLoading ? (
          <div className="flex flex-col gap-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : resultsQuery.isError ? (
          <EmptyState
            icon={SearchIcon}
            title="Couldn't load results"
            description={resultsQuery.error instanceof Error ? resultsQuery.error.message : "Something went wrong."}
            action={
              <Button size="sm" variant="outline" onClick={() => resultsQuery.refetch()}>
                <RotateCw className="h-3.5 w-3.5" />
                Retry
              </Button>
            }
          />
        ) : resultsQuery.data ? (
          <SearchResultList results={resultsQuery.data} query={trimmed} />
        ) : null}
      </div>
    </div>
  );
}
