"""EPA (Environmental Protection Agency) ETL pipeline.

Ingests EPA licences from the LEAP database.
Creates EPALicence nodes and links to Company nodes via CRO number.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from ieacc_etl.base import Pipeline
from ieacc_etl.loader import Neo4jBatchLoader

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)


class EPAPipeline(Pipeline):
    """ETL pipeline for EPA licence data."""

    name = "epa"
    source_id = "epa"

    def __init__(
        self,
        driver: Driver,
        data_dir: str = "./data",
        limit: int | None = None,
        chunk_size: int = 50_000,
        neo4j_database: str | None = None,
    ) -> None:
        super().__init__(
            driver=driver,
            data_dir=data_dir,
            limit=limit,
            chunk_size=chunk_size,
            neo4j_database=neo4j_database,
        )
        self._df: pd.DataFrame = pd.DataFrame()
        self._licences: list[dict[str, Any]] = []
        self._licence_company_rels: list[dict[str, Any]] = []

    def extract(self) -> None:
        """Read EPA licences CSV."""
        data_path = Path(self.data_dir) / "epa"
        csv_path = data_path / "licences.csv"

        if not csv_path.exists():
            msg = f"EPA data not found at {csv_path}"
            raise FileNotFoundError(msg)

        self._df = pd.read_csv(csv_path, dtype=str, nrows=self.limit)
        self.rows_in = len(self._df)
        logger.info("Extracted %d EPA licences", self.rows_in)

    def transform(self) -> None:
        """Transform EPA licence data."""
        df = self._df

        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].str.strip()

        def _clean(val: object) -> str:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return ""
            return str(val).strip() if val else ""

        for _, row in df.iterrows():
            licence_number = _clean(row.get("licence_number"))
            if not licence_number:
                continue

            company_number = _clean(row.get("company_number"))

            self._licences.append({
                "licence_number": licence_number,
                "licence_type": _clean(row.get("licence_type")),
                "licensee_name": _clean(row.get("licensee_name")),
                "facility_name": _clean(row.get("facility_name")),
                "facility_address": _clean(row.get("facility_address")),
                "county": _clean(row.get("county")),
                "status": _clean(row.get("status")),
                "issue_date": _clean(row.get("issue_date")),
                "expiry_date": _clean(row.get("expiry_date")),
                "activity": _clean(row.get("activity")),
                "company_number": company_number,
            })

            if company_number:
                self._licence_company_rels.append({
                    "licence_number": licence_number,
                    "company_number": company_number,
                })

        self._df = pd.DataFrame()
        logger.info(
            "Transformed %d licences (%d with company links)",
            len(self._licences),
            len(self._licence_company_rels),
        )

    def load(self) -> None:
        """Load EPA licences into Neo4j."""
        loader = Neo4jBatchLoader(
            driver=self.driver,
            batch_size=self.chunk_size,
            neo4j_database=self.neo4j_database,
        )

        loader.load_nodes("EPALicence", self._licences, "licence_number")

        loader.load_relationships(
            "LICENSED_TO",
            self._licence_company_rels,
            "EPALicence", "licence_number",
            "Company", "company_number",
        )

        self.rows_loaded = len(self._licences)
        logger.info("Loaded %d EPALicence nodes", self.rows_loaded)
