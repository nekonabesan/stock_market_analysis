FROM python:3.12-slim

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies for psycopg2 + cryptography + TA-Lib C library
# For Apple Silicon / ARM hosts, ensure autotools config scripts are updated before running ./configure
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    wget \
    make \
    ca-certificates \
    && wget -q https://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    # Update config.guess/config.sub to support modern architectures (ARM / aarch64)
    && cd ta-lib && \
       wget -q -O config.guess "https://git.savannah.gnu.org/cgit/config.git/plain/config.guess" && \
       wget -q -O config.sub   "https://git.savannah.gnu.org/cgit/config.git/plain/config.sub" && \
       chmod +x config.guess config.sub && \
       ./configure --prefix=/usr && make && make install \
    && cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz \
    && apt-get purge -y wget make \
    && apt-get autoremove -y && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition and install dependencies (cache layer)
# --no-install-project: app/ がまだ存在しないためプロジェクト自体はスキップし依存のみインストール
COPY backend/pyproject.toml ./
RUN uv sync --no-dev --no-install-project

# Copy application source and migration config
COPY backend/app ./app
COPY backend/migrations ./migrations
COPY backend/seeds ./seeds
COPY backend/alembic.ini ./

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
