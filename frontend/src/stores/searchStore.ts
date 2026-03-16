import { create } from "zustand";
import { searchEntities, type SearchResult } from "../api/client";

interface SearchState {
  query: string;
  results: SearchResult[];
  loading: boolean;
  error: string | null;
  setQuery: (q: string) => void;
  search: (q: string) => Promise<void>;
  clear: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  query: "",
  results: [],
  loading: false,
  error: null,

  setQuery: (q) => set({ query: q }),

  search: async (q) => {
    set({ loading: true, error: null, query: q });
    try {
      const results = await searchEntities(q);
      set({ results, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false, results: [] });
    }
  },

  clear: () => set({ query: "", results: [], error: null }),
}));
