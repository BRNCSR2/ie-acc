# ie-acc — Irish Open Transparency Graph

An open-source graph infrastructure that cross-references Ireland's public databases into a single queryable Neo4j graph. Built to promote transparency and accountability in Irish public life.

Inspired by [br-acc](https://github.com/World-Open-Graph/br-acc) (Brazil's open transparency graph).

## Data Sources

| Source | Type | Status |
|--------|------|--------|
| Companies Registration Office (CRO) | Identity | Loaded |
| Lobbying Register | Political | Loaded |
| Oireachtas Open Data | Political | Loaded |
| Charities Regulator | Identity | Loaded |
| eTenders / OGP | Procurement | Loaded |
| EPA Open Data | Environment | Loaded |
| Property Price Register | Property | Loaded |
| CSO PxStat | Demographics | Planned |
| Planning Permissions | Property | Planned |

See `config/source_registry_ie.csv` for the full registry of 17 tracked sources.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  Frontend   │────▶│   API       │────▶│   Neo4j      │
│  React/Vite │     │  FastAPI    │     │   Graph DB   │
│  Port 3000  │     │  Port 8000  │     │  Port 7474   │
└─────────────┘     └─────────────┘     └──────────────┘
                                              ▲
                    ┌─────────────┐           │
                    │    ETL      │───────────┘
                    │  7 Pipelines│
                    └─────────────┘
```

- **ETL** (`etl/`) — 7 data pipelines (CRO, Lobbying, Oireachtas, Charities, eTenders, EPA, PPR) with extract/transform/load pattern
- **API** (`api/`) — FastAPI with search, entity detail, graph expansion, 8 intelligence patterns, investigation workspace, GDPR compliance
- **Frontend** (`frontend/`) — React 19 + TypeScript + Vite with search, entity explorer, force-directed graph visualisation, pattern analysis, investigation management, and data source dashboard
- **Infrastructure** (`infra/`) — Neo4j schema, seed data, Caddy reverse proxy

## Quick Start

### Prerequisites

- Docker and Docker Compose
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 22+

### Docker (recommended)

```bash
cp .env.example .env
make dev          # Start Neo4j, API, and Frontend
make seed         # Load synthetic seed data
```

Then visit:
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

### Local Development

```bash
# API
cd api && uv sync --extra dev
uv run uvicorn ieacc.main:app --reload --port 8000

# ETL
cd etl && uv sync --extra dev

# Frontend
cd frontend && npm install && npm run dev
```

## ETL Pipelines

Download data and run pipelines:

```bash
make download-all   # Download all source data
make etl-all        # Run all 7 pipelines

# Or individually:
make download-cro && make etl-cro
make download-lobbying && make etl-lobbying
```

Each pipeline follows the extract/transform/load pattern with:
- Synthetic test fixtures in `etl/tests/fixtures/`
- Unit tests per pipeline
- Pandera schema validation
- Neo4jBatchLoader with UNWIND-based batch operations

## Intelligence Patterns

8 predefined Cypher queries that identify noteworthy cross-source relationships:

1. **Lobbying Contract Overlap** — Companies that lobbied a body and were awarded contracts by it
2. **Director Network Contracts** — Shared directors across suppliers to the same authority
3. **Contract Concentration** — Excessive awards to a single supplier
4. **Charity Director Overlap** — Charity trustees directing companies receiving contracts
5. **EPA Violator Contracts** — Companies with EPA licences receiving public contracts
6. **Planning Director Links** — Directors linked to planning applications in their operating areas
7. **Revolving Door** — Politicians appearing in lobbying or company director records
8. **Split Contracts Below Threshold** — Potential contract splitting to avoid procurement thresholds

## GDPR Compliance

- **Public mode** (`PUBLIC_MODE=true`) — Redacts personal names in API responses; blocks access to person entity details
- **Public figures exempt** — TDs, Senators, and public officials remain visible
- **Right to object** — `POST /api/v1/gdpr/object` endpoint for data subjects
- **Privacy notice** — `GET /api/v1/gdpr/privacy-notice` (Art. 14 transparency notice)

## Testing

```bash
make check          # Lint + type-check + all tests
make test           # Unit tests only (API + ETL + Frontend)
make test-api       # API tests (49 tests)
make test-etl       # ETL tests (120 tests)
make test-frontend  # Frontend tests (10 tests)
make lint           # Ruff (Python) + ESLint (TypeScript)
make type-check     # mypy (Python) + tsc (TypeScript)
```

## Project Structure

```
BRNCSR/
├── api/                    # FastAPI backend
│   ├── src/ieacc/
│   │   ├── main.py
│   │   ├── neo4j_service.py
│   │   ├── middleware/gdpr.py
│   │   ├── routers/        # search, entity, graph, patterns, investigations, gdpr
│   │   └── queries/        # .cypher files
│   └── tests/
├── etl/                    # Data pipelines
│   ├── src/ieacc_etl/
│   │   ├── base.py         # Abstract Pipeline class
│   │   ├── loader.py       # Neo4jBatchLoader
│   │   ├── runner.py       # CLI runner
│   │   ├── transforms/     # Name normalisation, address parsing
│   │   ├── pipelines/      # 7 pipeline modules
│   │   └── linking_hooks.py
│   ├── scripts/            # Download scripts per source
│   └── tests/
├── frontend/               # React + TypeScript + Vite
│   ├── src/
│   │   ├── pages/          # 7 pages
│   │   ├── components/     # SearchBar, EntityCard, GraphCanvas
│   │   ├── stores/         # Zustand state management
│   │   └── api/client.ts   # Typed API client
│   └── tests/
├── infra/
│   ├── neo4j/init.cypher   # Graph schema (21 constraints)
│   ├── scripts/            # Seed data scripts
│   └── Caddyfile           # Reverse proxy config
├── config/
│   └── source_registry_ie.csv
├── docker-compose.yml
├── Makefile
└── .github/workflows/ci.yml
```

## License

[GNU Affero General Public License v3.0](LICENSE)
