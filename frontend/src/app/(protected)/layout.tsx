// Simple pass-through layout - auth is handled in page.tsx
export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
