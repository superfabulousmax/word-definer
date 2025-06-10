FROM python:3.11-slim

RUN echo "=== [Dockerfile] Starting build ==="

# Install system dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 && \
    rm -rf /var/lib/apt/lists/* && \
    echo "=== [Dockerfile] Tesseract, libGL, and OpenCV dependencies installed ==="

# Set workdir
WORKDIR /app
RUN echo "=== [Dockerfile] Workdir set to /app ==="

# Copy requirements and install
COPY requirements.txt .
RUN echo "=== [Dockerfile] requirements.txt copied ==="
RUN pip install --no-cache-dir -r requirements.txt \
    && echo "=== [Dockerfile] Python dependencies installed ==="

# Copy the rest of the app
COPY . .
RUN echo "=== [Dockerfile] App code copied ==="

# Expose port
EXPOSE 8000
ENV PYTHONPATH=/app/src
# Start the app with gunicorn
CMD ["gunicorn", "src.main:app", "--bind", "0.0.0.0:8000"] 