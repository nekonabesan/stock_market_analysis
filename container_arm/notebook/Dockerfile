FROM python:3.12-slim

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /workspace

# Install minimal system dependencies (do NOT build TA-Lib from source)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    poppler-utils \
    ca-certificates \
    chromium \
    && apt-get autoremove -y && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition and install dependencies
COPY container_arm/notebook/pyproject.toml ./
COPY container_arm/notebook/requestment.txt ./
RUN uv sync --no-dev --no-install-project

# Install Python packages that are managed outside uv project dependencies.
RUN uv run pip install --no-cache-dir -r requestment.txt

# Create notebook working directory
RUN mkdir -p /workspace/notebook

EXPOSE 8888

CMD ["uv", "run", "jupyter", "lab", \
     "--ip=0.0.0.0", \
     "--port=8888", \
     "--no-browser", \
     "--allow-root", \
    "--notebook-dir=/workspace/notebook", \
    "--ServerApp.token=", \
    "--ServerApp.password=", \
    "--ServerApp.allow_origin=*", \
    "--ServerApp.disable_check_xsrf=True"]
