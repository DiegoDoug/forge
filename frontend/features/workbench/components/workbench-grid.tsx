"use client";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useUpdateLayoutMutation, useWorkbenchQuery } from "../api";
import { getRegisteredPanels } from "../panel-registry";
// Side-effect import: runs every panel-owning feature's registration module
// exactly once (per 12_PANEL_INTERFACE.md §4). Imported here rather than
// from the (server-component) app shell layout, since ES module evaluation
// order only guarantees this runs before getRegisteredPanels() below when
// it's a direct static import of the client module that actually consumes
// the registry - a side-effect-only import of client modules from a Server
// Component isn't guaranteed to execute in the browser bundle at all.
import "../register-all";
import { WorkbenchEmptyState } from "./workbench-empty-state";
import { WorkbenchPanelCard } from "./workbench-panel-card";

export function WorkbenchGrid({ mode, onEnterCustomize }: { mode: "view" | "customize"; onEnterCustomize: () => void }) {
  const { data, isLoading, isError, refetch } = useWorkbenchQuery();
  const updateLayout = useUpdateLayoutMutation();

  if (isLoading) {
    return (
      <div className="grid gap-4 p-4 md:grid-cols-2 md:p-6 xl:grid-cols-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-40 w-full rounded-xl" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-4 md:p-6">
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border p-8 text-center">
          <p className="text-sm text-muted-foreground">Couldn&apos;t load your Workbench layout.</p>
          <Button size="sm" variant="outline" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  const registeredByType = new Map(getRegisteredPanels().map((p) => [p.type, p]));
  // Silently skip any saved panel type with no matching registry entry (e.g.
  // "recent_projects" before Phase 06 registers it) — per 12_PANEL_INTERFACE.md
  // §3, item 6, this is not an error state.
  const savedPanels = data.layout.panels.filter((p) => registeredByType.has(p.type));
  const visiblePanels = savedPanels.filter((p) => p.visible);

  if (mode === "view" && visiblePanels.length === 0) {
    return <WorkbenchEmptyState onCustomize={onEnterCustomize} />;
  }

  const panelsToRender = mode === "customize" ? savedPanels : visiblePanels;

  function handleVisibilityChange(type: string, visible: boolean) {
    const nextPanels = savedPanels.map((p) => (p.type === type ? { ...p, visible } : p));
    updateLayout.mutate({
      panels: nextPanels,
      pinned_tools: data!.layout.pinned_tools.map((t) => t.key),
    });
  }

  return (
    <div className="grid gap-4 p-4 md:grid-cols-2 md:p-6 xl:grid-cols-3">
      {panelsToRender.map((panel) => {
        const definition = registeredByType.get(panel.type)!;
        return (
          <WorkbenchPanelCard
            key={panel.type}
            definition={definition}
            visible={panel.visible}
            mode={mode}
            onVisibilityChange={(visible) => handleVisibilityChange(panel.type, visible)}
          />
        );
      })}
    </div>
  );
}
