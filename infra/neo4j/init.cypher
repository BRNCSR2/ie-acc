// ============================================================
// ie-acc Neo4j Schema — Irish Open Transparency Graph
// ============================================================

// ── Node Constraints (unique keys) ──

CREATE CONSTRAINT company_number IF NOT EXISTS
FOR (c:Company) REQUIRE c.company_number IS UNIQUE;

CREATE CONSTRAINT person_id IF NOT EXISTS
FOR (p:Person) REQUIRE p.person_id IS UNIQUE;

CREATE CONSTRAINT director_id IF NOT EXISTS
FOR (d:Director) REQUIRE d.director_id IS UNIQUE;

CREATE CONSTRAINT charity_rcn IF NOT EXISTS
FOR (ch:Charity) REQUIRE ch.rcn IS UNIQUE;

CREATE CONSTRAINT contract_ref IF NOT EXISTS
FOR (co:Contract) REQUIRE co.contract_ref IS UNIQUE;

CREATE CONSTRAINT contracting_authority_id IF NOT EXISTS
FOR (ca:ContractingAuthority) REQUIRE ca.authority_id IS UNIQUE;

CREATE CONSTRAINT lobbying_return_id IF NOT EXISTS
FOR (lr:LobbyingReturn) REQUIRE lr.return_id IS UNIQUE;

CREATE CONSTRAINT lobbyist_id IF NOT EXISTS
FOR (l:Lobbyist) REQUIRE l.lobbyist_id IS UNIQUE;

CREATE CONSTRAINT public_official_id IF NOT EXISTS
FOR (po:PublicOfficial) REQUIRE po.official_id IS UNIQUE;

CREATE CONSTRAINT td_or_senator_member_id IF NOT EXISTS
FOR (t:TDOrSenator) REQUIRE t.member_id IS UNIQUE;

CREATE CONSTRAINT epa_licence_number IF NOT EXISTS
FOR (e:EPALicence) REQUIRE e.licence_number IS UNIQUE;

CREATE CONSTRAINT planning_ref IF NOT EXISTS
FOR (pa:PlanningApplication) REQUIRE pa.planning_ref IS UNIQUE;

CREATE CONSTRAINT property_sale_id IF NOT EXISTS
FOR (ps:PropertySale) REQUIRE ps.sale_id IS UNIQUE;

CREATE CONSTRAINT electoral_division_code IF NOT EXISTS
FOR (ed:ElectoralDivision) REQUIRE ed.ed_code IS UNIQUE;

CREATE CONSTRAINT small_area_code IF NOT EXISTS
FOR (sa:SmallArea) REQUIRE sa.sa_code IS UNIQUE;

CREATE CONSTRAINT school_roll IF NOT EXISTS
FOR (s:School) REQUIRE s.roll_number IS UNIQUE;

CREATE CONSTRAINT ingestion_run_id IF NOT EXISTS
FOR (ir:IngestionRun) REQUIRE ir.run_id IS UNIQUE;

CREATE CONSTRAINT source_document_id IF NOT EXISTS
FOR (sd:SourceDocument) REQUIRE sd.doc_id IS UNIQUE;

CREATE CONSTRAINT trustee_id IF NOT EXISTS
FOR (t:Trustee) REQUIRE t.trustee_id IS UNIQUE;

CREATE CONSTRAINT bill_id IF NOT EXISTS
FOR (b:Bill) REQUIRE b.bill_id IS UNIQUE;

CREATE CONSTRAINT parliamentary_question_id IF NOT EXISTS
FOR (pq:ParliamentaryQuestion) REQUIRE pq.question_id IS UNIQUE;

// ── Indexes ──

CREATE INDEX company_name IF NOT EXISTS
FOR (c:Company) ON (c.name);

CREATE INDEX company_status IF NOT EXISTS
FOR (c:Company) ON (c.status);

CREATE INDEX company_type IF NOT EXISTS
FOR (c:Company) ON (c.company_type);

CREATE INDEX person_name IF NOT EXISTS
FOR (p:Person) ON (p.name);

CREATE INDEX person_name_county IF NOT EXISTS
FOR (p:Person) ON (p.name, p.county);

CREATE INDEX director_name IF NOT EXISTS
FOR (d:Director) ON (d.name);

CREATE INDEX charity_name IF NOT EXISTS
FOR (ch:Charity) ON (ch.name);

CREATE INDEX contract_value IF NOT EXISTS
FOR (co:Contract) ON (co.value);

CREATE INDEX epa_licence_type IF NOT EXISTS
FOR (e:EPALicence) ON (e.licence_type);

CREATE INDEX property_sale_date IF NOT EXISTS
FOR (ps:PropertySale) ON (ps.sale_date);

CREATE INDEX property_sale_county IF NOT EXISTS
FOR (ps:PropertySale) ON (ps.county);

CREATE INDEX ingestion_run_source IF NOT EXISTS
FOR (ir:IngestionRun) ON (ir.source_id);

// ── Fulltext Search Index ──

CREATE FULLTEXT INDEX entity_search IF NOT EXISTS
FOR (c:Company|Person|Director|Charity|Lobbyist|TDOrSenator|Trustee|PublicOfficial|ContractingAuthority)
ON EACH [c.name, c.company_number, c.rcn, c.member_id, c.description];
