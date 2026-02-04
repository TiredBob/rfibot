I have updated the `manage.sh` script to address the console output issue and redirect bot output to a `tmux` session.

**Key changes in `manage.sh`:**

*   **`tmux` Integration**: The bot now starts within a named `tmux` session (`rfibot-session`). All bot output (stdout and stderr) will be directed to this `tmux` session.
*   **Invite Link Output**: When you run `bash manage.sh start`, the script will still wait for and print the bot's invite link to your current terminal.
*   **Clean Shutdown**: The `stop` command now gracefully kills the `tmux` session, ensuring the bot process terminates cleanly.
*   **`bot.pid` Removed**: The `bot.pid` file is no longer used, as bot process management is handled via `tmux` sessions.

To use the script:
*   `bash manage.sh start`: Starts the bot in a detached `tmux` session.
*   `bash manage.sh stop`: Stops the bot's `tmux` session.
*   `bash manage.sh restart`: Stops and then starts the bot's `tmux` session.
*   To view the bot's output after starting, attach to the `tmux` session: `tmux attach -t rfibot-session`

This change has been committed locally.

I am awaiting your instruction to push these changes to the remote `main` branch.