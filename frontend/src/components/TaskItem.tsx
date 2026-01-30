"use client";

import { useState } from "react";
import { Task, api, ApiException } from "@/lib/api";

interface TaskItemProps {
  task: Task;
  onUpdate: () => void;
  onDelete: () => void;
}

export default function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || "");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleToggleComplete = async () => {
    setIsLoading(true);
    setError("");
    try {
      await api.updateTask(task.id, {
        is_completed: !task.is_completed,
      });
      onUpdate();
    } catch (err) {
      if (err instanceof ApiException) {
        setError(err.detail);
      } else {
        setError("Failed to update task");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editTitle.trim()) {
      setError("Title is required");
      return;
    }

    setIsLoading(true);
    setError("");
    try {
      await api.updateTask(task.id, {
        title: editTitle.trim(),
        description: editDescription.trim() || undefined,
      });
      setIsEditing(false);
      onUpdate();
    } catch (err) {
      if (err instanceof ApiException) {
        setError(err.detail);
      } else {
        setError("Failed to save changes");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || "");
    setIsEditing(false);
    setError("");
  };

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this task?")) {
      return;
    }

    setIsLoading(true);
    setError("");
    try {
      await api.deleteTask(task.id);
      onDelete();
    } catch (err) {
      if (err instanceof ApiException) {
        setError(err.detail);
      } else {
        setError("Failed to delete task");
      }
      setIsLoading(false);
    }
  };

  if (isEditing) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
        {error && (
          <div className="mb-4 text-sm text-red-700 bg-red-50 border border-red-200 p-3 rounded-lg">
            {error}
          </div>
        )}
        <div className="space-y-4">
          <div>
            <label htmlFor={`edit-title-${task.id}`} className="block text-sm font-semibold text-gray-800 mb-2">
              Title
            </label>
            <input
              id={`edit-title-${task.id}`}
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              maxLength={255}
              className="w-full px-4 py-2.5 text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent transition-all duration-200"
              disabled={isLoading}
            />
          </div>
          <div>
            <label htmlFor={`edit-desc-${task.id}`} className="block text-sm font-semibold text-gray-800 mb-2">
              Description (optional)
            </label>
            <textarea
              id={`edit-desc-${task.id}`}
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              maxLength={2000}
              rows={3}
              className="w-full px-4 py-2.5 text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent resize-none transition-all duration-200"
              disabled={isLoading}
            />
          </div>
          <div className="flex gap-3 justify-end pt-2">
            <button
              onClick={handleCancelEdit}
              disabled={isLoading}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 border border-gray-300 rounded-lg disabled:opacity-50 transition-all duration-200"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveEdit}
              disabled={isLoading || !editTitle.trim()}
              className="px-4 py-2 text-sm font-semibold text-white bg-gray-900 hover:bg-gray-800 rounded-lg disabled:opacity-50 flex items-center transition-all duration-200 shadow-sm"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-0.5 mr-1.5 h-3 w-3 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Saving...
                </>
              ) : (
                "Save"
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow duration-200 ${isLoading ? "opacity-50" : ""}`}>
      {error && (
        <div className="mb-3 text-sm text-red-700 bg-red-50 border border-red-200 p-2.5 rounded-lg">
          {error}
        </div>
      )}
      <div className="flex items-start gap-4">
        <button
          onClick={handleToggleComplete}
          disabled={isLoading}
          className={`mt-0.5 w-5 h-5 rounded-md border-2 flex-shrink-0 flex items-center justify-center transition-all duration-200 ${
            task.is_completed
              ? "bg-gray-900 border-gray-900 text-white"
              : "border-gray-300 hover:border-gray-500"
          } disabled:cursor-not-allowed`}
          aria-label={task.is_completed ? "Mark as incomplete" : "Mark as complete"}
        >
          {task.is_completed && (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>
        <div className="flex-1 min-w-0">
          <h3
            className={`text-base font-semibold ${
              task.is_completed ? "text-gray-400 line-through" : "text-gray-900"
            }`}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              className={`mt-1.5 text-sm leading-relaxed ${
                task.is_completed ? "text-gray-400" : "text-gray-600"
              }`}
            >
              {task.description}
            </p>
          )}
          <p className="mt-2.5 text-xs text-gray-400 font-medium">
            Created {new Date(task.created_at).toLocaleDateString()}
            {task.is_completed && task.completed_at && (
              <span> · Completed {new Date(task.completed_at).toLocaleDateString()}</span>
            )}
          </p>
        </div>
        <div className="flex gap-2 flex-shrink-0">
          <button
            onClick={() => setIsEditing(true)}
            disabled={isLoading}
            className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded-lg disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200 flex items-center gap-1.5"
            aria-label="Edit task"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={isLoading}
            className="px-3 py-1.5 text-sm font-medium text-red-700 bg-red-50 hover:bg-red-100 border border-red-200 rounded-lg disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200 flex items-center gap-1.5"
            aria-label="Delete task"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
