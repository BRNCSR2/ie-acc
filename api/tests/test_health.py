"""Tests for health endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_meta_health_neo4j_connected(client: AsyncClient) -> None:
    response = await client.get("/api/v1/meta/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["neo4j"] == "connected"


@pytest.mark.anyio
async def test_meta_sources_returns_list(client: AsyncClient) -> None:
    response = await client.get("/api/v1/meta/sources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
