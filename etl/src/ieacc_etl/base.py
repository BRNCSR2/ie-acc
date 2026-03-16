"""Abstract base class for all ETL pipelines."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)


class Pipeline(ABC):
    """Base class for ETL pipelines.

    Subclasses must define `name`, `source_id` and implement
    `extract()`, `transform()`, and `load()`.
    """

    name: str
    source_id: str

    def __init__(
        self,
        driver: Driver,
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 50_000,
        neo4j_database: str | None = None,
    ) -> None:
        self.driver = driver
        self.data_dir = data_dir
        self.limit = limit
        self.chunk_size = chunk_size
        self.neo4j_database = neo4j_database

        self.rows_in: int = 0
        self.rows_loaded: int = 0
        self.extracted: bool = False
        self.transformed: bool = False
        self.loaded: bool = False
        self._run_id: str = f"{self.source_id}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"

    @abstractmethod
    def extract(self) -> None:
        """Download / read raw data from source."""

    @abstractmethod
    def transform(self) -> None:
        """Normalise, deduplicate, and validate data."""

    @abstractmethod
    def load(self) -> None:
        """Load transformed data into Neo4j."""

    def run(self) -> None:
        """Execute the full ETL pipeline with operational tracking."""
        started_at = datetime.now(UTC).isoformat()
        self._upsert_ingestion_run(status="running", started_at=started_at)

        try:
            logger.info("Pipeline %s: extracting", self.name)
            self.extract()
            self.extracted = True

            logger.info("Pipeline %s: transforming (%d rows)", self.name, self.rows_in)
            self.transform()
            self.transformed = True

            logger.info("Pipeline %s: loading", self.name)
            self.load()
            self.loaded = True

            finished_at = datetime.now(UTC).isoformat()
            self._upsert_ingestion_run(
                status="loaded",
                started_at=started_at,
                finished_at=finished_at,
            )
            logger.info(
                "Pipeline %s: done — %d rows in, %d loaded",
                self.name,
                self.rows_in,
                self.rows_loaded,
            )
        except Exception as exc:
            finished_at = datetime.now(UTC).isoformat()
            self._upsert_ingestion_run(
                status="failed",
                started_at=started_at,
                finished_at=finished_at,
                error=str(exc),
            )
            logger.exception("Pipeline %s failed", self.name)
            raise

    def _upsert_ingestion_run(
        self,
        *,
        status: str,
        started_at: str | None = None,
        finished_at: str | None = None,
        error: str | None = None,
    ) -> None:
        """Persist pipeline run state to Neo4j as an IngestionRun node."""
        params: dict[str, Any] = {
            "run_id": self._run_id,
            "source_id": self.source_id,
            "pipeline": self.name,
            "status": status,
            "rows_in": self.rows_in,
            "rows_loaded": self.rows_loaded,
        }
        if started_at:
            params["started_at"] = started_at
        if finished_at:
            params["finished_at"] = finished_at
        if error:
            params["error"] = error

        query = """
        MERGE (ir:IngestionRun {run_id: $run_id})
        SET ir += $props
        """
        try:
            with self.driver.session(database=self.neo4j_database) as session:
                session.run(query, run_id=self._run_id, props=params)
        except Exception:
            logger.warning("Failed to upsert IngestionRun for %s", self._run_id, exc_info=True)
