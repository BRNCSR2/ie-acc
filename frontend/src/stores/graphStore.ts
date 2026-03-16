import { create } from "zustand";
import { getGraphExpansion, type GraphData } from "../api/client";

interface GraphState {
  graphData: GraphData | null;
  selectedNode: string | null;
  loading: boolean;
  error: string | null;
  fetchGraph: (type: string, id: string, depth?: number) => Promise<void>;
  setSelectedNode: (id: string | null) => void;
  clear: () => void;
}

export const useGraphStore = create<GraphState>((set) => ({
  graphData: null,
  selectedNode: null,
  loading: false,
  error: null,

  fetchGraph: async (type, id, depth = 2) => {
    set({ loading: true, error: null });
    try {
      const graphData = await getGraphExpansion(type, id, depth);
      set({ graphData, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false, graphData: null });
    }
  },

  setSelectedNode: (id) => set({ selectedNode: id }),

  clear: () => set({ graphData: null, selectedNode: null, error: null }),
}));
