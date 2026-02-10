"use client";

import { useState, useCallback, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const MAX_MESSAGE_LENGTH = 16000;
const MIN_MESSAGE_LENGTH = 1;

export default function ChatInput({ onSend, disabled = false, placeholder = "Type a message..." }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const trimmedMessage = message.trim();
  const isValid = trimmedMessage.length >= MIN_MESSAGE_LENGTH && trimmedMessage.length <= MAX_MESSAGE_LENGTH;
  const isTooLong = message.length > MAX_MESSAGE_LENGTH;
  const charCount = message.length;

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [message]);

  // Restore draft from localStorage on mount
  useEffect(() => {
    const draft = localStorage.getItem('chat-draft');
    if (draft) {
      setMessage(draft);
      localStorage.removeItem('chat-draft');
    }
  }, []);

  const handleSend = useCallback(() => {
    if (!isValid || disabled) return;
    onSend(trimmedMessage);
    setMessage('');
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [isValid, disabled, trimmedMessage, onSend]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Enter to send, Shift+Enter for newline
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
  }, []);

  // Save draft to localStorage when component unmounts or before unload
  useEffect(() => {
    const saveDraft = () => {
      if (message.trim()) {
        localStorage.setItem('chat-draft', message);
      }
    };

    window.addEventListener('beforeunload', saveDraft);
    return () => {
      window.removeEventListener('beforeunload', saveDraft);
    };
  }, [message]);

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="flex gap-3 items-end">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={`w-full resize-none rounded-xl border px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${
              isTooLong
                ? 'border-red-300 focus:ring-red-500'
                : 'border-gray-300'
            } ${disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-white'}`}
            style={{ minHeight: '44px', maxHeight: '150px' }}
          />

          {/* Character count */}
          <div className={`absolute bottom-1 right-3 text-xs ${
            isTooLong ? 'text-red-500' : 'text-gray-400'
          }`}>
            {charCount > 0 && (
              <span>
                {charCount.toLocaleString()}/{MAX_MESSAGE_LENGTH.toLocaleString()}
              </span>
            )}
          </div>
        </div>

        <button
          onClick={handleSend}
          disabled={!isValid || disabled}
          className={`flex-shrink-0 rounded-xl px-4 py-3 font-medium text-sm transition-all ${
            isValid && !disabled
              ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
          }`}
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </div>

      {/* Validation error */}
      {isTooLong && (
        <p className="mt-2 text-xs text-red-500">
          Message is too long (max {MAX_MESSAGE_LENGTH.toLocaleString()} characters)
        </p>
      )}
    </div>
  );
}
