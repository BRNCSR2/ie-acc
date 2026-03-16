import { useEffect } from "react";
import { useSearchParams } from "react-router";
import EntityCard from "../components/EntityCard";
import SearchBar from "../components/SearchBar";
import { useSearchStore } from "../stores/searchStore";

export default function Search() {
  const [params, setParams] = useSearchParams();
  const { query, results, loading, error, search } = useSearchStore();

  const q = params.get("q") ?? "";

  useEffect(() => {
    if (q && q !== query) {
      search(q);
    }
  }, [q, query, search]);

  const handleSearch = (newQuery: string) => {
    setParams({ q: newQuery });
    search(newQuery);
  };

  return (
    <main
      style={{
        maxWidth: 800,
        margin: "0 auto",
        padding: "2rem",
        fontFamily: "system-ui",
      }}
    >
      <h2 style={{ marginBottom: "1rem" }}>
        <a href="/" style={{ textDecoration: "none", color: "inherit" }}>
          ie-acc
        </a>
      </h2>
      <SearchBar onSearch={handleSearch} initialValue={q} />

      <div style={{ marginTop: "1.5rem" }}>
        {loading && <p>Searching...</p>}
        {error && <p style={{ color: "red" }}>Error: {error}</p>}
        {!loading && results.length === 0 && q && <p>No results found.</p>}
        {results.map((r) => (
          <EntityCard
            key={`${r.entity_type}-${r.entity_id}`}
            entityType={r.entity_type}
            entityId={r.entity_id}
            name={r.name}
            score={r.score}
            props={r.props}
          />
        ))}
      </div>
    </main>
  );
}
