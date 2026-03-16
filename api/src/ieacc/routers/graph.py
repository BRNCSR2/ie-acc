"""Graph expansion endpoint for visualisation."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import AsyncDriver  # noqa: TC002

from ieacc.neo4j_service import execute_query, get_driver

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


@router.get("/expand")
async def expand(
    entity_type: str = Query(..., description="Entity type (e.g., company, person)"),
    entity_id: str = Query(..., description="Entity unique identifier"),
    depth: int = Query(2, ge=1, le=4, description="Expansion depth (1-4)"),
    driver: AsyncDriver = Depends(get_driver),  # noqa: B008
) -> dict[str, Any]:
    """Expand a subgraph around an entity for visualisation."""
    from ieacc.routers.entity import _resolve_type

    label, key_field = _resolve_type(entity_type)

    query = f"""
    MATCH (root:{label})
    WHERE root.{key_field} = $entity_id
    MATCH path = (root)-[*1..{depth}]-(connected)
    WITH root, collect(DISTINCT connected) AS others,
         [r IN reduce(acc = [], p IN collect(path) |
           acc + relationships(p)) | r] AS allRels
    WITH [root] + others AS allNodes, allRels
    UNWIND allNodes AS n
    WITH collect(DISTINCT {{
      id: toString(elementId(n)),
      label: labels(n)[0],
      name: n.name,
      props: properties(n)
    }}) AS nodeList, allRels
    UNWIND allRels AS r
    WITH nodeList, collect(DISTINCT {{
      source: toString(elementId(startNode(r))),
      target: toString(elementId(endNode(r))),
      type: type(r),
      props: properties(r)
    }}) AS edgeList
    RETURN nodeList AS nodes, edgeList AS edges
    """

    records = await execute_query(
        driver, query, params={"entity_id": entity_id, "depth": depth}
    )

    if not records:
        raise HTTPException(status_code=404, detail=f"{label} {entity_id} not found")

    return {
        "nodes": records[0].get("nodes", []),
        "edges": records[0].get("edges", []),
    }
