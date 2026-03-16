"""Tests for GDPR middleware and endpoints."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ieacc.middleware.gdpr import _redact_dict, _redact_response_body

if TYPE_CHECKING:
    from httpx import AsyncClient


# ── Unit tests for redaction helpers ──


class TestRedactDict:
    def test_redacts_name_field(self) -> None:
        data = {"name": "John Smith", "company_number": "12345"}
        result = _redact_dict(data)
        assert result["name"] == "[REDACTED]"
        assert result["company_number"] == "12345"

    def test_preserves_public_figure_names(self) -> None:
        data = {"entity_type": "TDOrSenator", "name": "Leo Varadkar"}
        result = _redact_dict(data)
        assert result["name"] == "Leo Varadkar"

    def test_redacts_nested_name(self) -> None:
        data = {
            "entity_type": "Company",
            "props": {"name": "Secret Person", "county": "Dublin"},
        }
        result = _redact_dict(data)
        assert result["props"]["name"] == "[REDACTED]"
        assert result["props"]["county"] == "Dublin"

    def test_redacts_list_of_dicts(self) -> None:
        data = {
            "results": [
                {"target_type": "Director", "target_name": "Jane Doe"},
                {"target_type": "TDOrSenator", "target_name": "Public TD"},
            ],
        }
        result = _redact_dict(data)
        assert result["results"][0]["target_name"] == "[REDACTED]"
        assert result["results"][1]["target_name"] == "Public TD"

    def test_redacts_director_name(self) -> None:
        data = {"director_name": "Pat Murphy", "role": "Secretary"}
        result = _redact_dict(data)
        assert result["director_name"] == "[REDACTED]"
        assert result["role"] == "Secretary"

    def test_empty_name_not_redacted(self) -> None:
        data = {"name": "", "county": "Cork"}
        result = _redact_dict(data)
        assert result["name"] == ""

    def test_non_name_fields_preserved(self) -> None:
        data = {"facility_name": "Cork Factory", "status": "Active"}
        result = _redact_dict(data)
        assert result["facility_name"] == "Cork Factory"


class TestRedactResponseBody:
    def test_redacts_json_body(self) -> None:
        body = b'{"name": "Secret", "county": "Dublin"}'
        result = _redact_response_body(body)
        import json

        parsed = json.loads(result)
        assert parsed["name"] == "[REDACTED]"
        assert parsed["county"] == "Dublin"

    def test_handles_non_json(self) -> None:
        body = b"not json"
        result = _redact_response_body(body)
        assert result == b"not json"

    def test_redacts_list_body(self) -> None:
        body = b'[{"name": "A"}, {"name": "B"}]'
        result = _redact_response_body(body)
        import json

        parsed = json.loads(result)
        assert parsed[0]["name"] == "[REDACTED]"
        assert parsed[1]["name"] == "[REDACTED]"


# ── Integration tests for GDPR middleware ──


class TestGDPRMiddleware:
    @pytest.fixture
    def _enable_public_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("PUBLIC_MODE", "true")

    @pytest.mark.usefixtures("_enable_public_mode")
    async def test_person_entity_blocked_in_public_mode(
        self, client: AsyncClient,
    ) -> None:
        resp = await client.get("/api/v1/entity/person/P001")
        assert resp.status_code == 403
        assert "restricted" in resp.json()["detail"]

    @pytest.mark.usefixtures("_enable_public_mode")
    async def test_director_entity_blocked_in_public_mode(
        self, client: AsyncClient,
    ) -> None:
        resp = await client.get("/api/v1/entity/director/D001")
        assert resp.status_code == 403

    @pytest.mark.usefixtures("_enable_public_mode")
    async def test_health_not_affected(self, client: AsyncClient) -> None:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_no_redaction_without_public_mode(
        self, client: AsyncClient, mock_driver: MagicMock,
    ) -> None:
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.data = AsyncMock(return_value=[{
            "props": {"name": "John Smith", "company_number": "12345"},
        }])
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)

        resp = await client.get("/api/v1/entity/company/12345")
        assert resp.status_code == 200
        assert resp.json()["props"]["name"] == "John Smith"


# ── GDPR endpoint tests ──


class TestGDPREndpoints:
    async def test_privacy_notice(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/gdpr/privacy-notice")
        assert resp.status_code == 200
        data = resp.json()
        assert "title" in data
        assert "legal_basis" in data
        assert "rights" in data

    async def test_submit_objection(
        self, client: AsyncClient, tmp_path: object,
    ) -> None:
        with patch.dict(os.environ, {"GDPR_OBJECTIONS_DIR": str(tmp_path)}):
            resp = await client.post(
                "/api/v1/gdpr/object",
                json={
                    "name": "Test User",
                    "email": "test@example.com",
                    "entity_type": "person",
                    "entity_id": "P001",
                    "reason": "I want my data removed",
                },
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "pending_review"
        assert "objection_id" in data

    async def test_submit_objection_invalid_email(
        self, client: AsyncClient,
    ) -> None:
        resp = await client.post(
            "/api/v1/gdpr/object",
            json={
                "name": "Test User",
                "email": "not-an-email",
                "entity_type": "person",
                "entity_id": "P001",
            },
        )
        assert resp.status_code == 422
