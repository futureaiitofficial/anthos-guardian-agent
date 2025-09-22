# Multi-stage build for Ops Guardian Agent
FROM python:3.12.6-slim as base

# Build stage - install dependencies
FROM base as builder
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --prefix="/install" -r requirements.txt

# Production stage
FROM base as production
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Set proper permissions for security
RUN find . -type f -name '*' -exec chmod a+r '{}' \;

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

# Switch to non-root user
USER app

# Configure environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8083

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8083/ready || exit 1

# Run the application
EXPOSE 8083
CMD ["gunicorn", "--bind", "0.0.0.0:8083", "--workers", "2", "--threads", "4", "--timeout", "60", "ops_guardian:app"]
