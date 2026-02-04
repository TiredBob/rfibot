# rfibot: A Feature-Rich Discord Bot

## Overview

rfibot is a versatile Discord bot built with Python and `discord.py`. It offers a variety of commands for entertainment and utility. The bot is designed to be robust, featuring custom error handling and dedicated logging to a 'bot-status' channel.

## Features

*   **Game Commands**: Engage in interactive games like:
    *   `!roll <NdM>`: Roll dice (e.g., `!roll 2d6`).
    *   `!8ball <question>`: Ask the Magic 8-Ball a question.
    *   `!coinflip` / `!flip`: Flip a coin.
    *   `!rfi`: Roll for Initiative (d20).
    *   `!challenge @user`: Challenge another user to a d20 roll-off.
    *   `!rps @user`: Play Rock, Paper, Scissors against another user.
    *   `!tictactoe @user | bot`: Play Tic-Tac-Toe against a user or the bot.
*   **Social Commands**:
    *   `!slap @user`: Slap another user (with a random message).
*   **Utility**:
    *   `!invite`: Get the bot's invite link to add it to your own server.
    *   `!ping`: Check the bot's latency.

## Setup

To get rfibot running on your server:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/TiredBob/rfibot.git
    cd rfibot
    ```
2.  **Set up Virtual Environment**:
    It's highly recommended to use a virtual environment. This project uses `uv` for dependency management.
    ```bash
    uv venv
    source .venv/bin/activate
    ```
3.  **Install Dependencies**:
    ```bash
    uv pip install .
    ```
    *Note: This command installs dependencies listed in `pyproject.toml`.*
4.  **Configuration (`.env` file)**:
    Create a `.env` file in the root directory of the project. This file will hold your sensitive API keys and tokens.
    ```
    DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
    ```
    *   **DISCORD_TOKEN**: Obtain this from the Discord Developer Portal for your bot.
5.  **Run the Bot**:
    ```bash
    python bot.py
    ```

## Management Script (`manage.sh`)

The `manage.sh` script is a powerful tool for controlling your bot's lifecycle. It leverages `tmux` to run the bot in a detached session, allowing it to run continuously in the background, even after you close your terminal.

**Usage:**

```bash
bash manage.sh <command>
```

**Commands:**

*   `start`: Starts the bot in a new `tmux` session named `rfibot`. It will automatically activate the virtual environment, run `bot.py`, and print the bot's Discord invite link to your terminal once generated.
*   `stop`: Stops the running `rfibot` `tmux` session, gracefully shutting down the bot.
*   `restart`: Stops the bot (if running) and then starts it again.
*   `status`: Checks if the `rfibot` `tmux` session is active and reports the bot's running status.
*   `attach`: Attaches your terminal to the `rfibot` `tmux` session, allowing you to see the bot's live output. Press `Ctrl+b d` to detach without stopping the bot.
*   `clean`: Deletes log files in the bot's main directory (`bot.log`, `discord_bot.log`, etc.) that are older than 72 hours (3 days). This is also performed automatically when the bot starts via `manage.sh`.

**Example:**

```bash
# Start the bot
bash manage.sh start

# Check its status
bash manage.sh status

# Attach to see live output
tmux attach -t rfibot

# Stop the bot
bash manage.sh stop
```

**Important:** For the `manage.sh` script to work, the `tmux` server must be running. If `tmux ls` shows "no server running", simply type `tmux` in your terminal, then detach (`Ctrl+b d`) to start the server.

## Logging and Error Handling

The bot uses a custom error handler that logs warnings and errors to a dedicated Discord channel named `bot-status`. If this channel does not exist, the bot will attempt to create it in the first guild it's connected to. Uncaught exceptions and critical log messages will be sent to this channel.

## Troubleshooting

*   **`PyNaCl is not installed, voice will NOT be supported`**: This warning indicates a missing dependency for Discord voice features. If your bot does not require voice functionality, you can safely ignore this. Otherwise, install it: `uv pip install pynacl`.
*   **Commands not processing**: Ensure all cogs (`.py` files in the `cogs/` directory) are loading without `SyntaxError` or other issues. Check `discord_bot.log` for `Failed to load cog` messages.
*   **Duplicate log messages**: This can occur if logging is misconfigured. Ensure the `discord_bot` logger does not propagate messages to the root logger if both have console handlers.