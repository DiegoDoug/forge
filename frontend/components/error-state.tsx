import { AlertTriangle, RotateCw } from "lucide-react";

import { Button } from "@/components/ui/button";

// One retryable failure treatment. Replaces the 4 divergent inline
// "couldn't load + retry" blocks the Phase 09 audit found — including
// Search's pre-existing misuse of EmptyState for errors, and Project Init's
// catalog error, which previously had no retry at all. See 00_AUDIT.md §5.5.
export function ErrorState({
  title = "Couldn't load this",
  description,
  onRetry,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-border px-6 py-16 text-center">
      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-danger-subtle text-destructive">
        <AlertTriangle className="h-5 w-5" />
      </div>
      <div>
        <p className="text-sm font-medium">{title}</p>
        {description ? <p className="mt-1 max-w-sm text-sm text-muted-foreground">{description}</p> : null}
      </div>
      {onRetry ? (
        <Button size="sm" variant="outline" onClick={onRetry}>
          <RotateCw className="h-3.5 w-3.5" />
          Retry
        </Button>
      ) : null}
    </div>
  );
}
