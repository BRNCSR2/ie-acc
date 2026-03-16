const API_BASE = "/api/v1";

async function fetchJSON<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(path, window.location.origin);
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      url.searchParams.set(k, v);
    }
  }
  const res = await fetch(url.toString());
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

// --- Types ---

export interface SearchResult {
  entity_type: string;
  entity_id: string;
  name: string;
  score: number;
  props: Record<string, unknown>;
}

export interface EntityDetail {
  entity_type: string;
  entity_id: string;
  props: Record<string, unknown>;
}

export interface Connection {
  relationship: string;
  rel_props: Record<string, unknown>;
  target_type: string;
  target_name: string;
  target_props: Record<string, unknown>;
}

export interface GraphNode {
  id: string;
  label: string;
  name: string;
  props: Record<string, unknown>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  props: Record<string, unknown>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface StatsData {
  nodes: Record<string, number>;
  relationships: Record<string, number>;
}

// --- API calls ---

export function searchEntities(q: string, limit = 20): Promise<SearchResult[]> {
  return fetchJSON<SearchResult[]>(`${API_BASE}/search`, {
    q,
    limit: String(limit),
  });
}

export function getEntity(entityType: string, entityId: string): Promise<EntityDetail> {
  return fetchJSON<EntityDetail>(`${API_BASE}/entity/${entityType}/${entityId}`);
}

export function getConnections(entityType: string, entityId: string): Promise<Connection[]> {
  return fetchJSON<Connection[]>(`${API_BASE}/entity/${entityType}/${entityId}/connections`);
}

export function getGraphExpansion(
  entityType: string,
  entityId: string,
  depth = 2,
): Promise<GraphData> {
  return fetchJSON<GraphData>(`${API_BASE}/graph/expand`, {
    entity_type: entityType,
    entity_id: entityId,
    depth: String(depth),
  });
}

export function getStats(): Promise<StatsData> {
  return fetchJSON<StatsData>(`${API_BASE}/meta/stats`);
}

export interface PatternInfo {
  name: string;
  description: string;
}

export interface PatternResult {
  pattern: string;
  description: string;
  count: number;
  results: Record<string, unknown>[];
}

export function listPatterns(): Promise<PatternInfo[]> {
  return fetchJSON<PatternInfo[]>(`${API_BASE}/patterns/`);
}

export function runPattern(patternName: string): Promise<PatternResult> {
  return fetchJSON<PatternResult>(`${API_BASE}/patterns/${patternName}`);
}

// --- Investigations ---

export interface Investigation {
  id: string;
  title: string;
  description: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  annotations: Annotation[];
  saved_queries: SavedQuery[];
}

export interface InvestigationSummary {
  id: string;
  title: string;
  description: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  annotation_count: number;
  query_count: number;
}

export interface Annotation {
  id: string;
  entity_type: string;
  entity_id: string;
  note: string;
  tags: string[];
  created_at: string;
}

export interface SavedQuery {
  id: string;
  query_name: string;
  cypher: string;
  description: string;
  created_at: string;
}

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

async function deleteJSON<T>(path: string): Promise<T> {
  const res = await fetch(path, { method: "DELETE" });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function listInvestigations(): Promise<InvestigationSummary[]> {
  return fetchJSON<InvestigationSummary[]>(`${API_BASE}/investigations/`);
}

export function getInvestigation(id: string): Promise<Investigation> {
  return fetchJSON<Investigation>(`${API_BASE}/investigations/${id}`);
}

export function createInvestigation(
  title: string,
  description = "",
  tags: string[] = [],
): Promise<Investigation> {
  return postJSON<Investigation>(`${API_BASE}/investigations/`, {
    title,
    description,
    tags,
  });
}

export function deleteInvestigation(id: string): Promise<{ status: string }> {
  return deleteJSON<{ status: string }>(`${API_BASE}/investigations/${id}`);
}

export function addAnnotation(
  investigationId: string,
  entityType: string,
  entityId: string,
  note: string,
  tags: string[] = [],
): Promise<Annotation> {
  return postJSON<Annotation>(
    `${API_BASE}/investigations/${investigationId}/annotations`,
    { entity_type: entityType, entity_id: entityId, note, tags },
  );
}

export function addSavedQuery(
  investigationId: string,
  queryName: string,
  cypher: string,
  description = "",
): Promise<SavedQuery> {
  return postJSON<SavedQuery>(
    `${API_BASE}/investigations/${investigationId}/queries`,
    { query_name: queryName, cypher, description },
  );
}

// --- Sources ---

export interface SourceInfo {
  source_id: string;
  name: string;
  category: string;
  url: string;
  access_method: string;
  format: string;
  status: string;
  priority: string;
  identifier: string;
  notes: string;
}

export function listSources(): Promise<SourceInfo[]> {
  return fetchJSON<SourceInfo[]>(`${API_BASE}/meta/sources`);
}
