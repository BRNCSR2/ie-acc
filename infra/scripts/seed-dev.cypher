// ============================================================
// ie-acc Synthetic Seed Data — Development Only
// ============================================================

// ── Companies ──
CREATE (c1:Company {company_number: "100001", name: "Greenfield Construction Ltd", company_type: "LTD", status: "Normal", address: "12 Grafton Street, Dublin 2", county: "Dublin", date_registered: "2010-03-15"});
CREATE (c2:Company {company_number: "100002", name: "Atlantic Consulting DAC", company_type: "DAC", status: "Normal", address: "45 Patrick Street, Cork", county: "Cork", date_registered: "2015-07-22"});
CREATE (c3:Company {company_number: "100003", name: "Celtic Waste Solutions PLC", company_type: "PLC", status: "Normal", address: "8 Eyre Square, Galway", county: "Galway", date_registered: "2008-01-10"});
CREATE (c4:Company {company_number: "100004", name: "Liffey Digital Services Ltd", company_type: "LTD", status: "Normal", address: "Unit 5, Sandyford Business Park, Dublin 18", county: "Dublin", date_registered: "2018-11-03"});
CREATE (c5:Company {company_number: "100005", name: "Burren Heritage CLG", company_type: "CLG", status: "Normal", address: "Main Street, Lisdoonvarna, Co. Clare", county: "Clare", date_registered: "2012-06-01"});

// ── Persons / Directors ──
CREATE (p1:Person:Director {person_id: "P001", director_id: "D001", name: "Sean O'Brien", county: "Dublin"});
CREATE (p2:Person:Director {person_id: "P002", director_id: "D002", name: "Aoife McCarthy", county: "Cork"});
CREATE (p3:Person:Director {person_id: "P003", director_id: "D003", name: "Ciaran MacNamara", county: "Galway"});
CREATE (p4:Person:Director {person_id: "P004", director_id: "D004", name: "Niamh Fitzpatrick", county: "Dublin"});
CREATE (p5:Person:Director {person_id: "P005", director_id: "D005", name: "Padraig Doyle", county: "Clare"});

// ── Director Relationships ──
MATCH (p:Person {person_id: "P001"}), (c:Company {company_number: "100001"}) CREATE (p)-[:DIRECTOR_OF {appointed: "2010-03-15"}]->(c);
MATCH (p:Person {person_id: "P001"}), (c:Company {company_number: "100004"}) CREATE (p)-[:DIRECTOR_OF {appointed: "2018-11-03"}]->(c);
MATCH (p:Person {person_id: "P002"}), (c:Company {company_number: "100002"}) CREATE (p)-[:DIRECTOR_OF {appointed: "2015-07-22"}]->(c);
MATCH (p:Person {person_id: "P003"}), (c:Company {company_number: "100003"}) CREATE (p)-[:DIRECTOR_OF {appointed: "2008-01-10"}]->(c);
MATCH (p:Person {person_id: "P004"}), (c:Company {company_number: "100004"}) CREATE (p)-[:DIRECTOR_OF {appointed: "2018-11-03"}]->(c);
MATCH (p:Person {person_id: "P005"}), (c:Company {company_number: "100005"}) CREATE (p)-[:DIRECTOR_OF {appointed: "2012-06-01"}]->(c);
// Cross-company directorship (pattern: director_network_contracts)
MATCH (p:Person {person_id: "P002"}), (c:Company {company_number: "100003"}) CREATE (p)-[:DIRECTOR_OF {appointed: "2016-04-01"}]->(c);

// ── TDs / Senators ──
CREATE (td1:TDOrSenator {member_id: "TD001", name: "Sean O'Brien", constituency: "Dublin Central", party: "Independent", house: "Dail"});
CREATE (td2:TDOrSenator {member_id: "TD002", name: "Maeve Gallagher", constituency: "Galway West", party: "Fine Gael", house: "Dail"});

// ── Charities (linked to CLG company) ──
CREATE (ch1:Charity {rcn: "20100001", name: "Burren Heritage Foundation", chy_number: "CHY20001", status: "Registered"});
CREATE (ch2:Charity {rcn: "20100002", name: "Dublin Youth Support", chy_number: "CHY20002", status: "Registered"});
CREATE (ch3:Charity {rcn: "20100003", name: "Cork Community Care", chy_number: "CHY20003", status: "Registered"});

// Charity → Company link
MATCH (ch:Charity {rcn: "20100001"}), (c:Company {company_number: "100005"}) CREATE (ch)-[:REGISTERED_AS]->(c);

// ── Trustees ──
CREATE (t1:Trustee {trustee_id: "T001", name: "Padraig Doyle"});
CREATE (t2:Trustee {trustee_id: "T002", name: "Roisin Kelly"});
MATCH (t:Trustee {trustee_id: "T001"}), (ch:Charity {rcn: "20100001"}) CREATE (t)-[:TRUSTEE_OF]->(ch);
MATCH (t:Trustee {trustee_id: "T002"}), (ch:Charity {rcn: "20100002"}) CREATE (t)-[:TRUSTEE_OF]->(ch);

