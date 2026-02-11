import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "@neondatabase/serverless";

// Validate required environment variables
if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL environment variable is not set");
}

if (!process.env.BETTER_AUTH_SECRET) {
  throw new Error("BETTER_AUTH_SECRET environment variable is not set");
}

// Initialize database pool with error handling
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Log initialization (safe info only)
if (process.env.NODE_ENV === "development") {
  console.log("[Better Auth] Initializing with:", {
    baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
    nodeEnv: process.env.NODE_ENV,
    hasSecret: !!process.env.BETTER_AUTH_SECRET,
    hasDbUrl: !!process.env.DATABASE_URL,
  });
}

export const auth = betterAuth({
  database: pool,
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
  trustedOrigins: [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3030",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://172.26.56.163:3030",
    "http://172.26.56.163:3000",
    "https://hack2-phase2-frontend.vercel.app",
  ],
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
    requireEmailVerification: false,
  },
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  advanced: {
    cookiePrefix: "better-auth",
    // Disable secure cookies for HTTP development
    useSecureCookies: false,
    crossSubDomainCookies: {
      enabled: false,
    },
  },
  plugins: [
    jwt({
      jwt: {
        definePayload: async ({ user }) => ({
          sub: user.id,
          email: user.email,
        }),
      },
    }),
  ],
});
