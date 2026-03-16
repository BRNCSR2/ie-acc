"""Tests for the search endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest

from tests.conftest import make_mock_result

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from httpx import AsyncClient


@pytest.mark.anyio
async def test_search_returns_results(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(
        return_value=make_mock_result([
            {
                "entity_type": "Company",
                "entity_id": "123456",
                "name": "Ryanair Holdings PLC",
                "score": 5.5,
                "props": {
                    "company_number": "123456",
                    "name": "Ryanair Holdings PLC",
                    "status": "Normal",
                },
            }
        ])
    )
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get("/api/v1/search", params={"q": "Ryanair"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["entity_type"] == "Company"
    assert data[0]["name"] == "Ryanair Holdings PLC"
    assert data[0]["entity_id"] == "123456"


@pytest.mark.anyio
async def test_search_empty_query_rejected(client: AsyncClient) -> None:
    response = await client.get("/api/v1/search", params={"q": ""})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_search_no_results(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(return_value=make_mock_result([]))
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get("/api/v1/search", params={"q": "nonexistent12345"})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_search_respects_limit(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(return_value=make_mock_result([]))
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get("/api/v1/search", params={"q": "test", "limit": 5})
    assert response.status_code == 200

    # Verify the limit was passed to the query
    call_args = mock_session.run.call_args
    assert call_args is not None
    params = call_args.kwargs.get("parameters", {})
    assert params.get("limit") == 5


@pytest.mark.anyio
async def test_search_limit_out_of_range(client: AsyncClient) -> None:
    response = await client.get("/api/v1/search", params={"q": "test", "limit": 200})
    assert response.status_code == 422
