"""Lobbying Register ETL pipeline.

Ingests lobbying returns from lobbying.ie.
Creates LobbyingReturn, Lobbyist, and PublicOfficial nodes
and links to Company nodes via CRO number.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from ieacc_etl.base import Pipeline
from ieacc_etl.loader import Neo4jBatchLoader
from ieacc_etl.transforms.name_normalisation import (
    generate_person_id,
    normalise_person_name,
)

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)


class LobbyingPipeline(Pipeline):
    """ETL pipeline for the Lobbying Register."""

    name = "lobbying"
    source_id = "lobbying"

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
        self._returns: list[dict[str, Any]] = []
        self._lobbyists: list[dict[str, Any]] = []
        self._officials: list[dict[str, Any]] = []
        self._lobbyist_company_rels: list[dict[str, Any]] = []
        self._return_lobbyist_rels: list[dict[str, Any]] = []
        self._return_official_rels: list[dict[str, Any]] = []

    def extract(self) -> None:
        """Read lobbying returns CSV."""
        data_path = Path(self.data_dir) / "lobbying"
        csv_path = data_path / "returns.csv"

        if not csv_path.exists():
            msg = f"Lobbying data not found at {csv_path}"
            raise FileNotFoundError(msg)

        self._df = pd.read_csv(csv_path, dtype=str, nrows=self.limit)
        self.rows_in = len(self._df)
        logger.info("Extracted %d lobbying returns", self.rows_in)

    def transform(self) -> None:
        """Transform lobbying returns into graph entities."""
        df = self._df

        # Strip whitespace
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].str.strip()

        seen_lobbyists: dict[str, dict[str, Any]] = {}
        seen_officials: dict[str, dict[str, Any]] = {}

        for _, row in df.iterrows():
            return_id = str(row["return_id"])
            lobbyist_name = str(row.get("lobbyist_name") or "")
            official_name = str(row.get("public_official_name") or "")
            company_number = str(row.get("company_number") or "")

            # Normalise names
            lobbyist_name_norm = normalise_person_name(lobbyist_name) if lobbyist_name else ""
            official_name_norm = normalise_person_name(official_name) if official_name else ""

            # Generate IDs
            lobbyist_id = generate_person_id(lobbyist_name, "lobbyist")
            official_id = generate_person_id(official_name, "official")

            # Build return record
            self._returns.append({
                "return_id": return_id,
                "subject_matter": str(row.get("subject_matter") or ""),
                "intended_results": str(row.get("intended_results") or ""),
                "body_lobbied": str(row.get("body_lobbied") or ""),
                "period_from": str(row.get("period_from") or ""),
                "period_to": str(row.get("period_to") or ""),
                "lobbyist_type": str(row.get("lobbyist_type") or ""),
            })

            # Deduplicate lobbyists
            if lobbyist_id not in seen_lobbyists and lobbyist_name:
                seen_lobbyists[lobbyist_id] = {
                    "lobbyist_id": lobbyist_id,
                    "name": lobbyist_name_norm or lobbyist_name,
                    "lobbyist_type": str(row.get("lobbyist_type") or ""),
                }

            # Deduplicate officials
            if official_id not in seen_officials and official_name:
                seen_officials[official_id] = {
                    "official_id": official_id,
                    "name": official_name_norm or official_name,
                    "title": str(row.get("public_official_title") or ""),
                }

            # Relationships
            self._return_lobbyist_rels.append({
                "return_id": return_id,
                "lobbyist_id": lobbyist_id,
            })
            self._return_official_rels.append({
                "return_id": return_id,
                "official_id": official_id,
            })
            if company_number:
                self._lobbyist_company_rels.append({
                    "lobbyist_id": lobbyist_id,
                    "company_number": company_number,
                })

        self._lobbyists = list(seen_lobbyists.values())
        self._officials = list(seen_officials.values())

        self._df = pd.DataFrame()
        logger.info(
            "Transformed %d returns, %d lobbyists, %d officials",
            len(self._returns),
            len(self._lobbyists),
            len(self._officials),
        )

    def load(self) -> None:
        """Load lobbying data into Neo4j."""
        loader = Neo4jBatchLoader(
            driver=self.driver,
            batch_size=self.chunk_size,
            neo4j_database=self.neo4j_database,
        )

        loader.load_nodes("LobbyingReturn", self._returns, "return_id")
        loader.load_nodes("Lobbyist", self._lobbyists, "lobbyist_id")
        loader.load_nodes("PublicOfficial", self._officials, "official_id")

        loader.load_relationships(
            "FILED_BY",
            self._return_lobbyist_rels,
            "LobbyingReturn", "return_id",
            "Lobbyist", "lobbyist_id",
        )
        loader.load_relationships(
            "LOBBIED",
            self._return_official_rels,
            "LobbyingReturn", "return_id",
            "PublicOfficial", "official_id",
        )
        loader.load_relationships(
            "REPRESENTS_COMPANY",
            self._lobbyist_company_rels,
            "Lobbyist", "lobbyist_id",
            "Company", "company_number",
        )

        self.rows_loaded = len(self._returns)
        logger.info("Loaded %d lobbying returns", self.rows_loaded)
