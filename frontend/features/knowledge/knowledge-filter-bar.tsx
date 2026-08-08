"use client";

import { Tag as TagIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { SearchField } from "@/components/search-field";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Toolbar } from "@/components/toolbar";
import { ProjectPicker } from "@/features/projects/project-picker";
import { useKnowledgeTags } from "./api";
import type { KnowledgeFilters } from "./api";

const TYPE_LABELS: Record<string, string> = { all: "All types", note: "Notes only", document: "Documents only" };

export function KnowledgeFilterBar({
  filters,
  onChange,
}: {
  filters: KnowledgeFilters;
  onChange: (next: KnowledgeFilters) => void;
}) {
  const tagsQuery = useKnowledgeTags();
  const tags = tagsQuery.data ?? [];
  const selectedTagIds = filters.tagIds ?? [];

  function toggleTag(tagId: string) {
    const next = selectedTagIds.includes(tagId)
      ? selectedTagIds.filter((id) => id !== tagId)
      : [...selectedTagIds, tagId];
    onChange({ ...filters, tagIds: next.length ? next : undefined });
  }

  return (
    <Toolbar>
      <SearchField
        value={filters.q ?? ""}
        onChange={(q) => onChange({ ...filters, q: q || undefined })}
        placeholder="Filter by keyword…"
        className="max-w-xs flex-1"
      />

      <Select
        value={filters.type ?? "all"}
        onValueChange={(v) => onChange({ ...filters, type: v as KnowledgeFilters["type"] })}
      >
        <SelectTrigger className="h-8 w-36" aria-label="Filter by type">
          {/* Select.Value renders the raw item value, not its label, unless
              given a render function - see project-picker.tsx's precedent. */}
          <SelectValue>{(v: string) => TYPE_LABELS[v] ?? "All types"}</SelectValue>
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All types</SelectItem>
          <SelectItem value="note">Notes only</SelectItem>
          <SelectItem value="document">Documents only</SelectItem>
        </SelectContent>
      </Select>

      <Popover>
        <PopoverTrigger
          render={
            <button
              type="button"
              className="flex h-8 items-center gap-1.5 rounded-md border border-input bg-transparent px-2.5 text-sm shadow-xs hover:bg-accent"
              aria-label={`Filter by tag${selectedTagIds.length ? `, ${selectedTagIds.length} selected` : ""}`}
            />
          }
        >
          <TagIcon className="h-3.5 w-3.5 text-muted-foreground" />
          Tags
          {selectedTagIds.length > 0 ? (
            <Badge variant="secondary" className="h-4 px-1.5">
              {selectedTagIds.length}
            </Badge>
          ) : null}
        </PopoverTrigger>
        <PopoverContent className="w-56 p-2">
          {tags.length === 0 ? (
            <p className="px-1 py-2 text-xs text-muted-foreground">No tags in use yet.</p>
          ) : (
            <ul className="flex flex-col gap-1" role="listbox" aria-multiselectable="true">
              {tags.map((tag) => {
                const checked = selectedTagIds.includes(tag.id);
                return (
                  <li key={tag.id}>
                    <label className="flex cursor-pointer items-center gap-2 rounded px-1.5 py-1 text-sm hover:bg-accent">
                      <Checkbox checked={checked} onCheckedChange={() => toggleTag(tag.id)} aria-label={`Tag: ${tag.name}`} />
                      <span className="flex-1 truncate">{tag.name}</span>
                      <span className="text-xs text-muted-foreground">{tag.count}</span>
                    </label>
                  </li>
                );
              })}
            </ul>
          )}
          {selectedTagIds.length > 0 ? (
            <button
              type="button"
              className="mt-1 w-full rounded px-1.5 py-1 text-left text-xs text-muted-foreground hover:bg-accent"
              onClick={() => onChange({ ...filters, tagIds: undefined })}
            >
              Clear tags
            </button>
          ) : null}
        </PopoverContent>
      </Popover>

      <ProjectPicker
        value={filters.projectId ?? null}
        onChange={(id) => onChange({ ...filters, projectId: id ?? undefined })}
        className="h-8 w-40"
      />

      {(filters.q || (filters.type && filters.type !== "all") || selectedTagIds.length > 0 || filters.projectId) ? (
        <button
          type="button"
          className="text-xs text-muted-foreground underline-offset-2 hover:underline"
          onClick={() => onChange({})}
        >
          Clear filters
        </button>
      ) : null}
    </Toolbar>
  );
}
