import { create } from "zustand";
import {
  getConnections,
  getEntity,
  type Connection,
  type EntityDetail,
} from "../api/client";

interface EntityState {
  entity: EntityDetail | null;
  connections: Connection[];
  loading: boolean;
  error: string | null;
  fetchEntity: (type: string, id: string) => Promise<void>;
  clear: () => void;
}

export const useEntityStore = create<EntityState>((set) => ({
  entity: null,
  connections: [],
  loading: false,
  error: null,

  fetchEntity: async (type, id) => {
    set({ loading: true, error: null });
    try {
      const [entity, connections] = await Promise.all([
        getEntity(type, id),
        getConnections(type, id),
      ]);
      set({ entity, connections, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false, entity: null, connections: [] });
    }
  },

  clear: () => set({ entity: null, connections: [], error: null }),
}));
