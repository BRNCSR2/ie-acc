"""Tests for the graph expansion endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest

from tests.conftest import make_mock_result

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from httpx import AsyncClient


@pytest.mark.anyio
async def test_graph_expand_returns_nodes_and_edges(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(
        return_value=make_mock_result([
            {
                "nodes": [
                    {"id": "1", "label": "Company", "name": "Test Co", "props": {}},
                    {"id": "2", "label": "Director", "name": "Jane Doe", "props": {}},
                ],
                "edges": [
                    {"source": "1", "target": "2", "type": "DIRECTOR_OF", "props": {}},
                ],
            }
        ])
    )
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get(
        "/api/v1/graph/expand",
        params={"entity_type": "company", "entity_id": "100001"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1
    assert data["edges"][0]["type"] == "DIRECTOR_OF"


@pytest.mark.anyio
async def test_graph_expand_not_found(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(return_value=make_mock_result([]))
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get(
        "/api/v1/graph/expand",
        params={"entity_type": "company", "entity_id": "999999"},
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_graph_expand_invalid_type(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/graph/expand",
        params={"entity_type": "invalid", "entity_id": "123"},
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_graph_expand_depth_limited(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/graph/expand",
        params={"entity_type": "company", "entity_id": "123", "depth": 5},
    )
    assert response.status_code == 422  # depth max is 4


@pytest.mark.anyio
async def test_graph_expand_default_depth(
    client: AsyncClient, mock_driver: MagicMock
) -> None:
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(
        return_value=make_mock_result([{"nodes": [], "edges": []}])
    )
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

    response = await client.get(
        "/api/v1/graph/expand",
        params={"entity_type": "company", "entity_id": "100001"},
    )
    assert response.status_code == 200

    # Verify depth=2 was passed by default
    call_args = mock_session.run.call_args
    assert call_args is not None
    params = call_args.kwargs.get("parameters", {})
    assert params.get("depth") == 2
