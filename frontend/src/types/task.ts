// Extended task types for advanced features

export interface Tag {
  id: string;
  name: string;
}

export interface ExtendedTask {
  id: string;
  title: string;
  description?: string;
  is_completed: boolean;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
  user_id: string;
  priority: 'low' | 'medium' | 'high';
  due_at?: string | null;
  is_recurring: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly' | null;
  tags: Tag[];
}

export interface TaskFormData {
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  due_at?: string | null;
  is_recurring: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly' | null;
  tag_names?: string[];
}