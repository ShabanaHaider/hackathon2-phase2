# Feature Specification: Stateless Chat API Endpoint

**Feature Branch**: `007-stateless-chat-api`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Create a stateless chat endpoint that orchestrates conversation persistence and agent execution at POST /api/{user_id}/chat"

## Overview

This feature creates a stateless chat endpoint that serves as the orchestration layer between the frontend and the AI agent. Unlike the existing conversation-scoped endpoint, this endpoint operates at the user level, automatically managing conversation context while ensuring no in-memory state is retained between requests.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Send Chat Message (Priority: P1)

As a user, I want to send a natural language message to the AI assistant and receive a response, so that I can manage my tasks through conversation.

**Why this priority**: This is the core functionality - without message sending/receiving, the chat feature has no value.

**Independent Test**: Can be fully tested by sending a POST request with a message and verifying the response contains both user and assistant messages.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they send a message "Add a task to buy groceries", **Then** the system stores the user message, invokes the AI agent, stores the agent response, and returns both messages.
2. **Given** an authenticated user with no prior conversation, **When** they send their first message, **Then** a new conversation is automatically created for them.
3. **Given** an authenticated user, **When** they send a message, **Then** the response is returned within 5 seconds.

---

### User Story 2 - Resume Conversation Context (Priority: P1)

As a user, I want my conversation history to be automatically loaded when I send a new message, so that the AI assistant remembers our previous interactions.

**Why this priority**: Context continuity is essential for meaningful task management conversations (e.g., "Mark the task I just created as done").

**Independent Test**: Can be tested by sending multiple messages and verifying the AI agent receives prior context and responds appropriately.

**Acceptance Scenarios**:

1. **Given** a user with existing conversation history, **When** they send a new message, **Then** the system loads the last 20 messages as context for the AI agent.
2. **Given** a user who says "Mark that task as done" after creating a task, **When** the agent processes the message, **Then** it has access to the conversation history showing which task was created.
3. **Given** a user who closes and reopens the chat, **When** they send a new message, **Then** their conversation resumes from where they left off.

---

### User Story 3 - Tool Call Logging (Priority: P2)

As a system administrator, I want all AI agent tool invocations to be logged, so that I can audit task operations and debug issues.

**Why this priority**: Important for debugging and audit trails, but not critical for basic functionality.

**Independent Test**: Can be tested by sending a task creation message and verifying tool call details are captured in the response or logs.

**Acceptance Scenarios**:

1. **Given** a user sends "Add a task to buy groceries", **When** the agent invokes the add_task tool, **Then** the tool call (name, arguments, result) is logged.
2. **Given** an agent that makes multiple tool calls in one response, **When** the request completes, **Then** all tool calls are logged in order.
3. **Given** a tool call that fails, **When** the error occurs, **Then** the error is logged with the tool name and arguments.

---

### User Story 4 - Error Recovery (Priority: P2)

As a user, I want my message to be preserved even if the AI agent fails, so that I don't lose my input.

**Why this priority**: Data integrity is important for user trust, but errors should be rare.

**Independent Test**: Can be tested by simulating an agent failure and verifying the user message is still persisted.

**Acceptance Scenarios**:

1. **Given** a user sends a message, **When** the AI agent encounters an error, **Then** the user message is still persisted in the conversation.
2. **Given** an agent failure, **When** the system responds, **Then** it returns a user-friendly error message explaining the issue.
3. **Given** an agent timeout, **When** the request times out, **Then** the user can retry without losing their original message.

---

### Edge Cases

- What happens when the user has no existing conversation? → Automatically create a new conversation with a default title.
- What happens if the user_id in the URL doesn't match the authenticated user? → Return 403 Forbidden.
- What happens if the message exceeds the maximum length? → Return 400 Bad Request with validation error.
- What happens if the AI agent times out? → Return 504 Gateway Timeout with the user message still persisted.
- What happens if multiple requests arrive simultaneously for the same user? → Process sequentially within the same conversation to maintain message ordering.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a POST endpoint at `/api/{user_id}/chat` that accepts a message and returns a response.
- **FR-002**: System MUST validate that the authenticated user matches the user_id in the URL path.
- **FR-003**: System MUST automatically create a conversation for the user if none exists.
- **FR-004**: System MUST load the last 20 messages from the user's conversation as context for the AI agent.
- **FR-005**: System MUST persist the user's message before invoking the AI agent.
- **FR-006**: System MUST invoke the AI agent with the user message and conversation history.
- **FR-007**: System MUST persist the AI agent's response after successful execution.
- **FR-008**: System MUST return both the user message and assistant message in the response.
- **FR-009**: System MUST log all tool calls made by the AI agent (tool name, arguments, result, duration).
- **FR-010**: System MUST NOT retain any in-memory state between requests (stateless design).
- **FR-011**: System MUST handle agent failures gracefully, preserving the user message.
- **FR-012**: System MUST validate message length (1-16000 characters).

### Key Entities

- **User**: The authenticated user identified by user_id from JWT token.
- **Conversation**: A single conversation thread per user containing all their chat messages.
- **Message**: Individual chat messages with role (user/assistant), content, and timestamp.
- **ToolCall**: A record of AI agent tool invocations including name, arguments, result, and timing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users receive AI responses within 5 seconds for 95% of requests.
- **SC-002**: Conversation history is correctly loaded for 100% of returning users.
- **SC-003**: User messages are persisted even when agent fails (100% data integrity).
- **SC-004**: All tool calls are logged with complete details (name, arguments, result).
- **SC-005**: No memory leaks or state retention between requests (verified via load testing).
- **SC-006**: System correctly rejects requests where URL user_id doesn't match authenticated user (100% security compliance).

## Assumptions

- Users have already authenticated via Better Auth and have a valid JWT token.
- The AI agent (backend/agent.py) is already implemented and functional.
- The Conversation and Message models from Spec 4 are available.
- Each user has at most one active conversation (single-thread model).
- The existing chat endpoint at `/api/conversations/{id}/chat` may be deprecated in favor of this simplified endpoint.

## Dependencies

- **Spec 4**: Conversation and Message persistence (models, database tables).
- **Spec 6**: AI Agent with tool selection (agent.py, run_agent function).
- **Better Auth**: JWT authentication for user identification.
- **Neon PostgreSQL**: Database for conversation and message storage.

## Out of Scope

- Multiple conversations per user (single conversation thread only).
- Streaming responses (full response returned after completion).
- File attachments or image uploads.
- Conversation export or backup features.
- Real-time collaboration between users.
