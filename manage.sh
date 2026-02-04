#!/bin/bash

export TERM=xterm
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:$PATH"

BOT_NAME="rfibot"                  # tmux session name for this bot
BOT_DIR="/home/bob/dev/rfibot"     # Directory of the bot project
BOT_SCRIPT="bot.py"
VENV_DIR="$BOT_DIR/pybot"          # Path to the virtual environment
LOG_FILE="bot.log"                 # Main log file for the bot

cd "$BOT_DIR" || exit 1

# Function to check network connectivity
check_network() {
    until ping -c1 google.com &>/dev/null; do
        echo "Waiting for network connectivity..."
        sleep 2
    done
    echo "Network is available."
}

start_bot() {
    # Check if virtual environment exists
    if [ ! -d "$VENV_DIR" ]; then
        echo "Error: Virtual environment not found at $VENV_DIR"
        echo "Please create it using 'uv venv' or ensure the path is correct in manage.sh."
        exit 1
    fi

    # Check if bot is already running in tmux session
    if tmux has-session -t "$BOT_NAME" 2>/dev/null; then
        echo "$BOT_NAME is already running in a tmux session."
        echo "To attach: tmux attach -t $BOT_NAME"
        return
    fi

    echo "Starting $BOT_NAME in tmux session..."
    
    # Clear the log file before starting the bot
    > "$LOG_FILE"
    
    # Start the bot inside a new detached tmux session
    # Output is redirected to LOG_FILE, and 2>&1 ensures stderr also goes there
    tmux new-session -d -s "$BOT_NAME" -n "$BOT_NAME" "source $VENV_DIR/bin/activate && python $BOT_SCRIPT >> $LOG_FILE 2>&1"
    
    echo "$BOT_NAME started in tmux session '$BOT_NAME'."

    echo "Waiting for invite link (max 30 seconds)..."
    for i in {1..15}; do # Check for invite link every 2 seconds, for a total of 30 seconds
        invite_link=$(grep "Invite link:" "$LOG_FILE" | tail -n 1 | sed 's/.*Invite link: //')
        if [ -n "$invite_link" ]; then
            echo "Invite link: $invite_link"
            echo "Bot logs are written to '$LOG_FILE'."
            echo "To attach to the tmux session: tmux attach -t $BOT_NAME"
            return
        fi
        sleep 2
    done
    echo "Could not find invite link in the log file after 30 seconds."
    echo "Please check '$LOG_FILE' or attach to the tmux session ('tmux attach -t $BOT_NAME') for more details."
}

stop_bot() {
    if tmux has-session -t "$BOT_NAME" 2>/dev/null; then
        echo "Stopping $BOT_NAME (tmux session '$BOT_NAME')..."
        tmux kill-session -t "$BOT_NAME"
        echo "$BOT_NAME stopped."
    else
        echo "$BOT_NAME is not running (tmux session '$BOT_NAME' not found)."
    fi
}

status_bot() {
    if tmux has-session -t "$BOT_NAME" 2>/dev/null; then
        echo "$BOT_NAME is running in tmux session '$BOT_NAME'."
    else
        echo "$BOT_NAME is not running."
    fi
}

attach_bot() {
    if tmux has-session -t "$BOT_NAME" 2>/dev/null; then
        echo "Attaching to tmux session '$BOT_NAME'. Press 'Ctrl+b d' to detach."
        tmux attach -t "$BOT_NAME"
    else
        echo "$BOT_NAME is not running. Cannot attach."
    fi
}

# --- Main Script ---

# Ensure network is available before attempting any bot operations
check_network

case "$1" in
    start|"")
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        stop_bot
        sleep 1 # Give tmux a moment to clean up
        start_bot
        ;;
    status)
        status_bot
        ;;
    attach)
        attach_bot
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|attach}"
        exit 1
        ;;
esac

exit 0