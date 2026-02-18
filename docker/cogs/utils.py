import discord
from discord.ext import commands, tasks
import logging
import requests
import datetime
import os
from utils.logger import clean_old_logs

logger = logging.getLogger('discord_bot')

# =====================================================================================================================
# 1. MAIN COG CLASS
# =====================================================================================================================

class Utils(commands.Cog):
    """A cog for utility commands."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("Utils cog initialized")
        self.log_cleanup_task.start() # Start the scheduled task

    def cog_unload(self):
        # Ensure the task is stopped when the cog is unloaded
        self.log_cleanup_task.cancel()

    @tasks.loop(time=datetime.time(hour=10, minute=0, tzinfo=datetime.timezone.utc)) # 5:00 AM GMT-5 is 10:00 AM UTC
    async def log_cleanup_task(self):
        """Task to clean up old log files daily."""
        # Use configured log directory from config
        from config import LOG_DIR
        await self.bot.loop.run_in_executor(
            None, clean_old_logs, LOG_DIR, 3 # Run clean_old_logs in a separate thread pool executor
        )

    @log_cleanup_task.before_loop
    async def before_log_cleanup_task(self):
        await self.bot.wait_until_ready()
        logger.info("Log cleanup task is ready.")

    @commands.command(name='ping', hidden=True, help="Checks the bot's latency.")
    async def ping(self, ctx: commands.Context):
        """Checks the bot's latency."""
        logger.info(f'Ping command used by {ctx.author}')
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! Latency: {latency}ms 🌐')

    @commands.command(name='qotd', help='Gets the quote of the day.')
    async def qotd(self, ctx: commands.Context):
        """Gets the quote of the day."""
        logger.info(f'QOTD command used by {ctx.author}')
        try:
            response = requests.get("https://zenquotes.io/api/today")
            response.raise_for_status()
            data = response.json()[0]
            quote = data['q']
            author = data['a']
            embed = discord.Embed(
                title="Quote of the Day",
                description=f"> {quote}",
                color=discord.Color.random()
            )
            embed.set_footer(text=f"~ {author}")
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"QOTD command failed: {e}")
            await ctx.send("I couldn't fetch the quote of the day. Please try again later.")

# =====================================================================================================================
# 2. SETUP FUNCTION
# =====================================================================================================================
async def setup(bot: commands.Bot):
    """
    Loads the Utils cog.
    Args:
        bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(Utils(bot))
    logger.info("Utils cog loaded")
