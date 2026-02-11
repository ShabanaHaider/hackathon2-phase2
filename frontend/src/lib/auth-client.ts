"use client";

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: typeof window !== "undefined" ? window.location.origin : "http://localhost:3000",
  plugins: [jwtClient()],
  fetchOptions: {
    credentials: "include",
  },
});

export const { useSession, signIn, signUp, signOut } = authClient;

/**
 * Get JWT token for API calls
 * Uses Better Auth's JWT plugin to retrieve the access token
 */
export async function getToken(): Promise<string | null> {
  try {
    const response = await fetch('/api/auth/token', {
      credentials: 'include',
    });
    if (response.ok) {
      const data = await response.json();
      return data.token || null;
    }
    return null;
  } catch {
    return null;
  }
}
