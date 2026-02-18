from dataclasses import dataclass
from typing import Optional
import datetime


@dataclass
class UserCredits:
    """Represents a user's credit balance in a server"""
    user_id: str
    server_id: str
    credits: int
    last_transaction: datetime.datetime
    last_daily_reward: Optional[datetime.datetime] = None


@dataclass
class Transaction:
    """Represents a credit transaction"""
    transaction_id: Optional[int] = None
    user_id: str = ""
    server_id: str = ""
    amount: int = 0
    new_balance: int = 0
    transaction_type: str = ""
    description: str = ""
    created_at: Optional[datetime.datetime] = None


@dataclass
class ServerInfo:
    """Represents server information"""
    server_id: str
    server_name: str
    created_at: datetime.datetime
    last_updated: datetime.datetime


@dataclass
class UserInfo:
    """Represents user information"""
    user_id: str
    username: str
    created_at: datetime.datetime
    last_seen: datetime.datetime
    discriminator: Optional[str] = None
    last_username_change: Optional[datetime.datetime] = None
