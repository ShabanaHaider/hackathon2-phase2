# Research: ChatKit Frontend Integration

## Overview

Research findings for implementing the chat UI frontend that integrates with the stateless chat API (Spec 007).

## Design Decisions

### 1. Component Architecture

**Decision**: Create 5 focused chat components instead of a single monolithic component

**Rationale**:
- Separation of concerns (input, display, state management)
- Easier testing and maintenance
- Reusable message components
- Follows existing codebase patterns (TaskList, TaskItem, TaskForm)

**Alternatives Considered**:
- Single ChatWidget component: Rejected due to complexity and lack of reusability
- Third-party chat library: Rejected to maintain consistency with existing Tailwind styling

### 2. State Management

**Decision**: Use React useState hooks for local chat state

**Rationale**:
- Chat state is localized to the chat component tree
- No cross-component communication needed
- Simpler than adding Redux/Zustand for single feature
- Consistent with existing task components (TaskList uses useState)

**Alternatives Considered**:
- React Context: Overkill for single-conversation model
- Redux/Zustand: Adds unnecessary dependency
- jotai/recoil: Same as above

### 3. History Loading Strategy

**Decision**: Load conversation history on ChatContainer mount

**Rationale**:
- Backend already provides GET /api/conversations and GET /api/conversations/{id}/messages
- Single conversation per user simplifies logic
- No need for pagination initially (load last 20 messages)

**Alternatives Considered**:
- Lazy load on scroll: Premature optimization
- LocalStorage cache: Adds complexity; backend is source of truth

### 4. JWT Token Retrieval

**Decision**: Use Better Auth client's session to get JWT for API calls

**Rationale**:
- Better Auth already provides JWT plugin
- Token automatically included in session
- Consistent with existing API call patterns

**Implementation**:
```typescript
// Get JWT from Better Auth
const session = await authClient.getSession();
const token = session?.session?.accessToken;

// Include in fetch
fetch(`${API_URL}/api/${userId}/chat`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### 5. Optimistic UI

**Decision**: Show user message immediately before API response

**Rationale**:
- Better perceived performance
- User sees their message instantly
- Matches modern chat UX expectations

**Implementation**:
- Add message to local state with pending flag
- On success: Update with server response
- On error: Mark message as failed, show retry

### 6. Error Handling Pattern

**Decision**: Inline error display with retry capability

**Rationale**:
- User can see which message failed
- Retry preserves original message
- Non-blocking (user can still type new messages)

**Error States**:
| Error | User Message | Action |
|-------|-------------|--------|
| Network offline | "You're offline. Message will send when connected." | Auto-retry on reconnect |
| 401 Unauthorized | "Session expired. Please sign in again." | Redirect to /signin |
| 500 Server Error | "Something went wrong. Please try again." | Retry button |
| Timeout (>10s) | "AI is taking longer than usual..." | Continue waiting / Cancel |

### 7. Keyboard Shortcuts

**Decision**: Enter to send, Shift+Enter for newline

**Rationale**:
- Standard chat convention (Slack, Discord, WhatsApp Web)
- Familiar to users
- Easy to implement with onKeyDown handler

### 8. Responsive Layout

**Decision**: Chat panel alongside task list on desktop, stacked on mobile

**Rationale**:
- Users can see tasks while chatting
- Mobile: Full-width chat when focused
- Consistent with existing responsive patterns

**Layout Options**:
- Desktop (>1024px): Side-by-side layout
- Tablet (768-1024px): Collapsible chat panel
- Mobile (<768px): Tabbed or stacked view

## Existing Code Analysis

### Frontend Patterns to Follow

1. **Component Structure**: `frontend/src/components/` - Each component in its own file
2. **Auth Client**: `lib/auth-client.ts` - `useSession()` hook for auth state
3. **API Base URL**: Environment variable `NEXT_PUBLIC_API_URL` or localhost:8000
4. **Styling**: Tailwind CSS with gray color palette
5. **Loading States**: Spinner SVG pattern from `page.tsx`

### Backend API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/{user_id}/chat` | POST | Send message, get AI response |
| `/api/conversations` | GET | List user's conversations |
| `/api/conversations/{id}/messages` | GET | Get messages for history |

### Response Schemas

```typescript
// POST /api/{user_id}/chat response
interface UserChatResponse {
  user_message: MessageResponse;
  assistant_message: MessageResponse;
  tool_calls?: ToolCallInfo[];
}

interface MessageResponse {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface ToolCallInfo {
  name: string;
  arguments: Record<string, any>;
  result: string;
  duration_ms: number;
}
```

## No Outstanding Clarifications

All technical decisions are resolved. Implementation can proceed with:
- 5 new components
- 1 modified page (page.tsx)
- 1 modified lib file (api.ts or new chat-api.ts)
