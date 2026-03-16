"""eTenders/OGP procurement ETL pipeline.

Ingests public procurement contracts from eTenders/data.gov.ie.
Creates Contract and ContractingAuthority nodes, links to Company (supplier).
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


class ETendersPipeline(Pipeline):
    """ETL pipeline for eTenders procurement data."""

    name = "etenders"
    source_id = "etenders"

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
        self._contracts: list[dict[str, Any]] = []
        self._authorities: list[dict[str, Any]] = []
        self._contract_supplier_rels: list[dict[str, Any]] = []
        self._contract_authority_rels: list[dict[str, Any]] = []

    def extract(self) -> None:
        """Read eTenders contracts CSV."""
        data_path = Path(self.data_dir) / "etenders"
        csv_path = data_path / "contracts.csv"

        if not csv_path.exists():
            msg = f"eTenders data not found at {csv_path}"
            raise FileNotFoundError(msg)

        self._df = pd.read_csv(
            csv_path, dtype=str, nrows=self.limit, encoding="latin-1"
        )
        # Normalise column names from real OGP format
        col_map = {
            "Name of Contracting Authority": "contracting_authority",
            "Name of Client Contracting Authority": "client_authority",
            "Title of Contract": "title",
            "Suppliers": "supplier_name",
            "ContractAwardConfirmedDate": "award_date",
            "Contract Start Date": "start_date",
            "Contract End Date": "end_date",
            "Common Procurement Vocabulary (CPV) codes": "cpv_code",
        }
        self._df.rename(columns=col_map, inplace=True)
        self.rows_in = len(self._df)
        logger.info("Extracted %d contracts", self.rows_in)

    def transform(self) -> None:
        """Transform procurement data into graph entities."""
        df = self._df

        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].str.strip()

        def _clean(val: object) -> str:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return ""
            return str(val).strip() if val else ""

        seen_authorities: dict[str, dict[str, Any]] = {}

        for idx, row in df.iterrows():
            contract_ref = _clean(row.get("contract_ref"))
            if not contract_ref:
                contract_ref = f"OGP-{idx}"

            authority_name = _clean(row.get("contracting_authority"))
            authority_id = authority_name.replace(" ", "_")[:60] if authority_name else ""
            supplier_company = _clean(row.get("supplier_company_number"))

            # Parse value
            value_str = _clean(row.get("value_eur"))
            try:
                value = float(value_str) if value_str else 0.0
            except ValueError:
                value = 0.0

            self._contracts.append({
                "contract_ref": contract_ref,
                "title": _clean(row.get("title")),
                "supplier_name": _clean(row.get("supplier_name")),
                "value": value,
                "award_date": _clean(row.get("award_date")),
                "cpv_code": _clean(row.get("cpv_code")),
                "procedure_type": _clean(row.get("procedure_type")),
                "status": _clean(row.get("status")),
                "authority_id": authority_id,
            })

            # Deduplicate authorities
            if authority_id and authority_id not in seen_authorities:
                seen_authorities[authority_id] = {
                    "authority_id": authority_id,
                    "name": authority_name,
                }

            # Relationships
            if supplier_company:
                self._contract_supplier_rels.append({
                    "contract_ref": contract_ref,
                    "company_number": supplier_company,
                })

            if authority_id:
                self._contract_authority_rels.append({
                    "contract_ref": contract_ref,
                    "authority_id": authority_id,
                })

        self._authorities = list(seen_authorities.values())
        self._df = pd.DataFrame()
        logger.info(
            "Transformed %d contracts, %d authorities",
            len(self._contracts),
            len(self._authorities),
        )

    def load(self) -> None:
        """Load procurement data into Neo4j."""
        loader = Neo4jBatchLoader(
            driver=self.driver,
            batch_size=self.chunk_size,
            neo4j_database=self.neo4j_database,
        )

        loader.load_nodes("Contract", self._contracts, "contract_ref")
        loader.load_nodes("ContractingAuthority", self._authorities, "authority_id")

        loader.load_relationships(
            "AWARDED_TO",
            self._contract_supplier_rels,
            "Contract", "contract_ref",
            "Company", "company_number",
        )
        loader.load_relationships(
            "ISSUED_BY",
            self._contract_authority_rels,
            "Contract", "contract_ref",
            "ContractingAuthority", "authority_id",
        )

        self.rows_loaded = len(self._contracts)
        logger.info("Loaded %d Contract nodes", self.rows_loaded)
