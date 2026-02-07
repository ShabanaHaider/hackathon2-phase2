"use client";

import { useState, useCallback, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import type { ChatMessage } from '@/types/chat';
import { sendChatMessage, getConversations, getMessages, ChatError } from '@/lib/chat-api';
import ChatMessageList from './ChatMessageList';
import ChatInput from './ChatInput';
import ChatEmptyState from './ChatEmptyState';

interface ChatContainerProps {
  userId: string;
  token: string;
}

export default function ChatContainer({ userId, token }: ChatContainerProps) {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState(false);
  const stillThinkingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [isStillThinking, setIsStillThinking] = useState(false);

  // Track online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Check initial status
    setIsOffline(!navigator.onLine);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Load conversation history on mount
  useEffect(() => {
    async function loadHistory() {
      try {
        setIsLoadingHistory(true);
        setError(null);

        // Get user's conversations
        const conversations = await getConversations(token);

        if (conversations.length > 0) {
          // Load messages from the first (most recent) conversation
          const conversationId = conversations[0].id;
          const historyMessages = await getMessages(conversationId, token);

          // Convert to ChatMessage format
          const chatMessages: ChatMessage[] = historyMessages.map((msg) => ({
            id: msg.id,
            role: msg.role as 'user' | 'assistant',
            content: msg.content,
            created_at: msg.created_at,
            status: 'sent' as const,
          }));

          setMessages(chatMessages);
        }
      } catch (err) {
        if (err instanceof ChatError) {
          if (err.isAuthError) {
            router.push('/signin');
            return;
          }
          // 404 is ok - means no conversation yet
          if (err.status !== 404) {
            setError(err.userMessage);
          }
        } else {
          console.error('Failed to load history:', err);
        }
      } finally {
        setIsLoadingHistory(false);
      }
    }

    if (userId && token) {
      loadHistory();
    }
  }, [userId, token, router]);

  // Handle sending a message
  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading || isOffline) return;

      // Clear any previous errors
      setError(null);

      // Create optimistic message
      const tempId = `temp-${Date.now()}`;
      const optimisticMessage: ChatMessage = {
        id: tempId,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
        status: 'pending',
      };

      // Add to messages immediately (optimistic UI)
      setMessages((prev) => [...prev, optimisticMessage]);
      setIsLoading(true);
      setIsStillThinking(false);

      // Set up "still thinking" timeout
      stillThinkingTimeoutRef.current = setTimeout(() => {
        setIsStillThinking(true);
      }, 10000);

      try {
        const response = await sendChatMessage(userId, content, token);

        // Clear timeout
        if (stillThinkingTimeoutRef.current) {
          clearTimeout(stillThinkingTimeoutRef.current);
        }

        // Update the optimistic message with real data and add assistant response
        setMessages((prev) => {
          const updated = prev.map((msg) =>
            msg.id === tempId
              ? {
                  ...msg,
                  id: response.user_message.id,
                  created_at: response.user_message.created_at,
                  status: 'sent' as const,
                }
              : msg
          );

          // Add assistant message
          const assistantMessage: ChatMessage = {
            id: response.assistant_message.id,
            role: 'assistant',
            content: response.assistant_message.content,
            created_at: response.assistant_message.created_at,
            status: 'sent',
          };

          return [...updated, assistantMessage];
        });
      } catch (err) {
        // Clear timeout
        if (stillThinkingTimeoutRef.current) {
          clearTimeout(stillThinkingTimeoutRef.current);
        }

        if (err instanceof ChatError) {
          if (err.isAuthError) {
            // Save draft before redirecting
            localStorage.setItem('chat-draft', content);
            router.push('/signin');
            return;
          }

          // Mark message as failed
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === tempId
                ? { ...msg, status: 'error' as const, error: err.userMessage }
                : msg
            )
          );
          setError(err.userMessage);
        } else {
          // Unknown error
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === tempId
                ? { ...msg, status: 'error' as const, error: 'Failed to send message' }
                : msg
            )
          );
          setError('Something went wrong. Please try again.');
        }
      } finally {
        setIsLoading(false);
        setIsStillThinking(false);
      }
    },
    [userId, token, isLoading, isOffline, router]
  );

  // Handle retry for failed messages
  const handleRetry = useCallback(
    (messageId: string) => {
      const failedMessage = messages.find((m) => m.id === messageId);
      if (failedMessage) {
        // Remove the failed message
        setMessages((prev) => prev.filter((m) => m.id !== messageId));
        // Resend
        handleSendMessage(failedMessage.content);
      }
    },
    [messages, handleSendMessage]
  );

  // Handle suggested prompt click
  const handleSuggestedPrompt = useCallback(
    (prompt: string) => {
      handleSendMessage(prompt);
    },
    [handleSendMessage]
  );

  const showEmptyState = !isLoadingHistory && messages.length === 0;

  return (
    <div className="flex flex-col h-[500px] md:h-[600px] bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <svg
              className="w-4 h-4 text-white"
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
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Task Assistant</h3>
            <p className="text-xs text-gray-500">
              {isOffline ? (
                <span className="text-orange-500">Offline</span>
              ) : isLoading ? (
                isStillThinking ? (
                  <span className="text-blue-500">Still thinking...</span>
                ) : (
                  <span className="text-blue-500">Thinking...</span>
                )
              ) : (
                'Online'
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Global error banner */}
      {error && !messages.some((m) => m.status === 'error') && (
        <div className="flex-shrink-0 px-4 py-2 bg-red-50 border-b border-red-100">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Offline banner */}
      {isOffline && (
        <div className="flex-shrink-0 px-4 py-2 bg-orange-50 border-b border-orange-100">
          <p className="text-sm text-orange-600">
            You're offline. Messages will send when you're back online.
          </p>
        </div>
      )}

      {/* Messages area */}
      {showEmptyState ? (
        <ChatEmptyState onSuggestedPrompt={handleSuggestedPrompt} />
      ) : (
        <ChatMessageList
          messages={messages}
          isLoading={isLoading}
          isLoadingHistory={isLoadingHistory}
          onRetry={handleRetry}
        />
      )}

      {/* Input area */}
      <ChatInput
        onSend={handleSendMessage}
        disabled={isLoading || isOffline}
        placeholder={isOffline ? "You're offline..." : "Type a message..."}
      />
    </div>
  );
}
