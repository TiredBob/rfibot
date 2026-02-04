I have implemented the log rotation functionality directly within the bot as requested.

**Here's how it works:**

1.  **`utils/logger.py`**: A new function `clean_old_logs(log_dir, days_old=3)` has been added. This function iterates through files in the bot's logging directory and deletes any `.log` files older than 3 days (72 hours).
2.  **`cogs/utils.py`**: A `discord.ext.tasks` loop named `log_cleanup_task` has been added to the `Utils` cog.
    *   This task is scheduled to run daily at **5:00 AM GMT-5 (10:00 AM UTC)**.
    *   It calls the `clean_old_logs` function, running the potentially blocking file I/O operations in a separate thread pool to avoid freezing the bot.
    *   The task starts when the cog is loaded and cancels upon cog unload.

This ensures that your bot's log files will be automatically cleaned up, keeping them from growing indefinitely, even when the bot runs for weeks on end without manual intervention.

The changes have been committed locally.

I am awaiting your instruction to push these changes to the remote `main` branch.