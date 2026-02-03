import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

// Export Better Auth handlers for Next.js App Router
// This catch-all route handles all Better Auth endpoints:
// - POST /api/auth/sign-in/email
// - POST /api/auth/sign-up/email
// - POST /api/auth/sign-out
// - GET /api/auth/session
// - And all other Better Auth routes
export const { GET, POST } = toNextJsHandler(auth);