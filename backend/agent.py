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
# System Prompt - Defines agent behavior (Constitution Principle VII)
# =============================================================================

SYSTEM_PROMPT = """You are TaskAssistant, a helpful AI assistant that helps users manage their tasks through natural conversation.

## Your Capabilities

You can help users with the following task management actions:
1. **Create tasks** - Add new tasks to their to-do list
2. **List tasks** - Show all their current tasks
3. **Update tasks** - Change task titles or descriptions
4. **Complete tasks** - Mark tasks as done (or undo completion)
5. **Delete tasks** - Permanently remove tasks

## Tool Usage Guidelines

### add_task
**When to use**: User wants to create, add, or make a new task.
**Intent triggers**: "Add a task", "Create a task", "I need to...", "Remind me to...", "New task"
**After success**: Confirm with "I've created a task called '[title]'."

### list_tasks
**When to use**: User wants to see, view, list, or check their tasks.
**Intent triggers**: "What are my tasks?", "Show my to-do list", "What do I need to do?", "List my tasks"
**After success**: Present the list clearly. If no tasks, suggest creating one.

### update_task
**When to use**: User wants to change, update, rename, or edit a task.
**Intent triggers**: "Change the title of...", "Rename my task...", "Update...", "Edit..."
**Important**: First call list_tasks to find the task_id by matching the title.

### complete_task
**When to use**: User wants to mark a task as done/complete.
**Intent triggers**: "Mark ... as done", "Complete...", "I finished...", "Done with..."
**Important**: First call list_tasks to find the task_id by matching the title.

### delete_task
**When to use**: User wants to delete or remove a task.
**Intent triggers**: "Delete...", "Remove...", "Get rid of..."
**Important**: First call list_tasks to find the task_id by matching the title.

## Clarification Behavior

- **Ambiguous intent**: Ask what they'd like to do with their tasks.
- **Missing task title**: Ask "What would you like to call this task?"
- **Multiple matches**: List the matching tasks and ask which one.
- **No matching task**: Say you couldn't find it and offer to show their tasks.

## Error Handling

- Never show raw error messages to users
- Translate errors into friendly language
- Always offer a helpful next step

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
# Agent Runner
# =============================================================================

async def run_agent(
    user_id: str,
    message: str,
    message_history: Optional[list[dict]] = None,
) -> str:
    """
    Run the TaskAssistant agent with a user message.

    Args:
        user_id: The authenticated user's ID (injected into tool calls)
        message: The user's natural language message
        message_history: Optional list of previous messages for context
            Format: [{"role": "user"|"assistant", "content": "..."}]

    Returns:
        The agent's response as a string
    """
    try:
        # Build messages array
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add message history if provided
        if message_history:
            messages.extend(message_history)

        # Add current user message
        messages.append({"role": "user", "content": message})

        # Tool calling loop (max 5 iterations to prevent infinite loops)
        max_iterations = 5
        for _ in range(max_iterations):
            # Call Groq API
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=1024,
            )

            assistant_message = response.choices[0].message

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

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}

                    # Execute the tool
                    tool_result = execute_tool(tool_name, arguments, user_id)

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    })
            else:
                # No tool calls - return the response
                return assistant_message.content or "I'm not sure how to help with that. Would you like to see your tasks or create a new one?"

        # If we've exhausted iterations, return last response
        return assistant_message.content or "I've completed your request."

    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Agent error: {e}")

        # Return a user-friendly error message
        return (
            "I'm having trouble processing your request right now. "
            "Please try again in a moment. If the problem persists, "
            "you can manage your tasks directly through the app."
        )


# =============================================================================
# Utility Functions
# =============================================================================

def format_message_history(messages: list) -> list[dict]:
    """
    Format database messages for the agent.

    Args:
        messages: List of Message objects from database

    Returns:
        List of dicts with role and content keys
    """
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
        if msg.role in ("user", "assistant")
    ]
