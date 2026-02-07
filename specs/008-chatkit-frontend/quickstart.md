# Quickstart: ChatKit Frontend Testing

## Prerequisites

1. **Backend running**: FastAPI server on port 8000
   ```bash
   cd backend
   source .venv/bin/activate
   uvicorn main:app --reload
   ```

2. **Frontend running**: Next.js dev server on port 3000
   ```bash
   cd frontend
   npm run dev
   ```

3. **User account**: Sign up/sign in at http://localhost:3000

## Testing the Chat UI

### Test 1: Send a Message (US1)

1. Sign in to the application
2. Locate the chat interface on the dashboard
3. Type "Hello, what can you help me with?"
4. Press Enter or click Send

**Expected**:
- Your message appears immediately (right side, user styling)
- Loading indicator shows while AI responds
- AI response appears within 5 seconds (left side, assistant styling)

### Test 2: Create a Task via Chat

1. Type "Add a task called 'Buy groceries'"
2. Send the message

**Expected**:
- AI responds confirming task creation
- Tool calls may be visible in the response
- Task appears in the task list

### Test 3: Conversation History (US2)

1. Send a few messages
2. Refresh the page (F5)
3. Check the chat interface

**Expected**:
- Previous messages are restored
- Messages appear in chronological order
- History loads within 2 seconds

### Test 4: Empty State (New User)

1. Sign up as a new user
2. Navigate to the dashboard

**Expected**:
- Chat shows welcome message or empty state
- Suggested prompts are visible (e.g., "Try: Add a task to buy groceries")

### Test 5: Error Handling (US3)

#### 5a. Network Error
1. Open browser DevTools → Network tab
2. Enable "Offline" mode
3. Try to send a message

**Expected**:
- Error message appears: "You're offline..."
- User's message is preserved
- Retry option available when online

#### 5b. Long Response
1. Send a complex request (e.g., "List all my tasks and summarize them")
2. Wait more than 5 seconds

**Expected**:
- Loading indicator persists
- "Still thinking..." message may appear
- Response eventually arrives

### Test 6: Keyboard Shortcuts

1. Type a message
2. Press Enter

**Expected**: Message sends

3. Type a multi-line message:
   - Line 1
   - Press Shift+Enter
   - Line 2
4. Press Enter

**Expected**: Message with line break sends

### Test 7: Authentication (US4)

1. Sign out
2. Navigate to the dashboard URL directly

**Expected**: Redirected to sign-in page

### Test 8: Session Expiry

1. Sign in and open chat
2. Wait for session to expire (or manually clear cookies)
3. Try to send a message

**Expected**:
- Error message about session
- Redirect to sign-in
- Draft message preserved (optional)

### Test 9: Message Validation

#### 9a. Empty Message
1. Click Send without typing anything

**Expected**: Send button disabled or nothing happens

#### 9b. Long Message
1. Paste text longer than 16000 characters
2. Try to send

**Expected**: Validation error before send

### Test 10: Responsive Design

1. Open browser DevTools → Toggle device toolbar
2. Switch to mobile viewport (e.g., iPhone 12)
3. Test sending messages

**Expected**:
- Chat is usable on mobile
- Input is accessible
- Messages are readable

## Verification Checklist

- [ ] User can send message and receive AI response
- [ ] Messages show immediately (optimistic UI)
- [ ] Loading indicator appears during AI processing
- [ ] Conversation history persists after refresh
- [ ] Empty state shows for new users
- [ ] Error messages are user-friendly
- [ ] Retry option works for failed messages
- [ ] Enter sends, Shift+Enter adds newline
- [ ] Authentication redirects work
- [ ] Chat is responsive on mobile

## Troubleshooting

### Chat not appearing
- Check browser console for errors
- Verify user is authenticated (session exists)
- Ensure ChatContainer is rendered in page.tsx

### Messages not sending
- Check Network tab for API calls
- Verify JWT token is included in Authorization header
- Check backend logs for errors

### History not loading
- Check if conversation exists: GET /api/conversations
- Verify conversation belongs to current user
- Check for 404 errors

### AI not responding
- Check backend GROQ_API_KEY is set
- Verify Groq API status
- Check backend logs for agent errors

## Performance Benchmarks

| Operation | Target | Notes |
|-----------|--------|-------|
| Message send (optimistic) | < 100ms | Local state update |
| AI response | < 5s | Depends on Groq API |
| History load | < 2s | Initial page load |
| Message render | < 50ms | Per message |
