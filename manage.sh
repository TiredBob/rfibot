#!/bin/bash

# Bot management script for rfibot

# --- Configuration ---
VENV_PATH="pybot/bin/activate"
BOT_SCRIPT="bot.py"
LOG_FILE="bot.log"
TMUX_SESSION_NAME="rfibot"

# --- Functions ---

start_bot() {
    if tmux has-session -t "$TMUX_SESSION_NAME" 2>/dev/null; then
        echo "Tmux session '$TMUX_SESSION_NAME' already exists. Please stop it manually or use 'restart'."
        return 1
    fi

    echo "Starting bot in tmux session '$TMUX_SESSION_NAME'..."

    # Ensure log file exists before tailing
    touch "$LOG_FILE"

    # Start the bot inside a new detached tmux session.
    # Redirect stderr to stdout so both go to the tmux pane.
    tmux new-session -d -s "$TMUX_SESSION_NAME" \
        "source $VENV_PATH && python $BOT_SCRIPT 2>&1"

    # Now, wait for the invite link from the log file
    echo "Waiting for invite link (this may take a moment)..."
    INVITE_LINK=$(tail -n 0 -f "$LOG_FILE" | grep --line-buffered -m 1 "Invite link:")
    
    # Print the invite link
    echo "$INVITE_LINK"
    
    echo "Bot is running in tmux session '$TMUX_SESSION_NAME'."
    echo "To attach to the session and see full output: tmux attach -t $TMUX_SESSION_NAME"
    echo "Bot logs are also written to '$LOG_FILE'."
}

stop_bot() {
    if tmux has-session -t "$TMUX_SESSION_NAME" 2>/dev/null; then
        echo "Stopping tmux session '$TMUX_SESSION_NAME'..."
        tmux kill-session -t "$TMUX_SESSION_NAME"
        echo "Bot stopped."
    else
        echo "Bot is not running (tmux session '$TMUX_SESSION_NAME' not found)."
        return 1
    fi
}

# --- Main Script ---

case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        stop_bot
        sleep 2
        start_bot
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0