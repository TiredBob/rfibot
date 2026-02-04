# rfibot: A Feature-Rich Discord Bot

## Overview

rfibot is a versatile Discord bot built with Python and `discord.py`. It offers a variety of commands for entertainment, utility, and even integrates with the Gemini API for generative AI features. The bot is designed to be robust, featuring custom error handling and dedicated logging to a 'bot-status' channel.

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
*   **AI Integration**: Answers questions and generates content using the Google Gemini API (requires configuration).

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
    uv pip install -r requirements.txt # Or uv pip install . if pyproject.toml is used directly
    ```
    *Note: If you don't have a `requirements.txt`, you might need to generate it from `uv.lock` or install based on `pyproject.toml`.*
4.  **Configuration (`.env` file)**:
    Create a `.env` file in the root directory of the project. This file will hold your sensitive API keys and tokens.
    ```
    DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
    # GOOGLE_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY # Uncomment and set if using Gemini API
    ```
    *   **DISCORD_TOKEN**: Obtain this from the Discord Developer Portal for your bot.
    *   **GOOGLE_API_KEY**: Obtain this from Google AI Studio or Google Cloud for Gemini API access.
5.  **Run the Bot**:
    ```bash
    python bot.py
    ```

## Logging and Error Handling

The bot uses a custom error handler that logs warnings and errors to a dedicated Discord channel named `bot-status`. If this channel does not exist, the bot will attempt to create it in the first guild it's connected to. Uncaught exceptions and critical log messages will be sent to this channel.

## Troubleshooting

*   **`PyNaCl is not installed, voice will NOT be supported`**: This warning indicates a missing dependency for Discord voice features. If your bot does not require voice functionality, you can safely ignore this. Otherwise, install it: `uv pip install pynacl`.
*   **Commands not processing**: Ensure all cogs (`.py` files in the `cogs/` directory) are loading without `SyntaxError` or other issues. Check `discord_bot.log` for `Failed to load cog` messages.
*   **Duplicate log messages**: This can occur if logging is misconfigured. Ensure the `discord_bot` logger does not propagate messages to the root logger if both have console handlers.
*   **Gemini API errors**: Issues like "API key not valid", "Resource exhausted", or "model not found" indicate problems with your `GOOGLE_API_KEY` or usage limits.