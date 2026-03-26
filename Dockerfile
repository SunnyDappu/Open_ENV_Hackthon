# Multi-stage build to reduce image size
FROM python:3.11-slim as builder

WORKDIR /app

# Install only necessary build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy production requirements (lightweight)
COPY requirements-prod.txt .

# Install Python dependencies in a virtual env
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-prod.txt

# Final stage - lightweight runtime
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set runtime environment
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Copy application code (minimal)
COPY warehouse_env/ ./warehouse_env/
COPY app.py .
COPY Procfile .

# Expose port
EXPOSE 7860

# Run the application
CMD ["python", "app.py"]
