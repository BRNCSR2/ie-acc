"""FastAPI application for ie-acc."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from neo4j import AsyncGraphDatabase

from ieacc.middleware.gdpr import GDPRMiddleware
from ieacc.routers import entity, gdpr, graph, investigations, meta, patterns, search

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage Neo4j driver lifecycle."""
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "changeme")

    driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
    app.state.neo4j_driver = driver
    logger.info("Neo4j driver connected to %s", uri)
    yield
    await driver.close()
    logger.info("Neo4j driver closed")


app = FastAPI(
    title="ie-acc API",
    description="Irish Open Transparency Graph API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GDPR middleware (active when PUBLIC_MODE=true)
app.add_middleware(GDPRMiddleware)

# Routers
app.include_router(meta.router)
app.include_router(search.router)
app.include_router(entity.router)
app.include_router(graph.router)
app.include_router(patterns.router)
app.include_router(gdpr.router)
app.include_router(investigations.router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Basic health check."""
    return {"status": "ok"}
