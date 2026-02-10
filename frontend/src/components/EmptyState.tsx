"use client";

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export default function EmptyState({
  title = "No tasks yet",
  description = "Create your first task to get started!",
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="text-center py-16 px-4">
      <div className="mx-auto w-20 h-20 mb-6 bg-gray-200 rounded-full flex items-center justify-center">
        <svg
          className="w-10 h-10 text-gray-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
          />
        </svg>
      </div>
      <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-500 mb-6 max-w-sm mx-auto">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="inline-flex items-center px-5 py-2.5 text-sm font-semibold text-white bg-gray-900 hover:bg-gray-800 rounded-lg shadow-sm hover:shadow transition-all duration-200"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
