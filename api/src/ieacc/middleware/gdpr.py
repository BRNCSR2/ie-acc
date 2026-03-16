"""GDPR middleware for name redaction and public mode enforcement.

In public mode (PUBLIC_MODE=true), personal names in API responses are
redacted unless the person is classified as a public figure (e.g., elected
officials, company directors of public companies).
"""

from __future__ import annotations

import json
import os
import re
from typing import TYPE_CHECKING, Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

if TYPE_CHECKING:
    from starlette.requests import Request

# Entity types whose names are always public (elected officials, etc.)
PUBLIC_FIGURE_TYPES = frozenset({
    "TDOrSenator",
    "PublicOfficial",
    "ContractingAuthority",
})

# Fields that contain personal names to redact
NAME_FIELDS = frozenset({
    "name",
    "director_name",
    "licensee_name",
    "lobbyist_name",
    "trustee_name",
    "target_name",
})

REDACTED = "[REDACTED]"


def is_public_mode() -> bool:
    """Check if the API is running in public mode."""
    return os.environ.get("PUBLIC_MODE", "false").lower() in ("true", "1", "yes")


def _redact_value(key: str, value: Any, entity_type: str | None = None) -> Any:
    """Redact a value if it's a name field and the entity isn't a public figure."""
    if entity_type and entity_type in PUBLIC_FIGURE_TYPES:
        return value
    if key in NAME_FIELDS and isinstance(value, str) and value:
        return REDACTED
    return value


def _redact_dict(data: dict[str, Any], entity_type: str | None = None) -> dict[str, Any]:
    """Recursively redact name fields in a dictionary."""
    result: dict[str, Any] = {}
    # Detect entity type from the data itself
    current_type = entity_type or data.get("entity_type") or data.get("target_type")

    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = _redact_dict(value, current_type)
        elif isinstance(value, list):
            result[key] = [
                _redact_dict(item, current_type) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            result[key] = _redact_value(key, value, current_type)
    return result


def _redact_response_body(body: bytes) -> bytes:
    """Parse JSON response body and redact name fields."""
    try:
        data = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return body

    redacted: Any
    if isinstance(data, dict):
        redacted = _redact_dict(data)
    elif isinstance(data, list):
        redacted = [
            _redact_dict(item) if isinstance(item, dict) else item
            for item in data
        ]
    else:
        return body

    return json.dumps(redacted).encode()


# Paths that are excluded from GDPR redaction
_EXEMPT_PATHS = re.compile(
    r"^/(health|api/v1/meta|api/v1/patterns|api/v1/gdpr)"
)

# Person-type entity paths that are blocked in public mode
_PERSON_ENTITY_TYPES = frozenset({
    "person", "director", "lobbyist", "trustee",
})


class GDPRMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces GDPR-compliant name redaction in public mode."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint,
    ) -> Response:
        if not is_public_mode():
            return await call_next(request)

        path = request.url.path

        # Skip redaction for health, meta, patterns, and GDPR endpoints
        if _EXEMPT_PATHS.match(path):
            return await call_next(request)

        # Block direct person entity lookups in public mode
        if path.startswith("/api/v1/entity/"):
            parts = path.split("/")
            if len(parts) >= 5:
                entity_type = parts[4].lower().replace("_", "")
                if entity_type in _PERSON_ENTITY_TYPES:
                    return Response(
                        content=json.dumps({
                            "detail": "Person entity details are restricted in public mode.",
                        }),
                        status_code=403,
                        media_type="application/json",
                    )

        response = await call_next(request)

        # Only redact JSON responses
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        # Read and redact body
        body = b""
        body_iter = getattr(response, "body_iterator", None)
        if body_iter is None:
            return response
        async for chunk in body_iter:
            if isinstance(chunk, str):
                body += chunk.encode()
            else:
                body += chunk

        redacted_body = _redact_response_body(body)

        return Response(
            content=redacted_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type="application/json",
        )
