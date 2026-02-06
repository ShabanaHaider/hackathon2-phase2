# Implementation Plan: AI Agent Behavior & Tool Selection

**Branch**: `006-ai-agent-tool-selection` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-ai-agent-tool-selection/spec.md`

## Summary

Implement an AI agent using the OpenAI Agents SDK that interprets natural language messages and invokes MCP tools to manage tasks. The agent will have a single, well-defined system prompt that guides tool selection based on user intent. MCP tools from Spec 5 are already implemented and will be connected via stdio transport.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: OpenAI Agents SDK (`openai-agents`), existing MCP server (`mcp[cli]`)
**Storage**: Existing Conversation/Message tables (Spec 4), Task table (Spec 1)
**Testing**: Manual testing via conversation interface
**Target Platform**: Linux server (FastAPI backend)
**Project Type**: Web application (backend extension)
**Performance Goals**: Response within 3 seconds (SC-002)
**Constraints**: Stateless interactions, context from database
**Scale/Scope**: Single user per conversation, 5 MCP tools

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. End-to-End Correctness | PASS | Agent output persisted via Message table |
| II. User Data Isolation | PASS | user_id passed to all MCP tools |
| III. Spec-Driven Development | PASS | This plan follows spec.md |
| IV. Framework-Idiomatic | PASS | OpenAI Agents SDK per constitution |
| V. RESTful API Design | N/A | No new endpoints; uses existing /conversations |
| VI. Secret Management | PASS | OPENAI_API_KEY from .env |
| VII. Agentic AI & Tool-Oriented | PASS | Agent uses MCP tools exclusively |
| VIII. Stateless AI Interactions | PASS | Context from Message table |

## Project Structure

### Documentation (this feature)

```text
specs/006-ai-agent-tool-selection/
├── plan.md              # This file
├── research.md          # SDK and MCP integration research
├── data-model.md        # Agent configuration (no new tables)
├── quickstart.md        # Testing instructions
├── contracts/
│   └── agent-tools.md   # Tool-to-intent mapping
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── agent.py             # NEW: OpenAI Agents SDK agent definition
├── mcp_server.py        # EXISTING: MCP tools (add_task, list_tasks, etc.)
├── routers/
│   └── conversations.py # MODIFY: Add agent invocation endpoint
├── models.py            # EXISTING: Conversation, Message tables
└── requirements.txt     # MODIFY: Add openai-agents
```

**Structure Decision**: Single new file `backend/agent.py` containing agent definition, system prompt, and tool configuration. Minimal changes to existing conversation router.

## Key Design Decisions

### 1. Agent Architecture: Single Agent with Stdio MCP

**Decision**: Use a single agent connected to the existing MCP server via stdio transport.

**Rationale**:
- Spec calls for "single agent with tool access"
- MCP server already exists with 5 tools
- Stdio transport is simplest for local subprocess communication
- No need for multi-agent handoffs for task management

### 2. Tool Selection: SDK-Managed with Explicit Prompt

**Decision**: Let the OpenAI Agents SDK handle tool selection based on a detailed system prompt.

**Rationale**:
- SDK automatically maps user intent to tools via LLM reasoning
- System prompt defines behavior, not business logic (Constitution VII)
- Tool schemas from MCP provide clear function signatures
- Reduces custom code for intent classification

### 3. Conversation Context: Database-Backed

**Decision**: Load message history from database on each request.

**Rationale**:
- Constitution VIII requires stateless server
- Conversation/Message tables from Spec 4 provide persistence
- Agent receives full context via message array
- Resilient to server restarts

### 4. Error Handling: Graceful with User Feedback

**Decision**: Catch MCP tool errors and translate to friendly messages.

**Rationale**:
- Spec FR-006 requires user-friendly error messages
- Agent prompt includes error handling guidelines
- Tool errors (e.g., "Task not found") passed back conversationally

### 5. Confirmation Responses: Built into Prompt

**Decision**: System prompt instructs agent to confirm actions with details.

**Rationale**:
- Spec FR-005 requires clear confirmation responses
- User input mentions "Confirmation requirement" as mitigation
- Agent acknowledges what was done (task title, ID, status)

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Hallucinated actions | Agent can ONLY act via MCP tools; no direct DB access |
| Wrong tool selection | Detailed system prompt with explicit intent→tool mapping |
| Missing parameters | Agent asks for clarification (FR-007) |
| Cross-user access | user_id enforced by MCP tools (already implemented) |
| Slow responses | Cache MCP tools list; limit message history |

## Implementation Phases

### Phase 1: Agent Setup
- Add `openai-agents` to requirements.txt
- Create `backend/agent.py` with agent definition
- Define system prompt with tool selection guidelines
- Configure stdio MCP transport to existing mcp_server.py

### Phase 2: Conversation Integration
- Add endpoint to invoke agent with user message
- Load message history from database
- Persist agent response as assistant message
- Return response to frontend

### Phase 3: Verification
- Test all 5 user stories (create, list, update, complete, delete)
- Test edge cases (ambiguous intent, missing params, errors)
- Verify cross-user isolation
- Measure response time (target: <3s)

## Dependencies

- **Spec 4** (Conversation/Message tables): COMPLETE
- **Spec 5** (MCP Server with 5 tools): COMPLETE
- **OpenAI API Key**: Required in .env

## Out of Scope

- New HTTP endpoints (uses existing /conversations)
- Frontend changes (uses existing chat UI)
- Multi-language support
- Voice input
