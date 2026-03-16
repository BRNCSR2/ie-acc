import { useCallback, useEffect, useState } from "react";
import {
  listInvestigations,
  createInvestigation,
  deleteInvestigation,
  getInvestigation,
  type InvestigationSummary,
  type Investigation,
} from "../api/client";

export default function Investigations() {
  const [investigations, setInvestigations] = useState<InvestigationSummary[]>(
    [],
  );
  const [selected, setSelected] = useState<Investigation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState("");

  const refresh = useCallback(() => {
    listInvestigations()
      .then(setInvestigations)
      .catch((err) => setError((err as Error).message));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    setLoading(true);
    try {
      await createInvestigation(newTitle.trim());
      setNewTitle("");
      refresh();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (id: string) => {
    setLoading(true);
    try {
      const inv = await getInvestigation(id);
      setSelected(inv);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    setLoading(true);
    try {
      await deleteInvestigation(id);
      if (selected?.id === id) setSelected(null);
      refresh();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

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
        <span>Investigations</span>
      </nav>

      <h1>Investigations</h1>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Create and manage investigation workspaces for tracking entities and
        queries.
      </p>

      <div
        style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem" }}
      >
        <input
          type="text"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="New investigation title..."
          style={{
            flex: 1,
            padding: "0.5rem 0.75rem",
            border: "1px solid #ccc",
            borderRadius: 6,
            fontSize: "0.9rem",
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleCreate();
          }}
        />
        <button
          onClick={handleCreate}
          disabled={loading || !newTitle.trim()}
          style={{
            padding: "0.5rem 1rem",
            background: "#1a73e8",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
          }}
        >
          Create
        </button>
      </div>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      <div style={{ display: "flex", gap: "2rem" }}>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: "1.1rem" }}>
            All Investigations ({investigations.length})
          </h2>
          {investigations.length === 0 && (
            <p style={{ color: "#888" }}>No investigations yet.</p>
          )}
          {investigations.map((inv) => (
            <div
              key={inv.id}
              style={{
                padding: "0.75rem",
                border:
                  selected?.id === inv.id
                    ? "2px solid #1a73e8"
                    : "1px solid #ddd",
                borderRadius: 8,
                marginBottom: "0.5rem",
                cursor: "pointer",
                background: selected?.id === inv.id ? "#e8f0fe" : "#fff",
              }}
              onClick={() => handleSelect(inv.id)}
            >
              <strong>{inv.title}</strong>
              <div
                style={{ fontSize: "0.8rem", color: "#666", marginTop: 4 }}
              >
                {inv.annotation_count} annotations, {inv.query_count} queries
              </div>
              <div
                style={{ fontSize: "0.75rem", color: "#999", marginTop: 2 }}
              >
                {inv.created_at}
              </div>
            </div>
          ))}
        </div>

        {selected && (
          <div style={{ flex: 2 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <h2 style={{ fontSize: "1.1rem" }}>{selected.title}</h2>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <a
                  href={`/api/v1/investigations/${selected.id}/export?fmt=html`}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    padding: "4px 12px",
                    border: "1px solid #ccc",
                    borderRadius: 4,
                    fontSize: "0.8rem",
                    textDecoration: "none",
                    color: "#333",
                  }}
                >
                  Export HTML
                </a>
                <button
                  onClick={() => handleDelete(selected.id)}
                  style={{
                    padding: "4px 12px",
                    border: "1px solid #e53935",
                    borderRadius: 4,
                    background: "#fff",
                    color: "#e53935",
                    cursor: "pointer",
                    fontSize: "0.8rem",
                  }}
                >
                  Delete
                </button>
              </div>
            </div>

            {selected.description && (
              <p style={{ color: "#666" }}>{selected.description}</p>
            )}

            <h3 style={{ fontSize: "1rem", marginTop: "1rem" }}>
              Annotations ({selected.annotations.length})
            </h3>
            {selected.annotations.length === 0 ? (
              <p style={{ color: "#888", fontSize: "0.9rem" }}>
                No annotations yet.
              </p>
            ) : (
              <table
                style={{
                  width: "100%",
                  borderCollapse: "collapse",
                  fontSize: "0.85rem",
                }}
              >
                <thead>
                  <tr>
                    <th
                      style={{
                        padding: "6px 8px",
                        borderBottom: "2px solid #ddd",
                        textAlign: "left",
                      }}
                    >
                      Entity
                    </th>
                    <th
                      style={{
                        padding: "6px 8px",
                        borderBottom: "2px solid #ddd",
                        textAlign: "left",
                      }}
                    >
                      Note
                    </th>
                    <th
                      style={{
                        padding: "6px 8px",
                        borderBottom: "2px solid #ddd",
                        textAlign: "left",
                      }}
                    >
                      Tags
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {selected.annotations.map((ann) => (
                    <tr
                      key={ann.id}
                      style={{ borderBottom: "1px solid #eee" }}
                    >
                      <td style={{ padding: "4px 8px" }}>
                        <a
                          href={`/entity/${ann.entity_type}/${ann.entity_id}`}
                          style={{ color: "#1a73e8" }}
                        >
                          {ann.entity_type}/{ann.entity_id}
                        </a>
                      </td>
                      <td style={{ padding: "4px 8px" }}>{ann.note}</td>
                      <td style={{ padding: "4px 8px" }}>
                        {ann.tags.join(", ")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            <h3 style={{ fontSize: "1rem", marginTop: "1rem" }}>
              Saved Queries ({selected.saved_queries.length})
            </h3>
            {selected.saved_queries.length === 0 ? (
              <p style={{ color: "#888", fontSize: "0.9rem" }}>
                No saved queries yet.
              </p>
            ) : (
              selected.saved_queries.map((sq) => (
                <div
                  key={sq.id}
                  style={{
                    padding: "0.5rem",
                    border: "1px solid #eee",
                    borderRadius: 4,
                    marginBottom: "0.5rem",
                  }}
                >
                  <strong>{sq.query_name}</strong>
                  {sq.description && (
                    <span style={{ color: "#666", marginLeft: 8 }}>
                      — {sq.description}
                    </span>
                  )}
                  <pre
                    style={{
                      background: "#f5f5f5",
                      padding: "0.5rem",
                      borderRadius: 4,
                      fontSize: "0.8rem",
                      overflow: "auto",
                      marginTop: 4,
                    }}
                  >
                    {sq.cypher}
                  </pre>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </main>
  );
}
