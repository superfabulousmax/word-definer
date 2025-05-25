FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y tesseract-ocr && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port (Render expects 8000 or 10000, but gunicorn default is 8000)
EXPOSE 8000

# Start the app with gunicorn
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000"] 