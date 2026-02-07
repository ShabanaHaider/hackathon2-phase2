import { auth } from "@/lib/auth";
import { NextRequest, NextResponse } from "next/server";

/**
 * GET /api/auth/token
 * Returns the JWT token for the current session
 * Used by the chat API to authenticate backend requests
 */
export async function GET(req: NextRequest) {
  try {
    // Get the session from Better Auth
    const session = await auth.api.getSession({
      headers: req.headers,
    });

    if (!session?.session) {
      return NextResponse.json(
        { error: "Not authenticated" },
        { status: 401 }
      );
    }

    // The JWT plugin should have added a token to the session
    // Try to get the token - it may be stored differently depending on config
    const token = (session.session as any).token ||
                  (session as any).token ||
                  null;

    if (!token) {
      // If no token in session, try to generate one using the JWT plugin
      // This depends on Better Auth configuration
      // For now, we'll return the session token which can be verified
      return NextResponse.json(
        {
          token: session.session.token || null,
          userId: session.user?.id,
          error: token ? null : "JWT token not available, using session token"
        },
        { status: 200 }
      );
    }

    return NextResponse.json({
      token,
      userId: session.user?.id,
    });
  } catch (error) {
    console.error("[Auth Token Error]", error);
    return NextResponse.json(
      { error: "Failed to get token" },
      { status: 500 }
    );
  }
}
