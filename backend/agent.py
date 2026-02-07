"""
AI Agent for Task Management

Implements an AI agent using Groq's API with function calling that interprets
natural language messages and invokes task management tools.

Agent: TaskAssistant
Model: llama-3.3-70b-versatile (configurable via GROQ_MODEL env var)
Tools: add_task, list_tasks, update_task, complete_task, delete_task
"""

import json
import os
import time
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
from groq import Groq

# Import tool functions directly from MCP server
from mcp_server import add_task, list_tasks, update_task, complete_task, delete_task

# Load environment variables
load_dotenv()

# Configuration
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# =============================================================================
# Tool Call Info (for logging and response) - T016
# =============================================================================

@dataclass
class ToolCallInfoData:
    """Data class for tool call information."""
    name: str
    arguments: dict
    result: str
    duration_ms: int

# =============================================================================
# System Prompt - Defines agent behavior (Constitution Principle VII)
# =============================================================================

SYSTEM_PROMPT = """You are a task management assistant. Use the provided tools to help users manage their tasks.

TOOL USAGE:
- add_task: Use directly with the title the user provides
- list_tasks: Use when user wants to see their tasks
- delete_task: FIRST call list_tasks to get the task_id (UUID), then call delete_task with that exact UUID
- update_task: FIRST call list_tasks to get the task_id (UUID), then call update_task with that exact UUID
- complete_task: FIRST call list_tasks to get the task_id (UUID), then call complete_task with that exact UUID

IMPORTANT: For delete, update, and complete - you MUST use the actual UUID from list_tasks, never use placeholder values like "unknown".

Always respond naturally after completing the action. Keep responses brief and helpful.

## Out of Scope

If the user asks about something unrelated to tasks:
"I'm TaskAssistant, and I specialize in helping you manage your tasks. Is there something I can help you with for your to-do list?"

## Important Guidelines

1. Always confirm actions with relevant details
2. Be conversational but concise
3. Ask for clarification rather than making assumptions
4. Be encouraging when users complete tasks
"""

# =============================================================================
# Tool Definitions for Groq Function Calling
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user. Use when user wants to add, create, or make a new task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task (1-255 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the task (max 2000 characters)"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for the user. Use when user wants to see, view, list, or check their tasks.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update the title or description of an existing task. Use when user wants to change, rename, or edit a task. Requires task_id - call list_tasks first to find it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The UUID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task (1-255 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the task (max 2000 characters)"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Toggle the completion status of a task. Use when user wants to mark a task as done/complete or undo completion. Requires task_id - call list_tasks first to find it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The UUID of the task to complete/uncomplete"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Permanently delete a task. Use when user wants to delete, remove, or get rid of a task. Requires task_id - call list_tasks first to find it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The UUID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        }
    }
]

# =============================================================================
# Tool Execution
# =============================================================================

def execute_tool(tool_name: str, arguments: dict, user_id: str) -> str:
    """
    Execute a tool function with the given arguments.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments from the model
        user_id: The authenticated user's ID

    Returns:
        Tool result as a string
    """
    # Ensure arguments is a dict (can be None from model)
    if arguments is None:
        arguments = {}

    # All tools require user_id
    arguments["user_id"] = user_id

    if tool_name == "add_task":
        return add_task(
            user_id=user_id,
            title=arguments.get("title", ""),
            description=arguments.get("description"),
        )
    elif tool_name == "list_tasks":
        return list_tasks(user_id=user_id)
    elif tool_name == "update_task":
        return update_task(
            user_id=user_id,
            task_id=arguments.get("task_id", ""),
            title=arguments.get("title"),
            description=arguments.get("description"),
        )
    elif tool_name == "complete_task":
        return complete_task(
            user_id=user_id,
            task_id=arguments.get("task_id", ""),
        )
    elif tool_name == "delete_task":
        return delete_task(
            user_id=user_id,
            task_id=arguments.get("task_id", ""),
        )
    else:
        return f"Error: Unknown tool '{tool_name}'"


# =============================================================================
# Failed Generation Parser (workaround for Groq tool format issues)
# =============================================================================

