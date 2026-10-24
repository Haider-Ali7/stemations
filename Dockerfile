FROM python:3.12-slim

# Prevent Python from writing .pyc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for Manim, FFmpeg, and audio synthesis
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY scripts/ /app/scripts/
COPY run.py /app/run.py

# Create output directories
RUN mkdir -p /app/backend/_output/scenes /app/backend/_output/audio /app/backend/_output/final

EXPOSE 8000

# Start unified FastAPI server serving both API and Frontend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
