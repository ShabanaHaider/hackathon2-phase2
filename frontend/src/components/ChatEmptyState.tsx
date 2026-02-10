"use client";

interface ChatEmptyStateProps {
  onSuggestedPrompt?: (prompt: string) => void;
}

const SUGGESTED_PROMPTS = [
  "Add a task to buy groceries",
  "Show my tasks",
  "What can you help me with?",
];

export default function ChatEmptyState({ onSuggestedPrompt }: ChatEmptyStateProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
      {/* Icon */}
      <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mb-6">
        <svg
          className="w-8 h-8 text-blue-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      </div>

      {/* Welcome message */}
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        Hi! I'm your task assistant
      </h3>
      <p className="text-gray-600 mb-6 max-w-sm">
        I can help you manage your tasks. Try asking me to add, list, update, or complete tasks.
      </p>

      {/* Suggested prompts */}
      <div className="space-y-2 w-full max-w-sm">
        <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-3">
          Try saying:
        </p>
        {SUGGESTED_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            onClick={() => onSuggestedPrompt?.(prompt)}
            className="w-full px-4 py-3 text-left text-sm text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-xl border border-gray-200 transition-colors"
          >
            "{prompt}"
          </button>
        ))}
      </div>
    </div>
  );
}
