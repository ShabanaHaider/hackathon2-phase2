---
name: database-skill
description: Design and manage databases including schema design, table creation, and migrations. Use for data modeling and persistence tasks.
---

# Database Skill

## Instructions

1. **Schema design**
   - Design normalized and scalable database schemas
   - Define relationships between tables
   - Choose appropriate data types and constraints

2. **Table creation**
   - Create tables with primary and foreign keys
   - Apply indexes for performance optimization
   - Enforce data integrity using constraints

3. **Migrations**
   - Create and manage database migrations
   - Handle schema changes safely over time
   - Ensure backward compatibility when possible

## Best Practices
- Follow database normalization principles
- Use clear and consistent naming conventions
- Avoid redundant data where possible
- Add indexes only where necessary
- Test migrations before applying to production
- Back up data before running destructive changes

## Example Structure
```sql
-- Create users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example migration
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true;
