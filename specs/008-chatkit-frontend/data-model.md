# Data Model: ChatKit Frontend

## Overview

Frontend TypeScript interfaces for the chat UI. These map to backend Pydantic models.

## Core Types

### ChatMessage (Frontend Display)

```typescript
interface ChatMessage {
  id: string;                    // UUID from backend
  role: 'user' | 'assistant';    // Message author
  content: string;               // Message text
  created_at: string;            // ISO timestamp
  status: 'pending' | 'sent' | 'error';  // Local state for optimistic UI
  error?: string;                // Error message if status === 'error'
}
```

### ToolCallInfo (AI Action Display)

```typescript
interface ToolCallInfo {
  name: string;           // Tool name (e.g., 'add_task', 'list_tasks')
  arguments: Record<string, any>;  // Tool parameters
  result: string;         // Tool execution result
  duration_ms: number;    // Execution time
}
```

### API Request/Response Types

```typescript
// Request to POST /api/{user_id}/chat
interface ChatRequest {
  message: string;  // 1-16000 characters
}

// Response from POST /api/{user_id}/chat
interface ChatResponse {
  user_message: {
    id: string;
    conversation_id: string;
    role: 'user';
    content: string;
    created_at: string;
  };
  assistant_message: {
    id: string;
    conversation_id: string;
    role: 'assistant';
    content: string;
    created_at: string;
  };
  tool_calls?: ToolCallInfo[];
}
```

### Conversation Types

```typescript
// Response from GET /api/conversations
interface Conversation {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

// Response from GET /api/conversations/{id}/messages
interface MessageListResponse {
  messages: Array<{
    id: string;
    conversation_id: string;
    role: 'user' | 'assistant';
    content: string;
    created_at: string;
  }>;
}
```

## Component State Types

### ChatContainer State

```typescript
interface ChatState {
  messages: ChatMessage[];        // All messages in conversation
  isLoading: boolean;             // AI is processing
  isSending: boolean;             // Message being sent
  isLoadingHistory: boolean;      // Initial history load
  error: string | null;           // Global error message
  conversationId: string | null;  // Current conversation ID
}
```

### ChatInput State

```typescript
interface ChatInputState {
  message: string;          // Current input value
  isValid: boolean;         // 1-16000 characters
  charCount: number;        // For display
}
```

## State Transitions

### Message Send Flow

```text
1. User types message
   └─► ChatInput.message = "Add a task to buy groceries"

2. User presses Enter
   └─► ChatContainer adds optimistic message:
       { id: temp-uuid, role: 'user', content: '...', status: 'pending' }
   └─► ChatContainer.isSending = true
   └─► ChatInput.message = '' (cleared)

3. API call succeeds
   └─► Replace optimistic message with server response
   └─► Add assistant message
   └─► ChatContainer.isSending = false

4. API call fails
   └─► Update optimistic message: status = 'error', error = 'message'
   └─► ChatContainer.isSending = false
```

### History Load Flow

```text
1. ChatContainer mounts
   └─► ChatContainer.isLoadingHistory = true

2. Fetch conversations
   └─► If conversation exists: fetch messages
   └─► If no conversation: show empty state

3. Load complete
   └─► ChatContainer.messages = [...history]
   └─► ChatContainer.isLoadingHistory = false
```

## Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| message | Min 1 character | "Message cannot be empty" |
| message | Max 16000 characters | "Message is too long (max 16000 characters)" |
| message | Non-whitespace only | "Message cannot be blank" |

## Entity Relationships

```text
User (from Better Auth)
  └── has one Conversation (auto-created)
        └── has many Messages (ordered by created_at)
```

Note: The backend enforces single conversation per user. The frontend doesn't need to manage multiple conversations.
