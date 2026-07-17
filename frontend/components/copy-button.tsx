"use client";

import { Check, Copy } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useClipboard } from "@/hooks/use-clipboard";
import { cn } from "@/lib/utils";

export function CopyButton({
  value,
  label,
  className,
  size = "icon-sm",
}: {
  value: string;
  label?: string;
  className?: string;
  size?: "icon" | "icon-sm";
}) {
  const { copy, copied } = useClipboard();

  return (
    <Button
      type="button"
      variant="ghost"
      size={size}
      className={cn("text-muted-foreground", className)}
      onClick={() => copy(value, label)}
    >
      {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
    </Button>
  );
}
