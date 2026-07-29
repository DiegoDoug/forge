import { AlertTriangle, Clock } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CopyButton } from "@/components/copy-button";
import type { PlaygroundResult } from "./api";

export function ResultPanel({ result }: { result: PlaygroundResult }) {
  return (
    <Card size="sm" className="flex flex-col">
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="text-sm">{result.model}</CardTitle>
          <StatusBadge status={result.status} />
        </div>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-2">
        {result.status === "success" ? (
          <>
            <p className="flex-1 whitespace-pre-wrap text-sm">{result.response_text}</p>
            <div className="flex items-center justify-between border-t border-border pt-2 text-xs text-muted-foreground">
              <span>
                {result.latency_ms != null ? `${result.latency_ms}ms` : ""}
                {result.prompt_tokens != null && result.completion_tokens != null
                  ? ` · ${result.prompt_tokens + result.completion_tokens} tokens`
                  : ""}
              </span>
              {result.response_text ? <CopyButton value={result.response_text} /> : null}
            </div>
          </>
        ) : (
          <div className="flex flex-1 items-center gap-2 text-sm text-muted-foreground">
            {result.status === "timeout" ? (
              <Clock className="h-4 w-4 shrink-0 text-destructive" />
            ) : (
              <AlertTriangle className="h-4 w-4 shrink-0 text-destructive" />
            )}
            <span>{result.error_message ?? "Request failed."}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function StatusBadge({ status }: { status: PlaygroundResult["status"] }) {
  if (status === "success") return <Badge variant="secondary">Success</Badge>;
  if (status === "timeout") return <Badge variant="destructive">Timed out</Badge>;
  return <Badge variant="destructive">Error</Badge>;
}
