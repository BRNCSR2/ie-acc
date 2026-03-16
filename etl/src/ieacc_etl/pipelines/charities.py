"""Charities Regulator ETL pipeline.

Ingests charity register data from the Charities Regulator.
Creates Charity nodes, links to Company nodes via CRO number (for CLGs).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from ieacc_etl.base import Pipeline
from ieacc_etl.loader import Neo4jBatchLoader
from ieacc_etl.transforms.name_normalisation import normalise_company_name

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)


class CharitiesPipeline(Pipeline):
    """ETL pipeline for Charities Regulator data."""

    name = "charities"
    source_id = "charities"

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
        self._charities: list[dict[str, Any]] = []
        self._charity_company_rels: list[dict[str, Any]] = []

    def extract(self) -> None:
        """Read charities CSV or XLSX from data directory."""
        data_path = Path(self.data_dir) / "charities"
        csv_path = data_path / "charities.csv"
        xlsx_path = data_path / "charities.xlsx"

        if csv_path.exists():
            self._df = pd.read_csv(csv_path, dtype=str, nrows=self.limit)
        elif xlsx_path.exists():
            self._df = pd.read_excel(
                xlsx_path, dtype=str, nrows=self.limit
            )
        else:
            msg = f"Charities data not found. Expected {csv_path} or {xlsx_path}"
            raise FileNotFoundError(msg)

        self.rows_in = len(self._df)
        logger.info("Extracted %d charities", self.rows_in)

    def transform(self) -> None:
        """Transform charities data into graph entities."""
        df = self._df

        # Strip whitespace
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].str.strip()

        def _clean(val: object) -> str:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return ""
            return str(val).strip() if val else ""

        for _, row in df.iterrows():
            rcn = _clean(row.get("rcn"))
            if not rcn:
                continue

            name = normalise_company_name(_clean(row.get("charity_name")))
            company_number = _clean(row.get("company_number"))

            # Build address
            addr_parts = [
                _clean(row.get("address_1")),
                _clean(row.get("address_2")),
                _clean(row.get("address_3")),
                _clean(row.get("address_4")),
            ]
            address = ", ".join(p for p in addr_parts if p)

            self._charities.append({
                "rcn": rcn,
                "name": name,
                "status": _clean(row.get("status")),
                "address": address,
                "charitable_purpose": _clean(row.get("charitable_purpose")),
                "beneficiaries": _clean(row.get("beneficiaries")),
                "date_registered": _clean(row.get("date_registered")),
                "company_number": company_number,
            })

            # Link charity to company if CRO number exists
            if company_number:
                self._charity_company_rels.append({
                    "rcn": rcn,
                    "company_number": company_number,
                })

        self._df = pd.DataFrame()
        logger.info(
            "Transformed %d charities (%d with CRO links)",
            len(self._charities),
            len(self._charity_company_rels),
        )

    def load(self) -> None:
        """Load charities into Neo4j."""
        loader = Neo4jBatchLoader(
            driver=self.driver,
            batch_size=self.chunk_size,
            neo4j_database=self.neo4j_database,
        )

        loader.load_nodes("Charity", self._charities, "rcn")

        loader.load_relationships(
            "REGISTERED_AS",
            self._charity_company_rels,
            "Charity", "rcn",
            "Company", "company_number",
        )

        self.rows_loaded = len(self._charities)
        logger.info("Loaded %d Charity nodes", self.rows_loaded)
