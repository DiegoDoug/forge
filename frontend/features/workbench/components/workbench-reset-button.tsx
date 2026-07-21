"use client";

import * as React from "react";
import { RotateCcw } from "lucide-react";
import { toast } from "sonner";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { useResetLayoutMutation } from "../api";

export const WorkbenchResetButton = React.forwardRef<HTMLButtonElement>(function WorkbenchResetButton(_props, ref) {
  const resetLayout = useResetLayoutMutation();

  function handleReset() {
    resetLayout.mutate(undefined, {
      onError: () => toast.error("Couldn't reset your layout. Try again."),
      onSuccess: () => toast.success("Workbench reset to the default layout."),
    });
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger render={<Button ref={ref} variant="outline" size="sm" />}>
        <RotateCcw className="h-4 w-4" />
        Reset to default
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Reset Workbench to the default layout?</AlertDialogTitle>
          <AlertDialogDescription>
            This restores the shipped panel arrangement and pinned tools. Your current customization will be lost.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleReset}>Reset</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
});
