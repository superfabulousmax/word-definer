FROM python:3.11-slim

RUN echo "=== [Dockerfile] Starting build on Render.com ==="

# Install system dependencies
RUN apt-get update && apt-get install -y tesseract-ocr && rm -rf /var/lib/apt/lists/* \
    && echo "=== [Dockerfile] Tesseract installed ==="

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

# Expose port (Render expects 8000 or 10000, but gunicorn default is 8000)
EXPOSE 8000

# Start the app with gunicorn
CMD echo "=== [Dockerfile] Starting app with gunicorn ===" && gunicorn main:app --bind 0.0.0.0:8000 