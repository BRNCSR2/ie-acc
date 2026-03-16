"""GDPR compliance endpoints."""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/v1/gdpr", tags=["gdpr"])

logger = logging.getLogger(__name__)

# Store objection records in a JSON file
_OBJECTIONS_DIR = Path(os.environ.get("GDPR_OBJECTIONS_DIR", "./gdpr_objections"))


class ObjectionRequest(BaseModel):
    """Request to object to data processing (GDPR Art. 21)."""

    name: str
    email: EmailStr
    entity_type: str
    entity_id: str
    reason: str = ""


class ObjectionResponse(BaseModel):
    """Response confirming objection receipt."""

    objection_id: str
    status: str
    message: str


@router.post("/object", response_model=ObjectionResponse)
async def submit_objection(request: ObjectionRequest) -> dict[str, Any]:
    """Submit a right-to-object request (GDPR Art. 21).

    Records the objection for manual review. Data subjects can request
    that their personal data no longer be processed.
    """
    _OBJECTIONS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(tz=UTC)
    objection_id = f"OBJ-{timestamp.strftime('%Y%m%d%H%M%S')}-{request.entity_id}"

    record = {
        "objection_id": objection_id,
        "submitted_at": timestamp.isoformat(),
        "name": request.name,
        "email": request.email,
        "entity_type": request.entity_type,
        "entity_id": request.entity_id,
        "reason": request.reason,
        "status": "pending_review",
    }

    objection_file = _OBJECTIONS_DIR / f"{objection_id}.json"
    objection_file.write_text(json.dumps(record, indent=2))

    logger.info("GDPR objection recorded: %s", objection_id)

    return {
        "objection_id": objection_id,
        "status": "pending_review",
        "message": (
            "Your objection has been recorded and will be reviewed. "
            "You will be contacted at the provided email address."
        ),
    }


@router.get("/privacy-notice")
async def privacy_notice() -> dict[str, str]:
    """Return the Art. 14 privacy notice."""
    return {
        "title": "Data Processing Transparency Notice (GDPR Art. 14)",
        "controller": "ie-acc Open Transparency Project",
        "purpose": (
            "Cross-referencing publicly available Irish government databases "
            "to promote transparency and accountability in public life."
        ),
        "legal_basis": (
            "Legitimate interest (Art. 6(1)(f)) in promoting transparency "
            "of public administration and use of public funds."
        ),
        "data_sources": (
            "Companies Registration Office, Lobbying Register, Oireachtas API, "
            "Charities Regulator, eTenders, EPA, Property Price Register, CSO."
        ),
        "data_categories": (
            "Names, roles, and addresses of company directors, elected officials, "
            "registered lobbyists, charity trustees, and other public figures as "
            "published in official public registers."
        ),
        "retention": (
            "Data is retained as long as it remains in the original public source. "
            "Removed data is purged within 30 days of source update."
        ),
        "rights": (
            "You have the right to access, rectify, erase, restrict processing, "
            "and object to processing of your personal data. Submit requests via "
            "the /api/v1/gdpr/object endpoint or by contacting the project maintainers."
        ),
    }
