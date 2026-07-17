"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { ApiError } from "@/lib/api-client";
import { authApi } from "./api";

export function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  const setupQuery = useQuery({
    queryKey: ["setup-status"],
    queryFn: authApi.setupStatus,
  });

  const sessionQuery = useQuery({
    queryKey: ["session"],
    queryFn: authApi.session,
    enabled: setupQuery.data?.setup_completed === true,
    retry: false,
  });

  useEffect(() => {
    if (setupQuery.isSuccess && !setupQuery.data.setup_completed) {
      router.replace("/setup");
    }
  }, [setupQuery.isSuccess, setupQuery.data, router]);

  useEffect(() => {
    if (sessionQuery.isError) {
      const err = sessionQuery.error;
      if (err instanceof ApiError && (err.status === 401 || err.code === "setup_required")) {
        router.replace("/unlock");
      }
    }
  }, [sessionQuery.isError, sessionQuery.error, router]);

  const ready = setupQuery.data?.setup_completed === true && sessionQuery.data?.authenticated === true;

  if (!ready) {
    return (
      <div className="flex h-dvh items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3 text-muted-foreground">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <p className="text-sm">Loading Forge…</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