// ── Contracting Authorities ──
CREATE (ca1:ContractingAuthority {authority_id: "CA001", name: "Dublin City Council"});
CREATE (ca2:ContractingAuthority {authority_id: "CA002", name: "Department of Housing"});

// ── Contracts (procurement) ──
CREATE (co1:Contract {contract_ref: "CON-2023-001", title: "Road Resurfacing Northside", value: 850000, award_date: "2023-06-15"});
CREATE (co2:Contract {contract_ref: "CON-2023-002", title: "IT Systems Upgrade", value: 420000, award_date: "2023-09-01"});
CREATE (co3:Contract {contract_ref: "CON-2024-001", title: "Waste Management Services", value: 1200000, award_date: "2024-02-20"});
CREATE (co4:Contract {contract_ref: "CON-2024-002", title: "Digital Transformation Consulting", value: 380000, award_date: "2024-05-10"});

// Contract → Company (awarded)
MATCH (co:Contract {contract_ref: "CON-2023-001"}), (c:Company {company_number: "100001"}) CREATE (co)-[:AWARDED_TO]->(c);
MATCH (co:Contract {contract_ref: "CON-2023-002"}), (c:Company {company_number: "100004"}) CREATE (co)-[:AWARDED_TO]->(c);
MATCH (co:Contract {contract_ref: "CON-2024-001"}), (c:Company {company_number: "100003"}) CREATE (co)-[:AWARDED_TO]->(c);
MATCH (co:Contract {contract_ref: "CON-2024-002"}), (c:Company {company_number: "100002"}) CREATE (co)-[:AWARDED_TO]->(c);

// Contract → Authority
MATCH (co:Contract {contract_ref: "CON-2023-001"}), (ca:ContractingAuthority {authority_id: "CA001"}) CREATE (co)-[:ISSUED_BY]->(ca);
MATCH (co:Contract {contract_ref: "CON-2023-002"}), (ca:ContractingAuthority {authority_id: "CA001"}) CREATE (co)-[:ISSUED_BY]->(ca);
MATCH (co:Contract {contract_ref: "CON-2024-001"}), (ca:ContractingAuthority {authority_id: "CA002"}) CREATE (co)-[:ISSUED_BY]->(ca);
MATCH (co:Contract {contract_ref: "CON-2024-002"}), (ca:ContractingAuthority {authority_id: "CA002"}) CREATE (co)-[:ISSUED_BY]->(ca);

// ── Lobbying Returns ──
// Pattern: lobbying_contract_overlap (Atlantic Consulting lobbied Dept of Housing, then got contract)
CREATE (lr1:LobbyingReturn {return_id: "LR001", subject: "Housing Policy Reform", period: "2023-Q3", date_published: "2023-10-15"});
CREATE (lr2:LobbyingReturn {return_id: "LR002", subject: "Waste Disposal Regulations", period: "2023-Q4", date_published: "2024-01-20"});
CREATE (lr3:LobbyingReturn {return_id: "LR003", subject: "Digital Government Strategy", period: "2024-Q1", date_published: "2024-04-15"});

CREATE (l1:Lobbyist {lobbyist_id: "LOB001", name: "Atlantic Consulting DAC", registration_number: "R001"});
CREATE (l2:Lobbyist {lobbyist_id: "LOB002", name: "Celtic Waste Solutions PLC", registration_number: "R002"});

// Lobbyist → Company
MATCH (l:Lobbyist {lobbyist_id: "LOB001"}), (c:Company {company_number: "100002"}) CREATE (l)-[:REGISTERED_AS]->(c);
MATCH (l:Lobbyist {lobbyist_id: "LOB002"}), (c:Company {company_number: "100003"}) CREATE (l)-[:REGISTERED_AS]->(c);

// LobbyingReturn → Lobbyist
MATCH (lr:LobbyingReturn {return_id: "LR001"}), (l:Lobbyist {lobbyist_id: "LOB001"}) CREATE (lr)-[:FILED_BY]->(l);
MATCH (lr:LobbyingReturn {return_id: "LR002"}), (l:Lobbyist {lobbyist_id: "LOB002"}) CREATE (lr)-[:FILED_BY]->(l);
MATCH (lr:LobbyingReturn {return_id: "LR003"}), (l:Lobbyist {lobbyist_id: "LOB001"}) CREATE (lr)-[:FILED_BY]->(l);

// LobbyingReturn → Public Official (who was lobbied)
CREATE (po1:PublicOfficial {official_id: "PO001", name: "Minister for Housing", department: "Department of Housing"});
MATCH (lr:LobbyingReturn {return_id: "LR001"}), (po:PublicOfficial {official_id: "PO001"}) CREATE (lr)-[:LOBBIED]->(po);
MATCH (lr:LobbyingReturn {return_id: "LR002"}), (po:PublicOfficial {official_id: "PO001"}) CREATE (lr)-[:LOBBIED]->(po);

// ── EPA Licences ──
CREATE (epa1:EPALicence {licence_number: "W0100-01", licence_type: "Waste", holder_name: "Celtic Waste Solutions PLC", status: "Active"});
MATCH (epa:EPALicence {licence_number: "W0100-01"}), (c:Company {company_number: "100003"}) CREATE (epa)-[:HELD_BY]->(c);
