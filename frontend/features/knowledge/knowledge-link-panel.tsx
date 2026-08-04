"use client";

import { useState } from "react";
import { FileText, Link2, StickyNote, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import type { KnowledgeItemType } from "./api";
import { useKnowledgeLinkMutations, useKnowledgeLinks } from "./api";
import { KnowledgeLinkPicker } from "./knowledge-link-picker";

/** Linked-items list plus an add-link picker and per-row remove. Mounted
 * into the Documents editor toolbar and the Notes card popover (T11). */
export function KnowledgeLinkPanel({ itemType, itemId }: { itemType: KnowledgeItemType; itemId: string }) {
  const [pickerOpen, setPickerOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const linksQuery = useKnowledgeLinks(itemType, itemId);
  const { createLink, removeLink } = useKnowledgeLinkMutations(itemType, itemId);

  const links = linksQuery.data ?? [];

  function pick(targetType: KnowledgeItemType, targetId: string) {
    setError(null);
    createLink.mutate(
      { targetType, targetId },
      {
        onSuccess: () => setPickerOpen(false),
        onError: (err: unknown) => {
          const message = err instanceof Error ? err.message : "Couldn't create that link.";
          setError(message);
        },
      },
    );
  }

  return (
    <div className="flex flex-col gap-2">
      {links.length === 0 ? (
        <p className="text-xs text-muted-foreground">No linked items.</p>
      ) : (
        <ul className="flex flex-col gap-0.5">
          {links.map((link) => {
            const Icon = link.other.type === "note" ? StickyNote : FileText;
            return (
              <li key={link.link_id} className="flex items-center gap-1.5 rounded px-1.5 py-1 text-xs hover:bg-accent">
                <Icon className="h-3 w-3 shrink-0 text-muted-foreground" />
                <span className="min-w-0 flex-1 truncate">{link.other.title}</span>
                <button
                  type="button"
                  onClick={() => removeLink.mutate(link.link_id)}
                  aria-label={`Remove link to ${link.other.title}`}
                  className="shrink-0 rounded-full p-0.5 hover:bg-black/10"
                >
                  <X className="h-2.5 w-2.5" />
                </button>
              </li>
            );
          })}
        </ul>
      )}

      {/* Self-link / duplicate-link errors render inline, not as a toast
          that can vanish before it's read (02_UI.md SS3, AC23). */}
      {error ? <p className="text-xs text-destructive">{error}</p> : null}

      <Popover open={pickerOpen} onOpenChange={setPickerOpen}>
        <PopoverTrigger
          render={
            <Button variant="outline" size="sm" className="h-6 w-fit gap-1 px-2 text-xs">
              <Link2 className="h-3 w-3" />
              Link item
            </Button>
          }
        />
        <PopoverContent className="w-64 p-2">
          <KnowledgeLinkPicker excludeType={itemType} excludeId={itemId} onPick={pick} />
        </PopoverContent>
      </Popover>
    </div>
  );
}
