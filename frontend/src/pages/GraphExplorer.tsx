import { useEffect } from "react";
import { useNavigate, useParams } from "react-router";
import GraphCanvas from "../components/GraphCanvas";
import { useGraphStore } from "../stores/graphStore";

export default function GraphExplorer() {
  const { type, id } = useParams<{ type: string; id: string }>();
  const navigate = useNavigate();
  const { graphData, loading, error, fetchGraph } = useGraphStore();

  useEffect(() => {
    if (type && id) fetchGraph(type, id);
  }, [type, id, fetchGraph]);

  const handleNodeClick = (nodeId: string, nodeLabel: string) => {
    navigate(`/entity/${nodeLabel.toLowerCase()}/${nodeId}`);
  };

  return (
    <main
      style={{
        maxWidth: 1200,
        margin: "0 auto",
        padding: "1rem 2rem",
        fontFamily: "system-ui",
      }}
    >
      <nav style={{ marginBottom: "1rem", fontSize: "0.9rem" }}>
        <a href="/" style={{ color: "#1a73e8" }}>Home</a>
        {type && id && (
          <>
            {" / "}
            <a
              href={`/entity/${type}/${id}`}
              style={{ color: "#1a73e8" }}
            >
              {type}/{id}
            </a>
            {" / "}
            <span>Graph</span>
          </>
        )}
      </nav>

      <h2>Graph Explorer</h2>

      {loading && <p>Loading graph...</p>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {graphData && graphData.nodes.length === 0 && <p>No graph data found.</p>}
      {graphData && graphData.nodes.length > 0 && (
        <div
          style={{
            border: "1px solid #e0e0e0",
            borderRadius: 8,
            overflow: "hidden",
          }}
        >
          <GraphCanvas data={graphData} onNodeClick={handleNodeClick} />
        </div>
      )}
    </main>
  );
}
