// Get 1-hop connections for an entity.
// Parameters: $entity_id (string)
// The caller constructs the MATCH clause dynamically based on entity_type.
MATCH (n)-[r]-(m)
WHERE n[$key_field] = $entity_id
RETURN
  labels(n)[0] AS source_type,
  type(r) AS relationship,
  properties(r) AS rel_props,
  labels(m)[0] AS target_type,
  id(m) AS target_neo4j_id,
  CASE labels(m)[0]
    WHEN 'Company' THEN m.company_number
    WHEN 'Person' THEN m.person_id
    WHEN 'Director' THEN m.director_id
    WHEN 'Charity' THEN m.rcn
    WHEN 'TDOrSenator' THEN m.member_id
    WHEN 'Lobbyist' THEN m.lobbyist_id
    WHEN 'Trustee' THEN m.trustee_id
    WHEN 'PublicOfficial' THEN m.official_id
    WHEN 'ContractingAuthority' THEN m.authority_id
    WHEN 'Contract' THEN m.contract_ref
    WHEN 'LobbyingReturn' THEN m.return_id
    WHEN 'EPALicence' THEN m.licence_number
    ELSE toString(id(m))
  END AS target_id,
  m.name AS target_name,
  properties(m) AS target_props
