/**
 * Chat API client for frontend
 * Communicates with backend POST /api/{user_id}/chat endpoint (Spec 007)
 */

import type {
  ChatResponse,
  Conversation,
  MessageResponse,
} from '@/types/chat';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

async function getFreshToken(): Promise<string | null> {
  try {
    const response = await fetch('/api/auth/token', {
      method: 'GET',
      credentials: 'include',
    });
    if (response.ok) {
      const data = await response.json();
      return data?.token || null;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Custom error class for chat API errors
 */
export class ChatError extends Error {
  constructor(
    public status: number,
    public detail: string | { error: string; message: string; user_message?: unknown }
  ) {
    super(typeof detail === 'string' ? detail : detail.message);
    this.name = 'ChatError';
  }

  get isAuthError(): boolean {
    return this.status === 401;
  }

  get isForbidden(): boolean {
    return this.status === 403;
  }

  get isServerError(): boolean {
    return this.status >= 500;
  }

  get userMessage(): string {
    if (this.isAuthError) {
      return 'Your session has expired. Please sign in again.';
    }
    if (this.isForbidden) {
      return 'You do not have permission to access this chat.';
    }
    if (this.isServerError) {
      return 'Something went wrong. Please try again.';
    }
    return typeof this.detail === 'string'
      ? this.detail
      : this.detail.message || 'An error occurred.';
  }
}

/**
 * Send a message to the AI assistant
 * POST /api/{user_id}/chat
 */
export async function sendChatMessage(
  userId: string,
  message: string,
  _token?: string
): Promise<ChatResponse> {
  const freshToken = await getFreshToken();
  if (!freshToken) {
    throw new ChatError(401, 'Not authenticated');
  }
  const response = await fetch(`${API_URL}/api/${userId}/chat`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${freshToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ChatError(response.status, error.detail || error);
  }

  return response.json();
}

/**
 * Get all conversations for the current user
 * GET /api/conversations
 */
export async function getConversations(_token?: string): Promise<Conversation[]> {
  const freshToken = await getFreshToken();
  if (!freshToken) {
    throw new ChatError(401, 'Not authenticated');
  }
  const response = await fetch(`${API_URL}/api/conversations`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${freshToken}`,
    },
  });

  if (!response.ok) {
    throw new ChatError(response.status, 'Failed to load conversations');
  }

  return response.json();
}

/**
 * Get messages for a specific conversation
 * GET /api/conversations/{id}/messages
 */
export async function getMessages(
  conversationId: string,
  _token?: string
): Promise<MessageResponse[]> {
  const freshToken = await getFreshToken();
  if (!freshToken) {
    throw new ChatError(401, 'Not authenticated');
  }
  const response = await fetch(
    `${API_URL}/api/conversations/${conversationId}/messages`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${freshToken}`,
      },
    }
  );

  if (!response.ok) {
    throw new ChatError(response.status, 'Failed to load messages');
  }

  return response.json();
}
