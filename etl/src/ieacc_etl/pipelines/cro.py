"""CRO (Companies Registration Office) ETL pipeline.

Ingests the full Irish company register from opendata.cro.ie.
Creates Company nodes and Director nodes (future: from annual returns).
"""

from __future__ import annotations

import logging
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from ieacc_etl.base import Pipeline
from ieacc_etl.loader import Neo4jBatchLoader
from ieacc_etl.schemas.cro import cro_company_schema
from ieacc_etl.transforms.address_parsing import (
    build_full_address,
    extract_county,
    extract_eircode,
)
from ieacc_etl.transforms.name_normalisation import normalise_company_name

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)

# CRO bulk CSV columns
CRO_COLUMNS = [
    "company_num",
    "company_name",
    "company_status_code",
    "company_status",
    "company_type_code",
    "company_type",
    "company_reg_date",
    "last_ar_date",
    "company_address_1",
    "company_address_2",
    "company_address_3",
    "company_address_4",
    "comp_dissolved_date",
    "nard",
    "last_accounts_date",
    "company_status_date",
    "nace_v2_code",
    "eircode",
    "company_name_eff_date",
    "company_type_eff_date",
    "princ_object_code",
]


class CROPipeline(Pipeline):
    """ETL pipeline for CRO company register data."""

    name = "cro"
    source_id = "cro"

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
        self._companies: list[dict[str, object]] = []

    def extract(self) -> None:
        """Read CRO companies CSV from data directory."""
        data_path = Path(self.data_dir) / "cro"
        csv_path = data_path / "companies.csv"
        zip_path = data_path / "companies.csv.zip"

        if csv_path.exists():
            logger.info("Reading %s", csv_path)
            self._df = pd.read_csv(
                csv_path,
                dtype=str,
                nrows=self.limit,
            )
        elif zip_path.exists():
            logger.info("Reading %s", zip_path)
            with zipfile.ZipFile(zip_path, "r") as zf:
                csv_name = next(
                    (n for n in zf.namelist() if n.endswith(".csv")),
                    zf.namelist()[0],
                )
                with zf.open(csv_name) as f:
                    self._df = pd.read_csv(
                        f,
                        dtype=str,
                        nrows=self.limit,
                    )
        else:
            msg = f"CRO data not found. Expected {csv_path} or {zip_path}"
            raise FileNotFoundError(msg)

        self.rows_in = len(self._df)
        logger.info("Extracted %d companies", self.rows_in)

    def transform(self) -> None:
        """Normalise and validate CRO company data."""
        df = self._df

        # Strip whitespace from all string columns
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].str.strip()

        # Normalise company names
        df["company_name"] = df["company_name"].apply(normalise_company_name)

        # Strip status (CRO has trailing spaces on some values)
        df["company_status"] = df["company_status"].str.strip()

        # Extract county from address fields
        df["county"] = df.apply(  # type: ignore[call-overload]
            lambda r: extract_county(
                r.get("company_address_1"),
                r.get("company_address_2"),
                r.get("company_address_3"),
                r.get("company_address_4"),
            ),
            axis=1,
        )

        # Extract or use existing eircode
        df["eircode_extracted"] = df.apply(  # type: ignore[call-overload]
            lambda r: extract_eircode(
                r.get("company_address_1"),
                r.get("company_address_2"),
                r.get("company_address_3"),
                r.get("company_address_4"),
            ),
            axis=1,
        )
        # Prefer the dedicated eircode column, fall back to extracted
        df["eircode"] = df["eircode"].fillna(df["eircode_extracted"])

        # Build full address
        df["address"] = df.apply(
            lambda r: build_full_address(
                r.get("company_address_1"),
                r.get("company_address_2"),
                r.get("company_address_3"),
                r.get("company_address_4"),
            ),
            axis=1,
        )

        # Coerce company_num to int
        df["company_num"] = pd.to_numeric(df["company_num"], errors="coerce")
        df = df.dropna(subset=["company_num"])
        df["company_num"] = df["company_num"].astype(int)

        # Validate schema
        validated = cro_company_schema.validate(df, lazy=True)

        # Build company records for loading
        def _clean(val: object) -> str:
            """Convert a value to string, treating NaN/None as empty."""
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return ""
            return str(val).strip() if val else ""

        self._companies = []
        for _, row in validated.iterrows():
            self._companies.append({
                "company_number": str(int(row["company_num"])),
                "name": row["company_name"],
                "status": _clean(row.get("company_status")),
                "company_type": _clean(row.get("company_type")),
                "date_registered": _clean(row.get("company_reg_date")),
                "county": _clean(row.get("county")),
                "address": _clean(row.get("address")),
                "eircode": _clean(row.get("eircode")),
                "nace_code": _clean(row.get("nace_v2_code")),
                "last_ar_date": _clean(row.get("last_ar_date")),
                "dissolved_date": _clean(row.get("comp_dissolved_date")),
                "status_date": _clean(row.get("company_status_date")),
            })

        self._df = pd.DataFrame()  # free memory
        logger.info("Transformed %d companies", len(self._companies))

    def load(self) -> None:
        """Load companies into Neo4j."""
        loader = Neo4jBatchLoader(
            driver=self.driver,
            batch_size=self.chunk_size,
            neo4j_database=self.neo4j_database,
        )

        self.rows_loaded = loader.load_nodes(
            label="Company",
            rows=self._companies,
            key_field="company_number",
        )

        logger.info("Loaded %d Company nodes", self.rows_loaded)
