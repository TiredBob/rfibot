I have addressed the issue of the bot logging every message received.

The problem was caused by a `logger.info` line within the `on_message` event in `bot.py`.

To fix this, I have:
-   Modified `bot.py`.
-   Commented out the `logger.info` line in the `on_message` event.

This change has been committed locally. The bot should no longer log every message it receives.

I am awaiting your instruction to push these changes to the remote `main` branch.