"use client";

import { useState } from "react";
import { toast } from "sonner";

export function useClipboard() {
  const [copied, setCopied] = useState(false);

  async function copy(value: string, label = "Copied to clipboard") {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      toast.success(label);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      toast.error("Couldn't copy to clipboard");
    }
  }

  return { copy, copied };
}
