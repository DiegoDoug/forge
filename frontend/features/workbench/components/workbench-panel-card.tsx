"use client";

import { useState } from "react";
import { AlertTriangle, GripVertical } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";
import type { WorkbenchPanelDefinition } from "../panel-types";
import { PanelErrorBoundary } from "./panel-error-boundary";

function PanelErrorFallback({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed border-destructive/40 p-4 text-center">
      <AlertTriangle className="h-4 w-4 text-destructive" />
      <p className="text-xs text-muted-foreground">This panel failed to load.</p>
      <Button size="xs" variant="outline" onClick={onRetry}>
        Retry
      </Button>
    </div>
  );
}

export function WorkbenchPanelCard({
  definition,
  visible,
  mode,
  onVisibilityChange,
  dragHandleRef,
  dragHandleAttributes,
  dragHandleListeners,
  className,
}: {
  definition: WorkbenchPanelDefinition;
  visible: boolean;
  mode: "view" | "customize";
  onVisibilityChange: (visible: boolean) => void;
  dragHandleRef?: (element: HTMLElement | null) => void;
  dragHandleAttributes?: React.HTMLAttributes<HTMLButtonElement>;
  dragHandleListeners?: React.HTMLAttributes<HTMLButtonElement>;
  className?: string;
}) {
  const [manualError, setManualError] = useState<unknown>(null);
  const Icon = definition.metadata.icon;
  const Panel = definition.component;
  const showBody = mode === "customize" || visible;

  return (
    <div
      className={cn(
        "flex flex-col gap-3 rounded-xl border border-border bg-card p-4",
        mode === "customize" && !visible && "opacity-50",
        className,
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2">
          {mode === "customize" && (
            <button
              ref={dragHandleRef}
              type="button"
              className="cursor-grab touch-none text-muted-foreground hover:text-foreground active:cursor-grabbing"
              aria-label={`Reorder ${definition.metadata.title}`}
              {...dragHandleAttributes}
              {...dragHandleListeners}
            >
              <GripVertical className="h-4 w-4" />
            </button>
          )}
          <Icon className="h-4 w-4 shrink-0 text-primary" />
          <h2 className="truncate text-sm font-medium">{definition.metadata.title}</h2>
          {mode === "customize" && !visible && <span className="shrink-0 text-xs text-muted-foreground">Hidden</span>}
        </div>
        {mode === "customize" && (
          <Switch
            checked={visible}
            onCheckedChange={onVisibilityChange}
            aria-label={`${visible ? "Hide" : "Show"} ${definition.metadata.title} panel`}
          />
        )}
      </div>

      {showBody &&
        (manualError !== null ? (
          <PanelErrorFallback onRetry={() => setManualError(null)} />
        ) : (
          <PanelErrorBoundary fallback={(_error, reset) => <PanelErrorFallback onRetry={reset} />}>
            <Panel mode={mode} onError={setManualError} />
          </PanelErrorBoundary>
        ))}
    </div>
  );
}
