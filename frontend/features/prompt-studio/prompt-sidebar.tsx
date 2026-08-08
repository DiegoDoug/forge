"use client";

import { useMemo, useState } from "react";
import { MessageSquareText, Plus, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SearchField } from "@/components/search-field";
import { formatRelativeTime } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { PromptListItem } from "./api";

export function PromptSidebar({
  prompts,
  isLoading,
  isError,
  onRetry,
  selectedId,
  query,
  onQueryChange,
  activeTag,
  onTagChange,
  onSelect,
  onNew,
  className,
}: {
  prompts: PromptListItem[];
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  selectedId: string | null;
  query: string;
  onQueryChange: (q: string) => void;
  activeTag: string | null;
  onTagChange: (tag: string | null) => void;
  onSelect: (id: string) => void;
  onNew: () => void;
  className?: string;
}) {
  const [showAllTags, setShowAllTags] = useState(false);

  const allTags = useMemo(() => {
    const set = new Set<string>();
    for (const p of prompts) for (const t of p.tags) set.add(t);
    return Array.from(set).sort();
  }, [prompts]);

  const visibleTags = showAllTags ? allTags : allTags.slice(0, 6);

  return (
    <aside className={cn("flex w-full shrink-0 flex-col border-r border-border lg:w-[var(--shell-filter-rail-w)]", className)}>
      <div className="flex items-center gap-2 border-b border-border p-3">
        <SearchField value={query} onChange={onQueryChange} placeholder="Search prompts…" className="flex-1" />
        <Button size="icon-sm" title="New prompt" onClick={onNew}>
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      {allTags.length > 0 ? (
        <div className="flex flex-wrap items-center gap-1.5 border-b border-border p-2">
          {activeTag ? (
            <Badge variant="secondary" className="cursor-pointer gap-1" onClick={() => onTagChange(null)}>
              {activeTag}
              <X className="h-3 w-3" />
            </Badge>
          ) : (
            <>
              {visibleTags.map((tag) => (
                <Badge
                  key={tag}
                  variant="outline"
                  className="cursor-pointer"
                  onClick={() => onTagChange(tag)}
                >
                  {tag}
                </Badge>
              ))}
              {allTags.length > visibleTags.length ? (
                <button
                  type="button"
                  className="text-xs text-muted-foreground hover:text-foreground"
                  onClick={() => setShowAllTags(true)}
                >
                  +{allTags.length - visibleTags.length} more
                </button>
              ) : null}
            </>
          )}
        </div>
      ) : null}

      <ScrollArea className="min-h-0 flex-1">
        <div className="flex flex-col gap-1 p-2">
          {isLoading ? (
            <p className="px-2 py-6 text-center text-xs text-muted-foreground">Loading…</p>
          ) : isError ? (
            <div className="flex flex-col items-center gap-2 px-2 py-6 text-center">
              <p className="text-xs text-destructive">Couldn&apos;t load prompts.</p>
              <Button size="xs" variant="outline" onClick={onRetry}>
                Retry
              </Button>
            </div>
          ) : prompts.length === 0 ? (
            <p className="px-2 py-6 text-center text-xs text-muted-foreground">
              {query || activeTag ? "No prompts match — clear filters." : "No prompts yet."}
            </p>
          ) : (
            prompts.map((prompt) => (
              <button
                key={prompt.id}
                onClick={() => onSelect(prompt.id)}
                className={cn(
                  "flex flex-col gap-1 rounded-lg px-2 py-2 text-left transition-colors",
                  selectedId === prompt.id ? "bg-accent text-accent-foreground" : "hover:bg-accent/50",
                )}
              >
                <div className="flex min-w-0 items-center gap-2">
                  <MessageSquareText className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                  <span className="min-w-0 flex-1 truncate text-sm">{prompt.name || "Untitled"}</span>
                  <Badge variant="secondary" className="shrink-0 text-[10px]">
                    v{prompt.version_number}
                  </Badge>
                </div>
                {prompt.description ? (
                  <p className="truncate pl-5 text-xs text-muted-foreground">{prompt.description}</p>
                ) : null}
                <div className="flex items-center justify-between pl-5">
                  <span className="text-[11px] text-muted-foreground">{formatRelativeTime(prompt.updated_at)}</span>
                  {prompt.tags.length > 0 ? (
                    <span className="text-[11px] text-muted-foreground">{prompt.tags.join(", ")}</span>
                  ) : null}
                </div>
              </button>
            ))
          )}
        </div>
      </ScrollArea>
    </aside>
  );
}
