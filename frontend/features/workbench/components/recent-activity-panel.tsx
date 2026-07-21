"use client";

import type { ComponentType } from "react";
import { Activity } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { formatRelativeTime } from "@/lib/format";
import { registerWorkbenchPanel } from "../panel-registry";
import type { WorkbenchPanelProps } from "../panel-types";
import { useWorkbenchQuery } from "../api";

// No owning feature: activity spans every feature, and there is no
// frontend/features/activity/ folder to home this in (mirrors the backend,
// which also has no dedicated activity feature/route) — treated the same as
// the three explicit workbench/components/ exceptions in 05_COMPONENTS.md §3.
const RecentActivityPanel: ComponentType<WorkbenchPanelProps> = () => {
  const { data, isLoading, isError, refetch } = useWorkbenchQuery();

  if (isLoading) {
    return (
      <div className="flex flex-col gap-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-8 w-full" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-col items-center gap-2 py-4 text-center">
        <p className="text-xs text-muted-foreground">Couldn&apos;t load recent activity.</p>
        <Button size="xs" variant="outline" onClick={() => refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  const activity = data.data.recent_activity;

  if (activity.length === 0) {
    return <EmptyState icon={Activity} title="No activity yet" description="Actions across Forge will show up here." />;
  }

  return (
    <ul className="flex flex-col divide-y divide-border">
      {activity.map((entry) => (
        <li key={entry.id} className="flex items-center justify-between py-2 text-sm">
          <span className="truncate">{entry.summary}</span>
          <span className="shrink-0 text-xs text-muted-foreground">{formatRelativeTime(entry.created_at)}</span>
        </li>
      ))}
    </ul>
  );
};

registerWorkbenchPanel({
  type: "recent_activity",
  metadata: {
    title: "Recent Activity",
    description: "Actions across every Forge feature.",
    icon: Activity,
    defaultVisible: true,
  },
  component: RecentActivityPanel,
});
