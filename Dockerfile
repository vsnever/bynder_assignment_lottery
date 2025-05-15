FROM python:3.12-slim

# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Streams python output directly to terminal
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Update PYTHONPATH to include the app directory
ENV PYTHONPATH=/app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./scripts ./scripts
COPY ./tests ./tests

# Clean up apt cache to reduce image size
RUN apt-get remove --purge -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
