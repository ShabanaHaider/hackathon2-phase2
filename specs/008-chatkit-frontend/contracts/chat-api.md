# Frontend Chat API Client Contract

## Overview

API functions for the chat UI to communicate with the backend.

## Environment

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

## Functions

### sendChatMessage

Send a message to the AI assistant.

```typescript
async function sendChatMessage(
  userId: string,
  message: string,
  token: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/${userId}/chat`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ChatError(response.status, error.detail);
  }

  return response.json();
}
```

**Parameters**:
| Name | Type | Description |
|------|------|-------------|
| userId | string | Authenticated user's ID |
| message | string | User's message (1-16000 chars) |
| token | string | JWT access token |

**Returns**: `ChatResponse`

**Errors**:
| Status | Meaning | Action |
|--------|---------|--------|
| 401 | Unauthorized | Redirect to signin |
| 403 | User ID mismatch | Show error |
| 422 | Validation error | Show error |
| 500 | Server error | Show retry |

---

### getConversations

Get user's conversations to find existing chat.

```typescript
async function getConversations(token: string): Promise<Conversation[]> {
  const response = await fetch(`${API_URL}/api/conversations`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new ChatError(response.status, 'Failed to load conversations');
  }

  return response.json();
}
```

---

### getMessages

Get messages for a conversation (for history loading).

```typescript
async function getMessages(
  conversationId: string,
  token: string
): Promise<MessageResponse[]> {
  const response = await fetch(
    `${API_URL}/api/conversations/${conversationId}/messages`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new ChatError(response.status, 'Failed to load messages');
  }

  return response.json();
}
```

---

## Error Handling

### ChatError Class

```typescript
class ChatError extends Error {
  constructor(
    public status: number,
    public detail: string | { error: string; message: string }
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
```

---

## Token Retrieval

Get JWT token from Better Auth client:

```typescript
import { authClient } from '@/lib/auth-client';

async function getToken(): Promise<string | null> {
  // Option 1: Get from session
  const session = await authClient.getSession();

  // The JWT token may be in different places depending on Better Auth config
  // Check the session object structure
  return session?.token || session?.session?.accessToken || null;
}

// Alternative: Use the jwtClient plugin
import { jwtClient } from 'better-auth/client/plugins';

// The token should be available after sign-in
// May need to call authClient.$fetch with credentials: 'include'
```

**Note**: The exact token location depends on Better Auth configuration. Verify during implementation.

---

## Usage Example

```typescript
import { useSession } from '@/lib/auth-client';
import { sendChatMessage, ChatError } from '@/lib/chat-api';

function useChatSend() {
  const { data: session } = useSession();

  const sendMessage = async (message: string) => {
    if (!session?.user?.id) {
      throw new Error('Not authenticated');
    }

    // Get token (implementation depends on Better Auth setup)
    const token = await getToken();
    if (!token) {
      throw new ChatError(401, 'No authentication token');
    }

    try {
      const response = await sendChatMessage(
        session.user.id,
        message,
        token
      );
      return response;
    } catch (error) {
      if (error instanceof ChatError && error.isAuthError) {
        // Handle redirect to signin
        window.location.href = '/signin';
      }
      throw error;
    }
  };

  return { sendMessage };
}
```

---

## Type Definitions

```typescript
// types/chat.ts

export interface ChatResponse {
  user_message: MessageResponse;
  assistant_message: MessageResponse;
  tool_calls?: ToolCallInfo[];
}

export interface MessageResponse {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface ToolCallInfo {
  name: string;
  arguments: Record<string, unknown>;
  result: string;
  duration_ms: number;
}

export interface Conversation {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}
```
