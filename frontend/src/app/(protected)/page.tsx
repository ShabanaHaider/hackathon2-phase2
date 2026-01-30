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
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Todo App</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600 hidden sm:block">
                {user.email}
              </span>
              <button
                onClick={handleSignOut}
                className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Welcome Header */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Your Tasks</h2>
          <p className="mt-1 text-sm text-gray-600">
            Manage your tasks and stay organized
          </p>
        </div>

        {/* Task Form */}
        <div className="mb-6">
          <TaskForm onTaskCreated={handleTaskCreated} />
        </div>

        {/* Task List */}
        <TaskList refreshTrigger={refreshTrigger} />
      </main>
    </div>
  );
}
