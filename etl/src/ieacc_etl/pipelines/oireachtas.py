"""Oireachtas ETL pipeline.

Ingests TD and Senator data from the Oireachtas API (api.oireachtas.ie).
Creates TDOrSenator nodes with member IDs, party, and constituency info.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ieacc_etl.base import Pipeline
from ieacc_etl.loader import Neo4jBatchLoader
from ieacc_etl.transforms.name_normalisation import normalise_person_name

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)


class OireachtasPipeline(Pipeline):
    """ETL pipeline for Oireachtas members data."""

    name = "oireachtas"
    source_id = "oireachtas"

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
        self._raw: list[dict[str, Any]] = []
        self._members: list[dict[str, Any]] = []

    def extract(self) -> None:
        """Read Oireachtas members JSON from data directory."""
        data_path = Path(self.data_dir) / "oireachtas"
        json_path = data_path / "members.json"

        if not json_path.exists():
            msg = f"Oireachtas data not found at {json_path}"
            raise FileNotFoundError(msg)

        with open(json_path) as f:
            data = json.load(f)

        self._raw = data.get("results", [])
        if self.limit:
            self._raw = self._raw[: self.limit]
        self.rows_in = len(self._raw)
        logger.info("Extracted %d Oireachtas members", self.rows_in)

    def transform(self) -> None:
        """Transform Oireachtas API data into member records."""
        for item in self._raw:
            member = item.get("member", {})
            member_code = member.get("memberCode", "")
            full_name = member.get("fullName", "")

            # House (Dáil or Seanad)
            house = member.get("house", {})
            house_name = house.get("showAs", "")
            house_code = house.get("houseCode", "")

            # Party
            party = member.get("party", {})
            party_name = party.get("showAs", "")

            # Constituency/Panel
            represents = member.get("represents", [])
            constituency = ""
            if represents:
                rep = represents[0].get("represent", {})
                constituency = rep.get("showAs", "")

            # Membership dates
            memberships = member.get("memberships", [])
            start_date = ""
            end_date = ""
            if memberships:
                date_range = memberships[0].get("membership", {}).get("dateRange", {})
                start_date = date_range.get("start", "")
                end_date = date_range.get("end", "")

            # Determine role
            role = "TD" if house_code == "dail" else "Senator"

            self._members.append({
                "member_id": member_code,
                "name": normalise_person_name(full_name),
                "first_name": member.get("firstName", ""),
                "last_name": member.get("lastName", ""),
                "house": house_name,
                "role": role,
                "party": party_name,
                "constituency": constituency,
                "start_date": start_date,
                "end_date": end_date,
                "gender": member.get("gender", ""),
            })

        logger.info("Transformed %d members", len(self._members))

    def load(self) -> None:
        """Load Oireachtas members into Neo4j."""
        loader = Neo4jBatchLoader(
            driver=self.driver,
            batch_size=self.chunk_size,
            neo4j_database=self.neo4j_database,
        )

        self.rows_loaded = loader.load_nodes(
            "TDOrSenator", self._members, "member_id"
        )

        logger.info("Loaded %d TDOrSenator nodes", self.rows_loaded)
