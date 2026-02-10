# Implementation Plan: ChatKit Frontend Integration

**Branch**: `008-chatkit-frontend` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-chatkit-frontend/spec.md`

## Summary

Add a conversational chat UI to the Next.js frontend that integrates with the stateless chat API (Spec 007). Users can send messages to an AI assistant to manage their todos, with conversation history persisting across browser sessions via the backend API.

## Technical Context

**Language/Version**: TypeScript 5.x, Next.js 16+ (App Router)
**Primary Dependencies**: React 18+, Better Auth client, Tailwind CSS
**Storage**: Backend REST API (no client-side persistence needed)
**Testing**: Manual verification per project convention
**Target Platform**: Web browsers (desktop and mobile responsive)
**Project Type**: Web application (frontend modification only)
**Performance Goals**: 5s response time for AI replies, 2s history load
**Constraints**: REST-based communication, JWT auth, optimistic UI
**Scale/Scope**: Single conversation per user, last 20 messages loaded

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. End-to-End Correctness | ✅ PASS | Frontend will integrate with existing Spec 007 backend API |
| II. User Data Isolation | ✅ PASS | JWT auth already enforced; user_id in API calls |
| III. Spec-Driven Development | ✅ PASS | This plan follows spec.md |
| IV. Framework-Idiomatic | ✅ PASS | Using React hooks, client components for interactivity |
| V. RESTful API Design | ✅ PASS | Using existing POST /api/{user_id}/chat endpoint |
| VI. Environment-Based Secrets | ✅ PASS | No new secrets needed; uses existing auth |
| VII. Agentic AI Architecture | ✅ N/A | Frontend only; agent logic in backend |
| VIII. Stateless AI Interactions | ✅ PASS | History loaded from backend on each visit |

**Gate Result**: PASS - All applicable principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/008-chatkit-frontend/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chat-api.md      # Frontend API client contract
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   └── page.tsx              # Modified: Add chat interface
│   ├── components/
│   │   ├── ChatContainer.tsx     # New: Main chat wrapper
│   │   ├── ChatMessageList.tsx   # New: Message display area
│   │   ├── ChatMessage.tsx       # New: Individual message bubble
│   │   ├── ChatInput.tsx         # New: Message input form
│   │   └── ChatEmptyState.tsx    # New: Welcome state for new users
│   └── lib/
│       └── api.ts                # Modified: Add chat API functions
└── ...
```

**Structure Decision**: Extend existing frontend structure with new chat components. No new pages needed - chat integrates into main dashboard.

## Implementation Phases

### Phase 1: Core Chat Components (P1 - US1: Send Message)

**Goal**: User can send a message and receive an AI response

1. Create `ChatInput.tsx` - Text input with send button
   - Controlled input with message state
   - Enter to send, Shift+Enter for newline
   - Disable send on empty input
   - Validation for 1-16000 characters

2. Create `ChatMessage.tsx` - Individual message bubble
   - Visual distinction: user (right, blue) vs assistant (left, gray)
   - Display timestamp
   - Role-based styling

3. Create `ChatMessageList.tsx` - Scrollable message container
   - Auto-scroll to bottom on new messages
   - Loading indicator during AI response

4. Create `ChatContainer.tsx` - Orchestrator component
   - State: messages, isLoading, error
   - Send message handler (POST /api/{user_id}/chat)
   - Optimistic UI: show user message immediately

5. Add chat API function to `lib/api.ts`
   - `sendChatMessage(userId, message, token)` → UserChatResponse
   - Include Authorization header with JWT

6. Integrate into `page.tsx`
   - Add ChatContainer to AuthenticatedDashboard
   - Pass user.id for API calls

### Phase 2: Conversation History (P1 - US2: Resume Context)

**Goal**: User sees previous messages when returning

1. Add history loading to `ChatContainer.tsx`
   - Fetch messages on mount: GET /api/conversations (to find conversation)
   - Then GET /api/conversations/{id}/messages
   - Or: Load from first chat response (auto-created conversation)

2. Create `ChatEmptyState.tsx` - First-time user experience
   - Welcome message
   - Suggested actions ("Try saying: Add a task to buy groceries")

3. Update `ChatMessageList.tsx`
   - Handle initial loading state
   - Display history in chronological order

### Phase 3: Error Handling (P2 - US3: Handle Errors)

**Goal**: User sees friendly errors and can retry

1. Add error state to `ChatContainer.tsx`
   - Catch API errors
   - Parse error response for user message preservation

2. Create error display in `ChatMessageList.tsx`
   - Inline error messages below failed message
   - Retry button

3. Handle edge cases:
   - Network offline: Show offline indicator
   - 401 Unauthorized: Redirect to signin
   - 500 Server Error: Show retry option
   - Long response (>10s): Show "still thinking" indicator

### Phase 4: Authentication Integration (P2 - US4)

**Goal**: Chat protected by authentication

1. Verify auth flow in `ChatContainer.tsx`
   - Get JWT token from Better Auth client
   - Include in API requests

2. Handle session expiry
   - Catch 401 responses
   - Preserve draft message in localStorage
   - Redirect to signin

### Phase 5: Polish & UX

**Goal**: Smooth user experience

1. Keyboard shortcuts
   - Enter to send
   - Shift+Enter for newline

2. Responsive design
   - Mobile-friendly layout
   - Collapsible chat on small screens (optional)

3. Loading states
   - Typing indicator animation
   - Skeleton loading for history

4. Scroll behavior
   - Auto-scroll on new messages
   - Scroll to bottom button if user scrolled up

## Complexity Tracking

> No violations detected - implementation uses standard React patterns

| Aspect | Approach | Justification |
|--------|----------|---------------|
| State Management | useState hooks | Simple chat state; no global state needed |
| API Calls | fetch with async/await | Standard pattern; no extra libraries |
| UI Components | Tailwind CSS | Consistent with existing app |

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| UX confusion | Clear message distinction (user vs AI), loading indicators |
| Error opacity | User-friendly error messages, retry option |
| Auth complexity | Leverage existing Better Auth integration |
| Long AI responses | Loading indicator with "still thinking" after 5s |

## Dependencies

- **Spec 007**: Stateless Chat API (POST /api/{user_id}/chat) - COMPLETE
- **Spec 004**: Conversation/Message persistence - COMPLETE
- **Spec 002**: Better Auth JWT integration - COMPLETE
- **Spec 003**: Frontend foundation (Next.js, Tailwind) - COMPLETE

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement Phase 1-5 sequentially
3. Manual testing per quickstart.md
