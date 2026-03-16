"""Tests for the entity endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest

from tests.conftest import make_mock_result

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_entity_returns_detail(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(
        return_value=make_mock_result([
            {
                "props": {
                    "company_number": "100001",
                    "name": "Greenfield Construction LTD",
                    "status": "Normal",
                    "county": "Dublin",
                },
            }
        ])
    )
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get("/api/v1/entity/company/100001")
    assert response.status_code == 200
    data = response.json()
    assert data["entity_type"] == "Company"
    assert data["entity_id"] == "100001"
    assert data["props"]["name"] == "Greenfield Construction LTD"


@pytest.mark.anyio
async def test_get_entity_not_found(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(return_value=make_mock_result([]))
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get("/api/v1/entity/company/999999")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_entity_unknown_type(client: AsyncClient) -> None:
    response = await client.get("/api/v1/entity/foobar/123")
    assert response.status_code == 404
    assert "Unknown entity type" in response.json()["detail"]


@pytest.mark.anyio
async def test_get_connections_returns_list(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(
        return_value=make_mock_result([
            {
                "relationship": "DIRECTOR_OF",
                "rel_props": {"appointed": "2020-01-01"},
                "target_type": "Director",
                "target_name": "Seán Murphy",
                "target_props": {"director_id": "d001", "name": "Seán Murphy"},
            }
        ])
    )
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get("/api/v1/entity/company/100001/connections")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["relationship"] == "DIRECTOR_OF"
    assert data[0]["target_name"] == "Seán Murphy"


@pytest.mark.anyio
async def test_get_connections_empty(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(return_value=make_mock_result([]))
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get("/api/v1/entity/charity/CHY999/connections")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_entity_type_case_insensitive(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(
        return_value=make_mock_result([
            {"props": {"rcn": "CHY001", "name": "Test Charity"}}
        ])
    )
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get("/api/v1/entity/Charity/CHY001")
    assert response.status_code == 200
    assert response.json()["entity_type"] == "Charity"
