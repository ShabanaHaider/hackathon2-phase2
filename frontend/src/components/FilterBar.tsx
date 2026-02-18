"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { api, Tag, FilterParams } from "@/lib/api";

interface FilterBarProps {
  filters: FilterParams;
  onChange: (filters: FilterParams) => void;
}

export default function FilterBar({ filters, onChange }: FilterBarProps) {
  const [tags, setTags] = useState<Tag[]>([]);
  const [searchInput, setSearchInput] = useState(filters.q || "");
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    api.listTags().then(setTags).catch(() => {});
  }, []);

  const handleSearchChange = useCallback(
    (value: string) => {
      setSearchInput(value);
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        onChange({ ...filters, q: value || undefined });
      }, 300);
    },
    [filters, onChange]
  );

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  const updateFilter = (key: keyof FilterParams, value: string | undefined) => {
    onChange({ ...filters, [key]: value || undefined });
  };

  const hasActiveFilters = filters.status || filters.priority || filters.tag || filters.q;

  const clearFilters = () => {
    setSearchInput("");
    onChange({});
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm space-y-3">
      {/* Search */}
      <div className="relative">
        <svg
          className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <input
          type="text"
          value={searchInput}
          onChange={(e) => handleSearchChange(e.target.value)}
          placeholder="Search tasks..."
          className="w-full pl-10 pr-4 py-2.5 text-sm text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent placeholder-gray-400 transition-all duration-200"
        />
      </div>

      {/* Filters row */}
      <div className="flex flex-wrap gap-2 items-center">
        {/* Status filter */}
        <select
          value={filters.status || ""}
          onChange={(e) => updateFilter("status", e.target.value)}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-400"
        >
          <option value="">All status</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
        </select>

        {/* Priority filter */}
        <select
          value={filters.priority || ""}
          onChange={(e) => updateFilter("priority", e.target.value)}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-400"
        >
          <option value="">All priorities</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        {/* Tag filter */}
        <select
          value={filters.tag || ""}
          onChange={(e) => updateFilter("tag", e.target.value)}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-400"
        >
          <option value="">All tags</option>
          {tags.map((t) => (
            <option key={t.id} value={t.name}>
              {t.name}
            </option>
          ))}
        </select>

        {/* Sort by */}
        <select
          value={filters.sort_by || ""}
          onChange={(e) => updateFilter("sort_by", e.target.value)}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-400"
        >
          <option value="">Default sort</option>
          <option value="created_at">Created date</option>
          <option value="due_at">Due date</option>
          <option value="priority">Priority</option>
          <option value="title">Title</option>
        </select>

        {/* Sort order */}
        {filters.sort_by && (
          <button
            type="button"
            onClick={() =>
              updateFilter("sort_order", filters.sort_order === "desc" ? "asc" : "desc")
            }
            className="px-2.5 py-1.5 text-sm border border-gray-300 rounded-lg bg-white text-gray-700 hover:bg-gray-50 transition-colors"
            title={filters.sort_order === "desc" ? "Descending" : "Ascending"}
          >
            {filters.sort_order === "desc" ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
            )}
          </button>
        )}

        {/* Clear filters */}
        {hasActiveFilters && (
          <button
            type="button"
            onClick={clearFilters}
            className="px-3 py-1.5 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
          >
            Clear filters
          </button>
        )}
      </div>
    </div>
  );
}
