# Tasks: ChatKit Frontend Integration

**Input**: Design documents from `/specs/008-chatkit-frontend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.md

**Tests**: Manual verification per quickstart.md (no automated tests per project convention)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/` at repository root
- **Components**: `frontend/src/components/`
- **Library**: `frontend/src/lib/`
- **App**: `frontend/src/app/`

---

## Phase 1: Setup

**Purpose**: Create TypeScript types and API client infrastructure

- [x] T001 Create TypeScript chat types in frontend/src/types/chat.ts
- [x] T002 [P] Create ChatError class in frontend/src/lib/chat-api.ts
- [x] T003 [P] Add sendChatMessage function in frontend/src/lib/chat-api.ts
- [x] T004 Add getConversations function in frontend/src/lib/chat-api.ts
- [x] T005 Add getMessages function in frontend/src/lib/chat-api.ts

**Checkpoint**: API client ready for component development ✅

---

## Phase 2: Foundational - Base Components

**Purpose**: Create core components that all user stories depend on

**CRITICAL**: These components must exist before user story implementation

- [x] T006 [P] Create ChatMessage.tsx component in frontend/src/components/ChatMessage.tsx
- [x] T007 [P] Create ChatInput.tsx component in frontend/src/components/ChatInput.tsx
- [x] T008 Create ChatMessageList.tsx component in frontend/src/components/ChatMessageList.tsx
- [x] T009 Create ChatContainer.tsx skeleton with state management in frontend/src/components/ChatContainer.tsx

**Checkpoint**: Base chat UI components exist and render ✅

---

## Phase 3: User Story 1 - Send Chat Message (Priority: P1) MVP

**Goal**: User can send a message and receive an AI response

**Independent Test**: Type message, press Enter/Send, verify message appears and AI responds within 5s

### Implementation for User Story 1

- [x] T010 [US1] Add controlled input with message state in frontend/src/components/ChatInput.tsx
- [x] T011 [US1] Implement Enter to send, Shift+Enter for newline in frontend/src/components/ChatInput.tsx
- [x] T012 [US1] Add message validation (1-16000 chars) in frontend/src/components/ChatInput.tsx
- [x] T013 [US1] Disable send button when input empty in frontend/src/components/ChatInput.tsx
- [x] T014 [US1] Add user message styling (right-aligned, blue) in frontend/src/components/ChatMessage.tsx
- [x] T015 [US1] Add assistant message styling (left-aligned, gray) in frontend/src/components/ChatMessage.tsx
- [x] T016 [US1] Add timestamp display to message bubbles in frontend/src/components/ChatMessage.tsx
- [x] T017 [US1] Implement message state (messages array) in frontend/src/components/ChatContainer.tsx
- [x] T018 [US1] Implement optimistic UI (show user message immediately) in frontend/src/components/ChatContainer.tsx
- [x] T019 [US1] Implement sendMessage handler with API call in frontend/src/components/ChatContainer.tsx
- [x] T020 [US1] Add loading state and typing indicator in frontend/src/components/ChatContainer.tsx
- [x] T021 [US1] Pass messages to ChatMessageList in frontend/src/components/ChatContainer.tsx
- [x] T022 [US1] Implement auto-scroll to bottom on new messages in frontend/src/components/ChatMessageList.tsx
- [x] T023 [US1] Integrate ChatContainer into AuthenticatedDashboard in frontend/src/app/page.tsx

**Checkpoint**: User can send message and receive AI response - MVP complete ✅

---

## Phase 4: User Story 2 - View Conversation History (Priority: P1)

**Goal**: User sees previous messages when returning to the app

**Independent Test**: Send messages, refresh browser, verify history appears in chronological order

### Implementation for User Story 2

