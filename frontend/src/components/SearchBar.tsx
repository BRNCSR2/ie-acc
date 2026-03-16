import { useCallback, useRef, useState } from "react";

interface SearchBarProps {
  onSearch: (query: string) => void;
  initialValue?: string;
  placeholder?: string;
}

export default function SearchBar({
  onSearch,
  initialValue = "",
  placeholder = "Search companies, people, charities\u2026",
}: SearchBarProps) {
  const [value, setValue] = useState(initialValue);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const v = e.target.value;
      setValue(v);
      if (timerRef.current) clearTimeout(timerRef.current);
      if (v.trim().length >= 2) {
        timerRef.current = setTimeout(() => onSearch(v.trim()), 300);
      }
    },
    [onSearch],
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (timerRef.current) clearTimeout(timerRef.current);
    if (value.trim()) onSearch(value.trim());
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", gap: 8 }}>
      <input
        type="text"
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        aria-label="Search"
        style={{
          flex: 1,
          padding: "0.75rem 1rem",
          fontSize: "1rem",
          border: "1px solid #ccc",
          borderRadius: 6,
        }}
      />
      <button
        type="submit"
        style={{
          padding: "0.75rem 1.5rem",
          fontSize: "1rem",
          background: "#1a73e8",
          color: "#fff",
          border: "none",
          borderRadius: 6,
          cursor: "pointer",
        }}
      >
        Search
      </button>
    </form>
  );
}
