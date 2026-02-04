import os
from dotenv import load_dotenv

# Load both .env and .envdiscord files
load_dotenv()


# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = '!'
