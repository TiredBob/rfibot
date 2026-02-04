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
        
    @commands.command(name="invite", help="Generates the bot's invite link.")
    async def invite(self, ctx: commands.Context):
        """Generates the bot's invite link."""
        client_id = self.bot.user.id
        # Permissions can be customized if needed. For a basic bot, 'scope=bot' is sufficient.
        # Example with specific permissions (e.g., Read Messages, Send Messages, Embed Links):
        # permissions = 277025779776 # This is an example, actual value depends on desired permissions
        invite_url = f"https://discord.com/oauth2/authorize?client_id={client_id}&scope=bot"
        await ctx.send(f"You can invite me to your server using this link: {invite_url}")


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
