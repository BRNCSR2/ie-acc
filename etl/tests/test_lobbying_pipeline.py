"""Tests for the Lobbying Register ETL pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from ieacc_etl.pipelines.lobbying import LobbyingPipeline

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline(limit: int | None = None) -> LobbyingPipeline:
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__ = MagicMock(return_value=session)
    driver.session.return_value.__exit__ = MagicMock(return_value=False)
    return LobbyingPipeline(
        driver=driver,
        data_dir=str(FIXTURES),
        limit=limit,
    )


class TestLobbyingExtract:
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
        pipeline = LobbyingPipeline(driver=driver, data_dir="/nonexistent")
        try:
            pipeline.extract()
            raise AssertionError("Should have raised")
        except FileNotFoundError:
            pass


class TestLobbyingTransform:
    def test_transform_creates_returns(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline._returns) == 8

    def test_transform_deduplicates_lobbyists(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        # Greenfield Construction LTD appears 3 times but should be 1 lobbyist
        names = [lob["name"] for lob in pipeline._lobbyists]
        assert len(names) == len(set(n.lower() for n in names))

    def test_transform_deduplicates_officials(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        # Seán Ó'Brien appears 3 times but should be 1 official
        ids = [o["official_id"] for o in pipeline._officials]
        assert len(ids) == len(set(ids))

    def test_transform_creates_company_rels(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        # All 8 returns have company_number
        assert len(pipeline._lobbyist_company_rels) == 8

    def test_transform_normalises_names(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        official_names = [o["name"] for o in pipeline._officials]
        # Check Ó' prefix preserved (fada Ó, not plain O)
        assert any("Ó'Brien" in n for n in official_names)
        # Check Mac prefix handling
        assert any("MacGiolla" in n for n in official_names)


class TestLobbyingLoad:
    def test_full_run(self) -> None:
        pipeline = _make_pipeline()
        pipeline.run()
        assert pipeline.extracted
        assert pipeline.transformed
        assert pipeline.loaded
        assert pipeline.rows_loaded == 8
