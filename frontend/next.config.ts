import type { NextConfig } from "next";

// In development, the backend runs as a separate process (see `docker
// compose` / `uvicorn --reload`); rewriting keeps every frontend fetch call
// same-origin (`/api/...`) so cookies and CORS never come into play. In the
// production image, Nginx performs the equivalent proxy in front of both
// services, so this rewrite is inert there.
const backendUrl = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${backendUrl}/api/:path*` },
      { source: "/health", destination: `${backendUrl}/health` },
    ];
  },
};

export default nextConfig;
