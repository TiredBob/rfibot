import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass
class CreditsConfig:
    """Configuration for the credits system"""

    # Database settings
    db_path: str = "credits.db"
    db_backup_path: str = "backups/credits_backup.db"
    auto_backup: bool = True
    backup_interval_hours: int = 24

    # Initial credits settings
    initial_credits: int = 500
    daily_reward: int = 100
    max_transfer_amount: int = 1000
    min_transfer_amount: int = 1

    # Command settings
    command_prefix: str = "!"  # Can be overridden by bot
    admin_roles: List[str] = field(default_factory=lambda: ["Admin", "Moderator", "Owner"])

    # Rate limiting
    command_cooldown: int = 5  # seconds
    daily_reward_cooldown: int = 86400  # 24 hours in seconds

    # Daily reset settings
    daily_reset_timezone_str: str = os.getenv('DAILY_RESET_TIMEZONE', 'America/Denver')
    
    @property
    def DAILY_RESET_TIMEZONE(self) -> ZoneInfo:
        try:
            return ZoneInfo(self.daily_reset_timezone_str)
        except ZoneInfoNotFoundError:
            # We can't easily log here without a logger, but we can print to stderr
            # as a fallback, or just return UTC.
            return ZoneInfo('UTC')

    # Leaderboard settings
    leaderboard_size: int = 10

    # Transaction types
    TRANSACTION_TYPES = {
        "initial": "Initial credits",
        "daily": "Daily reward", 
        "transfer_in": "Received transfer",
        "transfer_out": "Sent transfer",
        "game_win": "Game victory reward",
        "game_loss": "Game loss penalty",
        "admin_add": "Admin addition",
        "admin_remove": "Admin removal",
        "purchase": "Purchase",
        "reward": "Special reward"
    }


# Global configuration instance
config = CreditsConfig()
