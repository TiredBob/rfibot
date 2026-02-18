# rfibot Discord Bot - Docker Edition

A Dockerized version of the rfibot Discord bot for easy deployment and management.

## 🚀 Quick Start

### Prerequisites
- Docker installed on your system
- Docker Compose (usually included with Docker)
- A Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications)

### 1. Setup Configuration

Copy the example environment file and add your Discord token:

```bash
cd /home/bob/dev/rfibot/docker/
cp .env.example .env
nano .env
```

Edit the `.env` file and replace `your_bot_token_here` with your actual Discord bot token:

```env
DISCORD_TOKEN=your_actual_bot_token_here
COMMAND_PREFIX=!
DEBUG_MODE=False
LOG_LEVEL=INFO
```

### 2. Build and Run

```bash
docker-compose build
docker-compose up -d
```

### 3. Monitor Your Bot

```bash
docker-compose logs -f
```

## 📋 Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | ✅ Yes | None | Your Discord bot token |
| `COMMAND_PREFIX` | ❌ No | `!` | Bot command prefix |
| `DEBUG_MODE` | ❌ No | `False` | Enable debug logging |
| `LOG_LEVEL` | ❌ No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_DIR` | ❌ No | `/app/logs` | Log directory path for persistent logging |
| `TZ` | ❌ No | `UTC` | Timezone for container |

### Volume Mounts

- `./logs:/app/logs` - Persistent log storage (automatically created)
- **Note**: The `LOG_DIR` environment variable can be used to customize the log directory path

## 🛠️ Management Commands

### Start the bot
```bash
docker-compose up -d
```

### Stop the bot
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Check bot status
```bash
docker-compose ps
```

### Access container shell (for debugging)
```bash
docker-compose exec rfibot bash
```

### Update the bot
```bash
docker-compose down && docker-compose up -d --build
```

### Clean up old containers and images
```bash
docker system prune -f
```

## 🎯 New Features

### Graceful Shutdown

The bot now supports graceful shutdown handling for Docker containers:

- **SIGTERM/SIGINT handling**: Properly catches container stop signals
- **Clean resource cleanup**: Ensures all connections are closed properly
- **Logging**: Detailed shutdown logging for debugging

### Log Directory Configuration

The bot now supports configurable log directories via the `LOG_DIR` environment variable:

```bash
# Use default /app/logs
docker run -e LOG_DIR=/app/logs rfibot

# Use custom log directory
docker run -e LOG_DIR=/custom/logs -v /host/logs:/custom/logs rfibot
```

### Improved Error Handling

- **Filesystem operations**: Better error handling for log file operations
- **Configuration validation**: Proper validation of environment variables
- **Container health**: Improved health check consistency

## 🔧 Advanced Configuration

### Custom Log Directory Setup

To use a custom log directory:

```bash
# Create custom log directory
mkdir -p /path/to/custom/logs
chmod 777 /path/to/custom/logs

# Run with custom log directory
docker run -d \
  --name rfibot \
  -e LOG_DIR=/app/custom_logs \
  -v /path/to/custom/logs:/app/custom_logs \
  rfibot
```

### Debugging Filesystem Issues

If you encounter filesystem issues:

```bash
# Check container filesystem
docker exec -it rfibot ls -la /app/logs

# Check permissions
docker exec -it rfibot ls -la /app

# Check environment variables
docker exec -it rfibot env | grep LOG
```

### Custom Docker Build

If you need to customize the build process:

```bash
docker build -t rfibot .
docker run -d \
  --name rfibot \
  --restart unless-stopped \
  -e DISCORD_TOKEN=your_bot_token_here \
  -e LOG_DIR=/app/logs \
  -v $(pwd)/logs:/app/logs \
  rfibot
```

### Environment Variables in Command Line

```bash
docker run -d \
  --name rfibot \
  -e DISCORD_TOKEN=your_token \
  -e COMMAND_PREFIX="!" \
  -e DEBUG_MODE=True \
  -e LOG_LEVEL=DEBUG \
  -e LOG_DIR=/custom/log/path \
  rfibot
