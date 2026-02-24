# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV, Tesseract, and build tools for bcrypt
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install CPU-only torch first (avoids large CUDA downloads)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install ONNX Runtime for faster OCR (2-5x speedup on CPU)
RUN pip install --no-cache-dir onnxruntime

# Install sentence-transformers (will use already installed CPU torch)
RUN pip install --no-cache-dir sentence-transformers

# Install rest of Python dependencies (excluding sentence-transformers)
RUN grep -v "sentence-transformers" requirements.txt > /tmp/requirements.txt && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy backend application code
COPY backend/ .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
