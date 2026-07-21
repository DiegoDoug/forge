"use client";

import { useState, type ComponentType } from "react";
import Link from "next/link";
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
import { GripVertical, KeyRound, ListPlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { registerWorkbenchPanel } from "../panel-registry";
import type { WorkbenchPanelProps } from "../panel-types";
import { useUpdateLayoutMutation, useWorkbenchQuery, type PinnedTool } from "../api";
import { getToolMetadataMap, type ToolMetadata } from "../tool-metadata";
import { PinPickerDialog } from "./pin-picker-dialog";

function PinnedToolTile({
  tool,
  meta,
  editable,
}: {
  tool: PinnedTool;
  meta: ToolMetadata;
  editable: boolean;
}) {
  const { attributes, listeners, setNodeRef, setActivatorNodeRef, transform, transition, isDragging } = useSortable({
    id: tool.key,
    disabled: !editable,
  });
  const Icon = meta.icon;

  const style = {
    transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
    transition,
    opacity: isDragging ? 0.5 : undefined,
  };

  const inner = (
    <>
      {editable && (
        <button
          ref={setActivatorNodeRef}
          type="button"
          className="cursor-grab touch-none text-muted-foreground hover:text-foreground active:cursor-grabbing"
          aria-label={`Reorder ${meta.title}`}
          {...attributes}
          {...listeners}
        >
          <GripVertical className="h-3.5 w-3.5" />
        </button>
      )}
      <Icon className="h-4 w-4 shrink-0 text-primary" />
      <div className="min-w-0">
        <p className="truncate text-sm font-medium">{meta.title}</p>
        {!tool.available && <p className="text-xs text-muted-foreground">Coming soon</p>}
      </div>
    </>
  );

  return (
    <div ref={setNodeRef} style={style}>
      {tool.available && !editable ? (
        <Link
          href={meta.href}
          className="flex items-center gap-2 rounded-lg border border-border p-3 transition-colors hover:border-primary/40 hover:bg-accent/40"
        >
          {inner}
        </Link>
      ) : (
        <div
          aria-disabled={!tool.available || undefined}
          className="flex items-center gap-2 rounded-lg border border-border p-3 data-disabled:cursor-not-allowed data-disabled:border-dashed data-disabled:opacity-60"
          data-disabled={!tool.available || undefined}
        >
          {inner}
        </div>
      )}
    </div>
  );
}

const PinnedToolsPanel: ComponentType<WorkbenchPanelProps> = ({ mode }) => {
  const { data, isLoading, isError, refetch } = useWorkbenchQuery();
  const updateLayout = useUpdateLayoutMutation();
  const [pickerOpen, setPickerOpen] = useState(false);
  const metadataMap = getToolMetadataMap();
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );
  const editable = mode === "customize";

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

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = pinned.findIndex((t) => t.key === active.id);
    const newIndex = pinned.findIndex((t) => t.key === over.id);
    if (oldIndex === -1 || newIndex === -1) return;
    updateLayout.mutate({
      panels: data!.layout.panels,
      pinned_tools: arrayMove(pinned, oldIndex, newIndex).map((t) => t.key),
    });
  }

  const tiles = pinned.map((tool) => {
    const meta = metadataMap[tool.key];
    if (!meta) return null;
    return <PinnedToolTile key={tool.key} tool={tool} meta={meta} editable={editable} />;
  });

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
          {editable ? (
            <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
              <SortableContext items={pinned.map((t) => t.key)} strategy={rectSortingStrategy}>
                <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">{tiles}</div>
              </SortableContext>
            </DndContext>
          ) : (
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">{tiles}</div>
          )}
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
