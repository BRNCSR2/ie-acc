.PHONY: dev stop clean test test-api test-etl test-frontend test-integration lint type-check check seed api frontend

# ── Development ──

dev:
	docker compose up -d --build

stop:
	docker compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

# ── Testing ──

test: test-api test-etl test-frontend

test-api:
	cd api && uv run pytest -q

test-etl:
	cd etl && uv run pytest -q

test-frontend:
	cd frontend && npm test -- --run

test-integration:
	cd api && uv run pytest -m integration -q
	cd etl && uv run pytest -m integration -q

# ── Quality ──

lint:
	cd api && uv run ruff check src/ tests/
	cd etl && uv run ruff check src/ tests/
	cd frontend && npx eslint src/

type-check:
	cd api && uv run mypy src/
	cd etl && uv run mypy src/
	cd frontend && npx tsc --noEmit

check: lint type-check test

# ── Services ──

api:
	cd api && uv run uvicorn ieacc.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

seed:
	bash infra/scripts/seed-dev.sh

# ── ETL Pipelines ──

etl-cro:
	cd etl && uv run ieacc-etl run --source cro

download-cro:
	bash etl/scripts/download_cro.sh

download-lobbying:
	bash etl/scripts/download_lobbying.sh

download-oireachtas:
	bash etl/scripts/download_oireachtas.sh

download-charities:
	bash etl/scripts/download_charities.sh

download-etenders:
	bash etl/scripts/download_etenders.sh

download-epa:
	bash etl/scripts/download_epa.sh

download-ppr:
	bash etl/scripts/download_ppr.sh

download-all: download-cro download-lobbying download-oireachtas download-charities download-etenders download-epa download-ppr

etl-lobbying:
	cd etl && uv run ieacc-etl run --source lobbying

etl-oireachtas:
	cd etl && uv run ieacc-etl run --source oireachtas

etl-charities:
	cd etl && uv run ieacc-etl run --source charities

etl-etenders:
	cd etl && uv run ieacc-etl run --source etenders

etl-epa:
	cd etl && uv run ieacc-etl run --source epa

etl-ppr:
	cd etl && uv run ieacc-etl run --source ppr

etl-all:
	cd etl && uv run ieacc-etl run --source cro
	cd etl && uv run ieacc-etl run --source lobbying
	cd etl && uv run ieacc-etl run --source oireachtas
	cd etl && uv run ieacc-etl run --source charities
	cd etl && uv run ieacc-etl run --source etenders
	cd etl && uv run ieacc-etl run --source epa
	cd etl && uv run ieacc-etl run --source ppr
