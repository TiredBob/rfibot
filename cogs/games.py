import discord
from discord import ui
from discord.ext import commands
import secrets
import logging
import asyncio
from typing import Union

logger = logging.getLogger('discord_bot')

# =====================================================================================================================
# 1. CONFIGURATION & CONSTANTS
# =====================================================================================================================

RFI_CRITICAL_SUCCESS = [
    "is a Critical success! 🎉",
    "landed a nat 20! Incredible! 🎊",
    "achieved a perfect roll! ✨",
    "rolled a natural 20! The crowd goes wild! 🥳",
    "succeeded with legendary flair! 🌟",
    "aced the roll! It's a masterpiece of luck! 🎨",
    "nailed it! The universe bends to their will. 🌌",
    "achieved a flawless victory! 🏆",
    "is a stunning success! Absolutely brilliant! 💡",
    "pulled it off perfectly! What a legend! 👑",
]
RFI_SUCCESS = [
    "has succeeded!",
    "passed the check. Well done.",
    "managed to succeed.",
    "got the job done. Solid work.",
    "squeaked by with a success.",
    "has successfully navigated the challenge.",
    "made it look easy. (It wasn't.)",
    "passed. Nothing to see here, move along.",
    "achieved a favorable outcome.",
    "is in the clear. For now.",
]
RFI_FAILURE = [
    "is a failure!",
    "did not succeed.",
    "failed the check. Better luck next time.",
    "stumbled at the finish line.",
    "missed the mark. Whoops.",
    "couldn't quite make it happen.",
    "has failed. Try, try again?",
    "met with an unfortunate outcome.",
    "fumbled the attempt. It's okay, it happens.",
    "tripped on a conveniently placed banana peel. 🍌",
]
RFI_CRITICAL_FAILURE = [
    "is a Critical failure! 💀",
    "rolled a nat 1... Ouch. ☠️",
    "failed spectacularly! 💥",
    "somehow managed to set water on fire. 🔥💧",
    "tripped, fell, and discovered a new, embarrassing way to fail.",
    "snatched defeat from the jaws of victory.",
    "has entered a world of comedic failure. 🤡",
    "failed so hard, the universe felt secondhand embarrassment.",
    "rolled a 1. The dice gods are laughing.",
    "achieved a legendary fail. It will be spoken of for generations.",
]
RFI_SAVE_SUCCESS = [
    "but they managed to save themself from disaster!",
    "but narrowly escaped the worst outcome!",
    "but against all odds, they pulled through!",
    "but made a heroic recovery at the last second! 💪",
    "but managed to turn a failure into a... less-failurey situation.",
    "but luck was on their side this time!",
    "but dodged that bullet like a pro! 🏃💨",
    "but somehow, it all worked out in the end.",
    "but pulled a rabbit out of a hat and is safe! 🐇🎩",
    "but their quick thinking saved the day!",
]
RFI_SAVE_FAILURE = [
    "and the situation has gone from bad to worse.",
    "and things have escalated into a catastrophe.",
    "and now everything is on fire. Everything.",
    "and the dice gods demand a sacrifice.",
    "and the attempt to save only made it funnier for everyone else.",
    "and it seems luck has completely abandoned them.",
    "and now there are two problems.",
    "and the failure has been upgraded to 'epic'.",
    "and they are now questioning all their life choices.",
    "and the situation is now officially a dumpster fire. 🔥🗑️",
]
EIGHT_BALL_RESPONSES = [
    "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.",
    "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
    "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
    "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful.",
]

# =====================================================================================================================
# 2. UI VIEWS & HELPER CLASSES
# =====================================================================================================================

