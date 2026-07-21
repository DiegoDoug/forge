"use client";

import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { useUpdateLayoutMutation, useWorkbenchQuery } from "../api";
import { getToolMetadataMap } from "../tool-metadata";

export function PinPickerDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  const { data, isLoading } = useWorkbenchQuery();
  const updateLayout = useUpdateLayoutMutation();
  const metadataMap = getToolMetadataMap();

  const pinnedKeys = new Set((data?.layout.pinned_tools ?? []).map((t) => t.key));

  function togglePin(key: string) {
    if (!data) return;
    const nextKeys = pinnedKeys.has(key)
      ? data.layout.pinned_tools.filter((t) => t.key !== key).map((t) => t.key)
      : [...data.layout.pinned_tools.map((t) => t.key), key];
    updateLayout.mutate(
      { panels: data.layout.panels, pinned_tools: nextKeys },
      { onError: () => toast.error("Couldn't update pinned tools. Try again.") },
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Manage pinned tools</DialogTitle>
          <DialogDescription>Choose which tools appear in your Pinned Tools panel.</DialogDescription>
        </DialogHeader>
        <div className="flex max-h-96 flex-col gap-1 overflow-y-auto">
          {isLoading || !data
            ? Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)
            : data.layout.tool_catalog.map((entry) => {
                const meta = metadataMap[entry.key];
                if (!meta) return null;
                const Icon = meta.icon;
                const pinned = pinnedKeys.has(entry.key);
                return (
                  <div key={entry.key} className="flex items-center gap-3 rounded-lg px-2 py-2 hover:bg-accent/40">
                    <Icon className="h-4 w-4 shrink-0 text-muted-foreground" />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <p className="truncate text-sm font-medium">{meta.title}</p>
                        {!entry.available && <Badge variant="secondary">Coming soon</Badge>}
                      </div>
                      <p className="truncate text-xs text-muted-foreground">{meta.description}</p>
                    </div>
                    <Switch
                      checked={pinned}
                      onCheckedChange={() => togglePin(entry.key)}
                      aria-label={`${pinned ? "Unpin" : "Pin"} ${meta.title}`}
                    />
                  </div>
                );
              })}
        </div>
      </DialogContent>
    </Dialog>
  );
}
