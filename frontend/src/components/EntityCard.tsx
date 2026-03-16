import { useNavigate } from "react-router";

interface EntityCardProps {
  entityType: string;
  entityId: string;
  name: string;
  score?: number;
  props?: Record<string, unknown>;
}

const TYPE_COLORS: Record<string, string> = {
  Company: "#1a73e8",
  Person: "#e67c00",
  Director: "#e67c00",
  Charity: "#0b8043",
  Contract: "#9334e6",
  TDOrSenator: "#d93025",
  Lobbyist: "#f09300",
  LobbyingReturn: "#f09300",
  ContractingAuthority: "#9334e6",
  EPALicence: "#188038",
};

export default function EntityCard({
  entityType,
  entityId,
  name,
  score,
  props,
}: EntityCardProps) {
  const navigate = useNavigate();
  const color = TYPE_COLORS[entityType] ?? "#666";

  return (
    <div
      onClick={() => navigate(`/entity/${entityType.toLowerCase()}/${entityId}`)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter")
          navigate(`/entity/${entityType.toLowerCase()}/${entityId}`);
      }}
      style={{
        padding: "1rem",
        border: "1px solid #e0e0e0",
        borderRadius: 8,
        cursor: "pointer",
        marginBottom: 8,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span
          style={{
            background: color,
            color: "#fff",
            padding: "2px 8px",
            borderRadius: 4,
            fontSize: "0.75rem",
            fontWeight: 600,
          }}
        >
          {entityType}
        </span>
        <strong>{name}</strong>
        {score !== undefined && (
          <span style={{ marginLeft: "auto", color: "#999", fontSize: "0.8rem" }}>
            {score.toFixed(2)}
          </span>
        )}
      </div>
      {props && (
        <div style={{ marginTop: 4, fontSize: "0.85rem", color: "#555" }}>
          {props.county ? <span>County {String(props.county)}</span> : null}
          {props.status ? <span> &middot; {String(props.status)}</span> : null}
          {props.company_type ? <span> &middot; {String(props.company_type)}</span> : null}
        </div>
      )}
    </div>
  );
}
