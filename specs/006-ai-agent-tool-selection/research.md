# Research: AI Agent Behavior & Tool Selection

## Decision 1: Agent Framework Selection

- **Decision**: Use OpenAI Agents SDK (`openai-agents` Python package)
- **Rationale**: Constitution mandates OpenAI Agents SDK for agent logic. The SDK provides:
  - Built-in MCP integration via stdio, HTTP, and SSE transports
  - Automatic tool schema generation from function signatures
  - Conversation context management
  - Guardrail support for input/output validation
- **Alternatives considered**:
  - LangChain Agents: More complex, not mandated by constitution
  - Custom implementation: Violates spec-driven development principles
  - Anthropic Claude Tool Use: Different SDK, not the mandated choice

## Decision 2: MCP Transport Mechanism

- **Decision**: Use stdio transport to connect to existing `mcp_server.py`
- **Rationale**: The MCP server from Spec 5 already runs as a standalone Python script with stdio transport. The OpenAI Agents SDK supports `StdioMCPServer` which launches the server as a subprocess and communicates via stdin/stdout.
- **Alternatives considered**:
  - Streamable HTTP: Requires running MCP server as HTTP service, adds complexity
  - Hosted MCP Server Tools: Requires public reachability, not suitable for local dev
  - Direct function tools: Would bypass MCP, violating tool-oriented architecture

## Decision 3: Agent System Prompt Design

- **Decision**: Single detailed prompt with explicit intent-to-tool mapping and behavior guidelines
- **Rationale**:
  - User input specifies "behavior defined via system prompt"
  - Mitigates "wrong tool selection" risk through explicit guidance
  - Keeps business logic in tools, behavior in prompt (Constitution VII)
- **Prompt structure**:
  1. Role and capabilities statement
  2. Available tools and when to use each
  3. Clarification behavior for ambiguous requests
  4. Confirmation format for successful actions
  5. Error handling guidelines

## Decision 4: Conversation Context Loading

- **Decision**: Load last N messages from database before each agent invocation
- **Rationale**:
  - Constitution VIII requires stateless server
  - Conversation/Message tables from Spec 4 provide persistence
  - Agent SDK accepts message history array
  - Limit to recent messages to control context window and latency
- **Implementation**:
  - Load messages from `messages` table ordered by `created_at`
  - Convert to SDK-compatible format: `{"role": "user"|"assistant", "content": "..."}`
  - Pass to `Runner.run()` as input history

## Decision 5: Response Persistence

- **Decision**: Save agent response as assistant message in database
- **Rationale**:
  - Maintains conversation continuity across requests
  - Enables context loading on subsequent requests
  - Existing `create_message` endpoint in conversations router can be reused
- **Implementation**:
  - After agent returns response, create Message with role="assistant"
  - Update conversation's `updated_at` timestamp

## Decision 6: Error Response Format

- **Decision**: Return errors as natural language within assistant message
- **Rationale**:
  - Spec FR-006 requires user-friendly error messages
  - Agent processes tool errors and reformulates conversationally
  - No HTTP error codes for tool failures (user sees chat message)
- **Examples**:
  - Tool returns "Error: Task not found." → Agent says "I couldn't find that task. Can you check the name?"
  - Tool returns "Error: Title is required." → Agent says "Please provide a title for the task."

## Sources

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [OpenAI Agents SDK GitHub](https://github.com/openai/openai-agents-python)
- [MCP Integration Guide](https://openai.github.io/openai-agents-python/mcp/)
- [Tools Documentation](https://openai.github.io/openai-agents-python/tools/)
