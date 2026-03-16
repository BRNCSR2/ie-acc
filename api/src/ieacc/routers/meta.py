"""Meta endpoints: health, stats, source registry."""

import csv
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from neo4j import AsyncDriver  # noqa: TC002

from ieacc.neo4j_service import execute_query, get_database, get_driver

router = APIRouter(prefix="/api/v1/meta", tags=["meta"])


@router.get("/health")
async def neo4j_health(
    driver: AsyncDriver = Depends(get_driver),  # noqa: B008
) -> dict[str, str]:
    """Check Neo4j connectivity."""
    try:
        await driver.verify_connectivity()
        return {"status": "ok", "neo4j": "connected"}
    except Exception as exc:
        return {"status": "degraded", "neo4j": str(exc)}


@router.get("/stats")
async def stats(
    driver: AsyncDriver = Depends(get_driver),  # noqa: B008
) -> dict[str, Any]:
    """Return node and relationship counts by type."""
    db = get_database()

    node_query = """
    MATCH (n)
    WITH labels(n)[0] AS label, count(n) AS count
    RETURN label, count
    ORDER BY count DESC
    """
    rel_query = """
    MATCH ()-[r]->()
    WITH type(r) AS type, count(r) AS count
    RETURN type, count
    ORDER BY count DESC
    """

    nodes = await execute_query(driver, node_query, database=db)
    rels = await execute_query(driver, rel_query, database=db)

    return {
        "nodes": {r["label"]: r["count"] for r in nodes},
        "relationships": {r["type"]: r["count"] for r in rels},
    }


@router.get("/sources")
async def sources() -> list[dict[str, str]]:
    """Return the source registry."""
    registry_path = (
        Path(__file__).parent.parent.parent.parent.parent
        / "config"
        / "source_registry_ie.csv"
    )
    if not registry_path.exists():
        return []

    with open(registry_path) as f:
        reader = csv.DictReader(f)
        return list(reader)
