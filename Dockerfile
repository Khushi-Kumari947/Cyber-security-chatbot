FROM python:3.10-slim

# Prevent Python from buffering and writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system essentials for FAISS/RapidFuzz
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Pre-create asset directories so Boto3 doesn't fail on permissions/paths
RUN mkdir -p cyber_model_tuned vector_store

EXPOSE 10000

# Force 1 worker to stay under 512MB. 
# Lifespan in main.py handles the S3 download via s3_loader.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]