"use client";

import { FolderTree, Sparkles, type LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import type { TemplateKind, TemplateKindInfo } from "./api";

const KIND_ICONS: Record<TemplateKind, LucideIcon> = {
  fdk_phase: FolderTree,
  ai_instructions: Sparkles,
};

export function KindPicker({
  kinds,
  selected,
  onSelect,
}: {
  kinds: TemplateKindInfo[];
  selected: TemplateKind | null;
  onSelect: (kind: TemplateKind) => void;
}) {
  return (
    <div role="radiogroup" aria-label="Template kind" className="grid gap-3 sm:grid-cols-2">
      {kinds.map((kind) => {
        const Icon = KIND_ICONS[kind.kind];
        const isSelected = selected === kind.kind;
        return (
          <button
            key={kind.kind}
            type="button"
            role="radio"
            aria-checked={isSelected}
            onClick={() => onSelect(kind.kind)}
            className={cn(
              "flex flex-col items-start gap-2 rounded-xl border p-4 text-left transition-colors hover:border-foreground/30 focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
              isSelected ? "border-foreground bg-muted/50" : "border-border",
            )}
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted text-foreground">
              <Icon className="h-4 w-4" />
            </div>
            <div>
              <p className="text-sm font-medium">{kind.label}</p>
              <p className="text-xs text-muted-foreground">{kind.description}</p>
            </div>
          </button>
        );
      })}
    </div>
  );
}
