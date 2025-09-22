# Use Python 3.12 slim image
FROM python:3.12.6-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Build stage
FROM base as builder

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --prefix="/install" -r requirements.txt

# Production stage
FROM base

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Set permissions
RUN find . -type f -name '*' -exec chmod a+r '{}' \;

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8082

# Set environment variables
ENV PORT 8082
ENV WORKERS 1

# Start the application
CMD gunicorn explainer_agent:app --bind 0.0.0.0:$PORT --workers $WORKERS --worker-class uvicorn.workers.UvicornWorker --access-logfile - --error-logfile -
