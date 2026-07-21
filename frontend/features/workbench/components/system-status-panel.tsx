"use client";

import type { ComponentType } from "react";
import { HardDrive } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { formatBytes } from "@/lib/format";
import { registerWorkbenchPanel } from "../panel-registry";
import type { WorkbenchPanelProps } from "../panel-types";
import { useWorkbenchQuery } from "../api";

const SystemStatusPanel: ComponentType<WorkbenchPanelProps> = () => {
  const { data, isLoading, isError, refetch } = useWorkbenchQuery();

  if (isLoading || !data) {
    return isError ? (
      <div className="flex flex-col items-center gap-2 py-4 text-center">
        <p className="text-xs text-muted-foreground">Couldn&apos;t load system status.</p>
        <Button size="xs" variant="outline" onClick={() => refetch()}>
          Retry
        </Button>
      </div>
    ) : (
      <Skeleton className="h-16 w-full" />
    );
  }

  const { storage, version } = data.data;
  const storagePercent = Math.round((storage.disk_used_bytes / storage.disk_total_bytes) * 100);

  return (
    <div className="flex flex-col gap-2">
      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <div className="h-full rounded-full bg-primary" style={{ width: `${storagePercent}%` }} />
      </div>
      <p className="text-xs text-muted-foreground">
        {formatBytes(storage.disk_used_bytes)} used of {formatBytes(storage.disk_total_bytes)} · database{" "}
        {formatBytes(storage.database_bytes)}
      </p>
      <p className="mt-1 text-xs text-muted-foreground">Forge v{version}</p>
    </div>
  );
};

registerWorkbenchPanel({
  type: "system_status",
  metadata: {
    title: "Storage & System",
    description: "Disk usage, database size, and version.",
    icon: HardDrive,
    defaultVisible: true,
  },
  component: SystemStatusPanel,
});