# --- Tic-Tac-Toe Classes ---
class TicTacToeButton(ui.Button['TicTacToeGameView']):
    """A button on the Tic-Tac-Toe game board."""
    def __init__(self, x: int, y: int):
        """
        Initializes the TicTacToeButton.
        Args:
            x (int): The x-coordinate of the button on the board.
            y (int): The y-coordinate of the button on the board.
        """
        super().__init__(style=discord.ButtonStyle.secondary, label='​', row=y)
        self.x = x
        self.y = y
    async def callback(self, interaction: discord.Interaction):
        """
        Handles the button click event.
        Args:
            interaction (discord.Interaction): The interaction object.
        """
        assert self.view is not None
        view: TicTacToeGameView = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            await interaction.response.send_message("This space is already taken!", ephemeral=True)
            return
        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"It is now {view.challenged.mention}'s turn (O)"
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"It is now {view.challenger.mention}'s turn (X)"
        self.disabled = True
        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f'{view.challenger.mention} has won!'
            elif winner == view.O:
                content = f'{view.challenged.mention} has won!'
            else:
                content = "It's a tie!"
            for child in view.children:
                child.disabled = True
            view.stop()
            await interaction.response.edit_message(content=content, view=view)
            return
        await interaction.response.edit_message(content=content, view=view)
        if view.challenged.bot and view.current_player == view.O:
            await asyncio.sleep(1)
            await view.bot_move()

class TicTacToeGameView(ui.View):
    """A view for the Tic-Tac-Toe game, managing the board and player turns."""
    children: list[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2
    def __init__(self, challenger: discord.Member, challenged: Union[discord.Member, discord.ClientUser]):
        """
        Initializes the TicTacToeGameView.
        Args:
            challenger (discord.Member): The user who initiated the challenge.
            challenged (Union[discord.Member, discord.ClientUser]): The user who was challenged.
        """
        super().__init__()
        self.challenger = challenger
        self.challenged = challenged
        self.current_player = secrets.choice([self.X, self.O])
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        self.message = None
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))
    def check_board_winner(self) -> Union[int, None]:
        """
        Checks the board for a winner.
        Returns:
            Union[int, None]: The winner (X, O, or Tie), or None if there is no winner yet.
        """
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X
        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X
        if all(i != 0 for row in self.board for i in row):
            return self.Tie
        return None
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Checks if the user is allowed to interact with the view.
        Args:
            interaction (discord.Interaction): The interaction object.
        Returns:
            bool: True if the user is allowed to interact, False otherwise.
        """
        if self.challenged.bot:
            if self.current_player == self.X and interaction.user == self.challenger:
                return True
            else:
                await interaction.response.send_message("It's not your turn!", ephemeral=True)
                return False
        if self.current_player == self.X and interaction.user == self.challenger:
            return True
        elif self.current_player == self.O and interaction.user == self.challenged:
            return True
        else:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return False
    async def bot_move(self):
        """Makes a random move for the bot."""
        available_moves = []
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell == 0:
                    available_moves.append((x, y))
        if not available_moves:
            return
        x, y = secrets.choice(available_moves)
        button = self.children[y * 3 + x]
        button.style = discord.ButtonStyle.success
        button.label = 'O'
        button.disabled = True
        self.board[y][x] = self.O
        self.current_player = self.X
        winner = self.check_board_winner()
        if winner is not None:
            if winner == self.X:
                content = f'{self.challenger.mention} has won!'
            elif winner == self.O:
                content = f'{self.challenged.mention} has won!'
            else:
                content = "It's a tie!"
            for child in self.children:
                child.disabled = True
            self.stop()
        else:
            content = f"It is now {self.challenger.mention}'s turn (X)"
        if self.message:
            await self.message.edit(content=content, view=self)

class TicTacToeChallengeView(ui.View):
    """A view for the Tic-Tac-Toe challenge, with accept and deny buttons."""
    def __init__(self, challenger: discord.Member, challenged: Union[discord.Member, discord.ClientUser]):
        """
        Initializes the TicTacToeChallengeView.
        Args:
            challenger (discord.Member): The user who initiated the challenge.
            challenged (Union[discord.Member, discord.ClientUser]): The user who was challenged.
        """
        super().__init__(timeout=180.0)
        self.challenger = challenger
        self.challenged = challenged
        self.message = None
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Checks if the user is allowed to interact with the view.
        Args:
            interaction (discord.Interaction): The interaction object.
        Returns:
            bool: True if the user is allowed to interact, False otherwise.
        """
        if self.challenged.bot:
            if interaction.user.id != self.challenger.id:
                await interaction.response.send_message("This is not your challenge to accept or deny.", ephemeral=True)
                return False
        elif interaction.user.id not in [self.challenger.id, self.challenged.id]:
            await interaction.response.send_message("This is not your challenge to accept or deny.", ephemeral=True)
            return False
        return True
    async def on_timeout(self):
        """Handles the view timing out."""
        if self.message:
            await self.message.edit(content=f"Challenge from {self.challenger.mention} to {self.challenged.mention} timed out.", view=None)
    @ui.button(label="Accept", style=discord.ButtonStyle.primary)
    async def accept(self, interaction: discord.Interaction, button: ui.Button):
        """Callback for the accept button."""
        if not self.challenged.bot and interaction.user.id != self.challenged.id:
            await interaction.response.send_message("Only the challenged user can accept this challenge.", ephemeral=True)
            return
        logger.info(f'{self.challenged.name} accepted TicTacToe challenge from {self.challenger.name}')
        game_view = TicTacToeGameView(self.challenger, self.challenged)
        starting_player = game_view.challenger if game_view.current_player == game_view.X else game_view.challenged
        await interaction.response.edit_message(
            content=f"""**Tic-Tac-Toe!**
{self.challenger.mention} (X) vs {self.challenged.mention} (O)
It is now {starting_player.mention}'s turn.""",
            view=game_view
        )
        game_view.message = await interaction.original_response()
        self.stop()
    @ui.button(label="Deny", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: ui.Button):
        """Callback for the deny button."""
        if interaction.user.id == self.challenger.id:
            logger.info(f'{self.challenger.name} cancelled the TicTacToe challenge to {self.challenged.name}')
            await interaction.response.edit_message(
                content=f"{self.challenger.mention} cancelled the challenge to {self.challenged.mention}.",
                view=None
            )
            self.stop()
        elif interaction.user.id == self.challenged.id:
            logger.info(f'{self.challenged.name} denied TicTacToe challenge from {self.challenger.name}')
            await interaction.response.edit_message(
                content=f"{self.challenged.mention} denied the challenge from {self.challenger.mention}.",
                view=None
            )
            self.stop()

