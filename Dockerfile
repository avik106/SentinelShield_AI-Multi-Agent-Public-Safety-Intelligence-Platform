# ==============================================================================
# SentinelShield AI Backend Dockerfile
# ==============================================================================
FROM python:3.12-slim

# Prevent writing .pyc files and enable unbuffered logging stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system-level dependencies for OpenCV, PyTesseract, Librosa, and Scapy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libpcap-dev \
    libsndfile1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Upgrade pip and install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application files
COPY main.py .
COPY services/ ./services/
COPY shared/ ./shared/
COPY sample_data/ ./sample_data/

# Create reports and uploads directories inside the container
RUN mkdir -p reports uploads

# Expose API port
EXPOSE 8000

# Start server using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
