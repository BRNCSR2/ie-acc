#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEED_FILE="$SCRIPT_DIR/seed-dev.cypher"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-changeme}"

echo "Loading seed data into Neo4j..."

# Try docker exec first (if running in docker compose)
if docker compose ps neo4j --status running 2>/dev/null | grep -q neo4j; then
    echo "Using docker compose neo4j container..."
    docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" < "$SEED_FILE"
else
    echo "Using local cypher-shell..."
    cypher-shell -u neo4j -p "$NEO4J_PASSWORD" < "$SEED_FILE"
fi

echo "Seed data loaded successfully."
