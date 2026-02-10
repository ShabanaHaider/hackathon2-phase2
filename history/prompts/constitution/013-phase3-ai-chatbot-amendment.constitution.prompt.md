---
id: 013
title: Phase III AI Chatbot Constitution Amendment
stage: constitution
date: 2026-02-05
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 003-todo-web-frontend
user: shaid
command: /sp.constitution
labels: ["constitution", "phase3", "ai-chatbot", "mcp", "openai-agents"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

<!--
  Sync Impact Report
  ===================
  Version change: 1.0.0 → 1.1.0
  Modified principles: None
  Added principles:
    - Principle VII: Agentic AI & Tool-Oriented Architecture
    - Principle VIII: Stateless AI Interactions with Persistent Memory
  Added sections:
    - AI & MCP Constraints
  Removed sections: None
-->

# Todo Full-Stack Web Application Constitution
## Phase III Amendment (AI Chatbot Integration)

---

## New Core Principles

### VII. Agentic AI & Tool-Oriented Architecture

All AI behavior MUST be implemented using explicit, auditable agents and tools.
The AI model MUST NOT directly mutate application state.

- AI agents MUST operate exclusively via MCP tools.
- All task mutations MUST occur inside MCP tools backed by the database.
- Agent prompts MUST describe *intent and behavior*, never business logic.
- Tool schemas are the single source of truth for task operations.

This ensures:
- Deterministic state changes
- Auditable AI behavior
- Clear separation of reasoning vs execution

---

### VIII. Stateless AI Interactions with Persistent Memory

The backend server MUST remain stateless across requests, including AI interactions.

- No in-memory conversation state may be retained between requests.
- Conversation context MUST be reconstructed from the database on every request.
- AI agents MUST receive full context explicitly via message history.
- System MUST remain resilient to server restarts.

---

## AI & MCP Constraints

### Model Context Protocol (MCP)

- MCP server MUST be implemented using the **Official MCP SDK**.
- MCP tools MUST:
  - Be stateless
  - Accept all required data as parameters
  - Persist all state changes to the database
- MCP server MUST NOT:
  - Access frontend state
  - Maintain session memory
  - Contain AI reasoning logic

### OpenAI Agents SDK

- Agent logic MUST be implemented using OpenAI Agents SDK.
- Agents MUST:
  - Select tools based on user intent
  - Handle errors gracefully
  - Confirm actions conversationally
- Agents MUST NOT:
  - Perform direct database queries
  - Assume implicit state

---

## Compatibility Guarantee

- All Phase-2 REST APIs remain valid and unchanged.
- The AI chatbot is an **additive interface**, not a replacement.
- Manual Todo CRUD via REST MUST continue to work independently.

---

**Constitution Version**: 1.1.0
**Ratified**: 2026-02-05
**Supersedes**: None (additive amendment only)

## Response snapshot

Updated constitution from v1.0.0 to v1.1.0 with Phase III AI Chatbot Integration amendments:

1. Added **Principle VII: Agentic AI & Tool-Oriented Architecture** — AI agents operate exclusively via MCP tools; no direct state mutation by the model.
2. Added **Principle VIII: Stateless AI Interactions with Persistent Memory** — Backend remains stateless; conversation context reconstructed from database per request.
3. Added **AI & MCP Constraints** section under Technology Constraints — MCP SDK requirements, OpenAI Agents SDK requirements, tool statelessness rules.
4. Added **Compatibility Guarantee** — Phase-2 REST APIs unchanged; AI chatbot is additive.
5. Updated Technology Constraints table with AI Agent SDK and MCP Server rows.
6. Extended Quality Gates and Success Criteria with AI-specific checks.
7. Updated Loose Coupling to include AI agent data access constraint.
8. All three templates validated — no updates needed (generic structures accommodate new principles).

Version bump: MINOR (1.0.0 → 1.1.0) — new principles added, no existing principles modified or removed.

## Outcome

- ✅ Impact: Constitution amended with 2 new principles, 3 new sections, AI/MCP constraints codified
- 🧪 Tests: N/A (governance document)
- 📁 Files: `.specify/memory/constitution.md` updated
- 🔁 Next prompts: `/sp.specify` for AI chatbot feature, `/sp.adr` for MCP vs direct-DB decision
- 🧠 Reflection: Additive amendment pattern works well — no existing principles needed modification

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation PASS — no unresolved placeholders, version matches, dates ISO
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
