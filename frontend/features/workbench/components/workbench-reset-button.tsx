"use client";

import * as React from "react";
import { RotateCcw } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { useResetLayoutMutation } from "../api";

export const WorkbenchResetButton = React.forwardRef<HTMLButtonElement>(function WorkbenchResetButton(_props, ref) {
  const [open, setOpen] = React.useState(false);
  const resetLayout = useResetLayoutMutation();

  function handleReset() {
    resetLayout.mutate(undefined, {
      onError: () => toast.error("Couldn't reset your layout. Try again."),
      onSuccess: () => toast.success("Workbench reset to the default layout."),
    });
  }

  return (
    <>
      <Button ref={ref} variant="outline" size="sm" onClick={() => setOpen(true)}>
        <RotateCcw className="h-4 w-4" />
        Reset to default
      </Button>
      <ConfirmDialog
        open={open}
        onOpenChange={setOpen}
        title="Reset Workbench to the default layout?"
        description="This restores the shipped panel arrangement and pinned tools. Your current customization will be lost."
        confirmLabel="Reset"
        onConfirm={handleReset}
      />
    </>
  );
});
