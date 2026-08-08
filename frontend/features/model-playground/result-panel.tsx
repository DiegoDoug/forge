import { AlertTriangle, Clock } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CopyButton } from "@/components/copy-button";
import { StatusBadge } from "@/components/status-badge";
import type { PlaygroundResult } from "./api";

export function ResultPanel({ result }: { result: PlaygroundResult }) {
  return (
    <Card size="sm" className="flex flex-col">
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="text-sm">{result.model}</CardTitle>
          <ResultStatusBadge status={result.status} />
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

function ResultStatusBadge({ status }: { status: PlaygroundResult["status"] }) {
  if (status === "success") return <StatusBadge tone="success">Success</StatusBadge>;
  if (status === "timeout") return <StatusBadge tone="warning">Timed out</StatusBadge>;
  return <StatusBadge tone="danger">Error</StatusBadge>;
}