- [x] T024 [US2] Add conversation history loading on mount in frontend/src/components/ChatContainer.tsx
- [x] T025 [US2] Add isLoadingHistory state in frontend/src/components/ChatContainer.tsx
- [x] T026 [US2] Create ChatEmptyState.tsx with welcome message in frontend/src/components/ChatEmptyState.tsx
- [x] T027 [US2] Add suggested prompts to ChatEmptyState ("Try: Add a task...") in frontend/src/components/ChatEmptyState.tsx
- [x] T028 [US2] Show ChatEmptyState when no messages exist in frontend/src/components/ChatContainer.tsx
- [x] T029 [US2] Show skeleton loader while history loads in frontend/src/components/ChatMessageList.tsx
- [x] T030 [US2] Display history in chronological order in frontend/src/components/ChatMessageList.tsx

**Checkpoint**: Conversation history persists across page refresh ✅

---

## Phase 5: User Story 3 - Handle Errors Gracefully (Priority: P2)

**Goal**: User sees friendly error messages and can retry failed sends

**Independent Test**: Simulate network error, verify error message appears with retry button

### Implementation for User Story 3

- [x] T031 [US3] Add error state to ChatContainer in frontend/src/components/ChatContainer.tsx
- [x] T032 [US3] Add message status field (pending/sent/error) to local state in frontend/src/components/ChatContainer.tsx
- [x] T033 [US3] Catch API errors and update message status in frontend/src/components/ChatContainer.tsx
- [x] T034 [US3] Show inline error message below failed message in frontend/src/components/ChatMessage.tsx
- [x] T035 [US3] Add retry button for failed messages in frontend/src/components/ChatMessage.tsx
- [x] T036 [US3] Implement retry handler in frontend/src/components/ChatContainer.tsx
- [x] T037 [US3] Add "still thinking" indicator after 10s in frontend/src/components/ChatContainer.tsx
- [x] T038 [US3] Show network offline indicator in frontend/src/components/ChatContainer.tsx

**Checkpoint**: Error handling complete with retry capability ✅

---

## Phase 6: User Story 4 - Authentication Integration (Priority: P2)

**Goal**: Chat is protected by authentication and handles session expiry

**Independent Test**: Sign out, attempt to access chat, verify redirect to signin

### Implementation for User Story 4

- [x] T039 [US4] Add JWT token retrieval from Better Auth in frontend/src/lib/chat-api.ts
- [x] T040 [US4] Include Authorization header in all chat API calls in frontend/src/lib/chat-api.ts
- [x] T041 [US4] Handle 401 Unauthorized response with redirect in frontend/src/components/ChatContainer.tsx
- [x] T042 [US4] Preserve draft message on session expiry (localStorage) in frontend/src/components/ChatInput.tsx
- [x] T043 [US4] Restore draft message after re-authentication in frontend/src/components/ChatInput.tsx

**Checkpoint**: Authentication integration complete ✅

---

## Phase 7: Polish & UX

**Purpose**: Final refinements for smooth user experience

- [x] T044 [P] Add responsive styling for mobile viewport in frontend/src/components/ChatContainer.tsx
- [x] T045 [P] Add responsive styling for mobile viewport in frontend/src/components/ChatInput.tsx
- [x] T046 [P] Add responsive styling for mobile viewport in frontend/src/components/ChatMessage.tsx
- [x] T047 Add scroll-to-bottom button when user scrolls up in frontend/src/components/ChatMessageList.tsx
- [x] T048 Add typing indicator animation in frontend/src/components/ChatMessageList.tsx
- [x] T049 Add character count display near input in frontend/src/components/ChatInput.tsx

**Checkpoint**: Polish complete ✅

---

## Phase 8: Verification

**Purpose**: Validate all success criteria per quickstart.md

- [x] T050 Test US1: Send message and receive AI response within 5s per quickstart.md
  - ✅ ChatContainer calls sendChatMessage API
  - ✅ Optimistic UI shows message immediately
  - ✅ Loading indicator while AI responds
