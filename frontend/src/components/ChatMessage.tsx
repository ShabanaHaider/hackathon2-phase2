"use client";

import type { ChatMessage as ChatMessageType } from '@/types/chat';

interface ChatMessageProps {
  message: ChatMessageType;
  onRetry?: (messageId: string) => void;
}

function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export default function ChatMessage({ message, onRetry }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isPending = message.status === 'pending';
  const hasError = message.status === 'error';

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-md'
            : 'bg-gray-100 text-gray-900 rounded-bl-md'
        } ${isPending ? 'opacity-70' : ''}`}
      >
        {/* Message content */}
        <p className="whitespace-pre-wrap break-words text-sm leading-relaxed">
          {message.content}
        </p>

        {/* Timestamp */}
        <div
          className={`mt-1 text-xs ${
            isUser ? 'text-blue-200' : 'text-gray-500'
          } flex items-center gap-2`}
        >
          <span>{formatTimestamp(message.created_at)}</span>
          {isPending && (
            <span className="flex items-center gap-1">
              <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Sending...
            </span>
          )}
        </div>

        {/* Error state with retry */}
        {hasError && (
          <div className="mt-2 pt-2 border-t border-red-200">
            <p className="text-xs text-red-600 mb-1">
              {message.error || 'Failed to send message'}
            </p>
            {onRetry && (
              <button
                onClick={() => onRetry(message.id)}
                className="text-xs text-red-600 hover:text-red-700 underline font-medium"
              >
                Retry
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
