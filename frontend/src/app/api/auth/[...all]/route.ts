import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";
import { NextRequest } from "next/server";

// Export Better Auth handlers for Next.js App Router
// This catch-all route handles all Better Auth endpoints:
// - POST /api/auth/sign-in/email
// - POST /api/auth/sign-up/email
// - POST /api/auth/sign-out
// - GET /api/auth/session
// - And all other Better Auth routes

const handlers = toNextJsHandler(auth);

// Wrap handlers with error logging for debugging
export async function GET(req: NextRequest) {
  try {
    if (process.env.NODE_ENV === "development") {
      console.log("[Auth GET]", {
        url: req.url,
        origin: req.headers.get("origin"),
        referer: req.headers.get("referer"),
      });
    }
    return await handlers.GET(req);
  } catch (error: any) {
    console.error("[Auth GET Error]", {
      error: error.message,
      stack: error.stack,
      url: req.url,
    });
    throw error;
  }
}

export async function POST(req: NextRequest) {
  try {
    if (process.env.NODE_ENV === "development") {
      console.log("[Auth POST]", {
        url: req.url,
        origin: req.headers.get("origin"),
        referer: req.headers.get("referer"),
        contentType: req.headers.get("content-type"),
      });
    }
    return await handlers.POST(req);
  } catch (error: any) {
    console.error("[Auth POST Error]", {
      error: error.message,
      stack: error.stack,
      url: req.url,
    });
    throw error;
  }
}