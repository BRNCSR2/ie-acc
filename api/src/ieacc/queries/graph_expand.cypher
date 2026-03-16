// Expand a subgraph around a node for visualisation.
// Parameters: $entity_id (string), $depth (int)
// The caller constructs the MATCH clause dynamically based on entity_type.
MATCH (root)
WHERE root[$key_field] = $entity_id
MATCH path = (root)-[*1..2]-(connected)
WITH root, collect(DISTINCT connected) AS others,
     [r IN reduce(acc = [], p IN collect(path) |
       acc + relationships(p)) | r] AS allRels
WITH [root] + others AS allNodes, allRels
UNWIND allNodes AS n
WITH collect(DISTINCT {
  id: toString(elementId(n)),
  label: labels(n)[0],
  name: n.name,
  props: properties(n)
}) AS nodeList, allRels
UNWIND allRels AS r
WITH nodeList, collect(DISTINCT {
  source: toString(elementId(startNode(r))),
  target: toString(elementId(endNode(r))),
  type: type(r),
  props: properties(r)
}) AS edgeList
RETURN nodeList AS nodes, edgeList AS edges
