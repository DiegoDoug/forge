import type { NextConfig } from "next";

// In development, the backend runs as a separate process (see `docker
// compose` / `uvicorn --reload`); rewriting keeps every frontend fetch call
// same-origin (`/api/...`) so cookies and CORS never come into play. In the
// production image, Nginx performs the equivalent proxy in front of both
// services, so this rewrite is inert there.
const backendUrl = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  output: "standalone",
  async redirects() {
    return [
      // Compatibility alias for the pre-rename route — see ADR-0006
      // (forge-docs/decisions/0006-vault-renamed-to-secrets.md). Temporary,
      // not permanent, since the alias itself is meant to be removed later.
      { source: "/vault", destination: "/secrets", permanent: false },
      // Ingest was consolidated into the unified Converter page — see
      // Phase 04 (Universal Converter) 01_SPEC.md §3 requirement 2.
      // `permanent: false` matches the alias above rather than issuing a
      // cacheable 308, since a redirect is easier to adjust than to undo.
      { source: "/ingest", destination: "/converters", permanent: false },
      // Generators, Crypto, and Utilities were consolidated into the unified
      // Developer Toolkit page — see Phase 08 01_SPEC.md §3 requirement 2.
      // Each carries a `?tab=` so a bookmark lands on the section it named,
      // rather than defaulting to the first tab. `permanent: false` for the
      // same reason as the two aliases above.
      //
      // These three entries and the deletion of the corresponding
      // app/(app)/{generators,crypto,utilities}/page.tsx files are a single
      // atomic change (09_IMPLEMENTATION_TASKS.md T2+T3): the routes must
      // never resolve to a 404, at any commit.
      { source: "/generators", destination: "/developer-toolkit?tab=generators", permanent: false },
      { source: "/crypto", destination: "/developer-toolkit?tab=crypto", permanent: false },
      { source: "/utilities", destination: "/developer-toolkit?tab=utilities", permanent: false },
    ];
  },
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${backendUrl}/api/:path*` },
      { source: "/health", destination: `${backendUrl}/health` },
      // The backend mounts /system/status at the root, without the /api prefix
      // (app/api/routes/health.py), so it matched neither rewrite above and was
      // served by Next.js instead — a 404 with an HTML body, which made the
      // Settings "About" storage row silently never render. See Phase 09 T0.5b.
      //
      // NOTE: this fixes development only. docker/nginx.conf proxies /api/ and
      // /health but NOT /system/status, so production has the same 404 via a
      // different path. That is a deployment-config gap raised as a finding, not
      // patched here — see Phase-09 00_AUDIT.md §3.2 and 03_BACKEND.md §2.2.
      { source: "/system/status", destination: `${backendUrl}/system/status` },
    ];
  },
};

export default nextConfig;
