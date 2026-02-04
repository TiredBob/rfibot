I have refined the bot's logging behavior as requested:

1.  **Commands Received**: The `on_message` event in `bot.py` now checks if a message starts with the command prefix (`COMMAND_PREFIX`) and logs the full message content, author, and channel if it does.
2.  **Valid/Invalid Commands**:
    *   **Invalid Commands**: The `on_command_error` event now logs an `INFO` message when a `commands.CommandNotFound` error occurs, indicating that an invalid command was received.
    *   **Valid Commands**: Individual command functions within cogs typically have their own `logger.info` calls (e.g., `logger.info(f'Roll command used by {ctx.author}')`) which will continue to log when a valid command is used.
3.  **Other Messages Ignored**: The previous change to comment out the generic `logger.info` in `on_message` ensures that non-command messages are not logged.

These changes have been committed locally. The bot should now provide more focused logging for command interactions.

I am awaiting your instruction to push these changes to the remote `main` branch.