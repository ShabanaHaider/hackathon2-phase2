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

    if (!session?.session || !session?.user) {
      return NextResponse.json(
        { error: "Not authenticated" },
        { status: 401 }
      );
    }

    // Use the JWT plugin's getToken method to generate a proper JWT
    const jwtResponse = await auth.api.getToken({
      headers: req.headers,
    });

    if (jwtResponse?.token) {
      return NextResponse.json({
        token: jwtResponse.token,
        userId: session.user.id,
      });
    }

    // Fallback: return error if JWT generation fails
    return NextResponse.json(
      { error: "Failed to generate JWT token" },
      { status: 500 }
    );
  } catch (error) {
    console.error("[Auth Token Error]", error);
    return NextResponse.json(
      { error: "Failed to get token" },
      { status: 500 }
    );
  }
}
