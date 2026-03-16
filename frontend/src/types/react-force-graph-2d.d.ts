declare module "react-force-graph-2d" {
  import { Component } from "react";

  interface NodeObject {
    id?: string | number;
    x?: number;
    y?: number;
    [key: string]: unknown;
  }

  interface LinkObject {
    source?: string | number | NodeObject;
    target?: string | number | NodeObject;
    [key: string]: unknown;
  }

  interface ForceGraphProps {
    graphData?: { nodes: NodeObject[]; links: LinkObject[] };
    width?: number;
    height?: number;
    nodeLabel?: string | ((node: NodeObject) => string);
    nodeColor?: string | ((node: NodeObject) => string);
    nodeVal?: string | number | ((node: NodeObject) => number);
    linkLabel?: string | ((link: LinkObject) => string);
    linkColor?: string | ((link: LinkObject) => string);
    onNodeClick?: (node: NodeObject) => void;
    onNodeHover?: (node: NodeObject | null) => void;
    backgroundColor?: string;
    [key: string]: unknown;
  }

  export default class ForceGraph2D extends Component<ForceGraphProps> {}
}
