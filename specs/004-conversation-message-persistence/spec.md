# Feature Specification: Conversation & Message Persistence

**Feature Branch**: `004-conversation-message-persistence`
**Created**: 2026-02-05
**Status**: Draft
**Input**: User description: "Introduce persistent conversation and message storage to support stateless AI interactions."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Retrieve Conversations (Priority: P1)

A user starts a new AI chat session. The system creates a conversation record
tied to that user. The user can later return and see a list of their past
conversations, each with a title and timestamp.

**Why this priority**: Conversations are the top-level container for all
message data. Without persistent conversations, messages have no parent and
the stateless AI architecture (Constitution Principle VIII) cannot function.

**Independent Test**: Can be fully tested by creating a conversation via the
API, then retrieving it by ID and listing all conversations for the user.
Delivers the foundational data container for the entire AI chatbot feature.

**Acceptance Scenarios**:

1. **Given** an authenticated user with no conversations, **When** the user
   creates a new conversation, **Then** a conversation record is persisted
   with a unique ID, the user's ID, a title, and a creation timestamp.
2. **Given** an authenticated user with three existing conversations, **When**
   the user requests their conversation list, **Then** all three conversations
   are returned ordered by most recently updated first.
3. **Given** an authenticated user, **When** the user requests a conversation
   that belongs to a different user, **Then** the system returns a not-found
   error and reveals no data about the other user's conversation.

---

### User Story 2 - Store and Retrieve Messages (Priority: P2)

A user sends a message within a conversation and receives a response. Both the
user's message and the assistant's response are stored as ordered message
records within that conversation. The user can retrieve the full message
history of any conversation they own.

**Why this priority**: Messages are the core data unit for AI interactions.
They enable the stateless backend to reconstruct context (Constitution
Principle VIII) by loading prior messages from the database on each request.

**Independent Test**: Can be tested by creating a conversation, adding
multiple messages with different roles, then retrieving them and verifying
order and content integrity.

**Acceptance Scenarios**:

1. **Given** an existing conversation owned by the user, **When** the user
   sends a message, **Then** a message record is created with the
   conversation ID, a "user" role, the message content, and a timestamp.
2. **Given** a conversation with five messages, **When** the user retrieves
   the message history, **Then** all five messages are returned in
   chronological order (oldest first).
3. **Given** a conversation owned by user A, **When** user B attempts to add
   a message to or retrieve messages from that conversation, **Then** the
   system returns a not-found error.

---

### User Story 3 - Manage Conversation Lifecycle (Priority: P3)

A user can update a conversation's title and delete conversations they no
longer need. Deleting a conversation removes all associated messages.

**Why this priority**: Lifecycle management improves usability but is not
required for the core AI interaction loop. Users need to be able to rename
and clean up conversations over time.

**Independent Test**: Can be tested by creating a conversation with messages,
updating the title, verifying the change, then deleting the conversation and
confirming both the conversation and its messages are gone.

**Acceptance Scenarios**:

1. **Given** an existing conversation, **When** the user updates the title,
   **Then** the conversation's title and updated-at timestamp are changed and
   the change persists on subsequent retrieval.
2. **Given** a conversation with ten messages, **When** the user deletes the
   conversation, **Then** the conversation and all its messages are removed
   from the database.
3. **Given** a conversation owned by user A, **When** user B attempts to
   delete it, **Then** the system returns a not-found error and the
   conversation remains intact.

---

### Edge Cases

- What happens when a user creates a conversation with an empty or
  whitespace-only title? The system MUST reject it with a validation error.
- What happens when a user sends a message with empty content? The system
  MUST reject it with a validation error.
- What happens when a user tries to add a message to a non-existent
  conversation? The system MUST return a not-found error.
- What happens when the message content exceeds the maximum allowed length?
  The system MUST reject it with a validation error indicating the limit.
- What happens when a user retrieves messages for a conversation that has
  no messages yet? The system MUST return an empty list, not an error.
- How does the system handle concurrent message creation in the same
  conversation? Each message MUST receive a unique, monotonically increasing
  order regardless of concurrency.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authenticated users to create new
  conversations with a title.
- **FR-002**: System MUST allow authenticated users to list their own
  conversations, ordered by most recently updated first.
- **FR-003**: System MUST allow authenticated users to retrieve a single
  conversation by ID, scoped to the authenticated user.
- **FR-004**: System MUST allow authenticated users to update the title of
  their own conversations.
- **FR-005**: System MUST allow authenticated users to delete their own
  conversations, cascading to all associated messages.
- **FR-006**: System MUST allow authenticated users to create messages
  within their own conversations.
- **FR-007**: System MUST allow authenticated users to retrieve all messages
  for a conversation they own, returned in chronological order.
- **FR-008**: System MUST store each message with a role indicator
  (user, assistant, or system) and text content.
- **FR-009**: System MUST enforce that every conversation belongs to exactly
  one user and every message belongs to exactly one conversation.
- **FR-010**: System MUST reject requests that attempt to access or modify
  another user's conversations or messages, returning a not-found response.
- **FR-011**: System MUST validate that conversation titles are non-empty
  and do not exceed 255 characters.
- **FR-012**: System MUST validate that message content is non-empty and
  does not exceed 16,000 characters.
- **FR-013**: System MUST automatically set creation and update timestamps
  on all records.

### Key Entities

- **Conversation**: Represents a single chat session. Attributes: unique
  identifier, owning user identifier, title, creation timestamp, last-updated
  timestamp. Relationship: belongs to one user, contains zero or more
  messages.
- **Message**: Represents a single utterance within a conversation.
  Attributes: unique identifier, parent conversation identifier, role
  (user / assistant / system), text content, creation timestamp.
  Relationship: belongs to exactly one conversation.

### Assumptions

- User identity is provided by the existing JWT authentication system
  (Better Auth) established in Phase 2.
- The `user_id` field follows the same pattern as the existing Task model
  (string type, indexed).
- Message role values are limited to "user", "assistant", and "system" to
  align with standard LLM conversation formats.
- Message content limit of 16,000 characters accommodates typical AI
  conversation turns while preventing abuse.
- Cascade delete is acceptable for conversation removal — no soft-delete
  is required at this stage.
- Pagination of conversation lists and message histories is deferred to a
  future enhancement; initial implementation returns all records.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Conversations persist across independent requests — creating
  a conversation in one request and retrieving it in a subsequent request
  returns identical data.
- **SC-002**: Message ordering is correct 100% of the time — messages
  retrieved for a conversation appear in the exact chronological order
  they were created.
- **SC-003**: User data isolation is enforced — no user can access, list,
  or modify conversations or messages belonging to another user, verified
  by cross-user access attempts returning not-found.
- **SC-004**: Cascade integrity is maintained — deleting a conversation
  leaves zero orphaned messages in the database.
- **SC-005**: All CRUD operations for conversations and messages complete
  successfully for authenticated users without errors.
