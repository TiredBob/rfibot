"""
Credits System Package

A standalone, reusable credits/points system for Discord bots.
"""

from .database import CreditsDatabase
from .cog import CreditsCog
from .models import UserCredits, Transaction, ServerInfo, UserInfo
from .config import CreditsConfig, config

__version__ = "1.0.0"
__author__ = "Discord Bot Credits System"
__license__ = "MIT"

# Export main components for easy importing
__all__ = [
    'CreditsDatabase',
    'CreditsCog', 
    'UserCredits',
    'Transaction',
    'ServerInfo',
    'UserInfo',
    'CreditsConfig',
    'config',
    'setup'
]

# Re-export the setup function from cog module
async def setup(bot, db_path=None):
    """
    Convenience function to set up the credits system.
    
    Args:
        bot: The Discord bot instance
        db_path: Optional path to database file
    """
    from .cog import setup as cog_setup
    await cog_setup(bot, db_path)