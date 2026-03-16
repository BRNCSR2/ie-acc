"""Tests for investigation workspace endpoints."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


class TestInvestigationCRUD:
    @pytest.fixture(autouse=True)
    def _use_tmp_dir(self, tmp_path: object) -> None:  # type: ignore[type-arg]
        with patch.dict(os.environ, {"INVESTIGATIONS_DIR": str(tmp_path)}):
            # Patch the module-level variable
            import ieacc.routers.investigations as inv_mod

            inv_mod._INVESTIGATIONS_DIR = tmp_path  # type: ignore[assignment]
            yield
            inv_mod._INVESTIGATIONS_DIR = tmp_path  # type: ignore[assignment]

    async def test_create_investigation(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/v1/investigations/",
            json={
                "title": "Test Investigation",
                "description": "Testing",
                "tags": ["test", "demo"],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Test Investigation"
        assert "id" in data
        assert data["annotations"] == []
        assert data["saved_queries"] == []

    async def test_list_investigations(self, client: AsyncClient) -> None:
        # Create two investigations
        await client.post(
            "/api/v1/investigations/",
            json={"title": "Inv 1"},
        )
        await client.post(
            "/api/v1/investigations/",
            json={"title": "Inv 2"},
        )

        resp = await client.get("/api/v1/investigations/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    async def test_get_investigation(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/investigations/",
            json={"title": "Detail Test"},
        )
        inv_id = create_resp.json()["id"]

        resp = await client.get(f"/api/v1/investigations/{inv_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Detail Test"

    async def test_get_nonexistent_returns_404(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/investigations/nonexistent")
        assert resp.status_code == 404

    async def test_delete_investigation(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/investigations/",
            json={"title": "To Delete"},
        )
        inv_id = create_resp.json()["id"]

        resp = await client.delete(f"/api/v1/investigations/{inv_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"

        # Verify it's gone
        resp = await client.get(f"/api/v1/investigations/{inv_id}")
        assert resp.status_code == 404

    async def test_add_annotation(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/investigations/",
            json={"title": "Annotated"},
        )
        inv_id = create_resp.json()["id"]

        resp = await client.post(
            f"/api/v1/investigations/{inv_id}/annotations",
            json={
                "entity_type": "company",
                "entity_id": "100001",
                "note": "Suspicious activity",
                "tags": ["flag"],
            },
        )
        assert resp.status_code == 200
        assert resp.json()["note"] == "Suspicious activity"

        # Verify it was saved
        inv = await client.get(f"/api/v1/investigations/{inv_id}")
        assert len(inv.json()["annotations"]) == 1

    async def test_add_saved_query(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/investigations/",
            json={"title": "Query Test"},
        )
        inv_id = create_resp.json()["id"]

        resp = await client.post(
            f"/api/v1/investigations/{inv_id}/queries",
            json={
                "query_name": "Find directors",
                "cypher": "MATCH (d:Director) RETURN d LIMIT 10",
                "description": "Test query",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["query_name"] == "Find directors"

    async def test_export_html(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/investigations/",
            json={"title": "Export Test"},
        )
        inv_id = create_resp.json()["id"]

        # Add an annotation
        await client.post(
            f"/api/v1/investigations/{inv_id}/annotations",
            json={
                "entity_type": "company",
                "entity_id": "100001",
                "note": "Notable entity",
            },
        )

        resp = await client.get(f"/api/v1/investigations/{inv_id}/export?fmt=html")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "Export Test" in resp.text
        assert "Notable entity" in resp.text
