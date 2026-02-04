# rfibot: A Fun and Functional Discord Bot

Hey there! Welcome to rfibot - your new Discord companion for games, fun, and utility commands. Whether you're running a gaming server, a community hub, or just want to add some entertainment to your Discord, rfibot has you covered.

## What Can rfibot Do?

rfibot is packed with features to make your Discord server more engaging:

### 🎲 **Games and Entertainment**
- **Dice Rolling**: `!roll 2d6` - Perfect for tabletop RPGs! Roll any combination like `3d8`, `1d20`, etc.
- **Magic 8-Ball**: `!8ball Will I win the lottery?` - Get mystical answers to your burning questions
- **Coin Flips**: `!coinflip` or `!flip` - Quick and easy virtual coin toss
- **Roll for Initiative**: `!rfi` - A d20 roll with fun, dramatic outcomes
- **Challenges**: `!challenge @friend` - Compete in d20 roll-offs against your friends
- **Rock, Paper, Scissors**: `!rps @friend` - Classic game with interactive buttons
- **Tic-Tac-Toe**: `!tictactoe @friend` or `!tictactoe bot` - Play against friends or the bot itself

### 🤝 **Social Fun**
- **Slap Command**: `!slap @friend` - Playfully slap your friends with random funny messages

### 🛠️ **Utility Commands**
- **Ping Check**: `!ping` - See how responsive the bot is
- **Invite Link**: `!invite` - Get a link to add rfibot to other servers
- **Quote of the Day**: `!qotd` - Get inspiring quotes from zenquotes.io

### 🔧 **Advanced Features**
- **Interactive Games**: Many games use Discord's button interface for easy play
- **Save Rolls**: When you critically fail (`!rfi` rolls a 1), you get a chance to save yourself
- **Automatic Logging**: Errors and status messages go to a `bot-status` channel
- **Permission Management**: Smart handling of Discord permissions

## Getting Started with rfibot

Want to run your own instance of rfibot? Here's how to set it up:

