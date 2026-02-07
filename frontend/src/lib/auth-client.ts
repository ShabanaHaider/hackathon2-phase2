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
    // The jwtClient plugin adds a getToken method
    const token = await authClient.getSession();
    // Better Auth stores the token in the session
    // We need to get the actual JWT - it may be in cookies or returned by the session
    // For now, we'll use a workaround: fetch the token endpoint
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
