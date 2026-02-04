#!/bin/bash

# Bot management script for rfibot

# --- Configuration ---
VENV_PATH="pybot/bin/activate"
BOT_SCRIPT="bot.py"
PID_FILE="bot.pid"
LOG_FILE="bot.log"  # Assuming bot.log is the main log file

# --- Functions ---

start_bot() {
    if [ -f "$PID_FILE" ]; then
        echo "Bot is already running (PID: $(cat $PID_FILE)). Use 'restart' if you want to restart it."
        return 1
    fi

    echo "Starting bot..."

    # Activate virtual environment and run bot in the background
    source "$VENV_PATH"
    python "$BOT_SCRIPT" &
    
    # Save the PID
    echo $! > "$PID_FILE"
    
    echo "Bot started with PID: $(cat $PID_FILE)"
    
    # Wait for the invite link and print it
    echo "Waiting for invite link..."
    
    # Tail the log file until we find the invite link, then exit
    tail -n 0 -f "$LOG_FILE" | grep --line-buffered -m 1 "Invite link:"
}

stop_bot() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Bot is not running."
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    echo "Stopping bot (PID: $PID)..."
    
    # Send SIGTERM for graceful shutdown
    kill "$PID"
    
    # Remove the PID file
    rm "$PID_FILE"
    
    echo "Bot stopped."
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
