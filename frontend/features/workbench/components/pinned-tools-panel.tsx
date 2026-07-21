"use client";

import { useState, type ComponentType } from "react";
import Link from "next/link";
import { KeyRound, ListPlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { registerWorkbenchPanel } from "../panel-registry";
import type { WorkbenchPanelProps } from "../panel-types";
import { useWorkbenchQuery } from "../api";
import { getToolMetadataMap } from "../tool-metadata";
import { PinPickerDialog } from "./pin-picker-dialog";

const PinnedToolsPanel: ComponentType<WorkbenchPanelProps> = () => {
  const { data, isLoading, isError, refetch } = useWorkbenchQuery();
  const [pickerOpen, setPickerOpen] = useState(false);
  const metadataMap = getToolMetadataMap();

  if (isLoading) {
    return (
      <div className="grid grid-cols-3 gap-2">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-col items-center gap-2 py-4 text-center">
        <p className="text-xs text-muted-foreground">Couldn&apos;t load pinned tools.</p>
        <Button size="xs" variant="outline" onClick={() => refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  const pinned = data.layout.pinned_tools;

  return (
    <>
      {pinned.length === 0 ? (
        <EmptyState
          icon={KeyRound}
          title="No pinned tools yet"
          description="Pin the tools you reach for most."
          action={
            <Button size="sm" onClick={() => setPickerOpen(true)}>
              Manage pinned tools
            </Button>
          }
        />
      ) : (
        <div className="flex flex-col gap-2">
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {pinned.map((tool) => {
              const meta = metadataMap[tool.key];
              if (!meta) return null;
              const Icon = meta.icon;
              const tileContent = (
                <>
                  <Icon className="h-4 w-4 text-primary" />
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{meta.title}</p>
                    {!tool.available && <p className="text-xs text-muted-foreground">Coming soon</p>}
                  </div>
                </>
              );
              return tool.available ? (
                <Link
                  key={tool.key}
                  href={meta.href}
                  className="flex flex-col gap-2 rounded-lg border border-border p-3 transition-colors hover:border-primary/40 hover:bg-accent/40"
                >
                  {tileContent}
                </Link>
              ) : (
                <div
                  key={tool.key}
                  aria-disabled="true"
                  className="flex cursor-not-allowed flex-col gap-2 rounded-lg border border-dashed border-border p-3 opacity-60"
                >
                  {tileContent}
                </div>
              );
            })}
          </div>
          <Button size="xs" variant="ghost" className="self-start" onClick={() => setPickerOpen(true)}>
            <ListPlus className="h-3.5 w-3.5" />
            Manage pinned tools
          </Button>
        </div>
      )}
      <PinPickerDialog open={pickerOpen} onOpenChange={setPickerOpen} />
    </>
  );
};

registerWorkbenchPanel({
  type: "pinned_tools",
  metadata: {
    title: "Pinned Tools",
    description: "One-click access to the tools you use most.",
    icon: KeyRound,
    defaultVisible: true,
  },
  component: PinnedToolsPanel,
});
