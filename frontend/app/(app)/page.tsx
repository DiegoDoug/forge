"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Activity, HardDrive, KeyRound, StickyNote } from "lucide-react";

import { PageHeader } from "@/components/page-header";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { dashboardApi } from "@/features/dashboard/api";
import { formatBytes, formatRelativeTime } from "@/lib/format";
import { NAV_ITEMS } from "@/lib/nav-registry";

export default function DashboardPage() {
  const { data, isLoading } = useQuery({ queryKey: ["dashboard"], queryFn: dashboardApi.get });

  const pinnedTools = NAV_ITEMS.filter((item) => !["/", "/settings"].includes(item.href));
  const storagePercent = data ? Math.round((data.storage.disk_used_bytes / data.storage.disk_total_bytes) * 100) : 0;

  return (
    <div>
      <PageHeader title="Dashboard" description="Overview of your Forge instance" />

      <div className="grid gap-4 p-4 md:grid-cols-3 md:p-6">
        {/* Pinned tools */}
        <div className="rounded-xl border border-border p-4 md:col-span-2">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">Tools</h2>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {pinnedTools.map((tool) => (
              <Link
                key={tool.href}
                href={tool.href}
                className="flex flex-col gap-2 rounded-lg border border-border p-3 transition-colors hover:border-primary/40 hover:bg-accent/40"
              >
                <tool.icon className="h-4 w-4 text-primary" />
                <div>
                  <p className="text-sm font-medium">{tool.title}</p>
                  <p className="text-xs text-muted-foreground">{tool.description}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* System status */}
        <div className="rounded-xl border border-border p-4">
          <h2 className="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <HardDrive className="h-4 w-4" /> Storage
          </h2>
          {isLoading || !data ? (
            <Skeleton className="h-16 w-full" />
          ) : (
            <div className="flex flex-col gap-2">
              <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                <div className="h-full rounded-full bg-primary" style={{ width: `${storagePercent}%` }} />
              </div>
              <p className="text-xs text-muted-foreground">
                {formatBytes(data.storage.disk_used_bytes)} used of {formatBytes(data.storage.disk_total_bytes)} ·
                database {formatBytes(data.storage.database_bytes)}
              </p>
              <p className="mt-2 text-xs text-muted-foreground">Forge v{data.version}</p>
            </div>
          )}
        </div>

        {/* Recent notes */}
        <div className="rounded-xl border border-border p-4">
          <h2 className="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <StickyNote className="h-4 w-4" /> Recent notes
          </h2>
          {isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : data && data.recent_notes.length > 0 ? (
            <ul className="flex flex-col gap-2">
              {data.recent_notes.map((note) => (
                <li key={note.id}>
                  <Link
                    href={`/notes?open=${note.id}`}
                    className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm hover:bg-accent/40"
                  >
                    <span className="h-2 w-2 shrink-0 rounded-full" style={{ backgroundColor: note.color }} />
                    <span className="truncate">{note.title}</span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="px-1 text-sm text-muted-foreground">No notes yet.</p>
          )}
        </div>

        {/* Recent secrets */}
        <div className="rounded-xl border border-border p-4">
          <h2 className="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <KeyRound className="h-4 w-4" /> Recent secrets
          </h2>
          {isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : data && data.recent_secrets.length > 0 ? (
            <ul className="flex flex-col gap-2">
              {data.recent_secrets.map((secret) => (
                <li key={secret.id}>
                  <Link
                    href={`/vault?open=${secret.id}`}
                    className="flex items-center justify-between rounded-lg px-2 py-1.5 text-sm hover:bg-accent/40"
                  >
                    <span className="truncate">{secret.name}</span>
                    <span className="text-xs text-muted-foreground">{secret.type}</span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="px-1 text-sm text-muted-foreground">No secrets yet.</p>
          )}
        </div>

        {/* Recent activity */}
        <div className="rounded-xl border border-border p-4 md:col-span-3">
          <h2 className="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Activity className="h-4 w-4" /> Recent activity
          </h2>
          {isLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : data && data.recent_activity.length > 0 ? (
            <ul className="flex flex-col divide-y divide-border">
              {data.recent_activity.map((entry) => (
                <li key={entry.id} className="flex items-center justify-between py-2 text-sm">
                  <span>{entry.summary}</span>
                  <span className="shrink-0 text-xs text-muted-foreground">{formatRelativeTime(entry.created_at)}</span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState icon={Activity} title="No activity yet" description="Actions across Forge will show up here." />
          )}
        </div>
      </div>
    </div>
  );
}
