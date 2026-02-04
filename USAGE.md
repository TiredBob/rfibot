# How to Use rfibot After Joining Your Server

This guide explains how to get rfibot up and running in your Discord server once it has been invited.

## 1. Granting Permissions (if necessary)

When inviting rfibot, you generally grant it a set of permissions. If you notice the bot isn't responding to commands or performing certain actions, ensure it has the necessary permissions in the channels you want it to operate in.

*   **Check Channel Permissions**:
    1.  Right-click on the channel where you want to use the bot.
    2.  Go to `Edit Channel` -> `Permissions`.
    3.  Check the roles/members for the bot or its associated role. Ensure it has permissions like `Send Messages`, `Read Message History`, `Add Reactions`, `Use Slash Commands`, etc., as needed for its functions.

## 2. Using Bot Commands

rfibot listens for commands prefixed with `!`.

*   **Discover Commands**: To see a list of available commands and their descriptions, type:
    ```
    !help
    ```
*   **Specific Command Help**: For help on a specific command, type:
    ```
    !help <command_name>
    # Example: !help roll
    ```
*   **Basic Commands**:
    *   `!ping`: Check if the bot is online and responsive.
    *   `!invite`: Get the official invite link to add the bot to other servers.
    *   `!roll 2d6`: Roll two six-sided dice.
    *   `!8ball Will I be rich?`: Ask the magic 8-ball a question.
    *   `!coinflip`: Flip a coin.
    *   `!slap @user`: Slap a user.
    *   And many more! (Check `!help`)

## 3. Bot Status Channel

rfibot is configured to log important operational messages, warnings, and errors to a channel named `bot-status`.

*   **Ensure `bot-status` Channel Exists**:
    *   If you want to receive these logs, ensure there is a text channel named `bot-status` in your server. The bot will attempt to create it in the first server it joins if it doesn't exist, but it's best practice to have one ready.
    *   The bot needs `Send Messages` and `Read Message History` permissions in this channel.

## 4. Inviting the Bot to Other Servers

If you want to add rfibot to another Discord server you manage:

1.  Use the `!invite` command in any channel the bot is active in.
2.  The bot will respond with its official invite link.
3.  Click the link and follow the prompts to select the server you wish to add it to.
