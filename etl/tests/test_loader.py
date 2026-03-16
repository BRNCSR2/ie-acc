"""Tests for the Neo4j batch loader."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ieacc_etl.loader import Neo4jBatchLoader


def _make_loader(batch_size: int = 10_000) -> Neo4jBatchLoader:
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__ = MagicMock(return_value=session)
    driver.session.return_value.__exit__ = MagicMock(return_value=False)
    return Neo4jBatchLoader(driver=driver, batch_size=batch_size)


def test_load_nodes_empty() -> None:
    loader = _make_loader()
    result = loader.load_nodes("Company", [], "company_number")
    assert result == 0


def test_load_nodes_filters_empty_keys() -> None:
    loader = _make_loader(batch_size=100)
    rows = [
        {"company_number": "100001", "name": "Test Ltd"},
        {"company_number": "", "name": "Empty Key"},
        {"company_number": None, "name": "Null Key"},
        {"company_number": "100002", "name": "Valid Ltd"},
    ]
    result = loader.load_nodes("Company", rows, "company_number")
    assert result == 2


def test_load_nodes_batching() -> None:
    loader = _make_loader(batch_size=2)
    rows = [
        {"company_number": f"{i}", "name": f"Company {i}"}
        for i in range(5)
    ]
    result = loader.load_nodes("Company", rows, "company_number")
    assert result == 5


def test_load_relationships_empty() -> None:
    loader = _make_loader()
    result = loader.load_relationships(
        "DIRECTOR_OF", [], "Person", "person_id", "Company", "company_number"
    )
    assert result == 0


def test_load_relationships_filters_missing_keys() -> None:
    loader = _make_loader(batch_size=100)
    rows = [
        {"person_id": "P001", "company_number": "100001"},
        {"person_id": "P002", "company_number": ""},
        {"person_id": "", "company_number": "100003"},
        {"person_id": "P004", "company_number": "100004"},
    ]
    result = loader.load_relationships(
        "DIRECTOR_OF", rows, "Person", "person_id", "Company", "company_number"
    )
    assert result == 2


def test_run_query_empty() -> None:
    loader = _make_loader()
    result = loader.run_query("UNWIND $rows AS row RETURN row", [])
    assert result == 0


def test_run_query_with_retry_empty() -> None:
    loader = _make_loader()
    result = loader.run_query_with_retry("UNWIND $rows AS row RETURN row", [])
    assert result == 0


@patch("ieacc_etl.loader.time.sleep")
def test_run_query_with_retry_retries_on_transient(mock_sleep: MagicMock) -> None:
    from neo4j.exceptions import TransientError

    loader = _make_loader(batch_size=100)
    session = MagicMock()
    # First call raises, second succeeds
    session.run.side_effect = [TransientError("deadlock"), None]
    loader.driver.session.return_value.__enter__ = MagicMock(return_value=session)

    rows = [{"id": "1"}]
    result = loader.run_query_with_retry("UNWIND $rows AS row RETURN row", rows)
    assert result == 1
    mock_sleep.assert_called_once_with(1)
