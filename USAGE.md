# How to Use rfibot After Joining Your Server

Welcome to rfibot! This guide will help you get started with using the bot in your Discord server. Whether you're new to Discord bots or just need a refresher, we'll walk you through everything you need to know.

## 1. Understanding Bot Permissions

When you invite rfibot to your server, it needs certain permissions to work properly. Don't worry - we'll explain what these permissions mean and how to manage them.

### What Permissions Does rfibot Need?

rfibot requires these basic permissions to function:
- **Send Messages**: Allows the bot to respond to commands
- **Read Message History**: Allows the bot to see previous messages in channels
- **Add Reactions**: Allows the bot to add emoji reactions to messages
- **Embed Links**: Allows the bot to send rich embed messages (like help menus)
- **Use Slash Commands**: Allows the bot to respond to slash commands

### How to Check and Fix Permissions

If the bot isn't responding to commands or seems to be having issues, you may need to check its permissions:

**For the entire server:**
1. Go to your server settings (click the server name at the top left)
2. Click on "Roles" in the left sidebar
3. Find the role assigned to rfibot (usually named after the bot)
4. Make sure the permissions listed above are enabled (green checkmark)

**For specific channels:**
1. Right-click on the channel where you want to use the bot
2. Click "Edit Channel"
3. Go to the "Permissions" tab
4. Find rfibot in the list of roles/members
5. Make sure the permissions listed above are enabled (green checkmark)

**Troubleshooting Tip:** If you're still having issues, try giving rfibot the "Administrator" permission temporarily to test if it's a permission issue. If it works, you can then fine-tune the permissions.

## 2. Using Bot Commands

rfibot responds to commands that start with `!`. Here's how to use them:

### Getting Help

**See all available commands:**
```
!help
```

**Get help with a specific command:**
```
!help roll
```

This will show you detailed information about how to use that command, including examples.

### Basic Commands to Try

Here are some fun commands to get you started:

**🎲 Games and Fun:**
- `!roll 2d6` - Roll two six-sided dice (great for tabletop games!)
- `!8ball Will I have a good day?` - Ask the Magic 8-Ball a question
- `!coinflip` - Flip a virtual coin
- `!rfi` - Roll for Initiative (a d20 roll with fun outcomes)

**🤝 Social Commands:**
- `!slap @friend` - Playfully slap a friend
- `!challenge @friend` - Challenge someone to a d20 roll-off
- `!rps @friend` - Play Rock, Paper, Scissors
- `!tictactoe @friend` - Play Tic-Tac-Toe
- `!tictactoe bot` - Play Tic-Tac-Toe against the bot itself!

**🛠️ Utility Commands:**
- `!ping` - Check if the bot is online and see its response time
- `!invite` - Get a link to invite the bot to other servers
- `!qotd` - Get the Quote of the Day

### Command Format Tips

- Always start commands with `!`
- For commands that require a user mention (like `!slap`), you can:
  - Type `@` and select the user from the dropdown
  - Click on a user's message and copy their mention
- For dice rolling (`!roll`), use the format `NdM` where:
  - `N` = number of dice
  - `M` = number of sides on each die
  - Example: `!roll 3d8` rolls three 8-sided dice

## 3. Bot Status Channel

rfibot has a special feature - it logs important messages, warnings, and errors to a channel called `bot-status`. This helps you keep track of what the bot is doing.

### Setting Up the Bot Status Channel

**Option 1: Let the bot create it (easiest)**
1. Make sure rfibot has the "Manage Channels" permission
2. The bot will automatically try to create a `bot-status` channel when it joins your first server

**Option 2: Create it manually (recommended)**
1. Click the "+" button next to "Text Channels" in your server
2. Name the channel `bot-status` (exactly this name, all lowercase)
3. Make sure rfibot has these permissions in this channel:
   - Send Messages ✅
   - Read Message History ✅

### What You'll See in the Bot Status Channel

The bot will post messages like:
- When it connects to your server
- Important operational updates
- Error messages if something goes wrong
- Status changes and maintenance notifications

## 4. Inviting the Bot to Other Servers

Want to add rfibot to another Discord server you manage? Here's how:

### Step-by-Step Guide

1. **Get the invite link:**
   ```
   !invite
   ```
   Type this command in any channel where the bot is active.

2. **Click the link:**
   The bot will send you an invite link. Click on it.

3. **Choose your server:**
   - A webpage will open showing your Discord servers
   - Select the server you want to add rfibot to
   - Make sure you have "Manage Server" permissions in that server

