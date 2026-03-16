"""Neo4j batch loader with UNWIND-based operations."""

from __future__ import annotations

import logging
import re
import time
from typing import TYPE_CHECKING, Any

from neo4j.exceptions import TransientError

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)

_VALID_KEY = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


class Neo4jBatchLoader:
    """Efficient batch loader for Neo4j using UNWIND operations."""

    def __init__(
        self,
        driver: Driver,
        batch_size: int = 10_000,
        neo4j_database: str | None = None,
    ) -> None:
        self.driver = driver
        self.batch_size = batch_size
        self.neo4j_database = neo4j_database

    def load_nodes(
        self,
        label: str,
        rows: list[dict[str, Any]],
        key_field: str,
    ) -> int:
        """MERGE nodes by key_field, set all other properties.

        Returns the number of rows processed.
        """
        if not rows:
            return 0

        # Filter rows with empty/None keys
        valid_rows = [r for r in rows if r.get(key_field)]

        # Build SET clause from first row's keys (excluding key_field)
        sample = valid_rows[0] if valid_rows else {}
        props = [k for k in sample if k != key_field and _VALID_KEY.match(k)]
        set_parts = ", ".join(f"n.{k} = row.{k}" for k in props)
        set_clause = f"SET {set_parts}" if set_parts else ""

        query = f"""
        UNWIND $rows AS row
        MERGE (n:{label} {{{key_field}: row.{key_field}}})
        {set_clause}
        """

        total = 0
        for i in range(0, len(valid_rows), self.batch_size):
            batch = valid_rows[i : i + self.batch_size]
            self._execute(query, batch)
            total += len(batch)
            if total % 100_000 == 0:
                logger.info("load_nodes %s: %d rows", label, total)

        return total

    def load_relationships(
        self,
        rel_type: str,
        rows: list[dict[str, Any]],
        source_label: str,
        source_key: str,
        target_label: str,
        target_key: str,
        properties: list[str] | None = None,
    ) -> int:
        """MERGE relationships between existing nodes.

        Returns the number of rows processed.
        """
        if not rows:
            return 0

        # Filter rows missing either key
        valid_rows = [r for r in rows if r.get(source_key) and r.get(target_key)]

        prop_parts = ""
        if properties:
            safe = [p for p in properties if _VALID_KEY.match(p)]
            prop_parts = ", ".join(f"r.{p} = row.{p}" for p in safe)
            prop_parts = f"SET {prop_parts}" if prop_parts else ""

        query = f"""
        UNWIND $rows AS row
        MATCH (a:{source_label} {{{source_key}: row.{source_key}}})
        MATCH (b:{target_label} {{{target_key}: row.{target_key}}})
        MERGE (a)-[r:{rel_type}]->(b)
        {prop_parts}
        """

        total = 0
        for i in range(0, len(valid_rows), self.batch_size):
            batch = valid_rows[i : i + self.batch_size]
            self._execute(query, batch)
            total += len(batch)

        return total

    def run_query(self, query: str, rows: list[dict[str, Any]]) -> int:
        """Execute a raw Cypher query with UNWIND $rows."""
        if not rows:
            return 0

        total = 0
        for i in range(0, len(rows), self.batch_size):
            batch = rows[i : i + self.batch_size]
            self._execute(query, batch)
            total += len(batch)
        return total

    def run_query_with_retry(
        self,
        query: str,
        rows: list[dict[str, Any]],
        max_retries: int = 5,
    ) -> int:
        """Execute with exponential-backoff retry on transient errors."""
        if not rows:
            return 0

        total = 0
        for i in range(0, len(rows), self.batch_size):
            batch = rows[i : i + self.batch_size]
            for attempt in range(max_retries):
                try:
                    self._execute(query, batch)
                    total += len(batch)
                    break
                except TransientError:
                    if attempt == max_retries - 1:
                        logger.error("Batch at offset %d failed after %d retries", i, max_retries)
                        break
                    delay = 2**attempt
                    logger.warning("Transient error, retrying in %ds (attempt %d)", delay, attempt)
                    time.sleep(delay)
        return total

    def _execute(self, query: str, batch: list[dict[str, Any]]) -> None:
        with self.driver.session(database=self.neo4j_database) as session:
            session.run(query, rows=batch)
