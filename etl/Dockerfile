FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --no-install-project 2>/dev/null || uv pip install --system -r <(uv pip compile pyproject.toml)

COPY src/ src/
RUN uv sync --no-dev 2>/dev/null || uv pip install --system .

WORKDIR /workspace
CMD ["bash"]
