FROM python:3.12-slim

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies for psycopg2 + cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition and install dependencies (cache layer)
# --no-install-project: app/ がまだ存在しないためプロジェクト自体はスキップし依存のみインストール
COPY backend/pyproject.toml ./
RUN uv sync --no-dev --no-install-project

# Copy application source and migration config
COPY backend/app ./app
COPY backend/migrations ./migrations
COPY backend/alembic.ini ./

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
