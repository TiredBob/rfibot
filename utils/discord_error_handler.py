#!/usr/bin/env python3
"""
Discord Error Handler - Logs Python errors and warnings to Discord bot-status channel.
"""

import discord
from discord.ext import commands
import logging
import traceback
import sys
import time
import asyncio
from typing import Optional

class DiscordErrorHandler:
    """Handles logging of Python errors and warnings to Discord."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.status_channel_name = "bot-status"
        self.status_channel = None
        self.last_channel_find_attempt = 0
        self.channel_find_cooldown = 60  # Cooldown in seconds
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging to capture Python errors and warnings."""
        # Create a logger for Discord error handling
        self.logger = logging.getLogger('discord_error_handler')
        self.logger.setLevel(logging.INFO)
        
        # Add a custom handler that sends errors to Discord
        discord_handler = DiscordLogHandler(self)
        discord_handler.setLevel(logging.WARNING)  # Only send WARNING and above to Discord
        
        # Add the handler to the root logger to catch all errors
        root_logger = logging.getLogger()
        root_logger.addHandler(discord_handler)
        
        # Also catch uncaught exceptions
        sys.excepthook = self.handle_uncaught_exception
        
        # Note: We can't call async methods here during __init__
        # The channel finding will be done in initialize_async()
    
    async def find_status_channel(self) -> Optional[discord.TextChannel]:
        """Find the bot-status channel."""
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if channel.name == self.status_channel_name:
                    self.status_channel = channel
                    self.logger.info(f"Found bot-status channel: {channel.name}")
                    return channel
        
        self.logger.warning(f"bot-status channel not found. Will create it if possible.")
        return None
    
    async def ensure_status_channel_exists(self, guild: discord.Guild) -> discord.TextChannel:
        """Ensure the bot-status channel exists, create it if it doesn't."""
        # Check if channel already exists
        for channel in guild.text_channels:
            if channel.name == self.status_channel_name:
                self.status_channel = channel
                return channel
        
        # Create the channel if it doesn't exist
        try:
            channel = await guild.create_text_channel(self.status_channel_name)
            self.status_channel = channel
            self.logger.info(f"Created bot-status channel: {channel.name}")
            return channel
        except Exception as e:
            self.logger.error(f"Failed to create bot-status channel: {e}")
            return None
    
    async def initialize_async(self):
        """Initialize async components after the event loop is running."""
        # Find the status channel
        await self.find_status_channel()
        self.logger.info("Discord error handler initialized")
    
    def handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions and log them to Discord."""
        # Format the exception
        error_message = f"🚨 **Uncaught Exception** 🚨\n"
        error_message += f"**Type:** `{exc_type.__name__}`\n"
        error_message += f"**Value:** `{exc_value}`\n"
        error_message += f"**Traceback:**\n```\n"
        
        # Get the traceback as a string
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        error_message += "".join(tb_lines)
        error_message += "```"
        
        # Log to Discord asynchronously
        asyncio.create_task(self.send_error_to_discord(error_message))
        
        # Also log to console
        self.logger.error(f"Uncaught exception: {exc_value}")
        
        # Call the original excepthook
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    async def send_error_to_discord(self, message: str):
        """Send an error message to the bot-status channel."""
        # Check if we're in an async context
        try:
            if not self.status_channel:
                now = time.time()
                if now - self.last_channel_find_attempt < self.channel_find_cooldown:
                    return  # Cooldown active, do not attempt to find channel
                self.last_channel_find_attempt = now

                # Try to find the channel again
                self.status_channel = await self.find_status_channel()
                
            if self.status_channel:
                try:
                    # Split long messages into chunks (Discord has a 2000 character limit)
                    chunks = [message[i:i+1900] for i in range(0, len(message), 1900)]
                    
                    for chunk in chunks:
                        await self.status_channel.send(chunk)
                    self.logger.info("Error message sent to Discord bot-status channel")
                except Exception as e:
                    self.logger.error(f"Failed to send error to Discord: {e}")
            else:
                self.logger.warning("No bot-status channel available to send error message")
        except RuntimeError as e:
            if "no running event loop" in str(e):
                # Fallback to console logging if no event loop
                print(f"Discord error (no event loop): {message}", file=sys.stderr)
            else:
                raise
    
    async def log_mqtt_error(self, error_message: str):
        """Log MQTT-specific errors to Discord."""
        formatted_message = f"📡 **MQTT Error** 📡\n```\n{error_message}\n```"
        await self.send_error_to_discord(formatted_message)

class DiscordLogHandler(logging.Handler):
    """Custom logging handler that sends logs to Discord."""
    
    def __init__(self, error_handler: DiscordErrorHandler):
        super().__init__()
        self.error_handler = error_handler
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record to Discord."""
        try:
            # Format the log message
            msg = self.format(record)
            
            # Add some formatting for Discord
            level_name = record.levelname
            formatted_message = f"📝 **{level_name}** 📝\n```\n{msg}\n```"
            
            # Send asynchronously, but handle cases where event loop might not be available
            try:
                asyncio.create_task(self.error_handler.send_error_to_discord(formatted_message))
            except RuntimeError:
                # Event loop not available, just print to stderr
                print(f"Discord error (no event loop): {formatted_message}", file=sys.stderr)
            
        except Exception as e:
            # Don't let errors in the error handler cause more problems
            print(f"Failed to send log to Discord: {e}", file=sys.stderr)