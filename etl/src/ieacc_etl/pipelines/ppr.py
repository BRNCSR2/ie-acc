"""Property Price Register ETL pipeline.

Ingests property sales data from the Property Services Regulatory Authority.
Creates PropertySale nodes with price, address, and county.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from ieacc_etl.base import Pipeline
from ieacc_etl.loader import Neo4jBatchLoader
from ieacc_etl.transforms.address_parsing import extract_county

if TYPE_CHECKING:
    from neo4j import Driver

logger = logging.getLogger(__name__)


class PPRPipeline(Pipeline):
    """ETL pipeline for Property Price Register data."""

    name = "ppr"
    source_id = "ppr"

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
        self._sales: list[dict[str, Any]] = []

    def extract(self) -> None:
        """Read PPR sales CSV."""
        data_path = Path(self.data_dir) / "ppr"
        csv_path = data_path / "sales.csv"

        if not csv_path.exists():
            msg = f"PPR data not found at {csv_path}"
            raise FileNotFoundError(msg)

        self._df = pd.read_csv(
            csv_path, dtype=str, nrows=self.limit, encoding="latin-1"
        )
        # Normalise column names from real PPR format
        col_map = {
            "Date of Sale (dd/mm/yyyy)": "sale_date",
            "Address": "address",
            "County": "county",
            "Eircode": "eircode",
            "Not Full Market Price": "not_full_market_price",
            "VAT Exclusive": "vat_exclusive",
            "Description of Property": "description",
            "Property Size Description": "property_size_desc",
        }
        self._df.rename(columns=col_map, inplace=True)
        # Handle price column (may contain euro symbol and commas)
        price_col = next(
            (c for c in self._df.columns if "price" in c.lower()), None
        )
        if price_col and price_col != "price_eur":
            self._df.rename(columns={price_col: "price_eur"}, inplace=True)
        self.rows_in = len(self._df)
        logger.info("Extracted %d property sales", self.rows_in)

    def transform(self) -> None:
        """Transform property sales data."""
        df = self._df

        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].str.strip()

        def _clean(val: object) -> str:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return ""
            return str(val).strip() if val else ""

        for idx, row in df.iterrows():
            sale_id = _clean(row.get("sale_id"))
            if not sale_id:
                sale_id = f"PPR-{idx}"

            # Parse price — handle €123,456.00 format
            price_str = _clean(row.get("price_eur"))
            price_str = price_str.replace("\u20ac", "").replace(",", "").strip()
            try:
                price = float(price_str) if price_str else 0.0
            except ValueError:
                price = 0.0

            county = _clean(row.get("county"))
            if not county:
                county = extract_county(addr4=_clean(row.get("address"))) or ""

            self._sales.append({
                "sale_id": sale_id,
                "sale_date": _clean(row.get("sale_date")),
                "address": _clean(row.get("address")),
                "county": county,
                "eircode": _clean(row.get("eircode")),
                "price": price,
                "not_full_market_price": _clean(row.get("not_full_market_price")),
                "vat_exclusive": _clean(row.get("vat_exclusive")),
                "property_size": _clean(row.get("property_size_desc")),
                "description": _clean(row.get("description")),
            })

        self._df = pd.DataFrame()
        logger.info("Transformed %d property sales", len(self._sales))

    def load(self) -> None:
        """Load property sales into Neo4j."""
        loader = Neo4jBatchLoader(
            driver=self.driver,
            batch_size=self.chunk_size,
            neo4j_database=self.neo4j_database,
        )

        self.rows_loaded = loader.load_nodes(
            "PropertySale", self._sales, "sale_id"
        )

        logger.info("Loaded %d PropertySale nodes", self.rows_loaded)
