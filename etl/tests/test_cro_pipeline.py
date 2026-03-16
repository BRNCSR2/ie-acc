"""Tests for the CRO ETL pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from ieacc_etl.pipelines.cro import CROPipeline

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline(limit: int | None = None) -> CROPipeline:
    """Create a CROPipeline with mocked Neo4j driver."""
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__ = MagicMock(return_value=session)
    driver.session.return_value.__exit__ = MagicMock(return_value=False)
    return CROPipeline(
        driver=driver,
        data_dir=str(FIXTURES),
        limit=limit,
    )


class TestCROExtract:
    def test_extract_reads_csv(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        assert pipeline.rows_in == 12
        assert pipeline.extracted is False  # not set until run()

    def test_extract_with_limit(self) -> None:
        pipeline = _make_pipeline(limit=5)
        pipeline.extract()
        assert pipeline.rows_in == 5

    def test_extract_missing_file_raises(self) -> None:
        driver = MagicMock()
        session = MagicMock()
        driver.session.return_value.__enter__ = MagicMock(return_value=session)
        driver.session.return_value.__exit__ = MagicMock(return_value=False)
        pipeline = CROPipeline(driver=driver, data_dir="/nonexistent")
        try:
            pipeline.extract()
            raise AssertionError("Should have raised")
        except FileNotFoundError:
            pass


class TestCROTransform:
    def test_transform_normalises_names(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        names = [c["name"] for c in pipeline._companies]
        # "GREENFIELD CONSTRUCTION LIMITED" -> "GREENFIELD CONSTRUCTION LTD"
        assert "GREENFIELD CONSTRUCTION LTD" in names
        # "CELTIC WASTE SOLUTIONS PUBLIC LIMITED COMPANY" -> "CELTIC WASTE SOLUTIONS PLC"
        assert "CELTIC WASTE SOLUTIONS PLC" in names
        # "SÉAMUS Ó'BRIAIN TEORANTA" -> "SÉAMUS Ó'BRIAIN TEO"
        assert "SÉAMUS Ó'BRIAIN TEO" in names

    def test_transform_extracts_counties(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        county_map = {c["company_number"]: c["county"] for c in pipeline._companies}
        assert county_map["100001"] == "Dublin"
        assert county_map["100002"] == "Cork"
        assert county_map["100003"] == "Galway"
        assert county_map["100005"] == "Clare"

    def test_transform_extracts_eircodes(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        eircode_map = {c["company_number"]: c["eircode"] for c in pipeline._companies}
        assert eircode_map["100001"] == "D02 AF30"
        assert eircode_map["100004"] == "D18 Y037"
        assert eircode_map["100005"] == "V95 X2K3"

    def test_transform_builds_full_address(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        addr_map = {c["company_number"]: c["address"] for c in pipeline._companies}
        # Multi-field address
        assert "Sandyford Business Park" in addr_map["100004"]
        assert "Dublin 18" in addr_map["100004"]

    def test_transform_handles_dissolved_company(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        dissolved = next(c for c in pipeline._companies if c["company_number"] == "300001")
        assert dissolved["status"] == "Dissolved"
        assert dissolved["dissolved_date"] != ""

    def test_transform_handles_empty_address(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        empty = next(c for c in pipeline._companies if c["company_number"] == "300002")
        assert empty["address"] == ""
        assert empty["county"] == ""

    def test_transform_strips_trailing_status_spaces(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        # Fixture has "Normal " with trailing space for some entries
        statuses = [c["status"] for c in pipeline._companies]
        for s in statuses:
            assert s == s.strip(), f"Status has trailing whitespace: '{s}'"

    def test_transform_row_count(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline._companies) == 12


class TestCROLoad:
    def test_load_calls_loader(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        pipeline.load()
        assert pipeline.rows_loaded == 12

    def test_full_run(self) -> None:
        pipeline = _make_pipeline()
        pipeline.run()
        assert pipeline.extracted
        assert pipeline.transformed
        assert pipeline.loaded
        assert pipeline.rows_in == 12
        assert pipeline.rows_loaded == 12