def _parse_failed_generation_direct(failed_gen: str, user_id: str) -> tuple | None:
    """
    Parse Groq's failed_generation content to extract and execute the intended tool call.

    Groq's llama-3.3-70b-versatile sometimes outputs function calls in an incorrect format:
    <function=add_task {"title": "Buy milk"} </function>

    This function extracts the tool name and arguments, executes the tool, and returns the result.
    """
    import re

    # Parse format: <function=tool_name {"arg": "value"} </function> or <function=tool_name({"arg": "value"})></function>
    func_match = re.search(r"function=(\w+)[\s\(]*(\{[^}]+\})", failed_gen)
    if not func_match:
        return None

    tool_name = func_match.group(1)
    args_str = func_match.group(2)

    try:
        arguments = json.loads(args_str)
    except json.JSONDecodeError:
        return None

    # Execute the tool
    start_time = time.perf_counter()
    result = execute_tool(tool_name, arguments, user_id)
    duration_ms = int((time.perf_counter() - start_time) * 1000)

    tool_info = {
        "name": tool_name,
        "arguments": arguments,
        "result": result,
        "duration_ms": duration_ms,
    }

    return (tool_name, result, tool_info)


# =============================================================================
# Agent Runner
# =============================================================================

async def run_agent(
    user_id: str,
    message: str,
    message_history: Optional[list[dict]] = None,
) -> tuple[str, Optional[list[dict]]]:
    """
    Run the TaskAssistant agent with a user message.

    Args:
        user_id: The authenticated user's ID (injected into tool calls)
        message: The user's natural language message
        message_history: Optional list of previous messages for context
            Format: [{"role": "user"|"assistant", "content": "..."}]

    Returns:
        Tuple of (agent_response, tool_calls)
        - agent_response: The agent's response as a string
        - tool_calls: List of ToolCallInfo dicts or None if no tools called
    """
    # T016-T018: Collect tool call information
    collected_tool_calls: list[dict] = []

    try:
        # Build messages array
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add message history if provided
        if message_history:
            messages.extend(message_history)

        # Add current user message
        messages.append({"role": "user", "content": message})

        # Tool calling loop (max 5 iterations - extra needed for text-based function parsing)
        max_iterations = 5
        for _ in range(max_iterations):
            # Call Groq API - catch and handle failed_generation errors
            try:
                response = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    parallel_tool_calls=False,
                    max_tokens=1024,
                )
                assistant_message = response.choices[0].message
            except Exception as api_error:
                # Check if this is a tool_use_failed error with failed_generation
                failed_gen = None
                print(f"[DEBUG] Caught API error: {type(api_error).__name__}")

                # Try to get failed_generation from error body
                if hasattr(api_error, 'body'):
                    print(f"[DEBUG] Error has body: {api_error.body}")
                    if isinstance(api_error.body, dict):
                        error_body = api_error.body.get('error', {})
                        failed_gen = error_body.get('failed_generation', '')
                        print(f"[DEBUG] Extracted failed_gen from body: {failed_gen[:100] if failed_gen else 'None'}")

                # Fallback to string parsing
                if not failed_gen:
                    error_str = str(api_error)
                    print(f"[DEBUG] Trying string parsing on: {error_str[:200]}")
                    if "failed_generation" in error_str:
                        import re
                        match = re.search(r"'failed_generation':\s*'([^']+)'", error_str)
                        if match:
                            failed_gen = match.group(1)
                            print(f"[DEBUG] Extracted from string: {failed_gen}")

                if failed_gen and "function=" in failed_gen:
                    print(f"[DEBUG] Parsing failed_gen: {failed_gen}")
                    # Parse the failed generation to extract function call
                    parsed = _parse_failed_generation_direct(failed_gen, user_id)
                    print(f"[DEBUG] Parse result: {parsed}")
                    if parsed:
                        tool_name, result, tool_info = parsed
                        collected_tool_calls.append(tool_info)
                        print(f"[TOOL CALL] {tool_name} | args={tool_info['arguments']} | duration={tool_info['duration_ms']}ms")
                        title = tool_info['arguments'].get('title', 'your task')
                        return (f"I've added '{title}' to your task list.", collected_tool_calls)
                raise  # Re-raise if we can't handle it

            # Check if the model wants to call tools
            if assistant_message.tool_calls:
                # Add assistant message with tool calls to history
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call with timing (T017)
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        args_str = tool_call.function.arguments
                        arguments = json.loads(args_str) if args_str else {}
                    except (json.JSONDecodeError, TypeError):
                        arguments = {}

                    # Ensure arguments is always a dict (not None)
                    if arguments is None:
                        arguments = {}

                    # T017: Time the tool execution
                    start_time = time.perf_counter()

                    # Execute the tool
                    tool_result = execute_tool(tool_name, arguments, user_id)

                    # Calculate duration in milliseconds
                    duration_ms = int((time.perf_counter() - start_time) * 1000)

                    # T016, T018: Capture tool call info
                    tool_call_info = {
                        "name": tool_name,
                        "arguments": arguments,
                        "result": tool_result,
                        "duration_ms": duration_ms,
                    }
                    collected_tool_calls.append(tool_call_info)

                    # T020: Console logging for tool calls
                    print(f"[TOOL CALL] {tool_name} | args={arguments} | duration={duration_ms}ms")

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    })

                    # For add_task, return immediately to prevent hallucinating more tasks
                    if tool_name == "add_task":
                        title = arguments.get("title", "your task")
                        return (f"I've added '{title}' to your task list.", collected_tool_calls)
            else:
                # No tool calls - check if model output function call as text
                response_text = assistant_message.content or ""

                # Check for function call pattern in text response
                if "<function=" in response_text or "function=" in response_text:
                    import re
                    # Parse: <function=tool_name></function> or <function=tool_name {...}></function>
                    func_match = re.search(r"function=(\w+)(?:[\s\(]*(\{[^}]*\}))?", response_text)
                    if func_match:
                        tool_name = func_match.group(1)
                        args_str = func_match.group(2)
                        try:
                            arguments = json.loads(args_str) if args_str else {}
                        except (json.JSONDecodeError, TypeError):
                            arguments = {}

                        # Execute the tool
                        start_time = time.perf_counter()
                        tool_result = execute_tool(tool_name, arguments, user_id)
                        duration_ms = int((time.perf_counter() - start_time) * 1000)

                        tool_info = {
                            "name": tool_name,
                            "arguments": arguments,
                            "result": tool_result,
                            "duration_ms": duration_ms,
                        }
                        collected_tool_calls.append(tool_info)
                        print(f"[TOOL CALL FROM TEXT] {tool_name} | args={arguments} | duration={duration_ms}ms")

                        # Add tool result to messages and continue the loop
                        messages.append({
                            "role": "assistant",
                            "content": response_text,
                        })
                        messages.append({
                            "role": "user",
                            "content": f"Tool result: {tool_result}\n\nNow complete the user's request based on this information.",
                        })
                        continue  # Continue the loop to get final response

                # No function calls found - return the response
                if not response_text:
                    response_text = "I'm not sure how to help with that. Would you like to see your tasks or create a new one?"
                return (response_text, collected_tool_calls if collected_tool_calls else None)

        # If we've exhausted iterations, return last response
        response_text = assistant_message.content or "I've completed your request."
        return (response_text, collected_tool_calls if collected_tool_calls else None)

    except Exception as e:
        # Log the error with full details
        import traceback
        print(f"[AGENT ERROR] {type(e).__name__}: {e}")
        print(f"[AGENT ERROR] Full traceback:\n{traceback.format_exc()}")

        # Return a user-friendly error message with any collected tool calls
        error_response = (
            "I'm having trouble processing your request right now. "
            "Please try again in a moment. If the problem persists, "
            "you can manage your tasks directly through the app."
        )
        return (error_response, collected_tool_calls if collected_tool_calls else None)


# =============================================================================
# Utility Functions
# =============================================================================

def format_message_history(messages: list, max_messages: int = 10) -> list[dict]:
    """
    Format database messages for the agent.

    Limits history to prevent context pollution that can cause
    Groq to use incorrect function call formats.

    Args:
        messages: List of Message objects from database
        max_messages: Maximum number of messages to include (default 10)

    Returns:
        List of dicts with role and content keys
    """
    # Only include recent messages to avoid context pollution
    recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages

    formatted = []
    for msg in recent_messages:
        if msg.role not in ("user", "assistant"):
            continue
        # Skip assistant messages that mention tool execution details
        # (these can confuse the model's function calling format)
        content = msg.content or ""
        if msg.role == "assistant" and "I'm having trouble" in content:
            continue
        formatted.append({"role": msg.role, "content": content})

    return formatted
