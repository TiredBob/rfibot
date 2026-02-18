# Credits System for Discord Bots

A standalone, reusable credits/points system for Discord bots.

## Features

- **Per-server credit tracking**: Each user has separate credits for each server
- **Automatic initialization**: New users get 250 credits when they join
- **Comprehensive commands**: Balance checking, leaderboards, transfers, etc.
- **Daily Rewards**: Claim `10` credits daily with `!daily`. The reset time is midnight in the configured `DAILY_RESET_TIMEZONE` (default: America/Denver).
- **Transaction logging**: Full audit trail of all credit changes
- **Admin tools**: Manage credits and view statistics
- **Portable design**: Easy to integrate with any Discord bot
- **SQLite database**: Simple, file-based, no external dependencies

## Installation

1. Copy the `credits_system` directory to your bot project
2. Install required dependencies (none beyond standard library!)
3. Add the cog to your bot

## Usage

### Basic Setup

```python
from credits_system import setup as setup_credits

# In your bot's setup/extension loading code:
await setup_credits(bot)
```

### Custom Database Path

```python
from credits_system import setup as setup_credits

# Use a custom database path
await setup_credits(bot, db_path="path/to/your/credits.db")
```

### Using in Other Cogs

```python
# Get the credits cog from your bot
credits_cog = bot.get_cog('CreditsCog')

if credits_cog:
    # Add credits to a user
    credits_cog.add_credits(str(user.id), str(ctx.guild.id), 50, "Game reward")

    # Get user's balance
    balance = credits_cog.get_credits(str(user.id), str(ctx.guild.id))
```

## Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `!credits` | Check your credit balance | `!credits` or `!credits @user` |
| `!leaderboard` | Show top users by credits | `!leaderboard` |
| `!daily` | Claim daily credit reward | `!daily` |
| `!transfer` | Transfer credits to another user | `!transfer amount @user` |
| `!admin add` / `!admn add` | Admin: Add credits to user | `!admin add @user amount` |
| `!admin remove` / `!admn remove` | Admin: Remove credits from user | `!admin remove @user amount` |
| `!admin set` / `!admn set` | Admin: Set user's credits | `!admin set @user amount` |
| `!admin stats` / `!admn stats` | Admin: Show server statistics | `!admin stats` |
| `!admin backup` / `!admn backup` | Admin: Create database backup | `!admin backup` |

## Configuration

Edit `credits_system/config.py` to customize:

- Initial credits amount
- Daily reward amount
- Daily reward reset timezone: Configured via `DAILY_RESET_TIMEZONE` (e.g., `America/Denver`).
- Transaction limits
- Admin roles
- Database settings

## Database Schema

The system uses SQLite with the following tables:

- `servers`: Server information
- `users`: User information (global)
- `user_credits`: Credit balances per user per server
- `transactions`: Complete transaction history

## Backup & Restore

```python
from credits_system.database import CreditsDatabase

db = CreditsDatabase()

# Backup
db.backup_database()

# Restore
db.restore_database("path/to/backup.db")
```

## Requirements

- Python 3.8+
- discord.py 2.0+
- SQLite3 (included in Python standard library)

## License

MIT License

## Integration Examples

### Rewarding Credits for Game Wins

```python
# In your game cog
class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play_game(self, ctx):
        # ... game logic ...
        
        if game_won:
            # Get credits cog
            credits_cog = self.bot.get_cog('CreditsCog')
            if credits_cog:
                # Reward 50 credits for winning
                credits_cog.add_credits(
                    str(ctx.author.id),
                    str(ctx.guild.id),
                    50,
                    "game_win"
                )
                await ctx.send("🎉 You won 50 credits!")
```

### Checking Balance Before Purchase

```python
# In your shop cog
class ShopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def buy_item(self, ctx, item_name: str):
        # Get item price
        item_price = get_item_price(item_name)  # Your function
        
        # Get credits cog
        credits_cog = self.bot.get_cog('CreditsCog')
        if not credits_cog:
            await ctx.send("❌ Credits system not available.")
            return
        
        # Check user balance
        user_balance = credits_cog.get_credits(str(ctx.author.id), str(ctx.guild.id))
        
        if user_balance is None:
            await ctx.send("❌ You don't have any credits yet!")
            return
        
        if user_balance < item_price:
            await ctx.send(f"❌ You don't have enough credits! You need {item_price} but have {user_balance}.")
            return
        
        # Purchase item
        if purchase_item(ctx.author.id, item_name):  # Your function
            # Deduct credits
            credits_cog.subtract_credits(
                str(ctx.author.id),
                str(ctx.guild.id),
                item_price,
                "purchase"
            )
            await ctx.send(f"🛒 Purchased {item_name} for {item_price} credits!")
        else:
            await ctx.send("❌ Failed to purchase item.")
```

## Database Management

### Manual Backup

```python
from credits_system.database import CreditsDatabase

db = CreditsDatabase()
success = db.backup_database("/path/to/backup.db")
```

### Manual Restore

```python
from credits_system.database import CreditsDatabase

db = CreditsDatabase()
success = db.restore_database("/path/to/backup.db")
```

## Troubleshooting

### Database Connection Issues

- Ensure the bot has write permissions to the database directory
- Check that the database file isn't locked by another process
- Verify SQLite is properly installed (it comes with Python standard library)

### Permission Issues

- Make sure admin roles are properly configured in `config.py`
- Check that the bot has the necessary Discord permissions
- Verify the bot's role hierarchy allows it to manage the specified roles

### Credit Balance Issues

- Use `!credits admin stats` to check server-wide statistics
- Review transaction history with database queries if needed
- Check that users are properly initialized when they join

## Future Enhancements

The system is designed to be easily extended with:

- **Credit earning mechanisms**: Tie into existing games and activities
- **Credit spending**: Purchase items, roles, or special features
- **Achievements system**: Reward credits for milestones
- **Economy plugins**: Shops, gambling, auctions
- **Web dashboard**: View stats and manage credits
- **Multi-bot sync**: Share credit data between bots

## Support

For issues or questions, check the database files and logs first. The system includes comprehensive logging for troubleshooting.