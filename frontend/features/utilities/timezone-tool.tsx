"use client";

import { useMemo, useState } from "react";

import { Input } from "@/components/ui/input";
import { ToolCard } from "@/components/tool-card";

const ZONES = [
  "UTC",
  "America/Los_Angeles",
  "America/New_York",
  "Europe/London",
  "Europe/Berlin",
  "Asia/Kolkata",
  "Asia/Tokyo",
  "Australia/Sydney",
];

export function TimezoneTool() {
  const [value, setValue] = useState(() => new Date().toISOString().slice(0, 16));

  const date = useMemo(() => new Date(value), [value]);
  const valid = !Number.isNaN(date.getTime());

  return (
    <ToolCard title="Timezone converter" description="See one moment in time across zones">
      <Input type="datetime-local" value={value} onChange={(e) => setValue(e.target.value)} />
      {valid ? (
        <div className="flex flex-col divide-y divide-border rounded-lg border border-border">
          {ZONES.map((zone) => (
            <div key={zone} className="flex items-center justify-between px-3 py-1.5 text-xs">
              <span className="text-muted-foreground">{zone}</span>
              <span className="font-mono">
                {new Intl.DateTimeFormat(undefined, {
                  timeZone: zone,
                  dateStyle: "medium",
                  timeStyle: "short",
                }).format(date)}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs text-destructive">Invalid date</p>
      )}
    </ToolCard>
  );
}
