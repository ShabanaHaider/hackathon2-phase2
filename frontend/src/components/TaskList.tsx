"use client";

import { useState, useEffect, useCallback } from "react";
import { Task, api, ApiException } from "@/lib/api";
import TaskItem from "./TaskItem";
import EmptyState from "./EmptyState";

interface TaskListProps {
  onTaskCreated?: () => void;
  refreshTrigger?: number;
}

export default function TaskList({ refreshTrigger }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError("");
    try {
      const data = await api.listTasks();
      setTasks(data);
    } catch (err) {
      if (err instanceof ApiException) {
        if (err.status !== 401) {
          setError(err.detail);
        }
      } else {
        setError("Failed to load tasks. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks, refreshTrigger]);

  const handleRetry = () => {
    fetchTasks();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center text-gray-600">
          <svg className="animate-spin -ml-1 mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading tasks...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto w-16 h-16 mb-4 bg-red-100 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-1">Unable to load tasks</h3>
        <p className="text-gray-500 mb-4">{error}</p>
        <button
          onClick={handleRetry}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Try again
        </button>
      </div>
    );
  }

  if (tasks.length === 0) {
    return <EmptyState />;
  }

  // Sort tasks: incomplete first, then by creation date (newest first)
  const sortedTasks = [...tasks].sort((a, b) => {
    if (a.is_completed !== b.is_completed) {
      return a.is_completed ? 1 : -1;
    }
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  return (
    <div className="space-y-3">
      {sortedTasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onUpdate={fetchTasks}
          onDelete={fetchTasks}
        />
      ))}
    </div>
  );
}
