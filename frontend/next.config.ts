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
    ];
  },
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${backendUrl}/api/:path*` },
      { source: "/health", destination: `${backendUrl}/health` },
    ];
  },
};

export default nextConfig;
