# Use official Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables for better performance
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Create and switch to non-root user for security
RUN useradd -m botuser && \
    mkdir /app && \
    chown botuser:botuser /app
WORKDIR /app
USER botuser

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Copy only requirements first for better layer caching
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY . .

# Ensure proper permissions and create logs directory
RUN mkdir -p /app/logs && \
    chown -R botuser:botuser /app && \
    chmod -R 755 /app

# Health check (optional but recommended)
HEALTHCHECK --interval=30s --timeout=5s \
    CMD python -c "import discord; print('Healthy')" || exit 1

# Command to run the bot
CMD ["python", "bot.py"]