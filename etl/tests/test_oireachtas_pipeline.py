"""Tests for the Oireachtas ETL pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from ieacc_etl.pipelines.oireachtas import OireachtasPipeline

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline(limit: int | None = None) -> OireachtasPipeline:
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__ = MagicMock(return_value=session)
    driver.session.return_value.__exit__ = MagicMock(return_value=False)
    return OireachtasPipeline(
        driver=driver,
        data_dir=str(FIXTURES),
        limit=limit,
    )


class TestOireachtasExtract:
    def test_extract_reads_json(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        assert pipeline.rows_in == 5

    def test_extract_with_limit(self) -> None:
        pipeline = _make_pipeline(limit=2)
        pipeline.extract()
        assert pipeline.rows_in == 2

    def test_extract_missing_file_raises(self) -> None:
        driver = MagicMock()
        session = MagicMock()
        driver.session.return_value.__enter__ = MagicMock(return_value=session)
        driver.session.return_value.__exit__ = MagicMock(return_value=False)
        pipeline = OireachtasPipeline(driver=driver, data_dir="/nonexistent")
        try:
            pipeline.extract()
            raise AssertionError("Should have raised")
        except FileNotFoundError:
            pass


class TestOireachtasTransform:
    def test_transform_creates_members(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline._members) == 5

    def test_transform_assigns_roles(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        roles = {m["member_id"]: m["role"] for m in pipeline._members}
        # Dáil members should be TD
        assert roles["Seán-ÓBrien.D.2020-02-08"] == "TD"
        assert roles["Máire-NíCheallaigh.D.2016-03-10"] == "TD"
        # Seanad members should be Senator
        assert roles["Pádraig-MacGiolla.S.2020-04-30"] == "Senator"

    def test_transform_extracts_parties(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        parties = {m["member_id"]: m["party"] for m in pipeline._members}
        assert parties["Seán-ÓBrien.D.2020-02-08"] == "Fianna Fáil"
        assert parties["Máire-NíCheallaigh.D.2016-03-10"] == "Sinn Féin"
        assert parties["Pádraig-MacGiolla.S.2020-04-30"] == "Fine Gael"

    def test_transform_extracts_constituencies(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        const = {m["member_id"]: m["constituency"] for m in pipeline._members}
        assert const["Seán-ÓBrien.D.2020-02-08"] == "Dublin Bay South"
        assert const["Aoife-McCarthy.D.2024-11-29"] == "Galway West"

    def test_transform_normalises_names(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        names = {m["member_id"]: m["name"] for m in pipeline._members}
        # Name normalisation should handle O' and Mac prefixes
        assert "Ó'Brien" in names["Seán-ÓBrien.D.2020-02-08"]
        assert "MacGiolla" in names["Pádraig-MacGiolla.S.2020-04-30"]


class TestOireachtasLoad:
    def test_full_run(self) -> None:
        pipeline = _make_pipeline()
        pipeline.run()
        assert pipeline.extracted
        assert pipeline.transformed
        assert pipeline.loaded
        assert pipeline.rows_loaded == 5
