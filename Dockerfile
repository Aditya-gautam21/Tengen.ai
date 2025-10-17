# Multi-stage Docker build for Tengen.ai
FROM python:3.10-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r tengen && useradd -r -g tengen tengen

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/tengen/.local

# Copy application code
COPY backend/ ./backend/
COPY data/ ./data/ 2>/dev/null || true
COPY db/ ./db/ 2>/dev/null || true

# Create necessary directories
RUN mkdir -p logs && \
    chown -R tengen:tengen /app

# Switch to non-root user
USER tengen

# Add local Python packages to PATH
ENV PATH=/home/tengen/.local/bin:$PATH
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health/live || exit 1

# Default environment variables
ENV HOST=0.0.0.0
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Run the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
