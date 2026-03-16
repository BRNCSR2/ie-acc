"""CLI runner for ie-acc ETL pipelines."""

from __future__ import annotations

import logging
import os

import click
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)


@click.group()
@click.option("--log-level", default="INFO", help="Logging level")
def cli(log_level: str) -> None:
    """ie-acc ETL pipeline runner."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )


@cli.command()
@click.option("--source", required=True, help="Pipeline source ID")
@click.option("--limit", type=int, default=None, help="Row limit for development")
@click.option("--chunk-size", type=int, default=50_000, help="Batch size")
@click.option("--data-dir", default="./data", help="Data directory")
def run(source: str, limit: int | None, chunk_size: int, data_dir: str) -> None:
    """Run a specific ETL pipeline."""
    from ieacc_etl.pipelines import PIPELINES

    if source not in PIPELINES:
        available = ", ".join(sorted(PIPELINES.keys()))
        raise click.ClickException(f"Unknown source: {source}. Available: {available}")

    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "changeme")
    database = os.environ.get("NEO4J_DATABASE", "neo4j")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        pipeline_cls = PIPELINES[source]
        pipeline = pipeline_cls(
            driver=driver,
            data_dir=data_dir,
            limit=limit,
            chunk_size=chunk_size,
            neo4j_database=database,
        )
        pipeline.run()
    finally:
        driver.close()


@cli.command()
def sources() -> None:
    """List available pipeline sources."""
    from ieacc_etl.pipelines import PIPELINES

    for name in sorted(PIPELINES.keys()):
        click.echo(f"  {name}")
