import { authClient } from "./auth-client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

// TypeScript interfaces for API
export interface Tag {
  id: string;
  name: string;
  user_id: string;
  created_at: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  is_completed: boolean;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  user_id: string;
  priority: 'low' | 'medium' | 'high';
  due_at: string | null;
  is_recurring: boolean;
  recurrence_pattern: string | null;
  tags: Tag[];
}

export interface TaskCreateRequest {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  due_at?: string | null;
  is_recurring?: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly';
  tag_names?: string[];
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  is_completed?: boolean;
  priority?: 'low' | 'medium' | 'high';
  due_at?: string | null;
  is_recurring?: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly';
  tag_names?: string[];
}

export interface TagCreateRequest {
  name: string;
}

export interface FilterParams {
  status?: 'pending' | 'completed' | 'all';
  priority?: 'low' | 'medium' | 'high';
  tag?: string;
  sort_by?: 'created_at' | 'due_at' | 'priority' | 'title';
  sort_order?: 'asc' | 'desc';
  q?: string; // search query
}

export interface ApiError {
  detail: string;
}

export class ApiException extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail);
    this.name = "ApiException";
  }
}

async function getToken(): Promise<string | null> {
  try {
    const response = await fetch("/api/auth/token", {
      method: "GET",
      credentials: "include",
    });

    if (response.ok) {
      const data = await response.json();
      if (data?.token) {
        return data.token;
      }
    }

    return null;
  } catch {
    return null;
  }
}

export async function apiClient<T>(
  path: string,
  options: RequestInit = {},
  retryCount = 0
): Promise<T> {
  const token = await getToken();

  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });

  // Handle 401 - retry once after a short delay (token timing issue)
  if (response.status === 401 && retryCount < 1) {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return apiClient<T>(path, options, retryCount + 1);
  }

  // Handle 401 after retry - throw error for component to handle
  if (response.status === 401) {
    throw new ApiException(401, "Not authenticated");
  }

  // Handle 204 No Content (for DELETE)
  if (response.status === 204) {
    return undefined as T;
  }

  // Handle errors
  if (!response.ok) {
    let detail = "An error occurred";
    try {
      const errorData = await response.json();
      detail = errorData.detail || detail;
    } catch {
      // Ignore JSON parse errors
    }
    throw new ApiException(response.status, detail);
  }

  return response.json();
}

// API methods
export const api = {
  // List all tasks for the authenticated user
  listTasks: (filters?: FilterParams): Promise<Task[]> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    const queryString = params.toString();
    return apiClient<Task[]>(`/api/todos${queryString ? '?' : ''}${queryString}`);
  },

  // Create a new task
  createTask: (data: TaskCreateRequest): Promise<Task> =>
    apiClient<Task>("/api/todos", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Update a task
  updateTask: (id: string, data: TaskUpdateRequest): Promise<Task> =>
    apiClient<Task>(`/api/todos/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  // Delete a task
  deleteTask: (id: string): Promise<void> =>
    apiClient<void>(`/api/todos/${id}`, {
      method: "DELETE",
    }),

  // Tags API
  listTags: (): Promise<Tag[]> => apiClient<Tag[]>("/api/tags"),

  createTag: (data: TagCreateRequest): Promise<Tag> =>
    apiClient<Tag>("/api/tags", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteTag: (id: string): Promise<void> =>
    apiClient<void>(`/api/tags/${id}`, {
      method: "DELETE",
    }),
};
