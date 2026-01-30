---
name: backend-skill
description: Build backend application logic including API route generation, request and response handling, and database connectivity. Use for server-side application development.
---

# Backend Development Skill

## Instructions

1. **API route generation**
   - Create RESTful API routes for backend services
   - Use appropriate HTTP methods (GET, POST, PUT, DELETE)
   - Organize routes by resource or domain

2. **Request and response handling**
   - Parse and validate incoming requests
   - Structure consistent and predictable API responses
   - Handle errors and edge cases gracefully

3. **Database connectivity**
   - Connect backend services to databases (SQL or NoSQL)
   - Perform CRUD operations securely
   - Manage database sessions or connections efficiently

## Best Practices
- Follow RESTful API design principles
- Keep request and response schemas consistent
- Separate routing, business logic, and data access layers
- Validate and sanitize all incoming data
- Use environment variables for database credentials
- Handle failures with meaningful error responses

## Example Structure
```python
# Example backend route
@app.post("/users")
async def create_user(user: UserCreate):
    db_user = create_user_in_db(user)
    return {
        "id": db_user.id,
        "email": db_user.email
    }