4. **Review permissions:**
   - You'll see a list of permissions the bot is requesting
   - These are the same permissions we discussed earlier
   - You can adjust them if needed, but the default set is recommended

5. **Complete the invite:**
   - Click "Authorize"
   - Complete any CAPTCHA verification if required
   - The bot will join your server!

### Troubleshooting Invites

**"I don't see my server in the list"**
- Make sure you're logged into the correct Discord account
- You need "Manage Server" permissions in the server you want to add the bot to

**"The invite link expired"**
- Invite links can expire after a while
- Just type `!invite` again to get a fresh link

**"I get a permissions error"**
- Double-check that you have administrator or "Manage Server" permissions
- Try logging out and back into Discord

## 5. Managing the Bot in Your Server

### Bot Roles and Hierarchy

Discord has a role hierarchy system. For the bot to work properly:

1. **Bot role position matters:**
   - The bot's role should be higher than regular members
   - But it doesn't need to be at the very top

2. **How to adjust the bot's role:**
   - Go to Server Settings > Roles
   - Drag the bot's role to the appropriate position
   - A good rule: Put it above regular members but below moderators/admins

### Best Practices for Bot Management

**Channel Organization:**
- Create a dedicated channel like `#bot-commands` for bot usage
- This keeps your main channels clean
- Give rfibot full permissions in this channel

**Permission Safety:**
- Don't give the bot "Administrator" permission unless necessary
- The bot only needs the permissions listed earlier to work properly
- Regularly review the bot's permissions (every few months)

**Keeping the Bot Active:**
- Bots need to be online to respond to commands
- If the bot seems offline, check the `bot-status` channel for error messages
- The bot owner can restart it if needed

## 6. Advanced Features

### Interactive Games

rfibot has several interactive games that use buttons:

**Tic-Tac-Toe:**
- Challenge a friend with `!tictactoe @friend`
- Or play against the bot with `!tictactoe bot`
- Click the buttons to make your moves

**Rock, Paper, Scissors:**
- Challenge a friend with `!rps @friend`
- Both players click their choice (Rock 🪨, Paper 📄, or Scissors ✂️)
- The winner is announced automatically

**Roll for Initiative Challenges:**
- Challenge a friend with `!challenge @friend`
- Both players roll a d20
- The higher roll wins!

### Special Features

**Save Rolls:**
- If you roll a critical failure (rolling a 1 on `!rfi`), you get a chance to "save"
- A button will appear letting you roll again to try to recover

**Game Timeouts:**
- Interactive games have time limits (usually 3 minutes)
- If no one responds, the game will time out automatically
- This prevents abandoned games from cluttering channels

## 7. Getting More Help

If you're having trouble with rfibot:

1. **Check the bot-status channel** for error messages
2. **Try the help command** `!help` for command-specific assistance
3. **Review permissions** as described in section 1
4. **Contact the bot owner** if you're still having issues

## 8. Command Reference

Here's a quick reference of all available commands:

| Command | Description | Example |
|---------|-------------|---------|
| `!help` | Show all commands or get help on a specific command | `!help roll` |
| `!ping` | Check bot latency | `!ping` |
| `!invite` | Get bot invite link | `!invite` |
| `!roll <dice>` | Roll dice (format: NdM) | `!roll 2d6` |
| `!8ball <question>` | Ask the Magic 8-Ball | `!8ball Will it rain?` |
| `!coinflip` | Flip a coin | `!coinflip` |
| `!rfi` | Roll for Initiative (d20) | `!rfi` |
| `!challenge @user` | Challenge to d20 roll-off | `!challenge @friend` |
| `!rps @user` | Play Rock, Paper, Scissors | `!rps @friend` |
| `!tictactoe @user|bot` | Play Tic-Tac-Toe | `!tictactoe bot` |
| `!slap @user` | Playfully slap a user | `!slap @friend` |
| `!qotd` | Get Quote of the Day | `!qotd` |

## 9. Tips for New Users

1. **Start simple:** Try `!ping` first to make sure the bot is working
2. **Use help:** If you're unsure about a command, use `!help [command]`
3. **Be patient:** Some commands take a moment to process
4. **Check permissions:** If a command doesn't work, check the bot's permissions
5. **Have fun:** Experiment with different commands and games!

## 10. Safety and Privacy

rfibot is designed with safety in mind:
- It only collects minimal information needed to function
- It doesn't store personal data or messages
- All game data is temporary and not saved
- The bot respects Discord's privacy policies

Enjoy using rfibot! If you have any questions or need help, don't hesitate to ask in the `bot-status` channel or contact the bot owner.