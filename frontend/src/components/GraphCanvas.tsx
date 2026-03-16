import { useCallback, useMemo } from "react";
import ForceGraph2D from "react-force-graph-2d";
import type { GraphData } from "../api/client";

interface GraphCanvasProps {
  data: GraphData;
  width?: number;
  height?: number;
  onNodeClick?: (nodeId: string, nodeLabel: string) => void;
}

const LABEL_COLORS: Record<string, string> = {
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

export default function GraphCanvas({
  data,
  width = 800,
  height = 600,
  onNodeClick,
}: GraphCanvasProps) {
  const graphData = useMemo(
    () => ({
      nodes: data.nodes.map((n) => ({
        id: n.id,
        label: n.label,
        name: n.name || n.id,
      })),
      links: data.edges.map((e) => ({
        source: e.source,
        target: e.target,
        type: e.type,
      })),
    }),
    [data],
  );

  const nodeColor = useCallback(
    (node: Record<string, unknown>) =>
      LABEL_COLORS[String(node["label"] ?? "")] ?? "#999",
    [],
  );

  const nodeLabel = useCallback(
    (node: Record<string, unknown>) =>
      `${String(node["name"] ?? "?")} (${String(node["label"] ?? "?")})`,
    [],
  );

  const handleNodeClick = useCallback(
    (node: Record<string, unknown>) => {
      if (onNodeClick && node.id != null) {
        onNodeClick(String(node.id), String(node["label"] ?? ""));
      }
    },
    [onNodeClick],
  );

  return (
    <ForceGraph2D
      graphData={graphData}
      width={width}
      height={height}
      nodeColor={nodeColor}
      nodeLabel={nodeLabel}
      onNodeClick={handleNodeClick}
      linkLabel="type"
      backgroundColor="#fafafa"
    />
  );
}
