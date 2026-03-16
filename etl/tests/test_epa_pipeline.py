"""Tests for the EPA licence ETL pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from ieacc_etl.pipelines.epa import EPAPipeline

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline(limit: int | None = None) -> EPAPipeline:
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__ = MagicMock(return_value=session)
    driver.session.return_value.__exit__ = MagicMock(return_value=False)
    return EPAPipeline(
        driver=driver,
        data_dir=str(FIXTURES),
        limit=limit,
    )


class TestEPAExtract:
    def test_extract_reads_csv(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        assert pipeline.rows_in == 8

    def test_extract_with_limit(self) -> None:
        pipeline = _make_pipeline(limit=3)
        pipeline.extract()
        assert pipeline.rows_in == 3

    def test_extract_missing_file_raises(self) -> None:
        driver = MagicMock()
        session = MagicMock()
        driver.session.return_value.__enter__ = MagicMock(return_value=session)
        driver.session.return_value.__exit__ = MagicMock(return_value=False)
        pipeline = EPAPipeline(driver=driver, data_dir="/nonexistent")
        try:
            pipeline.extract()
            raise AssertionError("Should have raised")
        except FileNotFoundError:
            pass


class TestEPATransform:
    def test_transform_creates_licences(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline._licences) == 8

    def test_transform_creates_company_rels(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        # All 8 licences have company_number
        assert len(pipeline._licence_company_rels) == 8

    def test_transform_licence_fields(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        lic = next(
            lic for lic in pipeline._licences if lic["licence_number"] == "EPA-W-001"
        )
        assert lic["licence_type"] == "Waste"
        assert lic["licensee_name"] == "Celtic Waste Solutions PLC"
        assert lic["county"] == "Cork"
        assert lic["status"] == "Active"
        assert lic["company_number"] == "100002"

    def test_transform_celtic_waste_has_two_licences(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        celtic_rels = [
            r for r in pipeline._licence_company_rels
            if r["company_number"] == "100002"
        ]
        assert len(celtic_rels) == 2

    def test_transform_surrendered_licence(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        lic = next(
            lic for lic in pipeline._licences if lic["licence_number"] == "EPA-W-003"
        )
        assert lic["status"] == "Surrendered"


class TestEPALoad:
    def test_full_run(self) -> None:
        pipeline = _make_pipeline()
        pipeline.run()
        assert pipeline.extracted
        assert pipeline.transformed
        assert pipeline.loaded
        assert pipeline.rows_loaded == 8
