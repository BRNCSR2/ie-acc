"""Tests for cross-source linking hooks."""

from __future__ import annotations

from unittest.mock import MagicMock

from ieacc_etl.linking_hooks import ALL_HOOKS, run_all_hooks


class TestLinkingHooks:
    def test_all_hooks_defined(self) -> None:
        assert len(ALL_HOOKS) >= 3
        names = [name for name, _ in ALL_HOOKS]
        assert "link_officials_to_politicians" in names
        assert "link_lobbyists_to_companies" in names
        assert "link_charities_to_companies" in names

    def test_run_all_hooks_executes_queries(self) -> None:
        driver = MagicMock()
        session = MagicMock()
        mock_result = MagicMock()
        mock_summary = MagicMock()
        mock_summary.counters.relationships_created = 5
        mock_result.consume.return_value = mock_summary
        session.run.return_value = mock_result
        driver.session.return_value.__enter__ = MagicMock(return_value=session)
        driver.session.return_value.__exit__ = MagicMock(return_value=False)

        results = run_all_hooks(driver)
        assert len(results) == len(ALL_HOOKS)
        for name in results:
            assert results[name] == 5
        assert session.run.call_count == len(ALL_HOOKS)

    def test_run_all_hooks_handles_failure(self) -> None:
        driver = MagicMock()
        session = MagicMock()
        session.run.side_effect = RuntimeError("Neo4j down")
        driver.session.return_value.__enter__ = MagicMock(return_value=session)
        driver.session.return_value.__exit__ = MagicMock(return_value=False)

        results = run_all_hooks(driver)
        for name in results:
            assert results[name] == -1
