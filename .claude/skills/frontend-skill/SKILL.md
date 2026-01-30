---
name: frontend-skill
description: Build frontend user interfaces including pages, reusable components, layouts, and styling. Use for client-side application development.
---

# Frontend Development Skill

## Instructions

1. **Page construction**
   - Build application pages using a component-based approach
   - Structure pages for clarity and maintainability
   - Handle routing and navigation appropriately

2. **Component development**
   - Create reusable and composable UI components
   - Pass data via props or state management
   - Keep components focused on a single responsibility

3. **Layout and structure**
   - Design responsive layouts using modern CSS techniques
   - Use grids or flexbox for alignment and spacing
   - Maintain consistent layout patterns across pages

4. **Styling**
   - Apply clean and consistent styling
   - Use utility classes or component-level styles where appropriate
   - Ensure visual consistency across the application

## Best Practices
- Use a mobile-first and responsive design approach
- Keep components small and reusable
- Maintain consistent spacing, typography, and color usage
- Separate layout, logic, and presentation concerns
- Ensure accessibility basics (semantic HTML, contrast, focus states)

## Example Structure
```jsx
function PageLayout({ children }) {
  return (
    <div className="layout">
      <header className="header">Header</header>
      <main className="content">{children}</main>
      <footer className="footer">Footer</footer>
    </div>
  );
}

function Button({ label }) {
  return <button className="btn-primary">{label}</button>;
}
