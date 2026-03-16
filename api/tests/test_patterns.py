"""Tests for the intelligence patterns endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest

from tests.conftest import make_mock_result

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from httpx import AsyncClient


@pytest.mark.anyio
async def test_list_patterns(client: AsyncClient) -> None:
    response = await client.get("/api/v1/patterns/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 8
    names = [p["name"] for p in data]
    assert "lobbying_contract_overlap" in names
    assert "contract_concentration" in names
    assert "director_network_contracts" in names
    assert "charity_director_overlap" in names
    assert "epa_violator_contracts" in names
    assert "planning_director_links" in names
    assert "revolving_door" in names
    assert "split_contracts_below_threshold" in names


@pytest.mark.anyio
async def test_run_pattern_returns_results(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(
        return_value=make_mock_result([
            {
                "company_number": "100001",
                "company_name": "Greenfield Construction LTD",
                "body_lobbied": "Department of Housing",
                "lobbying_subject": "Housing policy",
                "lobbying_period": "2024-01-01",
                "contract_ref": "CT-2024-001",
                "contract_title": "Social Housing Phase 3",
                "contract_value": 4500000,
                "award_date": "2024-03-15",
            }
        ])
    )
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get("/api/v1/patterns/lobbying_contract_overlap")
    assert response.status_code == 200
    data = response.json()
    assert data["pattern"] == "lobbying_contract_overlap"
    assert data["count"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["company_name"] == "Greenfield Construction LTD"


@pytest.mark.anyio
async def test_run_pattern_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/patterns/nonexistent_pattern")
    assert response.status_code == 404
    assert "Unknown pattern" in response.json()["detail"]


@pytest.mark.anyio
async def test_run_pattern_empty_results(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(return_value=make_mock_result([]))
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get("/api/v1/patterns/contract_concentration")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["results"] == []


@pytest.mark.anyio
async def test_each_pattern_has_description(client: AsyncClient) -> None:
    response = await client.get("/api/v1/patterns/")
    data = response.json()
    for pattern in data:
        assert "description" in pattern
        assert len(pattern["description"]) > 10
