// Get entity detail by type and ID.
// Parameters: $entity_id (string)
// The caller constructs the MATCH clause dynamically based on entity_type.
MATCH (n)
WHERE n[$key_field] = $entity_id
RETURN
  labels(n)[0] AS entity_type,
  id(n) AS neo4j_id,
  properties(n) AS props
LIMIT 1
