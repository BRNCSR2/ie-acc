"""Investigation workspace endpoints.

CRUD operations for investigations — saved queries, entity annotations,
and tagged groups of entities for investigative analysis.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response as FastAPIResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/investigations", tags=["investigations"])
logger = logging.getLogger(__name__)

_INVESTIGATIONS_DIR = Path(
    os.environ.get("INVESTIGATIONS_DIR", "./investigations")
)


class InvestigationCreate(BaseModel):
    """Create a new investigation."""

    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)


class AnnotationCreate(BaseModel):
    """Add an annotation to an investigation."""

    entity_type: str
    entity_id: str
    note: str
    tags: list[str] = Field(default_factory=list)


class SavedQueryCreate(BaseModel):
    """Save a query to an investigation."""

    query_name: str
    cypher: str
    description: str = ""


def _load_investigation(investigation_id: str) -> dict[str, Any]:
    """Load investigation from disk."""
    path = _INVESTIGATIONS_DIR / f"{investigation_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Investigation {investigation_id} not found")
    result: dict[str, Any] = json.loads(path.read_text())
    return result


def _save_investigation(investigation_id: str, data: dict[str, Any]) -> None:
    """Save investigation to disk."""
    _INVESTIGATIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = _INVESTIGATIONS_DIR / f"{investigation_id}.json"
    path.write_text(json.dumps(data, indent=2, default=str))


@router.post("/")
async def create_investigation(req: InvestigationCreate) -> dict[str, Any]:
    """Create a new investigation workspace."""
    inv_id = str(uuid.uuid4())[:8]
    now = datetime.now(tz=UTC).isoformat()

    investigation = {
        "id": inv_id,
        "title": req.title,
        "description": req.description,
        "tags": req.tags,
        "created_at": now,
        "updated_at": now,
        "annotations": [],
        "saved_queries": [],
    }

    _save_investigation(inv_id, investigation)
    logger.info("Created investigation %s: %s", inv_id, req.title)
    return investigation


@router.get("/")
async def list_investigations() -> list[dict[str, Any]]:
    """List all investigations."""
    if not _INVESTIGATIONS_DIR.exists():
        return []

    investigations = []
    for path in sorted(_INVESTIGATIONS_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        investigations.append({
            "id": data["id"],
            "title": data["title"],
            "description": data["description"],
            "tags": data["tags"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
            "annotation_count": len(data.get("annotations", [])),
            "query_count": len(data.get("saved_queries", [])),
        })
    return investigations


@router.get("/{investigation_id}")
async def get_investigation(investigation_id: str) -> dict[str, Any]:
    """Get full investigation details."""
    return _load_investigation(investigation_id)


@router.delete("/{investigation_id}")
async def delete_investigation(investigation_id: str) -> dict[str, str]:
    """Delete an investigation."""
    path = _INVESTIGATIONS_DIR / f"{investigation_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Investigation not found")
    path.unlink()
    return {"status": "deleted", "id": investigation_id}


@router.post("/{investigation_id}/annotations")
async def add_annotation(
    investigation_id: str, req: AnnotationCreate,
) -> dict[str, Any]:
    """Add an entity annotation to an investigation."""
    data = _load_investigation(investigation_id)

    annotation = {
        "id": str(uuid.uuid4())[:8],
        "entity_type": req.entity_type,
        "entity_id": req.entity_id,
        "note": req.note,
        "tags": req.tags,
        "created_at": datetime.now(tz=UTC).isoformat(),
    }

    data["annotations"].append(annotation)
    data["updated_at"] = datetime.now(tz=UTC).isoformat()
    _save_investigation(investigation_id, data)

    return annotation


@router.post("/{investigation_id}/queries")
async def add_saved_query(
    investigation_id: str, req: SavedQueryCreate,
) -> dict[str, Any]:
    """Save a query to an investigation."""
    data = _load_investigation(investigation_id)

    saved_query = {
        "id": str(uuid.uuid4())[:8],
        "query_name": req.query_name,
        "cypher": req.cypher,
        "description": req.description,
        "created_at": datetime.now(tz=UTC).isoformat(),
    }

    data["saved_queries"].append(saved_query)
    data["updated_at"] = datetime.now(tz=UTC).isoformat()
    _save_investigation(investigation_id, data)

    return saved_query


def _render_investigation_html(data: dict[str, Any]) -> str:
    """Render investigation data as an HTML report."""
    annotations_html = ""
    for ann in data.get("annotations", []):
        annotations_html += (
            f"<tr><td>{ann['entity_type']}</td><td>{ann['entity_id']}</td>"
            f"<td>{ann['note']}</td><td>{', '.join(ann.get('tags', []))}</td></tr>"
        )

    queries_html = ""
    for sq in data.get("saved_queries", []):
        queries_html += (
            f"<tr><td>{sq['query_name']}</td>"
            f"<td>{sq.get('description', '')}</td>"
            f"<td><code>{sq['cypher']}</code></td></tr>"
        )

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{data['title']}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
h1 {{ color: #1a73e8; }}
table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
th, td {{ padding: 8px 12px; border: 1px solid #ddd; text-align: left; }}
th {{ background: #f5f5f5; }}
code {{ font-size: 0.85rem; }}
.meta {{ color: #666; font-size: 0.9rem; }}
</style></head>
<body>
<h1>{data['title']}</h1>
<p>{data.get('description', '')}</p>
<p class="meta">Created: {data['created_at']} | Tags: {', '.join(data.get('tags', []))}</p>

<h2>Annotations ({len(data.get('annotations', []))})</h2>
<table>
<thead><tr><th>Entity Type</th><th>Entity ID</th><th>Note</th><th>Tags</th></tr></thead>
<tbody>{annotations_html if annotations_html else '<tr><td colspan="4">No annotations</td></tr>'}
</tbody></table>

<h2>Saved Queries ({len(data.get('saved_queries', []))})</h2>
<table>
<thead><tr><th>Name</th><th>Description</th><th>Cypher</th></tr></thead>
<tbody>{queries_html if queries_html else '<tr><td colspan="3">No saved queries</td></tr>'}
</tbody></table>

<footer class="meta"><p>Generated by ie-acc Open Transparency Graph</p></footer>
</body></html>"""


@router.get("/{investigation_id}/export")
async def export_investigation(
    investigation_id: str, fmt: str = "html",
) -> FastAPIResponse:
    """Export investigation as HTML or PDF report."""
    data = _load_investigation(investigation_id)
    html = _render_investigation_html(data)

    if fmt == "pdf":
        try:
            from weasyprint import HTML  # type: ignore[import-not-found]

            pdf_bytes = HTML(string=html).write_pdf()
            return FastAPIResponse(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{investigation_id}.pdf"',
                },
            )
        except ImportError as err:
            raise HTTPException(
                status_code=501,
                detail="PDF export requires weasyprint. Install with: pip install weasyprint",
            ) from err

    return FastAPIResponse(
        content=html,
        media_type="text/html",
        headers={
            "Content-Disposition": f'attachment; filename="{investigation_id}.html"',
        },
    )
