import { useEffect, useState } from "react";
import { listSources, type SourceInfo } from "../api/client";

const STATUS_COLORS: Record<string, string> = {
  loaded: "#4caf50",
  partial: "#ff9800",
  not_built: "#9e9e9e",
  blocked: "#e53935",
};

const PRIORITY_LABELS: Record<string, string> = {
  P0: "Core",
  P1: "Secondary",
  P2: "Tertiary",
  P3: "Future",
};

export default function Sources() {
  const [sources, setSources] = useState<SourceInfo[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listSources()
      .then(setSources)
      .catch((err) => setError((err as Error).message));
  }, []);

  const grouped = sources.reduce<Record<string, SourceInfo[]>>((acc, s) => {
    const cat = s.category || "other";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(s);
    return acc;
  }, {});

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
        <a href="/" style={{ color: "#1a73e8" }}>
          Home
        </a>
        {" / "}
        <span>Data Sources</span>
      </nav>

      <h1>Data Sources</h1>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Status of all Irish public data sources tracked by the transparency
        graph.
      </p>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      <div
        style={{
          display: "flex",
          gap: "1rem",
          marginBottom: "1.5rem",
          flexWrap: "wrap",
        }}
      >
        {Object.entries(STATUS_COLORS).map(([status, color]) => (
          <span
            key={status}
            style={{ display: "flex", alignItems: "center", gap: 4 }}
          >
            <span
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: color,
                display: "inline-block",
              }}
            />
            <span style={{ fontSize: "0.85rem" }}>
              {status.replace("_", " ")}
            </span>
          </span>
        ))}
      </div>

      {Object.entries(grouped).map(([category, items]) => (
        <div key={category} style={{ marginBottom: "2rem" }}>
          <h2
            style={{
              fontSize: "1.1rem",
              textTransform: "capitalize",
              borderBottom: "1px solid #ddd",
              paddingBottom: 4,
            }}
          >
            {category}
          </h2>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              fontSize: "0.9rem",
            }}
          >
            <thead>
              <tr>
                <th
                  style={{
                    padding: "8px",
                    textAlign: "left",
                    borderBottom: "2px solid #ddd",
                  }}
                >
                  Source
                </th>
                <th
                  style={{
                    padding: "8px",
                    textAlign: "left",
                    borderBottom: "2px solid #ddd",
                  }}
                >
                  Status
                </th>
                <th
                  style={{
                    padding: "8px",
                    textAlign: "left",
                    borderBottom: "2px solid #ddd",
                  }}
                >
                  Priority
                </th>
                <th
                  style={{
                    padding: "8px",
                    textAlign: "left",
                    borderBottom: "2px solid #ddd",
                  }}
                >
                  Format
                </th>
                <th
                  style={{
                    padding: "8px",
                    textAlign: "left",
                    borderBottom: "2px solid #ddd",
                  }}
                >
                  Key
                </th>
                <th
                  style={{
                    padding: "8px",
                    textAlign: "left",
                    borderBottom: "2px solid #ddd",
                  }}
                >
                  Notes
                </th>
              </tr>
            </thead>
            <tbody>
              {items.map((s) => (
                <tr
                  key={s.source_id}
                  style={{ borderBottom: "1px solid #eee" }}
                >
                  <td style={{ padding: "6px 8px" }}>
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noreferrer"
                      style={{ color: "#1a73e8", textDecoration: "none" }}
                    >
                      {s.name}
                    </a>
                  </td>
                  <td style={{ padding: "6px 8px" }}>
                    <span
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: 4,
                      }}
                    >
                      <span
                        style={{
                          width: 8,
                          height: 8,
                          borderRadius: "50%",
                          background: STATUS_COLORS[s.status] || "#9e9e9e",
                        }}
                      />
                      {s.status.replace("_", " ")}
                    </span>
                  </td>
                  <td style={{ padding: "6px 8px" }}>
                    {PRIORITY_LABELS[s.priority] || s.priority}
                  </td>
                  <td style={{ padding: "6px 8px" }}>{s.format}</td>
                  <td style={{ padding: "6px 8px", fontFamily: "monospace" }}>
                    {s.identifier}
                  </td>
                  <td
                    style={{
                      padding: "6px 8px",
                      color: "#666",
                      fontSize: "0.85rem",
                    }}
                  >
                    {s.notes}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </main>
  );
}
