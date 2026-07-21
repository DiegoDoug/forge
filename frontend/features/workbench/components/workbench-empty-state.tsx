"use client";

import { LayoutGrid } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";

export function WorkbenchEmptyState({ onCustomize }: { onCustomize: () => void }) {
  return (
    <div className="p-4 md:p-6">
      <EmptyState
        icon={LayoutGrid}
        title="Every panel is hidden"
        description="Turn panels back on from customize mode."
        action={
          <Button size="sm" onClick={onCustomize}>
            Customize Workbench
          </Button>
        }
      />
    </div>
  );
}
