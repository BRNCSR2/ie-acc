import { useNavigate } from "react-router";
import SearchBar from "../components/SearchBar";
import { useSearchStore } from "../stores/searchStore";

export default function Landing() {
  const navigate = useNavigate();
  const search = useSearchStore((s) => s.search);

  const handleSearch = (q: string) => {
    search(q);
    navigate(`/search?q=${encodeURIComponent(q)}`);
  };

  return (
    <main
      style={{
        maxWidth: 800,
        margin: "0 auto",
        padding: "4rem 2rem",
        fontFamily: "system-ui",
        textAlign: "center",
      }}
    >
      <h1 style={{ fontSize: "2.5rem", marginBottom: "0.25rem" }}>ie-acc</h1>
      <p style={{ fontSize: "1.2rem", color: "#555", marginBottom: "2rem" }}>
        Irish Open Transparency Graph
      </p>
      <SearchBar onSearch={handleSearch} />
      <p style={{ marginTop: "2rem", color: "#888", fontSize: "0.9rem" }}>
        Search across companies, directors, charities, politicians, lobbyists, contracts, and more.
      </p>

      <nav
        style={{
          display: "flex",
          gap: "1rem",
          justifyContent: "center",
          marginTop: "2rem",
          flexWrap: "wrap",
        }}
      >
        {[
          { href: "/patterns", label: "Intelligence Patterns" },
          { href: "/investigations", label: "Investigations" },
          { href: "/sources", label: "Data Sources" },
        ].map((link) => (
          <a
            key={link.href}
            href={link.href}
            style={{
              padding: "0.5rem 1rem",
              border: "1px solid #ddd",
              borderRadius: 8,
              textDecoration: "none",
              color: "#1a73e8",
              fontSize: "0.9rem",
            }}
          >
            {link.label}
          </a>
        ))}
      </nav>
    </main>
  );
}
