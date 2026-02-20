"use client";

import { useState } from "react";
import { api, ApiException } from "@/lib/api";
import TagSelector from "./TagSelector";

interface TaskFormProps {
  onTaskCreated: () => void;
}

export default function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<"low" | "medium" | "high">("medium");
  const [dueAt, setDueAt] = useState("");
  const [tagNames, setTagNames] = useState<string[]>([]);
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurrencePattern, setRecurrencePattern] = useState<"daily" | "weekly" | "monthly">("daily");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [showDetails, setShowDetails] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      await api.createTask({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        due_at: dueAt ? new Date(dueAt).toISOString() : undefined,
        is_recurring: isRecurring || undefined,
        recurrence_pattern: isRecurring ? recurrencePattern : undefined,
        tag_names: tagNames.length > 0 ? tagNames : undefined,
      });
      setTitle("");
      setDescription("");
      setPriority("medium");
      setDueAt("");
      setIsRecurring(false);
      setRecurrencePattern("daily");
      setTagNames([]);
      setShowDetails(false);
      onTaskCreated();
    } catch (err) {
      if (err instanceof ApiException) {
        setError(err.detail);
      } else {
        setError("Failed to create task. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
      {error && (
        <div className="mb-4 text-sm text-red-700 bg-red-50 border border-red-200 p-3 rounded-lg">
          {error}
        </div>
      )}
      <div className="space-y-4">
        <div>
          <label htmlFor="task-title" className="sr-only">
            Task title
          </label>
          <input
            id="task-title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="What needs to be done?"
            maxLength={255}
            className="w-full px-4 py-3 text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent placeholder-gray-400 transition-all duration-200"
            disabled={isLoading}
          />
        </div>

        {showDetails ? (
          <div className="space-y-4">
            {/* Description */}
            <div>
              <label htmlFor="task-description" className="sr-only">
                Description
              </label>
              <textarea
                id="task-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add a description (optional)"
                maxLength={2000}
                rows={3}
                className="w-full px-4 py-3 text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent placeholder-gray-400 resize-none transition-all duration-200"
                disabled={isLoading}
              />
            </div>

            {/* Priority + Due Date row */}
            <div className="flex gap-3">
              <div className="flex-1">
                <label htmlFor="task-priority" className="block text-sm font-medium text-gray-700 mb-1">
                  Priority
                </label>
                <select
                  id="task-priority"
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as "low" | "medium" | "high")}
                  disabled={isLoading}
                  className="w-full px-3 py-2 text-sm text-gray-900 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent transition-all duration-200"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div className="flex-1">
                <label htmlFor="task-due-at" className="block text-sm font-medium text-gray-700 mb-1">
                  Due date
                </label>
                <input
                  id="task-due-at"
                  type="datetime-local"
                  value={dueAt}
                  onChange={(e) => setDueAt(e.target.value)}
                  disabled={isLoading}
                  className="w-full px-3 py-2 text-sm text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent transition-all duration-200"
                />
              </div>
            </div>

            {/* Recurring */}
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isRecurring}
                  onChange={(e) => setIsRecurring(e.target.checked)}
                  disabled={isLoading}
                  className="w-4 h-4 rounded border-gray-300 text-gray-900 focus:ring-gray-400"
                />
                Recurring task
              </label>
              {isRecurring && (
                <select
                  value={recurrencePattern}
                  onChange={(e) => setRecurrencePattern(e.target.value as "daily" | "weekly" | "monthly")}
                  disabled={isLoading}
                  aria-label="Recurrence pattern"
                  className="px-3 py-1.5 text-sm text-gray-900 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-gray-400"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              )}
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
              <TagSelector selectedTags={tagNames} onChange={setTagNames} disabled={isLoading} />
            </div>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => setShowDetails(true)}
            className="text-sm text-gray-500 hover:text-gray-800 flex items-center gap-1.5 transition-colors duration-200"
            disabled={isLoading}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add details
          </button>
        )}

        <div className="flex justify-end pt-1">
          <button
            type="submit"
            disabled={isLoading || !title.trim()}
            className="px-5 py-2.5 text-sm font-semibold text-white bg-gray-900 hover:bg-gray-800 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center transition-all duration-200 shadow-sm hover:shadow"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin -ml-0.5 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Adding...
              </>
            ) : (
              <>
                <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add task
              </>
            )}
          </button>
        </div>
      </div>
    </form>
  );
}
