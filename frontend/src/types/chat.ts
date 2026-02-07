/**
 * TypeScript types for the Chat UI
 * Maps to backend Pydantic models from Spec 007
 */

// Message status for optimistic UI
export type MessageStatus = 'pending' | 'sent' | 'error';

// Chat message for frontend display
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  status: MessageStatus;
  error?: string;
}

// Tool call information from AI agent
export interface ToolCallInfo {
  name: string;
  arguments: Record<string, unknown>;
  result: string;
  duration_ms: number;
}

// API response types matching backend schemas
export interface MessageResponse {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface ChatResponse {
  user_message: MessageResponse;
  assistant_message: MessageResponse;
  tool_calls?: ToolCallInfo[];
}

export interface Conversation {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

// Request type for sending messages
export interface ChatRequest {
  message: string;
}
