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
LOG_DIR = os.getenv('LOG_DIR', '/app/logs')