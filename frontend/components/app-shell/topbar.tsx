"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Lock, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { authApi } from "@/features/auth/api";
import { useCommandPalette } from "@/components/command-palette/command-palette-provider";
import { MobileNav } from "./mobile-nav";

export function Topbar() {
  const { openPalette } = useCommandPalette();
  const router = useRouter();

  const lockMutation = useMutation({
    mutationFn: authApi.lock,
    onSuccess: () => router.replace("/unlock"),
  });

  return (
    <header className="flex h-14 shrink-0 items-center justify-between gap-4 border-b border-border px-4 md:px-6">
      <div className="flex flex-1 items-center gap-2">
        <MobileNav />
        <button
          onClick={openPalette}
          className="flex w-full max-w-sm items-center gap-2 rounded-lg border border-border bg-secondary/50 px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-secondary"
        >
          <Search className="h-3.5 w-3.5" />
          <span className="flex-1 text-left">Search Forge…</span>
          <kbd className="rounded border border-border bg-background px-1.5 py-0.5 text-[10px] font-medium">⌘K</kbd>
        </button>
      </div>

      <Button
        variant="ghost"
        size="sm"
        onClick={() => lockMutation.mutate()}
        disabled={lockMutation.isPending}
        className="text-muted-foreground"
      >
        <Lock className="h-4 w-4" />
        Lock
      </Button>
    </header>
  );
}
