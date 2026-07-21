"use client";

import * as React from "react";
import { Pencil, X } from "lucide-react";

import { Button } from "@/components/ui/button";

export const WorkbenchCustomizeToggle = React.forwardRef<
  HTMLButtonElement,
  { mode: "view" | "customize"; onToggle: () => void }
>(function WorkbenchCustomizeToggle({ mode, onToggle }, ref) {
  const isCustomizing = mode === "customize";

  return (
    <Button ref={ref} variant={isCustomizing ? "secondary" : "outline"} size="sm" onClick={onToggle}>
      {isCustomizing ? <X className="h-4 w-4" /> : <Pencil className="h-4 w-4" />}
      {isCustomizing ? "Done" : "Customize"}
    </Button>
  );
});
