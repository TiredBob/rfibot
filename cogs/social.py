import discord
from discord.ext import commands
import secrets
import logging

logger = logging.getLogger('discord_bot')

# =====================================================================================================================
# 1. CONFIGURATION & CONSTANTS
# =====================================================================================================================

SLAPS = [
    "slaps {user} with a large trout! 🐟",
    "slaps {user} across the face!",
    "gives {user} a gentle slap.",
    "delivers a mighty slap to {user}!",
    "bitch slaps {user} into oblivion",
    "knocks {user} out cold with a slap to the face.",
]

# =====================================================================================================================
# 2. MAIN COG CLASS
# =====================================================================================================================

class Social(commands.Cog):
    """A cog for social commands."""
    def __init__(self, bot: commands.Bot):
        """
        Initializes the Social cog.
        Args:
            bot (commands.Bot): The bot instance.
        """
        self.bot = bot
        logger.info('Social cog initialized')
        # --- Dynamically create social commands ---
        social_command_definitions = [
            {
                "name": "slap",
                "help": "Slaps another user. Example: !slap @User",
                "responses": SLAPS,
                "aliases": []
            }
        ]
        for definition in social_command_definitions:
            self._create_social_command(**definition)
            
    def _create_social_command(self, name: str, help: str, responses: list, aliases: list):
        """A factory to create and register social commands."""
        
        @commands.command(name=name, help=help, aliases=aliases)
        async def social_command(self, ctx: commands.Context, user: discord.Member):
            logger.info(f'{name} command used by {ctx.author} on {user.name}')
            await ctx.send(f'{ctx.author.mention} {secrets.choice(responses).format(user=user.mention)}')
        
        # Bind the command to the class and add it to the bot
        social_command.cog = self
        self.bot.add_command(social_command)

# =====================================================================================================================
# 3. SETUP FUNCTION
# =====================================================================================================================
async def setup(bot: commands.Bot):
    """
    Loads the Social cog.
    Args:
        bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(Social(bot))
    logger.info("Social cog loaded")
