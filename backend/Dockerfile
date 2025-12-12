FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Render uses PORT env variable
ENV PORT=8000

# Remove --reload for production
CMD uvicorn app.api:app --host 0.0.0.0 --port $PORT
