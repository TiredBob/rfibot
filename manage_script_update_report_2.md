I have updated the `manage.sh` script with the more robust version you provided, adapting it for this bot.

**Summary of new features in `manage.sh`:**

*   **Network Check**: Waits for network connectivity before attempting to start the bot.
*   **Comprehensive `tmux` Management**:
    *   Starts the bot in a named `tmux` session (`rfibot`).
    *   Redirects all bot output (stdout and stderr) to that `tmux` session, which can be viewed by attaching to it.
    *   `start`, `stop`, `restart`, `status`, and `attach` commands are now available.
*   **Invite Link Retrieval**: Clears the log file on start, and then waits for the "Invite link:" message in `bot.log` with a timeout, printing it to the console if found.
*   **Error Handling**: Includes checks for virtual environment existence and existing `tmux` sessions.

The script has been updated, made executable, and the changes have been committed locally.

I am awaiting your instruction to push these changes to the remote `main` branch.