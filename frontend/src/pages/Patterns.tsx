import { useCallback, useEffect, useState } from "react";
import { listPatterns, runPattern, type PatternInfo, type PatternResult } from "../api/client";

export default function Patterns() {
  const [patterns, setPatterns] = useState<PatternInfo[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [result, setResult] = useState<PatternResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listPatterns()
      .then(setPatterns)
      .catch((err) => setError((err as Error).message));
  }, []);

  const handleRun = useCallback(async (name: string) => {
    setSelected(name);
    setLoading(true);
    setError(null);
    try {
      const data = await runPattern(name);
      setResult(data);
    } catch (err) {
      setError((err as Error).message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <main
      style={{
        maxWidth: 1000,
        margin: "0 auto",
        padding: "2rem",
        fontFamily: "system-ui",
      }}
    >
      <nav style={{ marginBottom: "1rem", fontSize: "0.9rem" }}>
        <a href="/" style={{ color: "#1a73e8" }}>Home</a>
        {" / "}
        <span>Intelligence Patterns</span>
      </nav>

      <h1>Intelligence Patterns</h1>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Predefined queries that identify noteworthy cross-source relationships.
      </p>

      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "2rem" }}>
        {patterns.map((p) => (
          <button
            key={p.name}
            onClick={() => handleRun(p.name)}
            style={{
              padding: "0.75rem 1rem",
              border: selected === p.name ? "2px solid #1a73e8" : "1px solid #ccc",
              borderRadius: 8,
              background: selected === p.name ? "#e8f0fe" : "#fff",
              cursor: "pointer",
              textAlign: "left",
              maxWidth: 300,
            }}
          >
            <strong style={{ display: "block", marginBottom: 4 }}>
              {p.name.replace(/_/g, " ")}
            </strong>
            <span style={{ fontSize: "0.8rem", color: "#666" }}>{p.description}</span>
          </button>
        ))}
      </div>

      {loading && <p>Running pattern...</p>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {result && (
        <div>
          <h2>
            {result.pattern.replace(/_/g, " ")}
            <span style={{ fontWeight: "normal", fontSize: "1rem", color: "#888", marginLeft: 8 }}>
              ({result.count} results)
            </span>
          </h2>

          {result.results.length === 0 && <p>No matches found.</p>}

          {result.results.length > 0 && (
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
                <thead>
                  <tr>
                    {Object.keys(result.results[0] ?? {}).map((key) => (
                      <th
                        key={key}
                        style={{
                          padding: "8px 12px",
                          borderBottom: "2px solid #ddd",
                          textAlign: "left",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {key.replace(/_/g, " ")}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.results.map((row, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid #eee" }}>
                      {Object.values(row).map((val, j) => (
                        <td key={j} style={{ padding: "6px 12px" }}>
                          {val != null ? String(val) : ""}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </main>
  );
}
