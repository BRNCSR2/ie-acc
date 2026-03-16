#!/usr/bin/env bash
set -euo pipefail

cd "$1"
uv sync --extra dev
uv run ruff check src/ tests/
uv run mypy src/
uv run pytest -q
