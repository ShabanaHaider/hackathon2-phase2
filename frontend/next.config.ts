import type { NextConfig } from "next";

const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || "http://todo-backend:8000";

const nextConfig: NextConfig = {
  output: "standalone",
  serverExternalPackages: ["pg", "pg-native"],
  async rewrites() {
    return [
      { source: "/api/todos/:path*", destination: `${BACKEND_URL}/api/todos/:path*` },
      { source: "/api/todos", destination: `${BACKEND_URL}/api/todos` },
      { source: "/api/tags/:path*", destination: `${BACKEND_URL}/api/tags/:path*` },
      { source: "/api/tags", destination: `${BACKEND_URL}/api/tags` },
      { source: "/api/conversations/:path*", destination: `${BACKEND_URL}/api/conversations/:path*` },
      { source: "/api/conversations", destination: `${BACKEND_URL}/api/conversations` },
      { source: "/api/:userId/chat", destination: `${BACKEND_URL}/api/:userId/chat` },
    ];
  },
};

export default nextConfig;
