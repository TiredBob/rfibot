import discord
from discord.ext import commands
import logging

logger = logging.getLogger('discord_bot')

class CustomHelpCommand(commands.HelpCommand):
    """Custom help command for a cleaner, embedded look."""

    def get_command_signature(self, command):
        """Generates a clean command usage string."""
        
        params = []
        # Iterate through the command's parameters, excluding self and ctx
        for name, param in command.clean_params.items():
            if param.default is not param.empty:
                # This is an optional argument with a default value.
                # We'll show it as [name] instead of [name=default].
                params.append(f'[{name}]')
            elif param.kind == param.VAR_POSITIONAL:
                # This is for *args
                params.append(f'[{name}...]')
            else:
                # This is a required argument.
                params.append(f'<{name}>')
        
        param_string = " ".join(params)
        return f'{self.context.clean_prefix}{command.qualified_name} {param_string}'.strip()

    async def send_bot_help(self, mapping):
        """Sends help for all commands."""
        embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
        
        for cog, command_list in mapping.items():
            # Filter out commands that shouldn't be shown
            filtered_commands = await self.filter_commands(command_list, sort=True)
            
            if not filtered_commands:
                continue

            # Get cog name, or "No Category" if it's a command without a cog
            cog_name = cog.qualified_name if cog else "No Category"
            command_usages = [self.get_command_signature(c) for c in filtered_commands]
            
            # Add a field for each cog
            embed.add_field(name=cog_name, value="\n".join(f"`{usage}`" for usage in command_usages), inline=False)

        embed.set_footer(text=f"Use {self.context.clean_prefix}help [command] for more info on a command.")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        """Sends help for a specific command."""
        if not command.help and not command.brief:
            await self.get_destination().send(f"No help available for `{command.name}`.")
            return
            
        embed = discord.Embed(title=f"Help: `!{command.name}`", color=discord.Color.green())
        
        # Add command usage
        embed.add_field(name="Usage", value=f"`{self.get_command_signature(command)}`", inline=False)

        # Add command description from the 'help' parameter
        if command.help:
            description = command.help
            example = None
            if "Example:" in description:
                parts = description.split("Example:", 1)
                description = parts[0].strip()
                example = parts[1].strip()
            
            embed.add_field(name="Description", value=description, inline=False)
            if example:
                embed.add_field(name="Example", value=f"`{example}`", inline=False)

        # Add aliases if they exist
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(f"`{alias}`" for alias in command.aliases), inline=False)

        # Add cooldown information if it exists
        if command._buckets and (cooldown := command._buckets._cooldown):
            embed.add_field(name="Cooldown", value=f"{cooldown.rate} time(s) per {cooldown.per:.0f} seconds.", inline=False)

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        """Sends help for a command group."""
        await self.send_command_help(group) # Treat groups like commands for this simple helper

    async def on_help_command_error(self, ctx, error):
        """Handles errors in the help command."""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Command or category not found: `{error.argument}`")
        else:
            logger.error(f"Error in help command: {error}")
            await ctx.send("An error occurred while trying to show help.")


class HelpCog(commands.Cog, name="Help"):
    """A cog to house the custom help command."""
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = CustomHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
    logger.info("Custom HelpCog loaded and help command replaced.")