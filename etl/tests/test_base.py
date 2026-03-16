"""Tests for the ETL Pipeline base class."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ieacc_etl.base import Pipeline


class DummyPipeline(Pipeline):
    name = "dummy"
    source_id = "test_dummy"

    def __init__(self) -> None:
        driver = MagicMock()
        session = MagicMock()
        driver.session.return_value.__enter__ = MagicMock(return_value=session)
        driver.session.return_value.__exit__ = MagicMock(return_value=False)
        super().__init__(driver=driver, data_dir="./data")

    def extract(self) -> None:
        self.rows_in = 10

    def transform(self) -> None:
        pass

    def load(self) -> None:
        self.rows_loaded = 10


class FailingPipeline(Pipeline):
    name = "failing"
    source_id = "test_failing"

    def __init__(self) -> None:
        driver = MagicMock()
        session = MagicMock()
        driver.session.return_value.__enter__ = MagicMock(return_value=session)
        driver.session.return_value.__exit__ = MagicMock(return_value=False)
        super().__init__(driver=driver, data_dir="./data")

    def extract(self) -> None:
        raise ValueError("extract failed")

    def transform(self) -> None:
        pass

    def load(self) -> None:
        pass


def test_pipeline_run_succeeds() -> None:
    pipeline = DummyPipeline()
    pipeline.run()
    assert pipeline.extracted
    assert pipeline.transformed
    assert pipeline.loaded
    assert pipeline.rows_in == 10
    assert pipeline.rows_loaded == 10


def test_pipeline_run_tracks_run_id() -> None:
    pipeline = DummyPipeline()
    assert pipeline._run_id.startswith("test_dummy_")


def test_pipeline_run_failure_raises() -> None:
    pipeline = FailingPipeline()
    with pytest.raises(ValueError, match="extract failed"):
        pipeline.run()
    assert not pipeline.extracted


def test_pipeline_default_values() -> None:
    pipeline = DummyPipeline()
    assert pipeline.rows_in == 0
    assert pipeline.rows_loaded == 0
    assert pipeline.chunk_size == 50_000
    assert pipeline.limit is None
