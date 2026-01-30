---
name: auth-skill
description: Build secure authentication systems including signup, signin, password hashing, JWT tokens, and Better Auth integration. Use for user authentication and access control.
---

# Authentication Skill

## Instructions

1. **Authentication flows**
   - Implement secure user signup and signin
   - Validate credentials and user input
   - Handle authentication errors gracefully

2. **Password handling**
   - Hash passwords using secure algorithms (bcrypt, argon2, or equivalent)
   - Apply proper salting
   - Never store passwords in plain text

3. **JWT authentication**
   - Generate JWT tokens on successful login
   - Configure token expiration
   - Verify tokens for protected routes and APIs

4. **Better Auth integration**
   - Integrate the Better Auth library correctly
   - Configure authentication providers
   - Manage sessions and token refresh logic

## Best Practices
- Follow OWASP authentication security guidelines
- Always use HTTPS for authentication endpoints
- Implement rate limiting on signup and signin
- Use secure, httpOnly cookies when applicable
- Sanitize and validate all user inputs

## Example Structure
```ts
// Password hashing
const hashedPassword = await bcrypt.hash(password, 12);

// Signup
await db.user.create({
  email,
  password: hashedPassword,
});

// JWT creation
const token = jwt.sign(
  { userId: user.id },
  process.env.JWT_SECRET,
  { expiresIn: "1h" }
);
