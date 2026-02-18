I have created a new shell script `manage.sh` to help you manage the bot.

**Features of the script:**

*   **Start**: `bash manage.sh start`
    *   Activates the virtual environment (`pybot`).
    *   Starts the bot in the background.
    *   Saves the bot's Process ID (PID) to a `bot.pid` file.
    *   Waits for the bot's invite link to be generated in `bot.log` and prints it to the terminal.
*   **Stop**: `bash manage.sh stop`
    *   Reads the PID from `bot.pid` and gracefully stops the bot process.
*   **Restart**: `bash manage.sh restart`
    *   Stops the bot and then starts it again, providing the new invite link.

The script has been made executable and the changes have been committed locally.

I am awaiting your instruction to push these changes to the remote `main` branch.