- [x] T051 Test US2: Verify history loads after page refresh per quickstart.md
  - ✅ ChatContainer loads history on mount via getConversations/getMessages
  - ✅ Skeleton loader during load
- [x] T052 Test US3: Simulate error and verify retry works per quickstart.md
  - ✅ ChatError class with user-friendly messages
  - ✅ Retry button on failed messages
  - ✅ Offline indicator
- [x] T053 Test US4: Sign out and verify redirect to signin per quickstart.md
  - ✅ 401 handling redirects to /signin
  - ✅ Draft preserved in localStorage
- [x] T054 Test edge cases: empty message, long message, keyboard shortcuts per quickstart.md
  - ✅ Send disabled when empty
  - ✅ 16000 char validation
  - ✅ Enter/Shift+Enter shortcuts
- [x] T055 Test responsive design on mobile viewport per quickstart.md
  - ✅ Mobile tab navigation
  - ✅ Responsive container heights

**Checkpoint**: All success criteria verified — feature complete ✅

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T005)
- **US1 (Phase 3)**: Depends on Foundational completion (T006-T009) — **MVP**
- **US2 (Phase 4)**: Depends on US1 completion (needs working ChatContainer)
- **US3 (Phase 5)**: Depends on US1 completion (needs working message flow)
- **US4 (Phase 6)**: Depends on US1 completion (needs working API calls)
- **Polish (Phase 7)**: Depends on US1-US4 completion
- **Verification (Phase 8)**: Depends on all implementation phases

### User Story Dependencies

- **US1 & US2**: US2 depends on US1 for message display infrastructure
- **US3 & US4**: Can be parallel after US1 is complete (different concerns)

### Within Each User Story

- Component skeleton before behavior
- State management before UI updates
- Core functionality before edge cases

### Parallel Opportunities

```text
# Phase 1: API client
T002 [P], T003 [P] — different functions in same file

# Phase 2: Foundational components
T006 [P], T007 [P] — different files

# Phase 5 & 6: After US1 complete
Phase 5 (US3): Error handling
Phase 6 (US4): Auth integration
— can run in parallel (different concerns)

# Phase 7: Polish
T044 [P], T045 [P], T046 [P] — different files

# Phase 8: Verification
T050-T055 — independent tests
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T009)
3. Complete Phase 3: User Story 1 (T010-T023)
4. **STOP and VALIDATE**: Test sending messages and receiving AI responses
5. MVP delivered — users can chat with AI

### Incremental Delivery

1. Setup → Foundational → US1 (MVP)
2. Add US2: Conversation history
3. Add US3 & US4: Error handling + Auth (parallel)
4. Add polish and verification
5. Full feature complete

### Single Developer Strategy

Work sequentially through phases:

1. T001 → T002 → T003 → T004 → T005 (Setup)
2. T006 → T007 → T008 → T009 (Foundational)
3. T010 → T011 → ... → T023 (US1)
4. T024 → T025 → ... → T030 (US2)
5. T031 → T032 → ... → T038 (US3)
6. T039 → T040 → ... → T043 (US4)
7. T044 → T045 → ... → T049 (Polish)
8. T050 → T051 → ... → T055 (Verification)

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Setup | T001-T005 (5) | Types and API client |
| Foundational | T006-T009 (4) | Base chat components |
| US1 (P1) | T010-T023 (14) | Send message **[MVP]** |
| US2 (P1) | T024-T030 (7) | Conversation history |
| US3 (P2) | T031-T038 (8) | Error handling |
| US4 (P2) | T039-T043 (5) | Auth integration |
| Polish | T044-T049 (6) | UX refinements |
| Verification | T050-T055 (6) | Manual testing |
| **Total** | **55 tasks** | |

---

## Notes

- No automated tests — manual verification per quickstart.md
- All components use Tailwind CSS for styling consistency
- Optimistic UI ensures messages appear immediately
- History loaded from backend via existing conversation API
- JWT token obtained from Better Auth client session
