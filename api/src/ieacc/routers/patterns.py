"""Intelligence patterns endpoint.

Executes predefined graph queries that identify noteworthy
cross-source relationships for investigative analysis.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncDriver  # noqa: TC002

from ieacc.neo4j_service import execute_query, get_driver

router = APIRouter(prefix="/api/v1/patterns", tags=["patterns"])

# Pattern definitions: name -> (description, Cypher query)
PATTERNS: dict[str, tuple[str, str]] = {
    "lobbying_contract_overlap": (
        "Companies that lobbied a government body and were subsequently awarded "
        "contracts by the same or related body.",
        """
        MATCH (lr:LobbyingReturn)-[:FILED_BY]->(l:Lobbyist)-[:REPRESENTS_COMPANY]->(c:Company)
        MATCH (co:Contract)-[:AWARDED_TO]->(c)
        WHERE lr.body_lobbied IS NOT NULL
        RETURN DISTINCT
          c.company_number AS company_number,
          c.name AS company_name,
          lr.body_lobbied AS body_lobbied,
          lr.subject_matter AS lobbying_subject,
          lr.period_from AS lobbying_period,
          co.contract_ref AS contract_ref,
          co.title AS contract_title,
          co.value AS contract_value,
          co.award_date AS award_date
        ORDER BY co.value DESC
        LIMIT 50
        """,
    ),
    "director_network_contracts": (
        "Companies sharing directors that supply the same contracting authority.",
        """
        MATCH (d:Director)-[:DIRECTOR_OF]->(c1:Company)<-[:AWARDED_TO]-(co1:Contract)
              -[:ISSUED_BY]->(auth:ContractingAuthority)
        MATCH (d)-[:DIRECTOR_OF]->(c2:Company)<-[:AWARDED_TO]-(co2:Contract)
              -[:ISSUED_BY]->(auth)
        WHERE c1 <> c2
        RETURN DISTINCT
          d.name AS shared_director,
          c1.name AS company_1,
          c2.name AS company_2,
          auth.name AS authority,
          co1.contract_ref AS contract_1_ref,
          co1.value AS contract_1_value,
          co2.contract_ref AS contract_2_ref,
          co2.value AS contract_2_value
        ORDER BY co1.value + co2.value DESC
        LIMIT 50
        """,
    ),
    "contract_concentration": (
        "Contracting authorities with excessive awards to a single supplier.",
        """
        MATCH (co:Contract)-[:AWARDED_TO]->(c:Company)
        MATCH (co)-[:ISSUED_BY]->(auth:ContractingAuthority)
        WITH auth, c, count(co) AS num_contracts, sum(co.value) AS total_value
        WHERE num_contracts >= 2
        RETURN
          auth.name AS authority,
          c.name AS supplier,
          c.company_number AS company_number,
          num_contracts,
          total_value
        ORDER BY num_contracts DESC, total_value DESC
        LIMIT 50
        """,
    ),
    "charity_director_overlap": (
        "Charity trustees who are also directors of companies receiving "
        "contracts or lobbying government.",
        """
        MATCH (ch:Charity)-[:REGISTERED_AS]->(c:Company)
        MATCH (d:Director)-[:DIRECTOR_OF]->(c)
        OPTIONAL MATCH (co:Contract)-[:AWARDED_TO]->(c)
        OPTIONAL MATCH (lr:LobbyingReturn)-[:FILED_BY]->(l:Lobbyist)
              -[:REPRESENTS_COMPANY]->(c)
        WHERE co IS NOT NULL OR lr IS NOT NULL
        RETURN DISTINCT
          ch.name AS charity_name,
          ch.rcn AS charity_rcn,
          c.name AS company_name,
          d.name AS director_name,
          CASE WHEN co IS NOT NULL THEN co.contract_ref ELSE null END AS contract_ref,
          CASE WHEN lr IS NOT NULL THEN lr.return_id ELSE null END AS lobbying_return
        LIMIT 50
        """,
    ),
    "epa_violator_contracts": (
        "Companies holding EPA licences (especially surrendered or under review) "
        "that also receive public contracts.",
        """
        MATCH (epa:EPALicence)-[:LICENSED_TO]->(c:Company)
        MATCH (co:Contract)-[:AWARDED_TO]->(c)
        RETURN DISTINCT
          c.company_number AS company_number,
          c.name AS company_name,
          epa.licence_number AS licence_number,
          epa.licence_type AS licence_type,
          epa.status AS licence_status,
          co.contract_ref AS contract_ref,
          co.title AS contract_title,
          co.value AS contract_value
        ORDER BY co.value DESC
        LIMIT 50
        """,
    ),
    "planning_director_links": (
        "Company directors linked to planning applications in areas "
        "where their companies operate.",
        """
        MATCH (d:Director)-[:DIRECTOR_OF]->(c:Company)
        MATCH (pa:PlanningApplication)
        WHERE c.county IS NOT NULL
          AND pa.county IS NOT NULL
          AND c.county = pa.county
        RETURN DISTINCT
          d.name AS director_name,
          c.name AS company_name,
          c.county AS county,
          pa.planning_ref AS planning_ref,
          pa.description AS planning_description,
          pa.status AS planning_status
        LIMIT 50
        """,
    ),
    "revolving_door": (
        "Individuals who appear in both Oireachtas (as TDs/Senators) and "
        "lobbying or company director records.",
        """
        MATCH (td:TDOrSenator)
        OPTIONAL MATCH (td)-[:SAME_AS]-(po:PublicOfficial)<-[:LOBBIED]-(lr:LobbyingReturn)
        OPTIONAL MATCH (d:Director)-[:DIRECTOR_OF]->(c:Company)
        WHERE d.name = td.name
        WITH td, lr, d, c
        WHERE lr IS NOT NULL OR d IS NOT NULL
        RETURN DISTINCT
          td.name AS politician_name,
          td.party AS party,
          td.constituency AS constituency,
          CASE WHEN d IS NOT NULL THEN c.name ELSE null END AS company_name,
          CASE WHEN lr IS NOT NULL THEN lr.return_id ELSE null END AS lobbying_return,
          CASE WHEN lr IS NOT NULL THEN lr.subject_matter ELSE null END AS lobbying_subject
        LIMIT 50
        """,
    ),
    "split_contracts_below_threshold": (
        "Potential contract splitting: multiple low-value contracts awarded to "
        "the same supplier by the same authority in a short period.",
        """
        MATCH (co:Contract)-[:AWARDED_TO]->(c:Company)
        MATCH (co)-[:ISSUED_BY]->(auth:ContractingAuthority)
        WHERE co.value < 25000
        WITH auth, c, collect(co) AS contracts, count(co) AS num_contracts,
             sum(co.value) AS total_value
        WHERE num_contracts >= 3
        RETURN
          auth.name AS authority,
          c.name AS supplier,
          c.company_number AS company_number,
          num_contracts,
          total_value,
          CASE WHEN total_value > 25000 THEN 'ABOVE_THRESHOLD' ELSE 'BELOW' END AS flag
        ORDER BY total_value DESC
        LIMIT 50
        """,
    ),
}


@router.get("/")
async def list_patterns() -> list[dict[str, str]]:
    """List all available intelligence patterns."""
    return [
        {"name": name, "description": desc}
        for name, (desc, _) in PATTERNS.items()
    ]


@router.get("/{pattern_name}")
async def run_pattern(
    pattern_name: str,
    driver: AsyncDriver = Depends(get_driver),  # noqa: B008
) -> dict[str, Any]:
    """Execute an intelligence pattern query and return results."""
    if pattern_name not in PATTERNS:
        available = ", ".join(sorted(PATTERNS.keys()))
        raise HTTPException(
            status_code=404,
            detail=f"Unknown pattern: {pattern_name}. Available: {available}",
        )

    description, query = PATTERNS[pattern_name]
    records = await execute_query(driver, query)

    return {
        "pattern": pattern_name,
        "description": description,
        "count": len(records),
        "results": records,
    }
