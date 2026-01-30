"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";
import TaskList from "@/components/TaskList";
import TaskForm from "@/components/TaskForm";

interface User {
  id: string;
  email: string;
  name?: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    authClient.getSession()
      .then((response) => {
        if (response?.data?.user) {
          setUser({
            id: response.data.user.id,
            email: response.data.user.email,
            name: response.data.user.name,
          });
        } else {
          router.push("/signin");
        }
        setIsLoading(false);
      })
      .catch(() => {
        router.push("/signin");
        setIsLoading(false);
      });
  }, [router]);

  const handleSignOut = async () => {
    await authClient.signOut();
    router.push("/signin");
  };

  const handleTaskCreated = useCallback(() => {
    setRefreshTrigger((prev) => prev + 1);
  }, []);

  if (isLoading) {
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

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation Header */}
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900 tracking-tight">Todo App</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600 hidden sm:block font-medium">
                {user.email}
              </span>
              <button
                onClick={handleSignOut}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded-lg transition-all duration-200 hover:shadow-sm"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Welcome Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Your Tasks</h2>
          <p className="mt-1 text-gray-600">
            Manage your tasks and stay organized
          </p>
        </div>

        {/* Task Form */}
        <div className="mb-8">
          <TaskForm onTaskCreated={handleTaskCreated} />
        </div>

        {/* Task List */}
        <TaskList refreshTrigger={refreshTrigger} />
      </main>
    </div>
  );
}