# --- Rock, Paper, Scissors Classes ---
class RPSGameView(ui.View):
    """A view for the Rock, Paper, Scissors game."""
    def __init__(self, challenger: discord.Member, challenged: discord.Member):
        """
        Initializes the RPSGameView.
        Args:
            challenger (discord.Member): The user who initiated the challenge.
            challenged (discord.Member): The user who was challenged.
        """
        super().__init__(timeout=180.0)
        self.challenger = challenger
        self.challenged = challenged
        self.choices = {challenger.id: None, challenged.id: None}
        self.message = None
        self.game_over = False
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Checks if the user is allowed to interact with the view.
        Args:
            interaction (discord.Interaction): The interaction object.
        Returns:
            bool: True if the user is allowed to interact, False otherwise.
        """
        # Allow only the challenger or challenged to interact
        if interaction.user.id not in [self.challenger.id, self.challenged.id]:
            await interaction.response.send_message("This is not your game to play.", ephemeral=True)
            return False
        return True
    async def on_timeout(self):
        """Handles the view timing out."""
        if self.game_over:
            return
        if self.message:
            await self.message.edit(content="The game timed out! The buttons have been removed.", view=None)
    async def _process_choice(self, interaction: discord.Interaction, choice: str):
        """
        Processes a player's choice.
        Args:
            interaction (discord.Interaction): The interaction object.
            choice (str): The player's choice ("Rock", "Paper", or "Scissors").
        """
        # Check if the user has already made a choice
        if self.choices[interaction.user.id] is not None:
            await interaction.response.send_message("You have already made your choice!", ephemeral=True)
            return
        self.choices[interaction.user.id] = choice
        await interaction.response.send_message(f"You chose **{choice}**. Waiting for the other player.", ephemeral=True)
        # Check if both players have made their choice
        challenger_choice = self.choices[self.challenger.id]
        challenged_choice = self.choices[self.challenged.id]
        if challenger_choice and challenged_choice:
            self.game_over = True
            # Both players have chosen, determine the winner
            winner = self._get_winner(challenger_choice, challenged_choice)
            result_message = self._format_result(winner, challenger_choice, challenged_choice)
            # Disable all buttons
            for item in self.children:
                item.disabled = True
            # Update the original message to show the game is over
            if self.message:
                await self.message.edit(content="The game has ended. See results below.", view=None)
            # Send the result in a new message
            await interaction.channel.send(result_message)
            self.stop()
    def _get_winner(self, choice1: str, choice2: str) -> Union[discord.Member, None]:
        """
        Determines the winner of the game.
        Args:
            choice1 (str): The challenger's choice.
            choice2 (str): The challenged user's choice.
        Returns:
            Union[discord.Member, None]: The winner, or None for a tie.
        """
        if choice1 == choice2:
            return None  # Tie
        rules = {
            "Rock": "Scissors",
            "Paper": "Rock",
            "Scissors": "Paper"
        }
        if rules[choice1] == choice2:
            return self.challenger
        else:
            return self.challenged
    def _format_result(self, winner: Union[discord.Member, None], challenger_choice: str, challenged_choice: str) -> str:
        """
        Formats the result message.
        Args:
            winner (Union[discord.Member, None]): The winner of the game.
            challenger_choice (str): The challenger's choice.
            challenged_choice (str): The challenged user's choice.
        Returns:
            str: The formatted result message.
        """
        result = f"""**Rock, Paper, Scissors Results:**
{self.challenger.mention} chose **{challenger_choice}**
{self.challenged.mention} chose **{challenged_choice}**"""

        if winner:
            result += f"\n🎉 **{winner.mention} wins!** 🎉"
        else:
            result += "\n🤝 **It's a tie!** 🤝"
        return result
    @ui.button(label="Rock", style=discord.ButtonStyle.primary, emoji="🪨")
    async def rock(self, interaction: discord.Interaction, button: ui.Button):
        """Callback for the rock button."""
        await self._process_choice(interaction, "Rock")
    @ui.button(label="Paper", style=discord.ButtonStyle.primary, emoji="📄")
    async def paper(self, interaction: discord.Interaction, button: ui.Button):
        """Callback for the paper button."""
        await self._process_choice(interaction, "Paper")
    @ui.button(label="Scissors", style=discord.ButtonStyle.primary, emoji="✂️")
    async def scissors(self, interaction: discord.Interaction, button: ui.Button):
        """Callback for the scissors button."""
        await self._process_choice(interaction, "Scissors")

class RPSChallengeView(ui.View):
    """A view for the Rock, Paper, Scissors challenge, with accept and deny buttons."""
    def __init__(self, challenger: discord.Member, challenged: discord.Member):
        """
        Initializes the RPSChallengeView.
        Args:
            challenger (discord.Member): The user who initiated the challenge.
            challenged (discord.Member): The user who was challenged.
        """
        super().__init__(timeout=180.0)
        self.challenger = challenger
        self.challenged = challenged
        self.message = None
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Checks if the user is allowed to interact with the view.
        Args:
            interaction (discord.Interaction): The interaction object.
        Returns:
            bool: True if the user is allowed to interact, False otherwise.
        """
        # Allow only the challenger or challenged to interact
        if interaction.user.id not in [self.challenger.id, self.challenged.id]:
            await interaction.response.send_message("This is not your challenge to accept or deny.", ephemeral=True)
            return False
        return True
    async def on_timeout(self):
        """Handles the view timing out."""
        if self.message:
            await self.message.edit(content=f"Challenge from {self.challenger.mention} to {self.challenged.mention} timed out.", view=None)
    @ui.button(label="Accept", style=discord.ButtonStyle.primary)
    async def accept(self, interaction: discord.Interaction, button: ui.Button):
        """Callback for the accept button."""
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message("Only the challenged user can accept this challenge.", ephemeral=True)
            return
        logger.info(f'{self.challenged.name} accepted RPS challenge from {self.challenger.name}')
        game_view = RPSGameView(self.challenger, self.challenged)
        await interaction.response.edit_message(
            content=f"**Rock, Paper, Scissors!**
{self.challenger.mention} vs {self.challenged.mention}
Make your choice!",
            view=game_view
        )
        game_view.message = await interaction.original_response()
        self.stop()
    @ui.button(label="Deny", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: ui.Button):
        """Callback for the deny button."""
        if interaction.user.id == self.challenger.id:
            logger.info(f'{self.challenger.name} cancelled the RPS challenge to {self.challenged.name}')
            await interaction.response.edit_message(
                content=f"{self.challenger.mention} cancelled the challenge to {self.challenged.mention}.",
                view=None
            )
            self.stop()
        elif interaction.user.id == self.challenged.id:
            logger.info(f'{self.challenged.name} denied RPS challenge from {self.challenger.name}')
            await interaction.response.edit_message(
                content=f"{self.challenged.mention} denied the challenge from {self.challenger.mention}.",
                view=None
            )
            self.stop()

