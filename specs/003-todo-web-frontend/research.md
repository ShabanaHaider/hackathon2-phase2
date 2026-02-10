# Research: Todo Web Frontend Application

**Feature Branch**: `003-todo-web-frontend`
**Date**: 2026-01-28

## Research Decisions

### R1: Client-Side Data Fetching with React Hooks

**Decision**: Use client-side data fetching with React hooks (`useEffect`, custom hooks) rather than server-side data fetching with Server Components.

**Rationale**:
- Tasks change frequently and need real-time updates after mutations
- Client components are required for interactivity (forms, toggles, delete confirmations)
- Simpler mental model: fetch data after authentication is confirmed on the client
- Avoids complexity of server-side JWT handling in RSC

**Trade-offs**:
- Slightly slower initial page load (data fetched after JS loads)
- No SEO benefit (acceptable for authenticated dashboard content)
- Consistent UX with loading states users expect

### R2: No Global State Library (React Context + Local State)

**Decision**: Use React Context for auth state and local component state for task data. No Redux, Zustand, or similar.

**Rationale**:
- Application is simple: one authenticated user, one list of tasks
- Better Auth provides `useSession()` hook for auth state
- Task list can be fetched fresh on dashboard mount
- After mutations, refetch the list (optimistic updates are out of scope)

**Trade-offs**:
- No client-side caching (acceptable given simplicity)
- Refetch on every navigation to dashboard (ensures fresh data)
- If complexity grows, can add Zustand later (incremental migration)

### R3: API Client as Thin Wrapper with JWT Injection

**Decision**: Create a minimal `api.ts` module that wraps `fetch`, automatically attaching the JWT from Better Auth session.

**Rationale**:
- Constitution requires JWT on all API requests (FR-011)
- Single point of truth for API base URL configuration
- Centralized error handling for 401 responses (redirect to sign-in)
- Type-safe with TypeScript interfaces for request/response

**Implementation Pattern**:
```typescript
// frontend/src/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function apiClient<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getJwtToken(); // from Better Auth
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
      ...options.headers,
    },
  });
  if (response.status === 401) {
    // Redirect to sign-in
  }
  if (!response.ok) {
    throw new ApiError(response.status, await response.json());
  }
  return response.json();
}
```

### R4: Loading and Error States via Component State

**Decision**: Each data-fetching component manages its own `isLoading`, `error`, and `data` states.

**Rationale**:
- Simple pattern that covers all use cases
- No need for React Query or SWR complexity
- Matches the "no global state" decision (R2)
- Easy to understand and debug

**Pattern**:
```typescript
const [tasks, setTasks] = useState<Task[]>([]);
const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  fetchTasks()
    .then(setTasks)
    .catch(e => setError(e.message))
    .finally(() => setIsLoading(false));
}, []);
```

### R5: Tailwind CSS for Responsive Design

**Decision**: Use Tailwind CSS (already installed with Next.js) for all styling. No additional UI component libraries.

**Rationale**:
- Already included in the Next.js project from feature 002 scaffolding
- Mobile-first responsive design with utility classes
- No additional bundle size from component libraries
- Fast to implement for hackathon timeline

**Responsive Breakpoints**:
- Mobile: 320px - 767px (default styles)
- Tablet: 768px - 1023px (`md:` prefix)
- Desktop: 1024px+ (`lg:` prefix)

### R6: Delete Confirmation via Browser Confirm Dialog

**Decision**: Use native `window.confirm()` for delete confirmation rather than a custom modal.

**Rationale**:
- Simplest implementation that meets the requirement (FR-009)
- Users are familiar with browser confirmation dialogs
- No additional component complexity
- Out of scope: advanced UI animations

**Trade-offs**:
- Less polished than custom modal
- Cannot be styled to match app theme
- Acceptable for hackathon MVP

### R7: Form Validation with Native HTML5 + Custom Messages

**Decision**: Use HTML5 validation attributes (`required`, `minLength`, `maxLength`) combined with custom error message display.

**Rationale**:
- Built into browsers, no library needed
- Meets FR-014 requirements (title required, password 8+ chars)
- Progressive enhancement: works even if JS fails

**Implementation**:
- `required` attribute for required fields
- `minLength={8}` for password
- `maxLength={255}` for task title
- Display error messages below fields on validation failure

## API Endpoints (from Backend)

The frontend consumes the following API endpoints (per 002-auth-jwt-security route transition):

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/todos` | List authenticated user's tasks |
| POST | `/api/todos` | Create a new task |
| GET | `/api/todos/{id}` | Get single task (unused in current UI) |
| PATCH | `/api/todos/{id}` | Update task (title, description, is_completed) |
| DELETE | `/api/todos/{id}` | Delete a task |

All endpoints require `Authorization: Bearer <jwt>` header.

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |
| `DATABASE_URL` | Neon PostgreSQL (for Better Auth) | `postgresql://...` |
| `BETTER_AUTH_SECRET` | Session encryption key | Random 32+ char string |

## Component Hierarchy

```
(protected)/layout.tsx       -- Auth guard, session check
  └── page.tsx (Dashboard)   -- Task list + create form
        ├── TaskList         -- Displays tasks, handles toggle/delete
        │     └── TaskItem   -- Single task row with actions
        ├── TaskForm         -- Create new task form
        └── EmptyState       -- Shown when no tasks exist

(auth)/layout.tsx            -- Minimal layout for auth pages
  ├── signin/page.tsx        -- Sign-in form
  └── signup/page.tsx        -- Sign-up form
```
