"""Shared test fixtures for API tests."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

from ieacc.main import app


@pytest.fixture
async def mock_driver() -> MagicMock:
    """Provide a standalone mock Neo4j driver for unit tests."""
    driver = MagicMock()
    driver.verify_connectivity = AsyncMock()
    mock_session = AsyncMock()
    driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    driver.session.return_value.__aexit__ = AsyncMock(return_value=None)
    return driver


@pytest.fixture
async def client(mock_driver: MagicMock) -> AsyncIterator[AsyncClient]:
    """Provide an async test client with mocked Neo4j driver."""
    app.state.neo4j_driver = mock_driver

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def make_mock_result(data: list[dict]) -> AsyncMock:  # type: ignore[type-arg]
    """Create a mock Neo4j result that returns the given data."""
    mock_result = AsyncMock()
    mock_result.data = AsyncMock(return_value=data)
    return mock_result
