"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authClient } from "@/lib/auth-client";

export default function SignUpPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [passwordError, setPasswordError] = useState("");

  const validatePassword = (value: string) => {
    if (value.length > 0 && value.length < 8) {
      setPasswordError("Password must be at least 8 characters");
    } else {
      setPasswordError("");
    }
    setPassword(value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Client-side validation
    if (password.length < 8) {
      setPasswordError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);

    try {
      const result = await authClient.signUp.email({
        email,
        password,
        name: email.split("@")[0], // Use email prefix as name
      });

      if (result.error) {
        // Handle duplicate email or other errors
        if (result.error.message?.toLowerCase().includes("email") ||
            result.error.message?.toLowerCase().includes("exist") ||
            result.error.message?.toLowerCase().includes("already")) {
          setError("This email is already registered. Please sign in instead.");
        } else {
          setError(result.error.message || "Sign up failed. Please try again.");
        }
        setLoading(false);
        return;
      }

      // Success - redirect to dashboard
      router.push("/");
    } catch (err) {
      console.error("Sign up error:", err);
      setError("An unexpected error occurred. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-2xl shadow-lg border border-gray-200">
        <div>
          <h2 className="text-center text-3xl font-bold text-gray-900 tracking-tight">
            Create your account
          </h2>
          <p className="mt-3 text-center text-gray-600">
            Start managing your tasks today
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}
          <div className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-gray-800 mb-2">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="block w-full px-4 py-3 text-gray-900 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent transition-all duration-200"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-gray-800 mb-2">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                maxLength={128}
                value={password}
                onChange={(e) => validatePassword(e.target.value)}
                className={`block w-full px-4 py-3 text-gray-900 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent transition-all duration-200 ${
                  passwordError ? "border-red-300" : "border-gray-300"
                }`}
                placeholder="Min. 8 characters"
              />
              {passwordError ? (
                <p className="mt-2 text-sm text-red-600">{passwordError}</p>
              ) : (
                <p className="mt-2 text-sm text-gray-500">Must be at least 8 characters</p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading || !!passwordError}
              className="w-full flex justify-center py-3 px-4 rounded-lg shadow-sm text-sm font-semibold text-white bg-gray-900 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {loading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating account...
                </span>
              ) : (
                "Sign up"
              )}
            </button>
          </div>

          <div className="text-center text-sm">
            <span className="text-gray-600">Already have an account? </span>
            <Link href="/signin" className="text-gray-900 hover:text-gray-700 font-semibold underline underline-offset-2">
              Sign in
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
