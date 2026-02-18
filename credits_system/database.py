import sqlite3
import os
import datetime
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import logging

from .models import UserCredits, Transaction, ServerInfo, UserInfo
from .config import config


class CreditsDatabase:
    """Standalone credits database system"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the credits database.

        Args:
            db_path: Optional path to database file. Uses config.db_path if None.
        """
        self.db_path = db_path or config.db_path
        self.logger = logging.getLogger('CreditsDatabase')
        self._ensure_database_directory()
        self._initialize_database()

    def _ensure_database_directory(self):
        """Ensure the directory for the database exists"""
        db_dir = Path(self.db_path).parent
        if db_dir and not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with proper settings"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")  # Better for concurrent access
        conn.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and speed
        conn.execute("PRAGMA busy_timeout=5000")   # 5 second busy timeout
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

    def _initialize_database(self):
        """Create tables if they don't exist"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")

                # Create tables
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS servers (
                    server_id TEXT PRIMARY KEY,
                    server_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    discriminator TEXT DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_username_change TIMESTAMP
                )
                """)

                cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS user_credits (
                    user_id TEXT NOT NULL,
                    server_id TEXT NOT NULL,
                    credits INTEGER DEFAULT {config.initial_credits},
                    last_transaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_daily_reward TIMESTAMP,
                    PRIMARY KEY (user_id, server_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (server_id) REFERENCES servers(server_id) ON DELETE CASCADE
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    server_id TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    new_balance INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (server_id) REFERENCES servers(server_id) ON DELETE CASCADE
                )
                """)

                # Create indexes for performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_credits_user ON user_credits(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_credits_server ON user_credits(server_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_server ON transactions(server_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)")

                conn.commit()
                self.logger.info(f"Database initialized at {self.db_path}")

        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise

    def ensure_server_exists(self, server_id: str, server_name: str) -> bool:
        """Ensure a server exists in the database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO servers (server_id, server_name) VALUES (?, ?)",
                    (server_id, server_name)
                )
                
                # Update server name and last_updated if it already exists
                cursor.execute(
                    "UPDATE servers SET server_name = ?, last_updated = CURRENT_TIMESTAMP WHERE server_id = ?",
                    (server_name, server_id)
                )
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error ensuring server exists: {e}")
            return False

    def ensure_user_exists(self, user_id: str, username: str, discriminator: Optional[str] = None) -> bool:
        """Ensure a user exists in the database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute("SELECT username, discriminator FROM users WHERE user_id = ?", (user_id,)) # Select discriminator too
                existing_user = cursor.fetchone()
                
                if existing_user:
                    # Update username, discriminator and last_seen if changed
                    # Compare existing discriminator from DB with the new one
                    if existing_user['username'] != username or existing_user['discriminator'] != discriminator:
                        cursor.execute(
                            "UPDATE users SET username = ?, discriminator = ?, last_seen = CURRENT_TIMESTAMP, last_username_change = CURRENT_TIMESTAMP WHERE user_id = ?",
                            (username, discriminator, user_id)
                        )
                    else:
                        # Only update last_seen if username/discriminator didn't change
                        cursor.execute(
                            "UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE user_id = ?",
                            (user_id,)
                        )
                else:
                    # Insert new user
                    cursor.execute(
                        "INSERT INTO users (user_id, username, discriminator) VALUES (?, ?, ?)",
                        (user_id, username, discriminator)
                    )
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error ensuring user exists: {e}")
            return False

    def user_has_credits(self, user_id: str, server_id: str) -> bool:
        """Check if a user has a credits record for a server"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM user_credits WHERE user_id = ? AND server_id = ?",
                    (user_id, server_id)
                )
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            self.logger.error(f"Error checking if user has credits: {e}")
            return False


    def _get_user_credits_internal(self, cursor: sqlite3.Cursor, user_id: str, server_id: str) -> Optional[int]:
        """Internal method to get a user's current credit balance using an existing cursor."""
        cursor.execute(
            "SELECT credits FROM user_credits WHERE user_id = ? AND server_id = ?",
            (user_id, server_id)
        )
        result = cursor.fetchone()
        return result['credits'] if result else None

    def _log_transaction_internal(self, cursor: sqlite3.Cursor, user_id: str, server_id: str, amount: int, transaction_type: str, description: str = "") -> bool:
        """Internal method to log a transaction using an existing cursor."""
        # Get current balance for the new_balance in transaction record.
        # This will be the balance *before* the current transaction.
        # The new_balance field in the transactions table should reflect the balance *after* the transaction.
        current_balance = self._get_user_credits_internal(cursor, user_id, server_id)
        if current_balance is None:
            # This should ideally not happen if user_credits record exists
            self.logger.error(f"Attempted to log transaction for non-existent user_credits record: {user_id}, {server_id}")
            return False
        
        cursor.execute(
            """
            INSERT INTO transactions 
            (user_id, server_id, amount, new_balance, transaction_type, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, server_id, amount, current_balance + amount, transaction_type, description) # new_balance should be the balance AFTER this transaction
        )
        return True

    def _initialize_user_credits_internal(self, cursor: sqlite3.Cursor, user_id: str, server_id: str) -> bool:
        """Internal method to initialize a user's credits for a server using an existing cursor."""
        cursor.execute(
            "INSERT INTO user_credits (user_id, server_id, credits) VALUES (?, ?, ?)",
            (user_id, server_id, config.initial_credits)
        )
        self._log_transaction_internal(
            cursor, user_id, server_id, config.initial_credits,
            "initial", "Initial credits"
        )
        return True

    def _add_credits_internal(self, cursor: sqlite3.Cursor, user_id: str, server_id: str, amount: int, reason: str = "") -> bool:
        """Internal method to add credits to a user's balance using an existing cursor."""
        if amount <= 0:
            return False
        
        current_balance = self._get_user_credits_internal(cursor, user_id, server_id)
        if current_balance is None:
            if not self._initialize_user_credits_internal(cursor, user_id, server_id):
                return False
            current_balance = config.initial_credits # After initialization
        
        new_balance = current_balance + amount
        cursor.execute(
            "UPDATE user_credits SET credits = ?, last_transaction = CURRENT_TIMESTAMP WHERE user_id = ? AND server_id = ?",
            (new_balance, user_id, server_id)
        )
        
        transaction_type = reason if reason in config.TRANSACTION_TYPES else "reward"
        self._log_transaction_internal(
            cursor, user_id, server_id, amount, transaction_type, 
            config.TRANSACTION_TYPES.get(transaction_type, reason)
        )
        return True

    def _subtract_credits_internal(self, cursor: sqlite3.Cursor, user_id: str, server_id: str, amount: int, reason: str = "") -> bool:
        """Internal method to subtract credits from a user's balance using an existing cursor."""
        if amount <= 0:
            return False
            
        current_balance = self._get_user_credits_internal(cursor, user_id, server_id)
        if current_balance is None or current_balance < amount:
            return False
            
        new_balance = current_balance - amount
        cursor.execute(
            "UPDATE user_credits SET credits = ?, last_transaction = CURRENT_TIMESTAMP WHERE user_id = ? AND server_id = ?",
            (new_balance, user_id, server_id)
        )
        
        transaction_type = reason if reason in config.TRANSACTION_TYPES else "purchase"
        self._log_transaction_internal(
            cursor, user_id, server_id, -amount, transaction_type, 
            config.TRANSACTION_TYPES.get(transaction_type, reason)
        )
        return True

    def initialize_user_credits(self, user_id: str, server_id: str) -> bool:
        """Initialize a user's credits for a server"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                success = self._initialize_user_credits_internal(cursor, user_id, server_id)
                conn.commit()
                return success
        except sqlite3.Error as e:
            self.logger.error(f"Error initializing user credits: {e}")
            return False

    def get_user_credits(self, user_id: str, server_id: str) -> Optional[int]:
        """Get a user's current credit balance"""
        try:
            with self._get_connection() as conn:
                return self._get_user_credits_internal(conn.cursor(), user_id, server_id)
        except sqlite3.Error as e:
            self.logger.error(f"Error getting user credits: {e}")
            return None

    def add_credits(self, user_id: str, server_id: str, amount: int, reason: str = "") -> bool:
        """Add credits to a user's balance"""
        if amount <= 0:
            self.logger.warning(f"Invalid amount to add: {amount}")
            return False
            
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                success = self._add_credits_internal(cursor, user_id, server_id, amount, reason)
                conn.commit()
                return success
        except sqlite3.Error as e:
            self.logger.error(f"Error adding credits: {e}")
            return False

    def subtract_credits(self, user_id: str, server_id: str, amount: int, reason: str = "") -> bool:
        """Subtract credits from a user's balance"""
        if amount <= 0:
            self.logger.warning(f"Invalid amount to subtract: {amount}")
            return False
            
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                success = self._subtract_credits_internal(cursor, user_id, server_id, amount, reason)
                conn.commit()
                return success
        except sqlite3.Error as e:
            self.logger.error(f"Error subtracting credits: {e}")
            return False

    def transfer_credits(self, from_user_id: str, to_user_id: str, server_id: str, amount: int) -> bool:
        """Transfer credits between users atomically"""
        if amount <= 0:
            self.logger.warning(f"Invalid transfer amount: {amount}")
            return False
            
        if amount > config.max_transfer_amount:
            self.logger.warning(f"Transfer amount {amount} exceeds maximum {config.max_transfer_amount}")
            return False
            
        if amount < config.min_transfer_amount:
            self.logger.warning(f"Transfer amount {amount} below minimum {config.min_transfer_amount}")
            return False
            
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check sender balance
            sender_balance = self._get_user_credits_internal(cursor, from_user_id, server_id)
            if sender_balance is None or sender_balance < amount:
                self.logger.warning(f"Sender {from_user_id} has insufficient funds")
                return False
            
            # Ensure recipient exists and initialize if necessary
            # We first check if user has credits using a method that gets its own connection
            # because _initialize_user_credits_internal assumes user_credits table exists
            if not self.user_has_credits(to_user_id, server_id):
                if not self._initialize_user_credits_internal(cursor, to_user_id, server_id):
                    return False

            # Subtract from sender
            if not self._subtract_credits_internal(cursor, from_user_id, server_id, amount, "transfer_out"):
                conn.rollback()
                return False
            
            # Add to recipient
            if not self._add_credits_internal(cursor, to_user_id, server_id, amount, "transfer_in"):
                conn.rollback() # This rollback should cover both subtract and add operations in this transaction
                return False
            
            # Log transfer transaction for sender
            # The new_balance in the transaction log will reflect the balance after the subtraction
            self._log_transaction_internal(
                cursor, from_user_id, server_id, -amount, "transfer_out",
                f"Transferred {amount} credits to user {to_user_id}"
            )
            
            # Log transfer transaction for recipient
            # The new_balance in the transaction log will reflect the balance after the addition
            self._log_transaction_internal(
                cursor, to_user_id, server_id, amount, "transfer_in",
                f"Received {amount} credits from user {from_user_id}"
            )
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Error transferring credits: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def log_transaction(self, user_id: str, server_id: str, amount: int, transaction_type: str, description: str = "") -> bool:
        """Log a transaction in the transactions table"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                success = self._log_transaction_internal(cursor, user_id, server_id, amount, transaction_type, description)
                conn.commit()
                return success
        except sqlite3.Error as e:
            self.logger.error(f"Error logging transaction: {e}")
            return False

    def get_leaderboard(self, server_id: str, limit: int = 10) -> List[UserCredits]:
        """Get the leaderboard for a server"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT user_id, server_id, credits, last_transaction, last_daily_reward
                    FROM user_credits
                    WHERE server_id = ?
                    ORDER BY credits DESC
                    LIMIT ?
                    """,
                    (server_id, limit)
                )
                
                return [
                    UserCredits(
                        user_id=row['user_id'],
                        server_id=row['server_id'],
                        credits=row['credits'],
                        last_transaction=datetime.datetime.fromisoformat(row['last_transaction']),
                        last_daily_reward=datetime.datetime.fromisoformat(row['last_daily_reward']) if row['last_daily_reward'] else None
                    )
                    for row in cursor.fetchall()
                ]
        except sqlite3.Error as e:
            self.logger.error(f"Error getting leaderboard: {e}")
            return []

    def get_bottom_users(self, server_id: str) -> List[UserCredits]:
        """Get the users with the lowest credit amount in a server"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Find the minimum credit amount
                cursor.execute(
                    "SELECT MIN(credits) FROM user_credits WHERE server_id = ?",
                    (server_id,)
                )
                min_row = cursor.fetchone()
                if min_row is None or min_row[0] is None:
                    return []
                
                min_credits = min_row[0]
                
                # Get all users with that amount
                cursor.execute(
                    """
                    SELECT user_id, server_id, credits, last_transaction, last_daily_reward
                    FROM user_credits
                    WHERE server_id = ? AND credits = ?
                    """,
                    (server_id, min_credits)
                )
                
                return [
                    UserCredits(
                        user_id=row['user_id'],
                        server_id=row['server_id'],
                        credits=row['credits'],
                        last_transaction=datetime.datetime.fromisoformat(row['last_transaction']),
                        last_daily_reward=datetime.datetime.fromisoformat(row['last_daily_reward']) if row['last_daily_reward'] else None
                    )
                    for row in cursor.fetchall()
                ]
        except sqlite3.Error as e:
            self.logger.error(f"Error getting bottom users: {e}")
            return []

    def get_user_transactions(self, user_id: str, server_id: str, limit: int = 10) -> List[Transaction]:
        """Get a user's transaction history"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT transaction_id, user_id, server_id, amount, new_balance, 
                           transaction_type, description, created_at
                    FROM transactions
                    WHERE user_id = ? AND server_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (user_id, server_id, limit)
                )
                
                return [
                    Transaction(
                        transaction_id=row['transaction_id'],
                        user_id=row['user_id'],
                        server_id=row['server_id'],
                        amount=row['amount'],
                        new_balance=row['new_balance'],
                        transaction_type=row['transaction_type'],
                        description=row['description'],
                        created_at=datetime.datetime.fromisoformat(row['created_at'])
                    )
                    for row in cursor.fetchall()
                ]
        except sqlite3.Error as e:
            self.logger.error(f"Error getting user transactions: {e}")
            return []

    def can_claim_daily_reward(self, user_id: str, server_id: str) -> bool:
        """Check if a user can claim their daily reward based on a fixed daily reset time."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT last_daily_reward FROM user_credits WHERE user_id = ? AND server_id = ?",
                    (user_id, server_id)
                )
                
                result = cursor.fetchone()
                if not result or not result['last_daily_reward']:
                    return True # User has never claimed, so they can claim

                last_reward_str = result['last_daily_reward']
                
                # SQLite stores TIMESTAMP as string in ISO format. It's usually UTC unless specified.
                # Assume stored timestamps are UTC.
                last_reward_utc = datetime.datetime.fromisoformat(last_reward_str).replace(tzinfo=datetime.timezone.utc)
                
                # Convert last_reward to the configured daily reset timezone
                last_reward_local = last_reward_utc.astimezone(config.DAILY_RESET_TIMEZONE)

                # Get the current time in the configured daily reset timezone
                now_local = datetime.datetime.now(config.DAILY_RESET_TIMEZONE)

                # Calculate today's midnight in the configured daily reset timezone
                today_midnight_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)

                # If the last reward was before today's midnight in the local timezone, they can claim
                return last_reward_local < today_midnight_local

        except Exception as e: # Catch general Exception for robustness, including ZoneInfo-related errors
            self.logger.error(f"Error checking daily reward eligibility: {e}")
            return False

    def claim_daily_reward(self, user_id: str, server_id: str) -> bool:
        """Claim daily reward for a user"""
        if not self.can_claim_daily_reward(user_id, server_id):
            return False
            
        success_add = self.add_credits(user_id, server_id, config.daily_reward, "daily")
        
        if success_add:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE user_credits SET last_daily_reward = CURRENT_TIMESTAMP WHERE user_id = ? AND server_id = ?",
                        (user_id, server_id)
                    )
                    conn.commit()
                    return True
            except sqlite3.Error as e:
                self.logger.error(f"Error updating last_daily_reward for user {user_id} in server {server_id}: {e}")
                # If updating fails, consider rolling back the add_credits or handling as a partial failure
                return False
        return False

    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """Create a backup of the database"""
        backup_path = backup_path or config.db_backup_path
        try:
            # Ensure backup directory exists
            backup_dir = Path(backup_path).parent
            if backup_dir and not backup_dir.exists():
                backup_dir.mkdir(parents=True, exist_ok=True)

            # Use sqlite3 backup API
            with self._get_connection() as src_conn:
                with sqlite3.connect(backup_path) as dest_conn:
                    src_conn.backup(dest_conn)
                    dest_conn.commit()

            self.logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False

    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:


            # Copy backup file over main database
            import shutil
            shutil.copy2(backup_path, self.db_path)

            self.logger.info(f"Database restored from {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
            return False

    def get_server_stats(self, server_id: str) -> Dict[str, Any]:
        """Get statistics for a server"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total users with credits
                cursor.execute("SELECT COUNT(*) FROM user_credits WHERE server_id = ?", (server_id,))
                total_users = cursor.fetchone()[0]
                
                # Total credits in circulation
                cursor.execute("SELECT SUM(credits) FROM user_credits WHERE server_id = ?", (server_id,))
                total_credits = cursor.fetchone()[0] or 0
                
                # Average credits per user
                avg_credits = total_credits / total_users if total_users > 0 else 0
                
                # Total transactions
                cursor.execute("SELECT COUNT(*) FROM transactions WHERE server_id = ?", (server_id,))
                total_transactions = cursor.fetchone()[0]
                
                return {
                    'server_id': server_id,
                    'total_users': total_users,
                    'total_credits': total_credits,
                    'avg_credits': avg_credits,
                    'total_transactions': total_transactions
                }
        except sqlite3.Error as e:
            self.logger.error(f"Error getting server stats: {e}")
            return {}

    def update_user_info(self, user_id: str, username: str, discriminator: Optional[str] = None) -> bool:
        """Update user information"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if username or discriminator changed
                cursor.execute("SELECT username, discriminator FROM users WHERE user_id = ?", (user_id,))
                existing = cursor.fetchone()
                
                if existing:
                    if existing['username'] != username or existing['discriminator'] != discriminator:
                        cursor.execute(
                            "UPDATE users SET username = ?, discriminator = ?, last_username_change = CURRENT_TIMESTAMP WHERE user_id = ?",
                            (username, discriminator, user_id)
                        )
                    
                    # Always update last_seen, regardless of username/discriminator change
                    cursor.execute(
                        "UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE user_id = ?",
                        (user_id,)
                    )
                else:
                    # User doesn't exist, add them (this handles cases where a user might be seen without being explicitly "ensured")
                    cursor.execute(
                        "INSERT INTO users (user_id, username, discriminator) VALUES (?, ?, ?)",
                        (user_id, username, discriminator)
                    )
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error updating user info: {e}")
            return False