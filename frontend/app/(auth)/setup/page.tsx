"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi } from "@/features/auth/api";

export default function SetupPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);

  const setupStatus = useQuery({ queryKey: ["setup-status"], queryFn: authApi.setupStatus });

  const mutation = useMutation({
    mutationFn: () => authApi.setup(password),
    onSuccess: () => router.replace("/"),
    onError: (err: Error) => setError(err.message),
  });

  useEffect(() => {
    if (setupStatus.data?.setup_completed) {
      router.replace("/unlock");
    }
  }, [setupStatus.data?.setup_completed, router]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError("Master password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    mutation.mutate();
  }

  return (
    <div className="flex flex-col gap-6 rounded-2xl border border-border bg-card p-8 shadow-xl shadow-black/5">
      <div className="flex flex-col items-center gap-2 text-center">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
          <ShieldCheck className="h-5 w-5" />
        </div>
        <h1 className="text-lg font-semibold">Welcome to Forge</h1>
        <p className="text-sm text-muted-foreground">
          Set a master password to encrypt this instance. It unlocks your secrets and cannot be recovered if lost.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <Label htmlFor="password">Master password</Label>
          <Input
            id="password"
            type="password"
            autoFocus
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 8 characters"
          />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="confirm">Confirm password</Label>
          <Input id="confirm" type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} />
        </div>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <Button type="submit" disabled={mutation.isPending} className="mt-2">
          {mutation.isPending ? "Setting up…" : "Finish setup"}
        </Button>
      </form>
    </div>
  );
}
