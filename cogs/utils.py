import discord
from discord.ext import commands
import logging
import requests

logger = logging.getLogger('discord_bot')

# =====================================================================================================================
# 1. MAIN COG CLASS
# =====================================================================================================================

class Utils(commands.Cog):
    """A cog for utility commands."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("Utils cog initialized")

    @commands.command(name='ping', hidden=True, help="Checks the bot's latency.")
    async def ping(self, ctx: commands.Context):
        """Checks the bot's latency."""
        logger.info(f'Ping command used by {ctx.author}')
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! Latency: {latency}ms 🌐')

    @commands.command(name='qotd', help='Gets the quote of the day.')
    async def qotd(self, ctx: commands.comdands.Context):
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
