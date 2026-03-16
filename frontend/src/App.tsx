import { Route, Routes } from "react-router";
import Landing from "./pages/Landing";
import Search from "./pages/Search";
import EntityDetail from "./pages/EntityDetail";
import GraphExplorer from "./pages/GraphExplorer";
import Patterns from "./pages/Patterns";
import Investigations from "./pages/Investigations";
import Sources from "./pages/Sources";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/search" element={<Search />} />
      <Route path="/entity/:type/:id" element={<EntityDetail />} />
      <Route path="/graph/:type/:id" element={<GraphExplorer />} />
      <Route path="/patterns" element={<Patterns />} />
      <Route path="/investigations" element={<Investigations />} />
      <Route path="/sources" element={<Sources />} />
    </Routes>
  );
}
