"""Neo4j driver utilities."""

import os
from pathlib import Path
from typing import Any

from fastapi import Request  # noqa: TC002
from neo4j import AsyncDriver  # noqa: TC002


def get_driver(request: Request) -> AsyncDriver:
    """Get the Neo4j async driver from app state."""
    return request.app.state.neo4j_driver  # type: ignore[no-any-return]


def get_database() -> str:
    """Get the configured Neo4j database name."""
    return os.environ.get("NEO4J_DATABASE", "neo4j")


def load_query(name: str) -> str:
    """Load a Cypher query from the queries directory."""
    path = Path(__file__).parent / "queries" / f"{name}.cypher"
    return path.read_text()


async def execute_query(
    driver: AsyncDriver,
    query: str,
    params: dict[str, Any] | None = None,
    database: str | None = None,
) -> list[dict[str, Any]]:
    """Execute a Cypher query and return results as dicts."""
    db = database or get_database()
    async with driver.session(database=db) as session:
        result = await session.run(query, parameters=params or {})
        records = await result.data()
        return records
