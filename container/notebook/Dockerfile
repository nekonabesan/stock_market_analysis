FROM python:3.12-slim

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /workspace

# Install system dependencies and compile TA-Lib C library from source
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    wget \
    make \
    libffi-dev \
    && wget -q https://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib && ./configure --prefix=/usr && make && make install \
    && cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz \
    && apt-get purge -y wget make \
    && apt-get autoremove -y && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition and install dependencies
COPY container/notebook/pyproject.toml ./
RUN uv sync --no-dev --no-install-project

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
