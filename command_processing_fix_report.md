I have fixed the `SyntaxError`s in `cogs/games.py` and `cogs/utils.py`. These errors were preventing the respective cogs from loading, which meant that any commands defined within them (such as `!ping` and `!coinflip`) were not being registered by the bot.

With these fixes applied, the cogs should now load successfully, and the bot should be able to process commands as expected.

The changes have been committed and pushed to the remote `main` branch.