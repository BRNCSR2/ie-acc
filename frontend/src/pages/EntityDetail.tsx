import { useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { useEntityStore } from "../stores/entityStore";

export default function EntityDetail() {
  const { type, id } = useParams<{ type: string; id: string }>();
  const navigate = useNavigate();
  const { entity, connections, loading, error, fetchEntity } = useEntityStore();

  useEffect(() => {
    if (type && id) fetchEntity(type, id);
  }, [type, id, fetchEntity]);

  if (loading) return <p style={{ padding: "2rem" }}>Loading...</p>;
  if (error) return <p style={{ padding: "2rem", color: "red" }}>Error: {error}</p>;
  if (!entity) return <p style={{ padding: "2rem" }}>Entity not found.</p>;

  const props = entity.props;

  return (
    <main
      style={{
        maxWidth: 900,
        margin: "0 auto",
        padding: "2rem",
        fontFamily: "system-ui",
      }}
    >
      <nav style={{ marginBottom: "1rem", fontSize: "0.9rem" }}>
        <a href="/" style={{ color: "#1a73e8" }}>Home</a>
        {" / "}
        <span>{entity.entity_type}</span>
      </nav>

      <h1>{String(props.name ?? entity.entity_id)}</h1>
      <span
        style={{
          background: "#1a73e8",
          color: "#fff",
          padding: "2px 10px",
          borderRadius: 4,
          fontSize: "0.8rem",
        }}
      >
        {entity.entity_type}
      </span>

      <table style={{ marginTop: "1.5rem", borderCollapse: "collapse", width: "100%" }}>
        <tbody>
          {Object.entries(props).map(([key, val]) => (
            <tr key={key} style={{ borderBottom: "1px solid #eee" }}>
              <td style={{ padding: "6px 12px", fontWeight: 600, color: "#555" }}>{key}</td>
              <td style={{ padding: "6px 12px" }}>{String(val ?? "")}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {connections.length > 0 && (
        <>
          <h2 style={{ marginTop: "2rem" }}>Connections ({connections.length})</h2>
          <div>
            {connections.map((c, i) => (
              <div
                key={i}
                style={{
                  padding: "0.75rem",
                  border: "1px solid #e0e0e0",
                  borderRadius: 6,
                  marginBottom: 6,
                }}
              >
                <span style={{ color: "#999", fontSize: "0.8rem" }}>{c.relationship}</span>
                {" \u2192 "}
                <strong>{c.target_name ?? "Unknown"}</strong>
                <span style={{ marginLeft: 8, color: "#888", fontSize: "0.8rem" }}>
                  ({c.target_type})
                </span>
              </div>
            ))}
          </div>
        </>
      )}

      <div style={{ marginTop: "2rem" }}>
        <Link
          to={`/graph/${type}/${id}`}
          style={{
            color: "#1a73e8",
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          View in Graph Explorer
        </Link>
        <button
          onClick={() => navigate(-1)}
          style={{
            marginLeft: "1rem",
            background: "none",
            border: "1px solid #ccc",
            borderRadius: 4,
            padding: "4px 12px",
            cursor: "pointer",
          }}
        >
          Back
        </button>
      </div>
    </main>
  );
}
