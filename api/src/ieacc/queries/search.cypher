// Fulltext search across all indexed entity types.
// Parameters: $query (string), $limit (int)
CALL db.index.fulltext.queryNodes("entity_search", $query)
YIELD node, score
WITH node, score, labels(node)[0] AS entity_type
RETURN
  entity_type,
  id(node) AS neo4j_id,
  score,
  CASE entity_type
    WHEN 'Company' THEN node.company_number
    WHEN 'Person' THEN node.person_id
    WHEN 'Director' THEN node.director_id
    WHEN 'Charity' THEN node.rcn
    WHEN 'TDOrSenator' THEN node.member_id
    WHEN 'Lobbyist' THEN node.lobbyist_id
    WHEN 'Trustee' THEN node.trustee_id
    WHEN 'PublicOfficial' THEN node.official_id
    WHEN 'ContractingAuthority' THEN node.authority_id
    ELSE toString(id(node))
  END AS entity_id,
  node.name AS name,
  properties(node) AS props
ORDER BY score DESC
LIMIT $limit
