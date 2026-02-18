import discord
from discord.ext import commands
from typing import Optional, Union
from .database import CreditsDatabase
from .models import UserCredits
from .config import config
import logging
import datetime


class CreditsCog(commands.Cog, name="Credits"):
    """Standalone credits system cog that can be added to any Discord bot"""

    def __init__(self, bot: commands.Bot, db_path: Optional[str] = None):
        """
        Initialize the credits cog.

        Args:
            bot: The Discord bot instance
            db_path: Optional path to database file
        """
        self.bot = bot
        self.db = CreditsDatabase(db_path)
        self.logger = logging.getLogger('CreditsCog')

        # Event listeners will be registered via decorators
        self.logger.info("CreditsCog initialized")

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.logger.info("CreditsCog unloaded")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle new members joining and initialize their credits"""
        try:
            # Ensure server is in database
            self.db.ensure_server_exists(str(member.guild.id), member.guild.name)

            # Ensure user is in database (discriminator is deprecated)
            self.db.ensure_user_exists(
                str(member.id),
                member.name,
                None # Pass None for discriminator as it's deprecated
            )

            # Initialize credits if they don't exist
            if not self.db.user_has_credits(str(member.id), str(member.guild.id)):
                self.db.initialize_user_credits(str(member.id), str(member.guild.id))
                self.logger.info(f"Initialized {config.initial_credits} credits for {member.name} in {member.guild.name}")

        except Exception as e:
            self.logger.error(f"Error in on_member_join for {member.name}: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Handle username changes (discriminator is deprecated)"""
        # Check if username or global_name changed (discriminator is deprecated)
        if before.name != after.name or (hasattr(before, 'global_name') and hasattr(after, 'global_name') and before.global_name != after.global_name):
            try:
                self.db.update_user_info(
                    str(after.id),
                    after.name,
                    None # Pass None for discriminator as it's deprecated
                )
                self.logger.info(f"Updated user info for {after.id}: {before.name} -> {after.name}")
            except Exception as e:
                self.logger.error(f"Error updating user info for {after.id}: {e}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Handle bot joining new server"""
        try:
            self.db.ensure_server_exists(str(guild.id), guild.name)
            self.logger.info(f"Added server to credits database: {guild.name} ({guild.id})")
        except Exception as e:
            self.logger.error(f"Error adding server {guild.id} to database: {e}")

    # Helper methods
    def _is_admin(self, member: discord.Member) -> bool:
        """Check if a member has admin privileges"""
        # Check if member is guild owner
        if member.guild.owner_id == member.id:
            return True
        
        # Check if member has any admin roles
        for role in member.roles:
            if role.name in config.admin_roles:
                return True
            
            # Check if role has administrator permission
            if role.permissions.administrator:
                return True
        
        return False

    def _format_credits(self, amount: int) -> str:
        """Format credit amount with emoji"""
        return f"{amount} 💰"

    # Commands


    @commands.command(name='leaderboard', aliases=['rich', 'lead'])
    async def leaderboard_command(self, ctx: commands.Context):
        """Show the credits leaderboard (top 10)"""
        try:
            leaderboard = self.db.get_leaderboard(str(ctx.guild.id), 10)

            if not leaderboard:
                await ctx.send("📊 The leaderboard is empty!")
                return

            embed = discord.Embed(
                title=f"🏆 Credits Leaderboard - {ctx.guild.name}",
                color=discord.Color.gold()
            )

            for i, entry in enumerate(leaderboard, 1):
                user = self.bot.get_user(int(entry.user_id)) or await self.bot.fetch_user(int(entry.user_id))
                username = user.display_name if user else f"User {entry.user_id}"
                embed.add_field(
                    name=f"{i}. {username}",
                    value=f"{self._format_credits(entry.credits)}",
                    inline=False
                )

            embed.set_footer(text=f"Showing top {len(leaderboard)} users")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in leaderboard command: {e}")
            await ctx.send("❌ An error occurred while generating the leaderboard.")

    @commands.command(name='top')
    async def top_command(self, ctx: commands.Context):
        """Show the top 3 richest users"""
        try:
            leaderboard = self.db.get_leaderboard(str(ctx.guild.id), 3)

            if not leaderboard:
                await ctx.send("📊 No users on the leaderboard yet!")
                return

            embed = discord.Embed(
                title=f"🥇 Top 3 Richest Users - {ctx.guild.name}",
                color=discord.Color.gold()
            )

            for i, entry in enumerate(leaderboard, 1):
                user = self.bot.get_user(int(entry.user_id)) or await self.bot.fetch_user(int(entry.user_id))
                username = user.display_name if user else f"User {entry.user_id}"
                embed.add_field(
                    name=f"{i}. {username}",
                    value=f"{self._format_credits(entry.credits)}",
                    inline=False
                )

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in top command: {e}")
            await ctx.send("❌ An error occurred while generating the top list.")

    @commands.command(name='bottom')
    async def bottom_command(self, ctx: commands.Context):
        """Show the user(s) at the very bottom of the credit barrel"""
        try:
            bottom_users = self.db.get_bottom_users(str(ctx.guild.id))

            if not bottom_users:
                await ctx.send("📊 Everyone is equally broke or rich here.")
                return

            if len(bottom_users) > 3:
                await ctx.send("🙄 Look at this bunch of losers! There are so many of you at the absolute bottom that I can't even pick one. Get some jobs!")
                return

            embed = discord.Embed(
                title=f"📉 The Bottom of the Barrel - {ctx.guild.name}",
                color=discord.Color.dark_red()
            )

            for i, entry in enumerate(bottom_users, 1):
                user = self.bot.get_user(int(entry.user_id)) or await self.bot.fetch_user(int(entry.user_id))
                username = user.display_name if user else f"User {entry.user_id}"
                embed.add_field(
                    name=f"Lowest #{i}: {username}",
                    value=f"{self._format_credits(entry.credits)}",
                    inline=False
                )

            embed.set_footer(text="The only way is up... hopefully.")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in bottom command: {e}")
            await ctx.send("❌ An error occurred while finding the bottom dwellers.")

    @commands.command(name='daily')
    @commands.cooldown(1, config.command_cooldown, commands.BucketType.user)
    async def daily_command(self, ctx: commands.Context):
        """Claim your daily credit reward"""
        try:
            # Check if user can claim (to provide better error message)
            if not self.db.can_claim_daily_reward(str(ctx.author.id), str(ctx.guild.id)):
                await ctx.send("⏳ You've already claimed your daily reward today! Come back after midnight.")
                return

            success = self.db.claim_daily_reward(str(ctx.author.id), str(ctx.guild.id))
            
            if success:
                await ctx.send(f"🎁 Daily reward claimed! You received {self._format_credits(config.daily_reward)}.")
            else:
                await ctx.send("❌ Failed to claim daily reward. Please try again later.")

        except Exception as e:
            self.logger.error(f"Error in daily command: {e}")
            await ctx.send("❌ An error occurred while claiming your daily reward.")

    @commands.command(name='transfer')
    async def transfer_command(self, ctx: commands.Context, amount: int, recipient: discord.Member):
        """Transfer credits to another user"""
        try:
            # Validate amount
            if amount <= 0:
                await ctx.send("❌ Amount must be positive.")
                return
            
            if amount > config.max_transfer_amount:
                await ctx.send(f"❌ Maximum transfer amount is {self._format_credits(config.max_transfer_amount)}.")
                return
            
            if amount < config.min_transfer_amount:
                await ctx.send(f"❌ Minimum transfer amount is {self._format_credits(config.min_transfer_amount)}.")
                return
            
            # Check if transferring to self
            if recipient.id == ctx.author.id:
                await ctx.send("😕 You can't transfer credits to yourself!")
                return
            
            # Check if recipient is a bot
            if recipient.bot:
                await ctx.send("🤖 You can't transfer credits to bots!")
                return
            
            # Perform transfer
            success = self.db.transfer_credits(
                str(ctx.author.id),
                str(recipient.id),
                str(ctx.guild.id),
                amount
            )
            
            if success:
                await ctx.send(f"✅ Successfully transferred {self._format_credits(amount)} to {recipient.display_name}!")
            else:
                # Check sender balance
                sender_balance = self.db.get_user_credits(str(ctx.author.id), str(ctx.guild.id))
                if sender_balance is not None and sender_balance < amount:
                    await ctx.send(f"❌ You don't have enough credits! You have {self._format_credits(sender_balance)}.")
                else:
                    await ctx.send("❌ Transfer failed. Please try again later.")

        except ValueError:
            await ctx.send("❌ Invalid amount. Please enter a valid number.")
        except Exception as e:
            self.logger.error(f"Error in transfer command: {e}")
            await ctx.send("❌ An error occurred during the transfer.")

    @commands.group(name='credits', aliases=['balance'], invoke_without_command=True)
    async def credits_group(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        """Check your credit balance or access admin commands."""
        if ctx.invoked_subcommand is None:
            target_user = user or ctx.author

            try:
                credits = self.db.get_user_credits(str(target_user.id), str(ctx.guild.id))

                if credits is None:
                    # Initialize credits if user doesn't have any
                    self.db.initialize_user_credits(str(target_user.id), str(ctx.guild.id))
                    credits = config.initial_credits
                    await ctx.send(f"🎉 Welcome {target_user.mention}! You've been credited with {self._format_credits(credits)}!")
                else:
                    await ctx.send(f"💰 {target_user.display_name} has {self._format_credits(credits)}.")

            except Exception as e:
                self.logger.error(f"Error in credits group default command: {e}")
                await ctx.send("❌ An error occurred while checking credits.")


    @commands.group(name='admin', aliases=['admn'], invoke_without_command=True)
    async def admin_top_level(self, ctx: commands.Context):
        """Admin credits management"""
        if not self._is_admin(ctx.author):
            await ctx.send("❌ You don't have permission to use admin commands.")
            return
        
        if ctx.invoked_subcommand is None:
            await ctx.send("🔧 Admin credits commands:\n"
                          "- `!admin add @user amount` - Add credits to a user\n"
                          "- `!admin remove @user amount` - Remove credits from a user\n"
                          "- `!admin set @user amount` - Set a user's credits\n"
                          "- `!admin stats` - Show server statistics\n"
                          "- `!admin backup` - Create a database backup")

    @admin_top_level.command(name='add')
    async def admin_add_command(self, ctx: commands.Context, user: discord.Member, amount: int):
        """Admin: Add credits to a user"""
        if not self._is_admin(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        try:
            if amount <= 0:
                await ctx.send("❌ Amount must be positive.")
                return
            
            success = self.db.add_credits(
                str(user.id), 
                str(ctx.guild.id), 
                amount, 
                "admin_add"
            )
            
            if success:
                await ctx.send(f"✅ Added {self._format_credits(amount)} to {user.display_name}.")
            else:
                await ctx.send("❌ Failed to add credits.")
        
        except ValueError:
            await ctx.send("❌ Invalid amount. Please enter a valid number.")
        except Exception as e:
            self.logger.error(f"Error in admin add command: {e}")
            await ctx.send("❌ An error occurred while adding credits.")

    @admin_top_level.command(name='remove')
    async def admin_remove_command(self, ctx: commands.Context, user: discord.Member, amount: int):
        """Admin: Remove credits from a user"""
        if not self._is_admin(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        try:
            if amount <= 0:
                await ctx.send("❌ Amount must be positive.")
                return
            
            success = self.db.subtract_credits(
                str(user.id), 
                str(ctx.guild.id), 
                amount, 
                "admin_remove"
            )
            
            if success:
                await ctx.send(f"✅ Removed {self._format_credits(amount)} from {user.display_name}.")
            else:
                # Check user balance
                balance = self.db.get_user_credits(str(user.id), str(ctx.guild.id))
                if balance is not None and balance < amount:
                    await ctx.send(f"❌ User doesn't have enough credits! They have {self._format_credits(balance)}.")
                else:
                    await ctx.send("❌ Failed to remove credits.")
        
        except ValueError:
            await ctx.send("❌ Invalid amount. Please enter a valid number.")
        except Exception as e:
            self.logger.error(f"Error in admin remove command: {e}")
            await ctx.send("❌ An error occurred while removing credits.")

    @admin_top_level.command(name='set')
    async def admin_set_command(self, ctx: commands.Context, user: discord.Member, amount: int):
        """Admin: Set a user's credits to a specific amount"""
        if not self._is_admin(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        try:
            if amount < 0:
                await ctx.send("❌ Amount cannot be negative.")
                return
            
            # Get current balance
            current_balance = self.db.get_user_credits(str(user.id), str(ctx.guild.id))
            if current_balance is None:
                # Initialize if no record exists
                self.db.initialize_user_credits(str(user.id), str(ctx.guild.id))
                current_balance = config.initial_credits
            
            # Calculate difference
            difference = amount - current_balance
            
            if difference > 0:
                success = self.db.add_credits(
                    str(user.id), 
                    str(ctx.guild.id), 
                    difference, 
                    "admin_add"
                )
            elif difference < 0:
                success = self.db.subtract_credits(
                    str(user.id), 
                    str(ctx.guild.id), 
                    -difference, 
                    "admin_remove"
                )
            else:
                # Amount is the same as current balance
                await ctx.send(f"ℹ️ {user.display_name} already has {self._format_credits(amount)}.")
                return
            
            if success:
                await ctx.send(f"✅ Set {user.display_name}'s credits to {self._format_credits(amount)}.")
            else:
                await ctx.send("❌ Failed to set credits.")
        
        except ValueError:
            await ctx.send("❌ Invalid amount. Please enter a valid number.")
        except Exception as e:
            self.logger.error(f"Error in admin set command: {e}")
            await ctx.send("❌ An error occurred while setting credits.")

    @admin_top_level.command(name='stats')
    async def admin_stats_command(self, ctx: commands.Context):
        """Admin: Show server credit statistics"""
        if not self._is_admin(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        try:
            stats = self.db.get_server_stats(str(ctx.guild.id))
            
            if not stats:
                await ctx.send("❌ No statistics available.")
                return
            
            embed = discord.Embed(
                title=f"📊 Credit Statistics - {ctx.guild.name}",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="👥 Total Users", value=f"{stats['total_users']}", inline=True)
            embed.add_field(name="💰 Total Credits", value=f"{self._format_credits(stats['total_credits'])}", inline=True)
            embed.add_field(name="📈 Average Credits", value=f"{self._format_credits(int(stats['avg_credits']))}", inline=True)
            embed.add_field(name="📝 Total Transactions", value=f"{stats['total_transactions']}", inline=True)
            
            await ctx.send(embed=embed)
        
        except Exception as e:
            self.logger.error(f"Error in admin stats command: {e}")
            await ctx.send("❌ An error occurred while getting statistics.")

    @admin_top_level.command(name='backup')
    async def admin_backup_command(self, ctx: commands.Context):
        """Admin: Create a database backup"""
        if not self._is_admin(ctx.author):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        
        try:
            success = self.db.backup_database()
            
            if success:
                await ctx.send("💾 Database backup created successfully!")
            else:
                await ctx.send("❌ Failed to create database backup.")
        
        except Exception as e:
            self.logger.error(f"Error in admin backup command: {e}")
            await ctx.send("❌ An error occurred while creating backup.")

    # Utility methods for other cogs to use
    def add_credits(self, user_id: str, server_id: str, amount: int, reason: str = "") -> bool:
        """Add credits to a user (for use by other cogs)"""
        try:
            return self.db.add_credits(user_id, server_id, amount, reason)
        except Exception as e:
            self.logger.error(f"Error adding credits: {e}")
            return False

    def subtract_credits(self, user_id: str, server_id: str, amount: int, reason: str = "") -> bool:
        """Subtract credits from a user (for use by other cogs)"""
        try:
            return self.db.subtract_credits(user_id, server_id, amount, reason)
        except Exception as e:
            self.logger.error(f"Error subtracting credits: {e}")
            return False

    def get_credits(self, user_id: str, server_id: str) -> Optional[int]:
        """Get a user's credit balance (for use by other cogs)"""
        try:
            return self.db.get_user_credits(user_id, server_id)
        except Exception as e:
            self.logger.error(f"Error getting credits: {e}")
            return None

    def can_claim_daily(self, user_id: str, server_id: str) -> bool:
        """Check if user can claim daily reward (for use by other cogs)"""
        try:
            return self.db.can_claim_daily_reward(user_id, server_id)
        except Exception as e:
            self.logger.error(f"Error checking daily reward: {e}")
            return False

async def setup(bot: commands.Bot, db_path: Optional[str] = None):
    """
    Setup function to add the cog to a bot.

    Args:
        bot: The Discord bot instance
        db_path: Optional path to database file
    """
    await bot.add_cog(CreditsCog(bot, db_path))