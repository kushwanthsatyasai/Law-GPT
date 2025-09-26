# Multi-stage build for production
FROM python:3.11-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    poppler-utils \
    tesseract-ocr \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --gid 1001 --system backend && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group backend

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/backend/.local

# Set up working directory
WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /data/uploads && \
    chown -R backend:backend /app /data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/home/backend/.local/lib/python3.11/site-packages:$PYTHONPATH
ENV PATH=/home/backend/.local/bin:$PATH

# Switch to non-root user
USER backend

EXPOSE 8000

# Health check (Railway handles health checks, so we'll make this optional)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#   CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Use PORT environment variable provided by Render, fallback to 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
