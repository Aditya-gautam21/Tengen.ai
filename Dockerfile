# Secure multi-stage Docker build for Tengen.ai
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Create non-root user with specific UID/GID
RUN groupadd -r -g 1000 tengen && useradd -r -g tengen -u 1000 tengen

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=tengen:tengen backend/ ./backend/
COPY --chown=tengen:tengen requirements.txt .

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/logs /tmp/tengen && \
    chown -R tengen:tengen /app /tmp/tengen && \
    chmod 755 /app/data /app/logs

# Switch to non-root user
USER tengen

# Security: Set read-only filesystem (except for specific directories)
VOLUME ["/app/data", "/app/logs", "/tmp/tengen"]

# Environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=8080 \
    LOG_LEVEL=INFO \
    TMPDIR=/tmp/tengen

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health/live || exit 1

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "backend/main.py"]
