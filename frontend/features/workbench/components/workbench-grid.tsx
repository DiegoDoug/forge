"use client";

import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import { SortableContext, arrayMove, rectSortingStrategy, sortableKeyboardCoordinates, useSortable } from "@dnd-kit/sortable";

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
import type { WorkbenchPanelDefinition } from "../panel-types";
import { WorkbenchEmptyState } from "./workbench-empty-state";
import { WorkbenchPanelCard } from "./workbench-panel-card";

function SortablePanelCard({
  panelType,
  definition,
  visible,
  mode,
  onVisibilityChange,
  spanClassName,
}: {
  panelType: string;
  definition: WorkbenchPanelDefinition;
  visible: boolean;
  mode: "view" | "customize";
  onVisibilityChange: (visible: boolean) => void;
  spanClassName?: string;
}) {
  const { attributes, listeners, setNodeRef, setActivatorNodeRef, transform, transition, isDragging } = useSortable({
    id: panelType,
  });

  const style = {
    transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
    transition,
    opacity: isDragging ? 0.5 : undefined,
  };

  return (
    <div ref={setNodeRef} style={style} className={spanClassName}>
      <WorkbenchPanelCard
        definition={definition}
        visible={visible}
        mode={mode}
        onVisibilityChange={onVisibilityChange}
        dragHandleRef={setActivatorNodeRef}
        dragHandleAttributes={attributes}
        dragHandleListeners={listeners}
        className="h-full"
      />
    </div>
  );
}

// Pinned Tools is the primary column's launcher panel — giving it the full
// row width (rather than sharing a row with a narrower panel) avoids an
// awkward unbalanced gap next to whichever panel would otherwise be its
// sole row-mate in a 2-column grid (Phase 10 UX elevation).
const FULL_WIDTH_PRIMARY_PANELS = new Set(["pinned_tools"]);

export function WorkbenchGrid({ mode, onEnterCustomize }: { mode: "view" | "customize"; onEnterCustomize: () => void }) {
  const { data, isLoading, isError, refetch } = useWorkbenchQuery();
  const updateLayout = useUpdateLayoutMutation();
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

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

  // Both handlers below build the PUT payload from the FULL data.layout.panels
  // (not the registered-only `savedPanels`), so any entry whose `type` isn't
  // registered in this frontend build (e.g. a not-yet-shipped phase's panel,
  // or one temporarily missing across a version mismatch) survives untouched
  // instead of being silently dropped from the persisted layout the next time
  // the user reorders or toggles an unrelated panel. Per 12_PANEL_INTERFACE.md
  // §3 item 6, an unregistered type must be safely and durably inert, not
  // deleted by an unrelated user action.
  function handleVisibilityChange(type: string, visible: boolean) {
    const nextPanels = data!.layout.panels.map((p) => (p.type === type ? { ...p, visible } : p));
    updateLayout.mutate({
      panels: nextPanels,
      pinned_tools: data!.layout.pinned_tools.map((t) => t.key),
    });
  }

  function columnOf(type: string): "primary" | "rail" {
    return registeredByType.get(type)?.metadata.column ?? "primary";
  }

  // Reordering is scoped to within one column (Phase 10 UX elevation): the
  // primary/rail split is fixed by panel metadata, not draggable, so the
  // user can't produce a layout where e.g. Recent Activity ends up wider
  // than Pinned Tools. Each column gets its own DndContext below, so dnd-kit
  // never offers a cross-column drop target in the first place.
  function makeDragEndHandler(column: "primary" | "rail") {
    return function handleDragEnd(event: DragEndEvent) {
      const { active, over } = event;
      if (!over || active.id === over.id) return;
      const columnPanels = panelsToRender.filter((p) => columnOf(p.type) === column);
      const oldIndex = columnPanels.findIndex((p) => p.type === active.id);
      const newIndex = columnPanels.findIndex((p) => p.type === over.id);
      if (oldIndex === -1 || newIndex === -1) return;
      const reordered = arrayMove(columnPanels, oldIndex, newIndex);
      let i = 0;
      const nextPanels = data!.layout.panels.map((p) =>
        registeredByType.has(p.type) && columnOf(p.type) === column ? reordered[i++] : p,
      );
      updateLayout.mutate({
        panels: nextPanels,
        pinned_tools: data!.layout.pinned_tools.map((t) => t.key),
      });
    };
  }

  function renderCard(panel: (typeof panelsToRender)[number]) {
    return (
      <SortablePanelCard
        key={panel.type}
        panelType={panel.type}
        definition={registeredByType.get(panel.type)!}
        visible={panel.visible}
        mode={mode}
        onVisibilityChange={(visible) => handleVisibilityChange(panel.type, visible)}
        spanClassName={FULL_WIDTH_PRIMARY_PANELS.has(panel.type) ? "sm:col-span-2" : undefined}
      />
    );
  }

  const primaryPanels = panelsToRender.filter((p) => columnOf(p.type) === "primary");
  const railPanels = panelsToRender.filter((p) => columnOf(p.type) === "rail");

  function renderColumn(panels: typeof panelsToRender, column: "primary" | "rail", gridClassName: string) {
    const cards = panels.map(renderCard);
    if (mode !== "customize") {
      return <div className={gridClassName}>{cards}</div>;
    }
    return (
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={makeDragEndHandler(column)}>
        <SortableContext items={panels.map((p) => p.type)} strategy={rectSortingStrategy}>
          <div className={gridClassName}>{cards}</div>
        </SortableContext>
      </DndContext>
    );
  }

  return (
    <div className="flex flex-col gap-4 p-4 md:p-6 lg:flex-row lg:items-start">
      <div className="flex-1 lg:w-2/3">
        {renderColumn(primaryPanels, "primary", "grid gap-4 sm:grid-cols-2")}
      </div>
      <div className="flex flex-col gap-4 lg:w-1/3 lg:shrink-0">
        {renderColumn(railPanels, "rail", "flex flex-col gap-4")}
      </div>
    </div>
  );
}
