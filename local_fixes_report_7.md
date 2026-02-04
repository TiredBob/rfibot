I have addressed the issue of the bot double-posting log messages.

The problem was caused by the logging configuration in `utils/logger.py`, where both the `discord_bot` logger and the root logger were configured to output to the console. This resulted in each log message being processed and emitted twice.

To fix this, I have:
-   Modified `utils/logger.py`.
-   Added `logger.propagate = False` to the `discord_bot` logger. This prevents messages from being passed up to the root logger, ensuring that each message is handled only once by its intended handlers.

This change has been committed locally. The bot should no longer spam duplicate log messages.

I am awaiting your instruction to push these changes to the remote `main` branch.