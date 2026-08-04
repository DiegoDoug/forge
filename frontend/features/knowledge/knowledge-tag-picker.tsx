"use client";

import { useState } from "react";
import { Plus, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { KnowledgeItem, KnowledgeItemType } from "./api";
import { useKnowledgeTagMutations } from "./api";

/** Assign/remove tags on a Note or Document, reusing the shared `tags`
 * vocabulary (01_SPEC.md SS6.3). Mounted into the Documents editor toolbar
 * and the Notes card popover (T11) - never on the Hub page itself, which
 * is read-and-navigate only (01_SPEC.md SS5). */
export function KnowledgeTagPicker({
  itemType,
  itemId,
  tags,
}: {
  itemType: KnowledgeItemType;
  itemId: string;
  tags: KnowledgeItem["tags"];
}) {
  const [draft, setDraft] = useState("");
  const { addTag, removeTag } = useKnowledgeTagMutations(itemType, itemId);

  function submit() {
    const name = draft.trim();
    if (!name) return;
    addTag.mutate({ name });
    setDraft("");
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-1">
        {tags.length === 0 ? (
          <p className="text-xs text-muted-foreground">No tags yet.</p>
        ) : (
          tags.map((tag) => (
            <Badge key={tag.id} variant="secondary" className="h-5 gap-1 pr-1">
              {tag.name}
              <button
                type="button"
                onClick={() => removeTag.mutate(tag.id)}
                aria-label={`Remove tag ${tag.name}`}
                className="rounded-full p-0.5 hover:bg-black/10"
              >
                <X className="h-2.5 w-2.5" />
              </button>
            </Badge>
          ))
        )}
      </div>
      <div className="flex items-center gap-1">
        <Input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Add a tag…"
          aria-label="New tag name"
          className="h-7 text-xs"
        />
        <Button size="icon-xs" variant="outline" onClick={submit} title="Add tag" disabled={!draft.trim()}>
          <Plus className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );
}
