# =============================================================================
# Mithrava Backend — Railway Dockerfile
# Self-contained: installs deps, copies all code, runs migrations on start.
# Build context: ./backend (Railway service source directory)
# =============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (cached layer — only rebuilds when requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy all application code (app/, alembic/, alembic.ini, start.sh, pyproject.toml)
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs

# Make start script executable
RUN chmod +x /app/start.sh

# Expose the port Railway will assign
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Use tini as PID 1 for proper signal handling
ENTRYPOINT ["tini", "--"]

# Start: run migrations then uvicorn
CMD ["/app/start.sh"]
