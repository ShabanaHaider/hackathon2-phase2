---
id: 024
title: AI Agent Plan Generated
stage: plan
date: 2026-02-06
surface: agent
model: claude-opus-4-5-20251101
feature: 006-ai-agent-tool-selection
branch: 006-ai-agent-tool-selection
user: shaid
command: /sp.plan
labels: ["plan", "ai-agent", "openai-agents-sdk", "mcp", "tool-selection"]
links:
  spec: specs/006-ai-agent-tool-selection/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-ai-agent-tool-selection/plan.md
  - specs/006-ai-agent-tool-selection/research.md
  - specs/006-ai-agent-tool-selection/data-model.md
  - specs/006-ai-agent-tool-selection/contracts/agent-tools.md
  - specs/006-ai-agent-tool-selection/quickstart.md
tests:
  - Constitution check: 8/8 principles PASS
---

## Prompt

/sp.plan read the frontend and backend folder and then create the plan. here is the plan:# Plan-6: AI Agent

## Architecture
- Single agent with tool access
- Behavior defined via system prompt
- Deterministic tool invocation

## Risks
- Hallucinated actions
- Wrong tool selection

## Mitigations
- Explicit intent mapping
- Confirmation requirement

## Response snapshot

Created implementation plan for AI Agent Behavior & Tool Selection feature.

**Key decisions:**
1. Use OpenAI Agents SDK with stdio MCP transport to connect to existing mcp_server.py
2. Single agent with detailed system prompt defining tool selection rules
3. Database-backed conversation context (stateless per Constitution VIII)
4. Agent confirms actions and translates errors to user-friendly messages
5. No new database tables — reuses Conversation/Message from Spec 4

**Architecture:**
- `backend/agent.py` — NEW: Agent definition, system prompt, MCP config
- `backend/routers/conversations.py` — MODIFY: Add agent invocation
- `backend/mcp_server.py` — EXISTING: 5 MCP tools unchanged

**Risk mitigations implemented:**
- Hallucinated actions → Agent can ONLY act via MCP tools
- Wrong tool selection → Detailed system prompt with intent→tool mapping
- Missing parameters → Agent asks for clarification
- Cross-user access → user_id enforced by MCP tools

**Files created:**
- plan.md — Implementation plan with 3 phases
- research.md — 6 research decisions with rationale
- data-model.md — Agent configuration (no new tables)
- contracts/agent-tools.md — Tool invocation contracts
- quickstart.md — 10 verification tests

## Outcome

- ✅ Impact: Complete plan for AI agent with MCP tool integration
- 🧪 Tests: Constitution check 8/8 PASS
- 📁 Files: 5 files created
- 🔁 Next prompts: /sp.tasks to generate task list
- 🧠 Reflection: User input specified risks/mitigations — incorporated into plan

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
