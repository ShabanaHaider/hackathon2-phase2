"use client";

import { useState, useCallback, useEffect } from "react";
import Link from "next/link";
import { useSession, signOut, authClient } from "@/lib/auth-client";
import TaskList from "@/components/TaskList";
import TaskForm from "@/components/TaskForm";
import ChatContainer from "@/components/ChatContainer";

interface User {
  id: string;
  email: string;
  name?: string;
}

interface AuthenticatedDashboardProps {
  user: User;
  onSignOut: () => void;
}

function AuthenticatedDashboard({ user, onSignOut }: AuthenticatedDashboardProps) {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [token, setToken] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'tasks' | 'chat'>('tasks');

  // Get JWT token for API calls
  useEffect(() => {
    async function fetchToken() {
      try {
        // Try to get token from session/cookie
        const response = await fetch('/api/auth/token', {
          credentials: 'include',
        });
        if (response.ok) {
          const data = await response.json();
          if (data.token) {
            setToken(data.token);
            return;
          }
        }
        // Fallback: try using the session token from cookies
        // The Better Auth JWT plugin should handle this
        const session = await authClient.getSession();
        if (session?.data?.session) {
          // Use session token as fallback
          setToken(session.data.session.token || null);
        }
      } catch (err) {
        console.error('Failed to get token:', err);
      }
    }
    fetchToken();
  }, []);

  const handleTaskCreated = useCallback(() => {
    setRefreshTrigger((prev) => prev + 1);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation Header */}
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900 tracking-tight">Todo App</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600 hidden sm:block font-medium">
                {user.email}
              </span>
              <button
                onClick={onSignOut}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded-lg transition-all duration-200 hover:shadow-sm"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Tab Navigation (Mobile) */}
      <div className="md:hidden bg-white border-b border-gray-200">
        <div className="flex">
          <button
            onClick={() => setActiveTab('tasks')}
            className={`flex-1 py-3 text-sm font-medium text-center border-b-2 transition-colors ${
              activeTab === 'tasks'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Tasks
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex-1 py-3 text-sm font-medium text-center border-b-2 transition-colors ${
              activeTab === 'chat'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            AI Assistant
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Tasks Section */}
          <div className={`${activeTab === 'chat' ? 'hidden md:block' : ''}`}>
            {/* Welcome Header */}
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Your Tasks</h2>
              <p className="mt-1 text-gray-600">
                Manage your tasks and stay organized
              </p>
            </div>

            {/* Task Form */}
            <div className="mb-6">
              <TaskForm onTaskCreated={handleTaskCreated} />
            </div>

            {/* Task List */}
            <TaskList refreshTrigger={refreshTrigger} />
          </div>

          {/* Chat Section */}
          <div className={`${activeTab === 'tasks' ? 'hidden md:block' : ''}`}>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 tracking-tight">AI Assistant</h2>
              <p className="mt-1 text-gray-600">
                Chat with AI to manage your tasks
              </p>
            </div>

            {token ? (
              <ChatContainer userId={user.id} token={token} onTaskChange={handleTaskCreated} />
            ) : (
              <div className="h-[500px] md:h-[600px] bg-white rounded-2xl border border-gray-200 shadow-sm flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <svg className="animate-spin h-8 w-8 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <p>Loading chat...</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default function HomePage() {
  const { data: session, isPending } = useSession();

  const handleSignOut = useCallback(async () => {
    await signOut();
  }, []);

  // Loading state while checking authentication
  if (isPending) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="flex items-center gap-3 text-gray-700">
          <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="font-medium">Loading...</span>
        </div>
      </div>
    );
  }

  // User is authenticated - show full dashboard with task management
  if (session?.user) {
    return <AuthenticatedDashboard user={session.user} onSignOut={handleSignOut} />;
  }

  // User is NOT authenticated - show landing page
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-200">
      {/* Navigation Header */}
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900 tracking-tight">Todo App</h1>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/signin"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
              >
                Sign in
              </Link>
              <Link
                href="/signup"
                className="px-4 py-2 text-sm font-semibold text-white bg-gray-900 hover:bg-gray-800 rounded-lg shadow-sm hover:shadow transition-all duration-200"
              >
                Sign up
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          {/* Icon */}
          <div className="flex justify-center mb-8">
            <div className="w-20 h-20 bg-gray-900 rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
          </div>

          {/* Heading */}
          <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-6 tracking-tight">
            Stay organized.<br />Get things done.
          </h1>

          {/* Subheading */}
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
            A simple, powerful task management app that helps you track your todos,
            stay productive, and accomplish your goals.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-20">
            <Link
              href="/signup"
              className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-white bg-gray-900 hover:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
            >
              Get started for free
              <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
            <Link
              href="/signin"
              className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-gray-900 bg-white hover:bg-gray-50 rounded-xl shadow-lg hover:shadow-xl border-2 border-gray-200 transition-all duration-200"
            >
              Sign in to your account
            </Link>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto mt-20">
            {/* Feature 1 */}
            <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow duration-200">
              <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <svg className="w-6 h-6 text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Create Tasks</h3>
              <p className="text-gray-600">
                Quickly add tasks with titles and descriptions to capture everything you need to do.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow duration-200">
              <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <svg className="w-6 h-6 text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Track Progress</h3>
              <p className="text-gray-600">
                Mark tasks as complete and watch your progress as you accomplish your goals.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-200 hover:shadow-xl transition-shadow duration-200">
              <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <svg className="w-6 h-6 text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Secure & Private</h3>
              <p className="text-gray-600">
                Your tasks are private and secure with user authentication and encrypted storage.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-600 text-sm">
            Built with Next.js, FastAPI, and PostgreSQL
          </p>
        </div>
      </footer>
    </div>
  );
}
