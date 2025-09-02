# MUZAM Docker Image
# ==================

# Use Python 3.11 slim image as base
# 🎵 MUZAM - GhostKitty Audio Recognition Docker Image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 
    PYTHONUNBUFFERED=1 
    PIP_NO_CACHE_DIR=1 
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y 
    ffmpeg 
    libsndfile1 
    gcc 
    g++ 
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash muzam

# Set work directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for database
RUN mkdir -p /app/data && chown -R muzam:muzam /app

# Switch to non-root user
USER muzam

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 
  CMD curl -f http://localhost:8000/api/health || exit 1

# Default command
CMD ["python", "-m", "muzam.web.app", "--host", "0.0.0.0", "--port", "8000"]

# Build arguments for version info
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Labels
LABEL maintainer="MUZAM Community <community@muzam.org>" \
      org.label-schema.name="MUZAM" \
      org.label-schema.description="Open Source Audio Recognition Engine" \
      org.label-schema.url="https://github.com/muzam-project/muzam" \
      org.label-schema.vcs-url="https://github.com/muzam-project/muzam" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.version=$VERSION \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.schema-version="1.0"
