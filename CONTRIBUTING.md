# Contributing to ie-acc

## Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Install dependencies:
   ```bash
   # API
   cd api && uv sync --extra dev

   # ETL
   cd etl && uv sync --extra dev

   # Frontend
   cd frontend && npm install
   ```

## Code Standards

### Python (API + ETL)

- **Formatter/Linter:** [ruff](https://docs.astral.sh/ruff/) with strict rules
- **Type checker:** [mypy](https://mypy-lang.org/) in strict mode
- **Testing:** [pytest](https://pytest.org/) with async support
- **Line length:** 100 characters
- **Target:** Python 3.12+

### TypeScript (Frontend)

- **Linter:** ESLint 9 flat config with typescript-eslint
- **Type checker:** TypeScript strict mode
- **Testing:** [vitest](https://vitest.dev/) with React Testing Library
- **Target:** ES2020

### Quality Gate

All code must pass before merging:

```bash
make check   # Runs: lint + type-check + test
```

## Adding a New ETL Pipeline

1. Create `etl/src/ieacc_etl/pipelines/{source}.py` implementing the `Pipeline` base class
2. Implement `extract()`, `transform()`, and `load()` methods
3. Register in `etl/src/ieacc_etl/pipelines/__init__.py`
4. Create test fixture at `etl/tests/fixtures/{source}/`
5. Write tests at `etl/tests/test_{source}_pipeline.py`
6. Create download script at `etl/scripts/download_{source}.sh`
7. Add Makefile targets: `etl-{source}` and `download-{source}`
8. Update `config/source_registry_ie.csv`

Use the `_clean()` helper pattern for NaN-safe value extraction:

```python
def _clean(val: object) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip() if val else ""
```

## Adding an Intelligence Pattern

1. Add the pattern query to `PATTERNS` dict in `api/src/ieacc/routers/patterns.py`
2. Each pattern is a tuple of `(description, cypher_query)`
3. Update the pattern count in `api/tests/test_patterns.py`
4. Ensure seed data in `infra/scripts/seed-dev.cypher` exercises the pattern

## Adding an API Endpoint

1. Create or extend a router in `api/src/ieacc/routers/`
2. Register in `api/src/ieacc/main.py`
3. Use `execute_query()` from `neo4j_service.py` for database access
4. Write tests with the `client` fixture from `conftest.py`
5. Update the frontend API client at `frontend/src/api/client.ts`

## Git Workflow

- Create feature branches from `main`
- Write descriptive commit messages
- Ensure `make check` passes before pushing
- CI runs automatically on every push and PR

## GDPR Considerations

When adding new data sources or entity types:

- Determine if data contains personal information
- Add appropriate name fields to `NAME_FIELDS` in `api/src/ieacc/middleware/gdpr.py`
- Public figures (elected officials, etc.) should be added to `PUBLIC_FIGURE_TYPES`
- Update the privacy notice at `api/src/ieacc/routers/gdpr.py` if new data categories are added

## Testing

- **Unit tests** run against synthetic fixtures (no external dependencies)
- **Integration tests** (`@pytest.mark.integration`) require a running Neo4j instance
- Default `make test` runs unit tests only
- `make test-integration` requires Docker or a local Neo4j
