"use client";

import { useRef, useEffect, useState } from 'react';
import type { ChatMessage as ChatMessageType } from '@/types/chat';
import ChatMessage from './ChatMessage';

interface ChatMessageListProps {
  messages: ChatMessageType[];
  isLoading?: boolean;
  isLoadingHistory?: boolean;
  onRetry?: (messageId: string) => void;
}

function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
}

function SkeletonLoader() {
  return (
    <div className="space-y-4 animate-pulse">
      {/* User message skeleton */}
      <div className="flex justify-end">
        <div className="bg-blue-200 rounded-2xl rounded-br-md px-4 py-3 w-2/3">
          <div className="h-4 bg-blue-300 rounded w-full mb-2" />
          <div className="h-3 bg-blue-300 rounded w-1/4" />
        </div>
      </div>
      {/* Assistant message skeleton */}
      <div className="flex justify-start">
        <div className="bg-gray-200 rounded-2xl rounded-bl-md px-4 py-3 w-3/4">
          <div className="h-4 bg-gray-300 rounded w-full mb-2" />
          <div className="h-4 bg-gray-300 rounded w-2/3 mb-2" />
          <div className="h-3 bg-gray-300 rounded w-1/4" />
        </div>
      </div>
    </div>
  );
}

export default function ChatMessageList({
  messages,
  isLoading = false,
  isLoadingHistory = false,
  onRetry,
}: ChatMessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [userScrolled, setUserScrolled] = useState(false);

  // Auto-scroll to bottom when new messages arrive (if user hasn't scrolled up)
  useEffect(() => {
    if (containerRef.current && !userScrolled) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages, isLoading, userScrolled]);

  // Track if user has scrolled up
  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
    setUserScrolled(!isNearBottom);
    setShowScrollButton(!isNearBottom && messages.length > 3);
  };

  const scrollToBottom = () => {
    if (containerRef.current) {
      containerRef.current.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior: 'smooth',
      });
      setUserScrolled(false);
    }
  };

  if (isLoadingHistory) {
    return (
      <div className="flex-1 overflow-y-auto p-4">
        <SkeletonLoader />
      </div>
    );
  }

  return (
    <div className="relative flex-1">
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="absolute inset-0 overflow-y-auto p-4"
      >
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            onRetry={onRetry}
          />
        ))}

        {isLoading && <TypingIndicator />}
      </div>

      {/* Scroll to bottom button */}
      {showScrollButton && (
        <button
          onClick={scrollToBottom}
          className="absolute bottom-4 right-4 bg-white border border-gray-200 rounded-full p-2 shadow-lg hover:shadow-xl transition-all"
        >
          <svg
            className="w-5 h-5 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
        </button>
      )}
    </div>
  );
}
