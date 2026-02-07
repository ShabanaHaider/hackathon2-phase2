# Research: MCP Server & Task Tools

## Decision 1: MCP SDK and Server Pattern

- **Decision**: Use `mcp` Python SDK with `FastMCP` high-level API
- **Rationale**: FastMCP is the official recommended pattern for Python MCP
  servers. It uses decorators (`@mcp.tool()`) and type hints to auto-generate
  tool schemas, reducing boilerplate. The SDK is mature (v1.25.0+, Python
  3.10+).
- **Alternatives considered**:
  - Low-level `Server` class: More control but requires manual schema
    definition and handler registration. Unnecessary complexity for 5 CRUD
    tools.
  - TypeScript SDK: Would require a separate Node.js process. Constitution
    mandates Python backend.

## Decision 2: Transport Mechanism

- **Decision**: Use `stdio` transport (default)
- **Rationale**: MCP stdio transport is the standard for agent-to-server
  communication. It is the simplest transport, requires no network
  configuration, and is the recommended default per the MCP documentation.
  The MCP server runs as a subprocess that communicates via stdin/stdout.
- **Alternatives considered**:
  - SSE (Server-Sent Events): For HTTP-based servers. Adds complexity with
    no benefit since the agent runs locally alongside the backend.
  - Streamable HTTP: Newer transport (spec 2025-03-26). Not needed for
    local agent communication.

## Decision 3: Database Access Pattern

- **Decision**: Use synchronous SQLModel sessions (not async) inside MCP
  tools, sharing the same database URL from `.env`
- **Rationale**: The MCP server runs as a separate process (not inside
  FastAPI), so it cannot use FastAPI's async event loop or dependency
  injection. Using synchronous `Session` from `sqlmodel` with a standard
  `create_engine` (not async) is the simplest approach. The MCP SDK's
  FastMCP tool functions can be either sync or async, but since the server
  runs standalone, sync DB access avoids the complexity of managing a
  separate async engine.
- **Alternatives considered**:
  - Async sessions with asyncpg: Would require an async engine and
    running tools inside an async context. Adds complexity with no
    performance benefit for single-user tool calls.
  - HTTP calls to FastAPI REST endpoints: Would reuse existing endpoints
    but adds network overhead and requires the FastAPI server to be running.
    Constitution requires MCP tools to access the database directly.

## Decision 4: Module Placement

- **Decision**: Create `backend/mcp_server.py` as a standalone module
- **Rationale**: The MCP server is a standalone process that runs
  independently from the FastAPI app. Placing it in the `backend/` directory
  allows it to import the existing `Task` model from `models.py` and reuse
  the `DATABASE_URL` from `.env`. The single-file approach is appropriate
  for 5 simple CRUD tools.
- **Alternatives considered**:
  - Separate `mcp/` package directory: Overkill for 5 tools.
  - Inside FastAPI as a mounted app: The MCP server uses stdio transport
    which is incompatible with HTTP server mounting.

## Decision 5: User Identity Handling

- **Decision**: Accept `user_id` as a required string parameter in each tool
- **Rationale**: MCP tools are stateless (Constitution Principle VII). They
  have no access to HTTP headers or JWT tokens. The AI agent that calls the
  tools must pass the user_id explicitly. The agent obtains the user_id from
  the authenticated session context.
- **Alternatives considered**:
  - MCP server-level auth context: Not supported by the MCP protocol.
    Tools must be self-contained.
  - Shared session/token: Violates stateless design. Would require the
    MCP server to parse JWTs, adding auth coupling.

## Decision 6: Error Handling and Return Format

- **Decision**: Return plain text strings from tools (success messages with
  task data, or error descriptions). Use Python try/except for DB errors.
- **Rationale**: MCP tools return `TextContent` by default when returning
  strings. Plain text is the simplest format for AI agents to parse and
  present to users. The FastMCP decorator handles the conversion to MCP
  protocol responses automatically.
- **Alternatives considered**:
  - Structured JSON output (with `outputSchema`): Would provide typed
    responses but adds schema definition complexity. Not needed for CRUD
    confirmations that the agent will reformulate in natural language.
  - Raising exceptions: MCP SDK converts unhandled exceptions to error
    responses, but explicit error messages are more informative.
