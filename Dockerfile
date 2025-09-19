# Dockerfile for Emergent Playtest Designer
# Lightweight version with mock implementations for easy shipping

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-minimal.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY emergent_playtest_designer/ ./emergent_playtest_designer/
COPY examples/ ./examples/
COPY cli_simple.py .
COPY pyproject.toml .

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose API port
EXPOSE 8000

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/status || exit 1

# Default command
CMD ["python", "cli_simple.py", "server", "--host", "0.0.0.0", "--port", "8000"]
