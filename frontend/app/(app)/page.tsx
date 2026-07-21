"use client";

import { useRef, useState } from "react";
import { ListPlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/page-header";
import { PinPickerDialog } from "@/features/workbench/components/pin-picker-dialog";
import { WorkbenchCustomizeToggle } from "@/features/workbench/components/workbench-customize-toggle";
import { WorkbenchGrid } from "@/features/workbench/components/workbench-grid";
import { WorkbenchResetButton } from "@/features/workbench/components/workbench-reset-button";

export default function WorkbenchPage() {
  const [mode, setMode] = useState<"view" | "customize">("view");
  const [pinPickerOpen, setPinPickerOpen] = useState(false);
  const toggleRef = useRef<HTMLButtonElement>(null);
  const manageRef = useRef<HTMLButtonElement>(null);

  function toggleMode() {
    const next = mode === "view" ? "customize" : "view";
    setMode(next);
    // Focus management per 02_UI.md §5: entering customize mode moves focus
    // to the first meaningful control; exiting returns it to the trigger.
    requestAnimationFrame(() => {
      if (next === "customize") manageRef.current?.focus();
      else toggleRef.current?.focus();
    });
  }

  return (
    <div>
      <PageHeader
        title="Workbench"
        description="Pinned tools, recent activity, and quick actions"
        actions={
          <>
            {mode === "customize" && (
              <>
                <Button ref={manageRef} variant="outline" size="sm" onClick={() => setPinPickerOpen(true)}>
                  <ListPlus className="h-4 w-4" />
                  Manage pinned tools
                </Button>
                <WorkbenchResetButton />
              </>
            )}
            <WorkbenchCustomizeToggle ref={toggleRef} mode={mode} onToggle={toggleMode} />
          </>
        }
      />
      <WorkbenchGrid mode={mode} onEnterCustomize={toggleMode} />
      <PinPickerDialog open={pinPickerOpen} onOpenChange={setPinPickerOpen} />
    </div>
  );
}
