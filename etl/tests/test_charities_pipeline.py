"""Tests for the Charities Regulator ETL pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from ieacc_etl.pipelines.charities import CharitiesPipeline

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline(limit: int | None = None) -> CharitiesPipeline:
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__ = MagicMock(return_value=session)
    driver.session.return_value.__exit__ = MagicMock(return_value=False)
    return CharitiesPipeline(
        driver=driver,
        data_dir=str(FIXTURES),
        limit=limit,
    )


class TestCharitiesExtract:
    def test_extract_reads_csv(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        assert pipeline.rows_in == 6

    def test_extract_with_limit(self) -> None:
        pipeline = _make_pipeline(limit=3)
        pipeline.extract()
        assert pipeline.rows_in == 3

    def test_extract_missing_file_raises(self) -> None:
        driver = MagicMock()
        session = MagicMock()
        driver.session.return_value.__enter__ = MagicMock(return_value=session)
        driver.session.return_value.__exit__ = MagicMock(return_value=False)
        pipeline = CharitiesPipeline(driver=driver, data_dir="/nonexistent")
        try:
            pipeline.extract()
            raise AssertionError("Should have raised")
        except FileNotFoundError:
            pass


class TestCharitiesTransform:
    def test_transform_creates_charities(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline._charities) == 6

    def test_transform_normalises_names(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        names = [c["name"] for c in pipeline._charities]
        # CLG suffix should be standardised
        assert "Dublin Housing Trust CLG" in names
        assert "Cork Youth Foundation CLG" in names

    def test_transform_links_to_companies(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        # 4 charities have company_number (500001-500004)
        assert len(pipeline._charity_company_rels) == 4
        company_numbers = [r["company_number"] for r in pipeline._charity_company_rels]
        assert "500001" in company_numbers
        assert "500002" in company_numbers

    def test_transform_handles_no_company(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        # Galway Arts & Culture Trust has no company_number
        galway = next(c for c in pipeline._charities if c["rcn"] == "CHY20003")
        assert galway["company_number"] == ""

    def test_transform_builds_address(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        dublin = next(c for c in pipeline._charities if c["rcn"] == "CHY20001")
        assert "Pearse Street" in dublin["address"]
        assert "Dublin 2" in dublin["address"]

    def test_transform_handles_dormant(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        dormant = next(c for c in pipeline._charities if c["rcn"] == "CHY20006")
        assert dormant["status"] == "Dormant"


class TestCharitiesLoad:
    def test_full_run(self) -> None:
        pipeline = _make_pipeline()
        pipeline.run()
        assert pipeline.extracted
        assert pipeline.transformed
        assert pipeline.loaded
        assert pipeline.rows_loaded == 6
