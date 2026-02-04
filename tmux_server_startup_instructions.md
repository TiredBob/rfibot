The output "no server running on /tmp/tmux-1000/default" indicates that the `tmux` server itself is not running on your system. This is why the bot couldn't be started in a `tmux` session, and why the script hung while waiting for the invite link.

To fix this, you need to first start the `tmux` server. You can do this by simply running `tmux` in your terminal:

1.  **Start the `tmux` server**:
    ```bash
    tmux
    ```
    This command will create and attach you to a new default `tmux` session.

2.  **Detach from the default `tmux` session**:
    Once you are inside the `tmux` session, press `Ctrl+b` then `d` (release `Ctrl+b` before pressing `d`). This will detach you from the session, but the `tmux` server will continue running in the background.

3.  **Try starting the bot again**:
    Once you've detached from `tmux` (or if you prefer, opened a *new* terminal window), run your `manage.sh` script again:
    ```bash
    bash manage.sh start
    ```

Please let me know if this resolves the issue and if the bot starts successfully this time.