### Prerequisites
- A Discord account and a server to test in
- Basic command line knowledge
- Python 3.11 or higher
- A Discord bot token (get this from the [Discord Developer Portal](https://discord.com/developers/applications))

### Step-by-Step Setup

**1. Clone the Repository**
```bash
git clone https://github.com/TiredBob/rfibot.git
cd rfibot
```

**2. Set Up Virtual Environment**
We recommend using `uv` for dependency management (it's fast and efficient):
```bash
uv venv        # Create virtual environment
source .venv/bin/activate  # Activate it
```

**3. Install Dependencies**
```bash
uv pip install .
```
This installs all required packages from `pyproject.toml`:
- `discord.py` (the Discord API wrapper)
- `requests` (for HTTP requests like the Quote of the Day)
- `python-dotenv` (for environment variable management)

**4. Configure Your Bot**
Create a `.env` file in the project root:
```bash
touch .env
```
Add your Discord bot token:
```
DISCORD_TOKEN=your_bot_token_here
```
**Important:** Never share your bot token! Keep this file secure.

**5. Run the Bot**
```bash
python bot.py
```
You should see the bot come online and display an invite link in the console.

## Managing Your Bot with `manage.sh`

Running a bot 24/7 can be tricky, but we've included a handy `manage.sh` script to make it easier. This script uses `tmux` to keep your bot running even when you close your terminal.

### What You'll Need
- `tmux` installed on your system
- Basic familiarity with terminal commands

### Available Commands

| Command | Description |
|---------|-------------|
| `bash manage.sh start` | Start the bot in a tmux session |
| `bash manage.sh stop` | Gracefully stop the bot |
| `bash manage.sh restart` | Restart the bot (stop + start) |
| `bash manage.sh status` | Check if the bot is running |
| `bash manage.sh attach` | View the bot's live console output |

### Example Usage

**Start your bot:**
```bash
bash manage.sh start
```
The script will:
1. Activate the virtual environment
2. Start the bot in a detached tmux session
3. Extract and display the invite link
4. Log all output to `bot.log`

**Check status:**
```bash
bash manage.sh status
```

**View live logs:**
```bash
bash manage.sh attach
```
Press `Ctrl+b d` to detach from the tmux session without stopping the bot.

**Stop the bot:**
```bash
bash manage.sh stop
```

### Pro Tips
- The bot automatically cleans up old log files (>72 hours)
- Logs are saved to `bot.log` in the project directory
- You can manually clean logs with `bash manage.sh clean`

**Troubleshooting tmux:**
If you get "no server running" errors:
```bash
tmux  # Start tmux server
# Press Ctrl+b d to detach
```

## Bot Configuration and Customization

### Permissions Setup
When inviting your bot to a server, it needs these basic permissions:
- ✅ Send Messages
- ✅ Read Message History  
- ✅ Add Reactions
- ✅ Embed Links
- ✅ Use Slash Commands

**Best Practice:** Create a dedicated `#bot-commands` channel and give rfibot full permissions there.

### Bot Status Channel
rfibot automatically logs important events to a channel named `bot-status`. If this channel doesn't exist, the bot will try to create it in the first server it joins.

**What gets logged:**
- Bot startup/shutdown events
- Error messages and warnings
- Operational status updates

### Customizing the Bot
Want to add more features? Check out the `cogs/` directory:
- `games.py` - All game-related commands
- `social.py` - Social interaction commands  
- `utils.py` - Utility commands and scheduled tasks
- `help.py` - Custom help system

The bot uses Discord.py's cog system, making it easy to add new features without modifying core files.

## Troubleshooting Common Issues

**🔴 "PyNaCl is not installed, voice will NOT be supported"**
This warning appears if you don't have the PyNaCl library installed. Since rfibot doesn't use voice features, you can safely ignore this warning. If you want to eliminate it:
```bash
uv pip install pynacl
```

**❌ Commands not working?**
1. **Check permissions:** Make sure rfibot has the required permissions in the channel
2. **Check logs:** Look at `discord_bot.log` for error messages
3. **Check cog loading:** Ensure all cogs in the `cogs/` directory are loading properly
4. **Restart the bot:** Sometimes a simple restart fixes issues

**📝 Duplicate log messages?**
This can happen if logging is misconfigured. The bot uses a custom logger that prevents this, but if you see duplicates:
- Check that you don't have multiple logging handlers
- Ensure the logger isn't propagating to the root logger

**🤖 Bot not responding?**
1. Check if the bot is online (look for its status in Discord)
2. Verify the bot has the "Send Messages" permission
3. Check the `bot-status` channel for error messages
4. Try restarting the bot with `bash manage.sh restart`

## Getting Help and Support

**Need help with rfibot?**
- Check the `bot-status` channel for error messages
- Review the [USAGE.md](USAGE.md) file for detailed usage instructions
- Look at the troubleshooting section above
- Contact the bot developer if issues persist

**Want to contribute?**
- Fork the repository and submit pull requests
- Report bugs by opening GitHub issues
- Suggest new features - we're always open to ideas!

## Technical Details

### Built With
- **Python 3.11+** - The programming language
- **discord.py 2.4.0+** - Discord API wrapper
- **uv** - Fast Python package installer and virtual environment manager
- **tmux** - Terminal multiplexer for 24/7 bot operation

### Architecture
- **Modular design** using Discord.py cogs
- **Custom error handling** with dedicated logging
- **Interactive games** using Discord UI components
- **Scheduled tasks** for maintenance (log cleanup)

### Performance
- Lightweight and efficient
- Minimal memory usage
- Fast response times
- Designed for 24/7 operation

## License and Credits

rfibot is open source software. Feel free to use, modify, and distribute it according to the license terms.

**Special Thanks:**
- To the Discord.py team for their amazing library
- To all contributors and testers
- To the open source community for inspiration

## Final Notes

rfibot is designed to be:
- **Easy to use** - Simple commands with clear feedback
- **Reliable** - Built for 24/7 operation
- **Extensible** - Easy to add new features
- **Fun** - Because Discord should be enjoyable!

We hope you enjoy using rfibot as much as we enjoyed creating it! 🎉

## Stay Connected

**Found a bug?** Report it on GitHub with details about what happened and how to reproduce it.

**Have an idea?** We'd love to hear your feature suggestions!

**Want to contribute?** Check out the code and submit a pull request. All contributions are welcome!

**Need help?** Don't hesitate to reach out. We're here to help you get the most out of rfibot.

---

*Happy bot-ing! 🤖🎮*  
The rfibot team