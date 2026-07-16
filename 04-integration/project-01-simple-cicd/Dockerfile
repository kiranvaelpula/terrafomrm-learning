# Build stage
FROM python:3.9-slim as builder

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.9-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app/ .

# Set environment
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Run with gunicorn for production
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "2", "app:app"]
