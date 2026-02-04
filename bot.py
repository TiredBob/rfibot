#!/usr/bin/env python3
import os
import discord
from discord.ext import commands
from discord.ext.commands import Context
import asyncio
import logging
import traceback
from config import TOKEN, COMMAND_PREFIX
from utils.logger import setup_logger
from utils.discord_error_handler import DiscordErrorHandler


# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Change the current working directory to the script's directory
os.chdir(BASE_DIR)

# Setup logging
logger = setup_logger(log_dir=BASE_DIR)

# Initialize bot with all intents
intents = discord.Intents.default()
intents.message_content = True  # Explicitly enable message content
intents.reactions = True
intents.guilds = True
intents.messages = True  # Explicitly enable messages intent
intents.members = True   # Enable member events for welcome messages
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, case_insensitive=True, help_command=None)

# Initialize Discord error handler (will be fully initialized in on_ready)
discord_error_handler = DiscordErrorHandler(bot)

# Load cogs
async def load_cogs():
    """Dynamically loads all cogs from the 'cogs' directory."""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f"Loaded cog: {filename}")
            except Exception as e:
                logger.error(f"Failed to load cog {filename}: {e}")
                traceback.print_exc()

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    
    # Initialize Discord error handler async components
    await discord_error_handler.initialize_async()
    
    # Ensure bot-status channel exists in the first guild
    if bot.guilds:
        first_guild = bot.guilds[0]
        await discord_error_handler.ensure_status_channel_exists(first_guild)
        
    # Log guild information
    guild_count = len(bot.guilds)
    if guild_count == 0:
        logger.warning('Bot is not in any guilds. Please invite the bot using the link below.')
    else:
        # Safely handle guild names with truncation and escaping
        safe_guild_names = []
        for guild in bot.guilds:
            # Truncate long guild names and escape special characters
            safe_name = guild.name.replace('`', '\\`').replace('*', '\\*').replace('_', '\\_')
            if len(safe_name) > 20:  # Truncate very long names
                safe_name = safe_name[:17] + '...'
            safe_guild_names.append(safe_name)
        
        guild_names = ", ".join(safe_guild_names)
        # Truncate the final string if it's too long
        if len(guild_names) > 100:
            guild_names = guild_names[:97] + '...'
        logger.info(f"Connected to {guild_count} guild(s): {guild_names}")

    # Generate invite link with explicit permissions
    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(
            send_messages=True,
            read_messages=True,
            add_reactions=True,
            embed_links=True,
            read_message_history=True
        )
    )
    logger.info(f'Invite link: {invite_link}')
    await bot.change_presence(activity=discord.Game(name="!help for commands"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if the message starts with the command prefix before logging
    if message.content.startswith(COMMAND_PREFIX):
        logger.info(f"Command received: {message.content} from {message.author} in channel {message.channel.name}")

    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    logger.info(f'Bot joined new guild: {guild.name} (id: {guild.id})')

@bot.event
async def on_error(event, *args, **kwargs):
    """Logs unhandled exceptions from events."""
    logger.error(f"Unhandled error in event: {event}")
    traceback.print_exc()

@bot.event
async def on_command_error(ctx: Context, error: commands.CommandError):
    """Handles errors that occur during command execution."""
    if hasattr(ctx.command, 'on_error'):
        # If the command has its own error handler, let it handle it.
        return

    # Get the original error for more specific handling
    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound):
        logger.info(f"Invalid command received: {ctx.message.content} from {ctx.author} in channel {ctx.channel.name}")
        # This is handled by the help command's on_help_command_error (or implicitly ignored if no help handler)
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"You're missing a required argument: `{error.param.name}`. Use `!help {ctx.command.name}` for more info.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.", delete_after=5)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.UserNotFound):
        await ctx.send("Could not find the specified user. Please make sure you @mention them correctly.")
    else:
        logger.error(f"An unhandled error occurred in command '{ctx.command.name}':")
        traceback.print_exception(type(error), error, error.__traceback__)
        await ctx.send("An error occurred while executing the command.")

async def main():
    try:
        async with bot:
            await load_cogs()
            await bot.start(TOKEN)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, shutting down.")
    finally:
        if bot.is_closed() is False:
            await bot.close()
            logger.info("Bot connection closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot shutdown complete.")