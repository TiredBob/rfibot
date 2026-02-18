# Dockerization Plan for rfibot Discord Bot

## Overview
This document outlines the complete plan to containerize the rfibot Discord bot using Docker, following security best practices and ensuring portability.

## Current Project Analysis

### Project Structure
- **Language**: Python 3.12
- **Framework**: discord.py 2.6.4
- **Dependencies**: discord-py, requests, python-dotenv
- **Configuration**: Environment variables via .env file
- **Entry Point**: bot.py

### Docker Compatibility Status
✅ **Python code is already Docker-compatible**
- Uses relative paths with `os.path.abspath(__file__)`
- No hardcoded absolute paths in Python files
- Environment variable-based configuration

⚠️ **Files needing attention**
- `manage.sh` - Contains hardcoded paths (will not be used in Docker)
- `config.py` - Can be improved for better Docker support

## Dockerization Plan

### 1. Files to Create

#### 1.1 Dockerfile
```dockerfile
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
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better layer caching
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY . .

# Ensure proper permissions
RUN chown -R botuser:botuser /app && \
    chmod -R 755 /app

# Health check (optional but recommended)
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import discord; print('Healthy')" || exit 1

# Command to run the bot
CMD ["python", "bot.py"]
```

#### 1.2 .dockerignore
```
__pycache__/
.venv/
venv/
*.pyc
*.pyo
*.pyd
.Python
env/
.venv/
.env
.envold
bot.log
*.log
.git/
.gitignore
Dockerfile
docker-compose.yml
README.md
LICENSE
USAGE.md
manage.sh
sync.sh
manage_script_report.md
systemd_service_instructions.md
tmux_server_startup_instructions.md
systemctl_file_locations.md
discord_bot.log
build/
*.bak
*.old
*.md
```

#### 1.3 docker-compose.yml
```yaml
version: '3.8'

services:
  rfibot:
    build: .
    container_name: rfibot
    restart: unless-stopped
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
      - TZ=UTC
    volumes:
      - ./logs:/app/logs
    # No exposed ports needed for Discord bots
    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import discord; print('Healthy')"]
      interval: 30s
      timeout: 5s
      retries: 3
```

### 2. Files to Modify

#### 2.1 config.py (Improved version)
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
# In Docker, we'll primarily use environment variables directly
load_dotenv()

# Bot configuration - ALL values from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required")

COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')

# Additional configuration options that can be set via environment variables
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

#### 2.2 utils/logger.py (Optional improvement)
```python
def setup_logger(log_dir=None):
    # Create logger
    logger = logging.getLogger('discord_bot')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Use /app/logs directory in Docker, or current directory
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, 'discord_bot.log')
    else:
        log_file_path = 'discord_bot.log'

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10000000,
        backupCount=5,
        encoding='utf-8'
    )

    # Rest of the function remains the same...
```

### 3. Files to Exclude from Docker

- `manage.sh` - Not needed in Docker environment
- Local virtual environment files
- Development-specific scripts

## Implementation Steps

### Step 1: Prepare Environment
```bash
# Create necessary directories
mkdir -p logs

# Create .env file (add to .gitignore!)
echo "DISCORD_TOKEN=your_bot_token_here" > .env
echo "COMMAND_PREFIX=!" >> .env
```

### Step 2: Create Docker Files
```bash
# Create Dockerfile
# Create .dockerignore
# Create docker-compose.yml
```

### Step 3: Build Docker Image
```bash
# Build using docker-compose
docker-compose build

# Or build directly with Docker
docker build -t rfibot .
```

### Step 4: Run Container
```bash
# Using docker-compose (recommended)
docker-compose up -d

# Using direct Docker command
docker run -d \
  --name rfibot \
  --restart unless-stopped \
  -e DISCORD_TOKEN=your_bot_token_here \
  -v $(pwd)/logs:/app/logs \
  rfibot
```

