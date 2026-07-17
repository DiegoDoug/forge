export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex h-dvh items-center justify-center overflow-hidden bg-background px-4">
      <div className="pointer-events-none absolute inset-0 [background:radial-gradient(circle_at_50%_-10%,color-mix(in_oklch,var(--primary)_18%,transparent),transparent_60%)]" />
      <div className="relative w-full max-w-sm">{children}</div>
    </div>
  );
}
