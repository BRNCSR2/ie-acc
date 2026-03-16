"""Tests for the eTenders procurement ETL pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from ieacc_etl.pipelines.etenders import ETendersPipeline

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline(limit: int | None = None) -> ETendersPipeline:
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__ = MagicMock(return_value=session)
    driver.session.return_value.__exit__ = MagicMock(return_value=False)
    return ETendersPipeline(
        driver=driver,
        data_dir=str(FIXTURES),
        limit=limit,
    )


class TestETendersExtract:
    def test_extract_reads_csv(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        assert pipeline.rows_in == 10

    def test_extract_with_limit(self) -> None:
        pipeline = _make_pipeline(limit=3)
        pipeline.extract()
        assert pipeline.rows_in == 3

    def test_extract_missing_file_raises(self) -> None:
        driver = MagicMock()
        session = MagicMock()
        driver.session.return_value.__enter__ = MagicMock(return_value=session)
        driver.session.return_value.__exit__ = MagicMock(return_value=False)
        pipeline = ETendersPipeline(driver=driver, data_dir="/nonexistent")
        try:
            pipeline.extract()
            raise AssertionError("Should have raised")
        except FileNotFoundError:
            pass


class TestETendersTransform:
    def test_transform_creates_contracts(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline._contracts) == 10

    def test_transform_deduplicates_authorities(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        # 9 unique authorities (AUTH001 appears twice)
        assert len(pipeline._authorities) == 9

    def test_transform_creates_supplier_rels(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline._contract_supplier_rels) == 10

    def test_transform_parses_value(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        ct1 = next(c for c in pipeline._contracts if c["contract_ref"] == "CT-2024-001")
        assert ct1["value"] == 4500000.0

    def test_transform_links_greenfield_to_multiple_contracts(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        # Greenfield Construction (100001) has 4 contracts
        greenfield_rels = [
            r for r in pipeline._contract_supplier_rels
            if r["company_number"] == "100001"
        ]
        assert len(greenfield_rels) == 4

    def test_transform_authority_rels(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline._contract_authority_rels) == 10


class TestETendersLoad:
    def test_full_run(self) -> None:
        pipeline = _make_pipeline()
        pipeline.run()
        assert pipeline.extracted
        assert pipeline.transformed
        assert pipeline.loaded
        assert pipeline.rows_loaded == 10
