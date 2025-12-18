# docker/Dockerfile
FROM python:3.11-alpine AS base

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apk update && \
    apk add --no-cache build-base

# Copy requirements and install deps
COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY ./app /app/app

# Environment
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Start app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

