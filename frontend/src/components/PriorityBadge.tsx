"use client";

const priorityConfig = {
  high: { label: "High", className: "bg-red-100 text-red-800 border-red-200" },
  medium: { label: "Medium", className: "bg-yellow-100 text-yellow-800 border-yellow-200" },
  low: { label: "Low", className: "bg-blue-100 text-blue-800 border-blue-200" },
};

interface PriorityBadgeProps {
  priority: "low" | "medium" | "high";
}

export default function PriorityBadge({ priority }: PriorityBadgeProps) {
  const config = priorityConfig[priority] || priorityConfig.medium;
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full border ${config.className}`}
    >
      {config.label}
    </span>
  );
}