### Step 5: Monitor and Manage
```bash
# View logs (docker-compose)
docker-compose logs -f

# View logs (direct Docker)
docker logs -f rfibot

# Check container status
docker ps

# Stop container
docker-compose down
# or
docker stop rfibot

# Update container
docker-compose down && docker-compose up -d --build
```

## Security Best Practices Implemented

1. **No Hardcoded API Keys**
   - All configuration via environment variables
   - `.env` file excluded from Docker build context

2. **Non-Root Execution**
   - Container runs as `botuser` not root
   - Minimal permissions within container

3. **Minimal Base Image**
   - Uses `python:3.12-slim` (smaller attack surface)
   - Only essential system packages installed

4. **No Unnecessary Ports**
   - Discord bots don't need exposed ports
   - Container is isolated from host network

5. **Volume for Logs**
   - Persistent logs stored outside container
   - Easy access to logs for debugging

6. **Health Monitoring**
   - Built-in health checks
   - Automatic container restart on failure

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | ✅ Yes | None | Your Discord bot token |
| `COMMAND_PREFIX` | ❌ No | `!` | Bot command prefix |
| `DEBUG_MODE` | ❌ No | `False` | Enable debug logging |
| `LOG_LEVEL` | ❌ No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `TZ` | ❌ No | `UTC` | Timezone for container |

### Volume Mounts

- `./logs:/app/logs` - Persistent log storage
- Can add more volumes as needed for additional data

## Development vs Production

### Development Workflow
```bash
# Build and run with live reload (if needed)
docker-compose up --build

# Access container shell for debugging
docker-compose exec rfibot bash

# Run tests inside container
docker-compose exec rfibot python -m pytest
```

### Production Deployment
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down && docker-compose up -d --build

# Clean up old images
docker system prune -f
```

## Troubleshooting

### Common Issues

1. **Missing DISCORD_TOKEN**
   - Error: `ValueError: DISCORD_TOKEN environment variable is required`
   - Solution: Set `DISCORD_TOKEN` in `.env` file or environment

2. **Permission Issues**
   - Error: `Permission denied` when creating logs
   - Solution: `mkdir -p logs && chmod 777 logs`

3. **Container Won't Start**
   - Check logs: `docker-compose logs`
   - Verify token is correct
   - Check Discord API status

4. **Bot Not Responding**
   - Check container is running: `docker ps`
   - Verify bot has correct permissions in Discord
   - Check `bot-status` channel for errors

## Migration from Current Setup

### From manage.sh to Docker
```bash
# Old way (manage.sh)
bash manage.sh start

# New way (Docker)
docker-compose up -d

# Old way to check status
bash manage.sh status

# New way to check status
docker-compose ps

# Old way to view logs
tail -f bot.log

# New way to view logs
docker-compose logs -f
```

## Benefits of Dockerization

1. **Consistent Environment** - Same runtime everywhere
2. **Easy Deployment** - Simple `docker-compose up -d`
3. **Isolation** - No conflicts with system Python
4. **Portability** - Runs on any system with Docker
5. **Version Control** - Easy to roll back versions
6. **Resource Management** - Control CPU/memory limits
7. **Security** - Container isolation from host system
8. **Scalability** - Easy to run multiple instances

## Future Enhancements

1. **Multi-stage Build** - Smaller final image
2. **CI/CD Integration** - Automatic builds on push
3. **Monitoring** - Prometheus/Grafana integration
4. **Backup System** - Automatic log backups
5. **Update Notifications** - Alert when new version available

## Conclusion

This Dockerization plan provides a secure, portable, and production-ready container setup for the rfibot Discord bot. The implementation follows Docker best practices and maintains full compatibility with the existing codebase while improving security and deployment flexibility.

**Next Steps:**
1. Create the Docker files as specified
2. Test locally with `docker-compose up -d`
3. Verify bot functionality
4. Deploy to production environment
