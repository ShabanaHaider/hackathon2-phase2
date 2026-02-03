import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "@neondatabase/serverless";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const auth = betterAuth({
  database: pool,
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
  trustedOrigins: [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://hack2-phase2-frontend.vercel.app",
    "https://hack2-phase2-frontend-lyqfs1cek-shabanahaiders-projects.vercel.app"
  ],
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
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
    useSecureCookies: process.env.NODE_ENV === "production", // Secure cookies in production only
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
