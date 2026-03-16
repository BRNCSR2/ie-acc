"""Search endpoint: fulltext search across all entity types."""

from typing import Any

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver  # noqa: TC002

from ieacc.neo4j_service import execute_query, get_driver, load_query

router = APIRouter(prefix="/api/v1", tags=["search"])

_SEARCH_QUERY = load_query("search")


@router.get("/search")
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    driver: AsyncDriver = Depends(get_driver),  # noqa: B008
) -> list[dict[str, Any]]:
    """Fulltext search across Company, Person, Charity, and other entities."""
    # Neo4j fulltext requires escaping special Lucene chars
    safe_query = _escape_lucene(q)

    records = await execute_query(
        driver,
        _SEARCH_QUERY,
        params={"query": safe_query, "limit": limit},
    )

    return [
        {
            "entity_type": r["entity_type"],
            "entity_id": r["entity_id"],
            "name": r["name"],
            "score": round(r["score"], 4),
            "props": _clean_props(r["props"]),
        }
        for r in records
    ]


def _escape_lucene(query: str) -> str:
    """Escape special Lucene query characters."""
    special = r'+-&|!(){}[]^"~*?:\/'
    escaped = []
    for ch in query:
        if ch in special:
            escaped.append(f"\\{ch}")
        else:
            escaped.append(ch)
    return "".join(escaped)


def _clean_props(props: dict[str, Any]) -> dict[str, Any]:
    """Remove internal props from results."""
    skip = {"_ingestion_run_id", "_source", "_updated_at"}
    return {k: v for k, v in props.items() if k not in skip}
