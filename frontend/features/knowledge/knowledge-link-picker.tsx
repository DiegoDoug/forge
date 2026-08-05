"use client";

import { useState } from "react";
import { FileText, StickyNote } from "lucide-react";

import { Input } from "@/components/ui/input";
import { useKnowledgeList } from "./api";
import type { KnowledgeItemType } from "./api";

/** Searches knowledge items to pick a link target; excludes the current
 * item so self-linking is impossible in the UI as well as the API
 * (05_COMPONENTS.md SS1). */
export function KnowledgeLinkPicker({
  excludeType,
  excludeId,
  onPick,
}: {
  excludeType: KnowledgeItemType;
  excludeId: string;
  onPick: (targetType: KnowledgeItemType, targetId: string) => void;
}) {
  const [q, setQ] = useState("");
  const listQuery = useKnowledgeList({ q });
  const candidates = (listQuery.data?.items ?? []).filter(
    (item) => !(item.type === excludeType && item.id === excludeId),
  );

  return (
    <div className="flex flex-col gap-2">
      <Input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search notes and documents to link…"
        aria-label="Search for a link target"
        className="h-7 text-xs"
        autoFocus
      />
      <ul className="flex max-h-48 flex-col gap-0.5 overflow-auto">
        {candidates.length === 0 ? (
          <li className="px-1 py-1 text-xs text-muted-foreground">No matches.</li>
        ) : (
          candidates.map((item) => {
            const Icon = item.type === "note" ? StickyNote : FileText;
            return (
              <li key={`${item.type}-${item.id}`}>
                <button
                  type="button"
                  onClick={() => onPick(item.type, item.id)}
                  className="flex w-full items-center gap-1.5 rounded px-1.5 py-1 text-left text-xs hover:bg-accent"
                >
                  <Icon className="h-3 w-3 shrink-0 text-muted-foreground" />
                  <span className="truncate">{item.title}</span>
                </button>
              </li>
            );
          })
        )}
      </ul>
    </div>
  );
}
