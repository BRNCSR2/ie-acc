"""Tests for the Property Price Register ETL pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from ieacc_etl.pipelines.ppr import PPRPipeline

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline(limit: int | None = None) -> PPRPipeline:
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__ = MagicMock(return_value=session)
    driver.session.return_value.__exit__ = MagicMock(return_value=False)
    return PPRPipeline(
        driver=driver,
        data_dir=str(FIXTURES),
        limit=limit,
    )


class TestPPRExtract:
    def test_extract_reads_csv(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        assert pipeline.rows_in == 10

    def test_extract_with_limit(self) -> None:
        pipeline = _make_pipeline(limit=5)
        pipeline.extract()
        assert pipeline.rows_in == 5

    def test_extract_missing_file_raises(self) -> None:
        driver = MagicMock()
        session = MagicMock()
        driver.session.return_value.__enter__ = MagicMock(return_value=session)
        driver.session.return_value.__exit__ = MagicMock(return_value=False)
        pipeline = PPRPipeline(driver=driver, data_dir="/nonexistent")
        try:
            pipeline.extract()
            raise AssertionError("Should have raised")
        except FileNotFoundError:
            pass


class TestPPRTransform:
    def test_transform_creates_sales(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline._sales) == 10

    def test_transform_parses_price(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        sale = next(
            s for s in pipeline._sales if s["sale_id"] == "PPR-2024-001"
        )
        assert sale["price"] == 450000.0

    def test_transform_sale_fields(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        sale = next(
            s for s in pipeline._sales if s["sale_id"] == "PPR-2024-001"
        )
        assert sale["county"] == "Dublin"
        assert sale["address"] == "12 Grafton Street"
        assert sale["eircode"] == "D02 VX88"
        assert sale["sale_date"] == "2024-01-15"

    def test_transform_missing_eircode(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        sale = next(
            s for s in pipeline._sales if s["sale_id"] == "PPR-2024-006"
        )
        assert sale["eircode"] == ""

    def test_transform_highest_price(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        sale = next(
            s for s in pipeline._sales if s["sale_id"] == "PPR-2024-005"
        )
        assert sale["price"] == 1200000.0

    def test_transform_county_preserved(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        counties = {s["county"] for s in pipeline._sales}
        assert "Dublin" in counties
        assert "Cork" in counties
        assert "Galway" in counties
        assert "Clare" in counties


class TestPPRLoad:
    def test_full_run(self) -> None:
        pipeline = _make_pipeline()
        pipeline.run()
        assert pipeline.extracted
        assert pipeline.transformed
        assert pipeline.loaded
        assert pipeline.rows_loaded == 10
