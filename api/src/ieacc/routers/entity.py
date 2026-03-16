"""Entity endpoints: detail view and connections."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path
from neo4j import AsyncDriver  # noqa: TC002

from ieacc.neo4j_service import execute_query, get_driver

router = APIRouter(prefix="/api/v1/entity", tags=["entity"])

# Map entity type to its unique key field
_KEY_FIELDS: dict[str, str] = {
    "company": "company_number",
    "person": "person_id",
    "director": "director_id",
    "charity": "rcn",
    "contract": "contract_ref",
    "contractingauthority": "authority_id",
    "lobbyingreturn": "return_id",
    "lobbyist": "lobbyist_id",
    "publicofficial": "official_id",
    "tdorsenator": "member_id",
    "epalicence": "licence_number",
    "planningapplication": "planning_ref",
    "propertysale": "sale_id",
    "electoraldivision": "ed_code",
    "trustee": "trustee_id",
    "bill": "bill_id",
    "parliamentaryquestion": "question_id",
}

# Map entity type to its Neo4j label
_LABELS: dict[str, str] = {
    "company": "Company",
    "person": "Person",
    "director": "Director",
    "charity": "Charity",
    "contract": "Contract",
    "contractingauthority": "ContractingAuthority",
    "lobbyingreturn": "LobbyingReturn",
    "lobbyist": "Lobbyist",
    "publicofficial": "PublicOfficial",
    "tdorsenator": "TDOrSenator",
    "epalicence": "EPALicence",
    "planningapplication": "PlanningApplication",
    "propertysale": "PropertySale",
    "electoraldivision": "ElectoralDivision",
    "trustee": "Trustee",
    "bill": "Bill",
    "parliamentaryquestion": "ParliamentaryQuestion",
}


def _resolve_type(entity_type: str) -> tuple[str, str]:
    """Resolve entity type to (Neo4j label, key field). Raises 404 if invalid."""
    key = entity_type.lower().replace("_", "")
    label = _LABELS.get(key)
    key_field = _KEY_FIELDS.get(key)
    if not label or not key_field:
        raise HTTPException(status_code=404, detail=f"Unknown entity type: {entity_type}")
    return label, key_field


@router.get("/{entity_type}/{entity_id}")
async def get_entity(
    entity_type: str = Path(..., description="Entity type (e.g., company, person, charity)"),
    entity_id: str = Path(..., description="Entity unique identifier"),
    driver: AsyncDriver = Depends(get_driver),  # noqa: B008
) -> dict[str, Any]:
    """Get entity detail by type and ID."""
    label, key_field = _resolve_type(entity_type)

    # Use parameterised label match for safety
    query = f"MATCH (n:{label}) WHERE n.{key_field} = $entity_id RETURN properties(n) AS props"
    records = await execute_query(driver, query, params={"entity_id": entity_id})

    if not records:
        raise HTTPException(status_code=404, detail=f"{label} {entity_id} not found")

    return {
        "entity_type": label,
        "entity_id": entity_id,
        "props": records[0]["props"],
    }


@router.get("/{entity_type}/{entity_id}/connections")
async def get_connections(
    entity_type: str = Path(..., description="Entity type"),
    entity_id: str = Path(..., description="Entity unique identifier"),
    driver: AsyncDriver = Depends(get_driver),  # noqa: B008
) -> list[dict[str, Any]]:
    """Get 1-hop connections for an entity."""
    label, key_field = _resolve_type(entity_type)

    query = f"""
    MATCH (n:{label})-[r]-(m)
    WHERE n.{key_field} = $entity_id
    RETURN
      type(r) AS relationship,
      properties(r) AS rel_props,
      labels(m)[0] AS target_type,
      properties(m) AS target_props,
      m.name AS target_name
    """

    records = await execute_query(driver, query, params={"entity_id": entity_id})

    return [
        {
            "relationship": r["relationship"],
            "rel_props": r["rel_props"],
            "target_type": r["target_type"],
            "target_name": r["target_name"],
            "target_props": r["target_props"],
        }
        for r in records
    ]