# --- Roll For Initiative (RFI) Classes ---
class RFIChallengeView(ui.View):
    """A view for the Roll for Initiative challenge, with accept and deny buttons."""
    def __init__(self, challenger: discord.Member, challenged: discord.Member):
        """
        Initializes the RFIChallengeView.
        Args:
            challenger (discord.Member): The user who initiated the challenge.
            challenged (discord.Member): The user who was challenged.
        """
        super().__init__(timeout=180.0)
        self.challenger = challenger
        self.challenged = challenged
        self.message = None
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Checks if the user is allowed to interact with the view.
        Args:
            interaction (discord.Interaction): The interaction object.
        Returns:
            bool: True if the user is allowed to interact, False otherwise.
        """
        # Allow challenger and challenged to interact
        if interaction.user.id not in [self.challenger.id, self.challenged.id]:
            await interaction.response.send_message("This is not your challenge to accept or deny.", ephemeral=True)
            return False
        return True
    async def on_timeout(self):
        """Handles the view timing out."""
        if self.message:
            await self.message.edit(content=f"Challenge from {self.challenger.mention} to {self.challenged.mention} timed out.", view=None)
    @ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: ui.Button):
        """Callback for the accept button."""
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message("Only the challenged user can accept this challenge.", ephemeral=True)
            return
        logger.info(f'{self.challenged.name} accepted RFI challenge from {self.challenger.name}')
        await interaction.response.edit_message(
            content=f'{self.challenged.mention} accepted the challenge! Rolling for initiative...',
            view=None
        )
        # RFI logic
        challenger_roll = secrets.randbelow(20) + 1
        challenged_roll = secrets.randbelow(20) + 1
        channel = interaction.channel
        await channel.send(f'{self.challenger.mention} rolled a {challenger_roll}')
        await channel.send(f'{self.challenged.mention} rolled a {challenged_roll}')
        if challenger_roll > challenged_roll:
            await channel.send(f'{self.challenger.mention} wins the RFI challenge! 🎉')
        elif challenger_roll < challenged_roll:
            await channel.send(f'{self.challenged.mention} wins the RFI challenge! 🎉')
        else:
            await channel.send('It's a tie! 🤝')
        self.stop()
    @ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: ui.Button):
        """Callback for the deny button."""
        if interaction.user.id == self.challenger.id:
            logger.info(f'{self.challenger.name} cancelled the RFI challenge to {self.challenged.name}')
            await interaction.response.edit_message(
                content=f"{self.challenger.mention} cancelled the challenge to {self.challenged.mention}.",
                view=None
            )
            self.stop()
        elif interaction.user.id == self.challenged.id:
            logger.info(f'{self.challenged.name} denied RFI challenge from {self.challenger.name}')
            await interaction.response.edit_message(
                content=f"{self.challenged.mention} denied the challenge from {self.challenger.mention}.",
                view=None
            )
            self.stop()

class SaveRollView(ui.View):
    """A view that allows a user to roll to save themselves from a critical failure."""
    def __init__(self, user: discord.Member):
        """
        Initializes the SaveRollView.
        Args:
            user (discord.Member): The user who can roll to save.
        """
        super().__init__(timeout=60.0)
        self.user = user
        self.message = None
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Checks if the user is allowed to interact with the view.
        Args:
            interaction (discord.Interaction): The interaction object.
        Returns:
            bool: True if the user is allowed to interact, False otherwise.
        """
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your roll to save.", ephemeral=True)
            return False
        return True
    async def on_timeout(self):
        """Handles the view timing out."""
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(content="The chance to save has passed.", view=self)
    @ui.button(label="Roll to Save", style=discord.ButtonStyle.secondary, emoji="🎲")
    async def roll_to_save(self, interaction: discord.Interaction, button: ui.Button):
        """Callback for the roll to save button."""
        roll = secrets.randbelow(20) + 1
        save_message = f"
{self.user.display_name} rolled a {roll} to save...
"
        if roll >= 10:
            save_message += secrets.choice(RFI_SAVE_SUCCESS)
        else:
            save_message += secrets.choice(RFI_SAVE_FAILURE)
        # Disable the button after clicking
        for item in self.children:
            item.disabled = True
        new_content = interaction.message.content + save_message
        await interaction.response.edit_message(content=new_content, view=self)
        self.stop()