```

## 📁 Project Structure

```
rfibot/docker/
├── bot.py                          # Main bot entry point
├── config.py                       # Docker-optimized configuration
├── pyproject.toml                  # Python dependencies
├── Dockerfile                      # Docker build instructions
├── docker-compose.yml              # Docker Compose configuration
├── .dockerignore                   # Files to exclude from Docker build
├── .env.example                    # Environment variable template
├── logs/                           # Persistent log storage directory
├── cogs/                           # Bot modules (games, help, social, utils)
└── utils/                          # Utility modules (logger, error handler)
```

## 🔒 Security Features

- **Non-root execution**: Container runs as `botuser` for security
- **Environment variables**: No hardcoded secrets
- **Minimal base image**: Uses `python:3.12-slim` for smaller attack surface
- **Volume isolation**: Logs stored separately from container
- **Health monitoring**: Built-in health checks
- **Automatic restarts**: Container restarts on failure

## 🐳 Docker Best Practices Implemented

1. **Multi-stage builds**: Optimized layer caching
2. **Non-root user**: Security best practice
3. **Minimal base image**: Reduced attack surface
4. **Proper .dockerignore**: Excludes unnecessary files
5. **Health checks**: Container monitoring
6. **Volume management**: Persistent data storage
7. **Environment variables**: Configurable without rebuilds
8. **Proper permissions**: Secure file access

## 🚫 Troubleshooting

### Common Issues

#### Missing DISCORD_TOKEN
**Error**: `ValueError: DISCORD_TOKEN environment variable is required`
**Solution**: Ensure `.env` file exists and contains your token

#### Permission Issues
**Error**: `Permission denied` when creating logs
**Solution**: 
```bash
# Ensure log directory exists and has proper permissions
mkdir -p logs
chmod 777 logs

# Or use a different log directory
mkdir -p /tmp/rfibot_logs
chmod 777 /tmp/rfibot_logs
docker run -e LOG_DIR=/app/logs -v /tmp/rfibot_logs:/app/logs rfibot
```

#### Container Won't Start
**Check**: `docker-compose logs`
**Verify**: Token is correct and Discord API is available

#### Container Won't Stop Gracefully

**Issue**: Container takes too long to stop
**Solution**: The bot now handles SIGTERM properly. If it still hangs:
```bash
# Check logs for shutdown issues
docker logs rfibot

# Force stop if needed
docker stop -t 10 rfibot
```

#### Log Files Not Persisting

**Issue**: Logs disappear when container restarts
**Solution**: Ensure volume mount is correct:
```bash
# Check volume mount
docker inspect rfibot | grep -A 10 Mounts

# Verify log directory exists on host
ls -la ./logs
```

#### Bot Not Responding
**Check**: `docker ps` to ensure container is running
**Verify**: Bot has correct permissions in Discord

## 📖 Bot Commands

The bot includes the following modules:

- **Basic Commands**: Core functionality
- **Games**: Interactive games
- **Help**: Command documentation
- **Social**: Social features
- **Utils**: Utility functions

Use `!help` in Discord to see available commands.

## 🔄 Migration from Non-Docker Setup

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

## 🎯 Benefits of Dockerization

1. **Consistent Environment**: Same runtime everywhere
2. **Easy Deployment**: Simple `docker-compose up -d`
3. **Isolation**: No conflicts with system Python
4. **Portability**: Runs on any system with Docker
5. **Version Control**: Easy to roll back versions
6. **Resource Management**: Control CPU/memory limits
7. **Security**: Container isolation from host system
8. **Scalability**: Easy to run multiple instances

## 📞 Support

For issues with the Docker setup, check:
- Docker logs: `docker-compose logs`
- Container status: `docker ps`
- Bot logs in the `logs/` directory

For Discord bot issues:
- Verify your bot token is correct
- Check Discord API status
- Ensure bot has proper permissions in your server

## 📝 License

This project is licensed under the same license as the original rfibot project. See the LICENSE file for details.