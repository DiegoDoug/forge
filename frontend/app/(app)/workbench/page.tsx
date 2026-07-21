"use client";

import { useRef, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { WorkbenchCustomizeToggle } from "@/features/workbench/components/workbench-customize-toggle";
import { WorkbenchGrid } from "@/features/workbench/components/workbench-grid";
import { WorkbenchResetButton } from "@/features/workbench/components/workbench-reset-button";

export default function WorkbenchPage() {
  const [mode, setMode] = useState<"view" | "customize">("view");
  const toggleRef = useRef<HTMLButtonElement>(null);
  const resetRef = useRef<HTMLButtonElement>(null);

  function toggleMode() {
    const next = mode === "view" ? "customize" : "view";
    setMode(next);
    // Focus management per 02_UI.md §5: entering customize mode moves focus
    // to the first meaningful control; exiting returns it to the trigger.
    requestAnimationFrame(() => {
      if (next === "customize") resetRef.current?.focus();
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
            {mode === "customize" && <WorkbenchResetButton ref={resetRef} />}
            <WorkbenchCustomizeToggle ref={toggleRef} mode={mode} onToggle={toggleMode} />
          </>
        }
      />
      <WorkbenchGrid mode={mode} onEnterCustomize={toggleMode} />
    </div>
  );
}