# =====================================================================================================================
# 3. MAIN COG CLASS
# =====================================================================================================================

class Games(commands.Cog):
    """A cog for game-related commands."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("Games cog initialized")
    
    @commands.command(name='roll', help="Rolls dice and returns the results and their sum. Defaults to '2d6'. Example: !roll 3d8")
    async def roll(self, ctx: commands.Context, dice: str = '2d6'):
        """Rolls dice in NdM format (e.g., 2d6)."""
        logger.info(f'Roll command used by {ctx.author} with argument {dice}')
        try:
            dice = dice.lower()
            rolls, limit = map(int, dice.split('d')) # This will fail for negative numbers, but that's fine for a dice roller
            if rolls > 100:
                await ctx.send('Please limit the number of rolls to 100 or less')
                return
            if limit > 100:
                await ctx.send('Please limit the number of sides to 100 or less')
                return
            results = [secrets.randbelow(limit) + 1 for _ in range(rolls)]
            await ctx.send(f'Results: {results}
Total: {sum(results)}')
        except ValueError:
            await ctx.send('Format must be NdM (e.g., 2d6)')
    
    @commands.command(name='8ball', help='Asks the Magic 8-Ball a question and gets a classic response. Example: !8ball Will I be rich?')
    async def magic_8_ball(self, ctx: commands.Context, *, question: str):
        """Asks the Magic 8-Ball a question."""
        logger.info(f'Magic 8-Ball command used by {ctx.author} with question "{question}"')
        if not question:
            await ctx.send("You need to ask a question!")
            return
        lower_question = question.lower().strip().rstrip('?')
        if lower_question == "am i dumb" or lower_question == "am i stupid":
            response = "You are holding a coconut."
        else:
            response = secrets.choice(EIGHT_BALL_RESPONSES)
        await ctx.send(f'{ctx.author.display_name} asked: "{question}"
🎱 Answer: {response}')
    
    @commands.command(name='rfi', help='Rolls a d20 to determine success or failure.')
    async def rfi(self, ctx: commands.Context):
        """Rolls a d20 to determine success or failure."""
        logger.info(f'RFI command used by {ctx.author}')
        roll = secrets.randbelow(20) + 1
        # Determine the outcome based on the roll
        if roll == 1:
            response_list = RFI_CRITICAL_FAILURE
        elif roll < 10:
            response_list = RFI_FAILURE
        elif roll < 20:
            response_list = RFI_SUCCESS
        else:  # roll == 20
            response_list = RFI_CRITICAL_SUCCESS
        # Construct the message
        message = (
            f'{ctx.author.display_name} rolled a {roll}
'
            f'{ctx.author.display_name} {secrets.choice(response_list)}'
        )
        # Handle the special case for critical failure, otherwise send normally
        if roll == 1:
            save_view = SaveRollView(ctx.author)
            sent_message = await ctx.send(message, view=save_view)
            save_view.message = sent_message
        else:
            await ctx.send(message)
    
    @commands.command(name='challenge', aliases=['ch'], help='Challenges another user to a d20 roll-off. Example: !challenge @Radar')
    async def rfi_challenge(self, ctx: commands.Context, user: discord.Member):
        """Challenges another user to a d20 roll-off."""
        challenger = ctx.author
        if user == challenger:
            await ctx.send('You cannot challenge yourself!', ephemeral=True)
            return
        if user.bot:
            await ctx.send("You cannot challenge a bot!", ephemeral=True)
            return
        logger.info(f'RFI challenge command used by {challenger.name} to challenge {user.name}')
        challenge_view = RFIChallengeView(challenger, user)
        challenge_message = await ctx.send(
            f"{user.mention}, you have been challenged by {challenger.mention} to a Roll for Initiative! Ready your die.",
            view=challenge_view
        )
        challenge_view.message = challenge_message
    
    @commands.command(name='rps', help='Challenges another user to a game of Rock, Paper, Scissors. Example: !rps @sed')
    async def rps(self, ctx: commands.Context, challenged: discord.Member):
        """Challenges another user to a game of Rock, Paper, Scissors."""
        challenger = ctx.author
        if challenged == challenger:
            await ctx.send("You cannot challenge yourself!", ephemeral=True)
            return
        if challenged.bot:
            await ctx.send("You cannot challenge a bot!", ephemeral=True)
            return
        logger.info(f'RPS challenge initiated by {challenger.name} against {challenged.name}')
        challenge_view = RPSChallengeView(challenger, challenged)
        challenge_message = await ctx.send(
            f"{challenged.mention}, you have been challenged to a game of Rock, Paper, Scissors by {challenger.mention}!",
            view=challenge_view
        )
        challenge_view.message = challenge_message
    
    @commands.command(name='tictactoe', aliases=['ttt'], help="Challenges a user or the bot to a game of Tic-Tac-Toe. Example: !ttt @Blynnewin or !ttt bot")
    async def tictactoe(self, ctx: commands.Context, opponent: Union[discord.Member, str]):
        """Challenges another user or the bot to a game of Tic-Tac-Toe."""
        challenger = ctx.author
        if isinstance(opponent, str) and opponent.lower() == 'bot':
            challenged_user = self.bot.user
        elif isinstance(opponent, discord.Member):
            challenged_user = opponent
        else:
            await ctx.send("Invalid opponent. Please mention a user or type 'bot'.")
            return
        if challenged_user == challenger:
            await ctx.send("You cannot challenge yourself!", ephemeral=True)
            return
        logger.info(f'TicTacToe challenge initiated by {challenger.name} against {challenged_user.name}')
        if challenged_user.bot:
            game_view = TicTacToeGameView(challenger, challenged_user)
            starting_player = game_view.challenger if game_view.current_player == game_view.X else game_view.challenged
            message = await ctx.send(
                f"**Tic-Tac-Toe!**
{challenger.mention} (X) vs {challenged_user.mention} (O)
It is now {starting_player.mention}'s turn.",
                view=game_view
            )
            game_view.message = message
            if starting_player == challenged_user:
                await asyncio.sleep(1)
                await game_view.bot_move()
        else:
            challenge_view = TicTacToeChallengeView(challenger, challenged_user)
            challenge_message = await ctx.send(
                f"{challenged_user.mention}, you have been challenged to a game of Tic-Tac-Toe by {challenger.mention}!",
                view=challenge_view
            )
            challenge_view.message = challenge_message
            
    @commands.command(name='coinflip', aliases=['flip'], help='Flips a coin.')
    async def coinflip(self, ctx: commands.Context):
        """Flips a coin."""
        logger.info(f'Coinflip command used by {ctx.author}')
        await ctx.send(f'The coin landed on **{secrets.choice(["Heads", "Tails"])}**!')

# =====================================================================================================================
# 4. SETUP FUNCTION
# =====================================================================================================================
async def setup(bot: commands.Bot):
    """
    Loads the Games cog.
    Args:
        bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(Games(bot))
    logger.info("Games cog loaded")
