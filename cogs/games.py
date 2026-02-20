import discord
from discord import ui
from discord.ext import commands
import secrets
import logging
import asyncio
from typing import Optional, Union
from credits_system.cog import CreditsCog # Import CreditsCog
import datetime
import pytz # Import pytz for timezone awareness

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
# Slot Machine Constants
SLOT_EMOJIS = ["🍒", "🍋", "🍊", "🍇", "🍉", "⭐"] # Star is the wildcard
SLOT_ANIMATION_FRAMES = ["|", "/", "-", "\\"] # Simple animation frames

# Payouts: (emoji1, emoji2, emoji3): multiplier
SLOT_PAYOUTS = {
    # Perfect matches
    ("🍒", "🍒", "🍒"): 10.0,
    ("🍋", "🍋", "🍋"): 10.0,
    ("🍊", "🍊", "🍊"): 10.0,
    ("🍇", "🍇", "🍇"): 15.0,
    ("🍉", "🍉", "🍉"): 20.0,
    ("⭐", "⭐", "⭐"): 50.0, # Three wildcards is a big win

    # Wildcard matches (wildcard replaces one emoji)
    ("🍒", "🍒", "⭐"): 5.0,
    ("🍒", "⭐", "🍒"): 5.0,
    ("⭐", "🍒", "🍒"): 5.0,
    ("🍋", "🍋", "⭐"): 5.0,
    ("🍋", "⭐", "🍋"): 5.0,
    ("⭐", "🍋", "🍋"): 5.0,
    ("🍊", "🍊", "⭐"): 5.0,
    ("🍊", "⭐", "🍊"): 5.0,
    ("⭐", "🍊", "🍊"): 5.0,
    ("🍇", "🍇", "⭐"): 7.5,
    ("🍇", "⭐", "🍇"): 7.5,
    ("⭐", "🍇", "🍇"): 7.5,
    ("🍉", "🍉", "⭐"): 10.0,
    ("🍉", "⭐", "🍉"): 10.0,
    ("⭐", "🍉", "🍉"): 10.0,

    # Mixed matches (two wildcards) - for simplicity, treat as three wildcards for now,
    # or implement a lower payout if needed. For this task, it's implied by 3 wildcards having highest.
    # The current logic will handle (X, *, *) and (*, X, *) as a match if X = Y, and if X = * they'll be 3 wildcards.
    # So we only need to define cases where a wildcard replaces ONE specific emoji type.
    # Note: A match like (🍒, ⭐, 🍋) would only pay if the 'matching 3 emojis' rule implies 'at least two specific emojis + wildcard'
    # For now, we assume (A, B, C) where A or B or C can be wildcard.
    # If two are wildcards, e.g. (🍒, ⭐, ⭐), this is implicitly covered by checking for "any two symbols + a wildcard".
    # Since we're checking for "3 of a kind" or "2 of a kind + wildcard", these are sufficient.
}
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
            content=f"""**Rock, Paper, Scissors!**
{self.challenger.mention} vs {self.challenged.mention}
Make your choice!""",
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
    def __init__(self, challenger: discord.Member, challenged: discord.Member, bet_amount: int = 0, credits_cog: Optional[CreditsCog] = None):
        """
        Initializes the RFIChallengeView.

        Args:
            challenger (discord.Member): The user who initiated the challenge.
            challenged (discord.Member): The user who was challenged.
            bet_amount (int): The amount of credits being bet.
            credits_cog (Optional[CreditsCog]): The credits cog instance for credit operations.
        """
        super().__init__(timeout=180.0)
        self.challenger = challenger
        self.challenged = challenged
        self.message = None
        self.bet_amount = bet_amount
        self.credits_cog = credits_cog

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
            bet_message = ""
            if self.bet_amount > 0:
                bet_message = f" (Bet of {self.bet_amount} credits was not placed.)"
            await self.message.edit(content=f"Challenge from {self.challenger.mention} to {self.challenged.mention} timed out.{bet_message}", view=None)

    @ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: ui.Button):
        """Callback for the accept button."""
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message("Only the challenged user can accept this challenge.", ephemeral=True)
            return
        
        logger.info(f'{self.challenged.name} accepted RFI challenge from {self.challenger.name}')
        
        # Initial response to update the message, then send results
        await interaction.response.edit_message(
            content=f'{self.challenged.mention} accepted the challenge! Rolling for initiative...', 
            view=None
        )

        # RFI logic
        challenger_roll = secrets.randbelow(20) + 1
        challenged_roll = secrets.randbelow(20) + 1

        channel = interaction.channel
        result_message = ""
        result_message += f'{self.challenger.mention} rolled a {challenger_roll}\n'
        result_message += f'{self.challenged.mention} rolled a {challenged_roll}\n'

        winner = None
        loser = None
        if challenger_roll > challenged_roll:
            winner = self.challenger
            loser = self.challenged
            result_message += f'{self.challenger.mention} wins the RFI challenge! 🎉'
        elif challenger_roll < challenged_roll:
            winner = self.challenged
            loser = self.challenger
            result_message += f'{self.challenged.mention} wins the RFI challenge! 🎉'
        else:
            result_message += "It's a tie! 🤝"
        
        # Handle betting
        if self.bet_amount > 0 and self.credits_cog:
            if winner and loser: # If there was a clear winner/loser
                winner_id = str(winner.id)
                loser_id = str(loser.id)
                guild_id = str(channel.guild.id) # Guild context from the channel interaction

                # Perform the transfer
                subtract_success = self.credits_cog.subtract_credits(loser_id, guild_id, self.bet_amount, "rfi_bet_loss")
                add_success = self.credits_cog.add_credits(winner_id, guild_id, self.bet_amount, "rfi_bet_win")

                if subtract_success and add_success:
                    result_message += f"💰 {winner.mention} won {self.bet_amount} credits from {loser.mention}!"
                else:
                    # This case should ideally not happen if initial credit check passed,
                    # but good to have a fallback.
                    logger.error(f"Failed to transfer RFI bet credits. Winner: {winner_id}, Loser: {loser_id}, Amount: {self.bet_amount}")
                    result_message += f"\n❌ An error occurred during credit transfer for the bet."
            else: # It was a tie, return credits
                result_message += f"🤝 It's a tie! Bet of {self.bet_amount} credits returned to both players."

        await channel.send(result_message)
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
                content=f"{self.challenged.mention} denied the challenge from {self.challenged.mention}.",
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
        save_message = f"""{self.user.display_name} rolled a {roll} to save..."""
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

# --- Coinflip Challenge Classes ---
class CoinflipGameView(ui.View):
    def __init__(self, challenger: discord.Member, challenged: discord.Member, bet_amount: int, credits_cog: Optional[CreditsCog] = None):
        super().__init__(timeout=180.0)
        self.challenger = challenger
        self.challenged = challenged
        self.bet_amount = min(bet_amount, 50) # Cap bet at 50
        self.credits_cog = credits_cog
        self.message = None
        self.chosen_side = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.challenged:
            await interaction.response.send_message("This is not your coinflip to choose for!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        if self.message:
            for item in self.children:
                item.disabled = True
            await self.message.edit(content=f"Coinflip challenge from {self.challenger.mention} to {self.challenged.mention} timed out. No choice was made.", view=self)

    @ui.button(label="Heads", style=discord.ButtonStyle.primary, emoji="🪙")
    async def choose_heads(self, interaction: discord.Interaction, button: ui.Button):
        self.chosen_side = "Heads"
        await self._process_flip(interaction)

    @ui.button(label="Tails", style=discord.ButtonStyle.primary, emoji="🪙")
    async def choose_tails(self, interaction: discord.Interaction, button: ui.Button):
        self.chosen_side = "Tails"
        await self._process_flip(interaction)

    async def _process_flip(self, interaction: discord.Interaction):
        self.clear_items() # Remove buttons after selection
        
        await interaction.response.edit_message(content=f"{self.challenged.mention} chose **{self.chosen_side}**! Flipping the coin...", view=self)
        
        await asyncio.sleep(2) # Simulate coin flip time

        coin_result = secrets.choice(["Heads", "Tails"])
        result_message = f"The coin landed on **{coin_result}**!\n"
        result_message += f"{self.challenged.mention} chose **{self.chosen_side}**.\n" # Added line

        if self.chosen_side == coin_result:
            result_message += f"🎉 {self.challenged.mention} guessed correctly!"
            if self.credits_cog and self.bet_amount > 0:
                user_id = str(self.challenged.id)
                guild_id = str(interaction.guild_id)
                credits_success = self.credits_cog.add_credits(user_id, guild_id, self.bet_amount, "coinflip_win")
                if credits_success:
                    result_message += f"💰 {self.challenged.mention} won {self.bet_amount} credits!"
                else:
                    logger.error(f"Failed to award {self.bet_amount} credits to coinflip winner {self.challenged.name}.")
                    result_message += f"❌ An error occurred while awarding credits to {self.challenged.mention}."
        else:
            result_message += f"😔 {self.challenged.mention} guessed incorrectly."
        
        if self.message:
            await self.message.edit(content=result_message, view=self)
        self.stop()


class CoinflipChallengeView(ui.View):
    def __init__(self, challenger: discord.Member, challenged: discord.Member, bet_amount: int, credits_cog: Optional[CreditsCog] = None):
        super().__init__(timeout=180.0)
        self.challenger = challenger
        self.challenged = challenged
        self.bet_amount = bet_amount
        self.credits_cog = credits_cog
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.challenged:
            await interaction.response.send_message("This is not your challenge to accept or deny.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        if self.message:
            await self.message.edit(content=f"Coinflip challenge from {self.challenger.mention} to {self.challenged.mention} timed out.", view=None)

    @ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: ui.Button):
        logger.info(f'{self.challenged.name} accepted Coinflip challenge from {self.challenger.name}')
        game_view = CoinflipGameView(self.challenger, self.challenged, self.bet_amount, self.credits_cog)
        
        initial_message = f"**Coinflip Challenge!**{self.challenger.mention} challenged {self.challenged.mention}."
        if self.bet_amount > 0:
            initial_message += f"The winner will receive {self.bet_amount} credits."
        initial_message += f"{self.challenged.mention}, choose your side!"

        await interaction.response.edit_message(
            content=initial_message,
            view=game_view
        )
        game_view.message = await interaction.original_response()
        self.stop()

    @ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: ui.Button):
        logger.info(f'{self.challenged.name} denied Coinflip challenge from {self.challenger.name}')
        await interaction.response.edit_message(
            content=f"{self.challenged.mention} denied the coinflip challenge from {self.challenger.mention}.",
            view=None
        )
        self.stop()

# =====================================================================================================================
# 3. MAIN COG CLASS
# =====================================================================================================================

class Games(commands.Cog):
    """A cog for game-related commands."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.credits_cog: Optional[CreditsCog] = None # Initialize credits_cog
        self.last_rfi_reward_time = {} # {user_id: datetime.datetime}
        self.slots_lock = asyncio.Lock()
        self.active_slots_users: set[str] = set()  # user_id strings with active slots
        self.active_slots_count = 0  # total active slots games across all users
        logger.info("Games cog initialized")
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot is fully ready and all cogs are loaded."""
        self.credits_cog = self.bot.get_cog("Credits")
        if self.credits_cog:
            logger.info("CreditsCog successfully retrieved in Games cog.")
        else:
            logger.warning("CreditsCog not found. Credit rewards for RFI will be unavailable.")
    
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
            await ctx.send(f"""Results: {results}
Total: {sum(results)}""")
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
        await ctx.send(f"""{ctx.author.display_name} asked: "{question}"
🎱 Answer: {response}""")
    
    @commands.command(name='rfi', help='Rolls a d20 to determine success or failure.')
    async def rfi(self, ctx: commands.Context):
        """Rolls a d20 to determine success or failure."""
        logger.info(f'RFI command used by {ctx.author}')
        roll = secrets.randbelow(20) + 1

        credits_awarded = 0
        reason = "rfi_roll" # Default reason

        # Determine the outcome based on the roll
        if roll == 1:
            response_list = RFI_CRITICAL_FAILURE
            reason = "rfi_critical_failure" # Specific reason for critical failure
        elif roll < 10: # Rolls 2-9
            response_list = RFI_FAILURE
            reason = "rfi_failure" # Specific reason for failure
        elif roll < 20: # Rolls 10-19
            response_list = RFI_SUCCESS
            credits_awarded = 100 # Award 10 credits for success
            reason = "rfi_success" # Specific reason for success
        else:  # roll == 20 (Critical Success)
            response_list = RFI_CRITICAL_SUCCESS
            credits_awarded = 1000 # Award 250 credits for critical success
            reason = "rfi_critical_success" # Specific reason for critical success

        # Construct the message
        message = (
            f'{ctx.author.display_name} rolled a {roll}\n'
            f'{ctx.author.display_name} {secrets.choice(response_list)}\n'
        )

        # Award credits if applicable
        if self.credits_cog and credits_awarded > 0:
            user_id = str(ctx.author.id)
            server_id = str(ctx.guild.id)
            
            # Define the timezone for GMT-7 (America/Denver)
            try:
                denver_tz = pytz.timezone('America/Denver') 
            except pytz.exceptions.UnknownTimeZoneError:
                logger.error("America/Denver timezone not found. Using UTC as fallback for RFI reward reset.")
                denver_tz = pytz.utc
            
            now_local_tz = datetime.datetime.now(denver_tz)
            today_local_tz = now_local_tz.date() # Get just the date part

            last_reward_date = self.last_rfi_reward_time.get(user_id)
            
            # Check if credits have already been awarded today (local timezone)
            if last_reward_date and last_reward_date == today_local_tz:
                # Credits already awarded today, do not add credit message
                pass 
            else:
                # Credits not yet awarded today, proceed to award
                credits_success = self.credits_cog.add_credits(user_id, server_id, credits_awarded, reason)
                if credits_success:
                    message += f"💰 You earned {credits_awarded} credits!"
                    self.last_rfi_reward_time[user_id] = today_local_tz # Store only the date
                else:
                    message += "❌ Failed to award credits."

        # Handle the special case for critical failure, otherwise send normally
        if roll == 1:
            save_view = SaveRollView(ctx.author)
            sent_message = await ctx.send(message, view=save_view)
            save_view.message = sent_message
        else:
            await ctx.send(message)
    
    @commands.command(name='challenge', aliases=['ch'], help='Challenges another user to a d20 roll-off. Example: !challenge @Radar or !challenge @Radar 50')
    async def rfi_challenge(self, ctx: commands.Context, user_str: str, bet: Optional[int] = None):
        """Challenges another user to a d20 roll-off."""
        try:
            user = await commands.MemberConverter().convert(ctx, user_str.strip())
        except commands.MemberNotFound:
            await ctx.send(f'Member "{user_str}" not found. Please make sure you @mention them correctly or provide a valid ID/username.', ephemeral=True)
            return
        
        challenger = ctx.author
        if user == challenger:
            await ctx.send('You cannot challenge yourself!', ephemeral=True)
            return

        if user.bot:
            await ctx.send("You cannot challenge a bot!", ephemeral=True)
            return

        bet_amount = 0
        if bet is not None:
            if bet <= 0:
                await ctx.send("Bet amount must be a positive number.", ephemeral=True)
                return
            bet_amount = bet

            if not self.credits_cog:
                await ctx.send("Credit system is not available, cannot place bets.", ephemeral=True)
                return

            challenger_credits = self.credits_cog.get_credits(str(challenger.id), str(ctx.guild.id))
            if challenger_credits is None or challenger_credits < bet_amount:
                await ctx.send(f"{challenger.mention}, you do not have enough credits to bet {bet_amount}. Your current balance: {challenger_credits if challenger_credits is not None else 0}.", ephemeral=True)
                return

            challenged_credits = self.credits_cog.get_credits(str(user.id), str(ctx.guild.id))
            if challenged_credits is None or challenged_credits < bet_amount:
                await ctx.send(f"{user.mention} does not have enough credits to accept a bet of {bet_amount}.", ephemeral=True)
                return

        logger.info(f'RFI challenge command used by {challenger.name} to challenge {user.name} with bet: {bet_amount}')

        challenge_view = RFIChallengeView(challenger, user, bet_amount, self.credits_cog)
        challenge_message_content = f"{user.mention}, you have been challenged by {challenger.mention} to a Roll for Initiative!"
        if bet_amount > 0:
            challenge_message_content += f" The stakes are {bet_amount} credits!"
        challenge_message_content += " Ready your die."

        challenge_message = await ctx.send(
            challenge_message_content,
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
                f"""**Tic-Tac-Toe!**
{challenger.mention} (X) vs {challenged_user.mention} (O)
It is now {starting_player.mention}'s turn.""",
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

    @commands.command(name='coinflipchallenge', aliases=['cfc'], help='Challenges another user to a coinflip. Winner gets credits (max 50). Example: !cfc @User 25')
    async def coinflipchallenge(self, ctx: commands.Context, challenged: discord.Member, coins: Optional[int] = 0):
        """Challenges another user to a coinflip."""
        challenger = ctx.author

        if challenged == challenger:
            await ctx.send("You cannot challenge yourself!", ephemeral=True)
            return

        if challenged.bot:
            await ctx.send("You cannot challenge a bot!", ephemeral=True)
            return

        bet_amount = min(coins, 50) # Cap the bet at 50

        if bet_amount <= 0:
            await ctx.send("You must bet at least 1 credit for a challenge, up to a maximum of 50 credits.", ephemeral=True)
            return

        if not self.credits_cog:
            await ctx.send("Credit system is not available, cannot run coinflip challenges with credits.", ephemeral=True)
            return
        
        # We don't need to check challenged's credits here because they only win, not lose.

        logger.info(f'Coinflip challenge initiated by {challenger.name} against {challenged.name} for {bet_amount} credits.')
        
        challenge_view = CoinflipChallengeView(challenger, challenged, bet_amount, self.credits_cog)
        
        challenge_message_content = f"{challenged.mention}, {challenger.mention} has challenged you to a coinflip!"
        if bet_amount > 0:
            challenge_message_content += f" If you guess correctly, you win {bet_amount} credits!"
        challenge_message_content += " Do you accept?"

        challenge_message = await ctx.send(
            challenge_message_content,
            view=challenge_view
        )
        challenge_view.message = challenge_message
    @commands.command(name='slots', help='Play a slot machine! Bet between 5 and 1000 credits (default: 5). Example: !slots 50')
    async def slots(self, ctx: commands.Context, bet: int = 5):
        """Plays a slot machine game with a given bet."""
        player = ctx.author

        def _get_reels_display(reels: list[str]) -> str:
            """Formats the reels for display."""
            return f"| {' | '.join(reels)} |"

        def _check_win(reels: list[str]) -> float:
            """
            Checks for winning combinations and returns the multiplier.
            The `reels` list contains 3 emojis.
            """
            # Check for exact matches (including three wildcards)
            reels_tuple = tuple(reels)
            if reels_tuple in SLOT_PAYOUTS:
                return SLOT_PAYOUTS[reels_tuple]

            # Handle cases with wildcards that form a match
            wildcard_count = reels.count("⭐")
            non_wildcards = [e for e in reels if e != "⭐"]

            # Case: Two wildcards (e.g., A, ⭐, ⭐)
            if wildcard_count == 2:
                if len(non_wildcards) == 1: # One non-wildcard emoji, two wildcards
                    base_emoji = non_wildcards[0]
                    # Effectively forms three of the base_emoji, but with wildcards, so pays less
                    # Check for (base_emoji, base_emoji, wildcard) payouts, as it should be equivalent
                    # to having two of the base emoji and one wildcard.
                    potential_payout_keys = [
                        (base_emoji, base_emoji, "⭐"),
                        (base_emoji, "⭐", base_emoji),
                        ("⭐", base_emoji, base_emoji)
                    ]
                    for key in SLOT_PAYOUTS: # Iterate through all keys in SLOT_PAYOUTS
                        # If a key matches one of our potential keys, and it's a wildcard payout
                        # for the base_emoji, then return that multiplier.
                        if key in potential_payout_keys:
                            return SLOT_PAYOUTS[key]
            
            # Case: One wildcard (e.g., A, A, ⭐ or A, B, ⭐ where A != B)
            # The A, A, ⭐ permutations are already handled by direct `SLOT_PAYOUTS` lookup
            # due to all permutations being listed. If A, B, ⭐ where A != B, it's not a win.

            return 0.0 # No win

        if not self.credits_cog:
            await ctx.send("Credit system is not available, cannot play slots.", ephemeral=True)
            return

        if not (5 <= bet <= 1000):
            await ctx.send("You must bet between 5 and 1000 credits.", ephemeral=True)
            return
        
        user_id = str(player.id)
        guild_id = str(ctx.guild.id)
        current_credits = self.credits_cog.get_credits(user_id, guild_id)

        if current_credits is None or current_credits < bet:
            await ctx.send(f"{player.mention}, you do not have enough credits to bet {bet}. Your current balance: {current_credits if current_credits is not None else 0}.", ephemeral=True)
            return

        # Concurrency checks: allow one slots game per user and up to 2 total concurrently
        user_id_str = user_id
        async with self.slots_lock:
            if user_id_str in self.active_slots_users:
                await ctx.send(f"{player.mention}, you already have a slots game running.", ephemeral=True)
                return
            if self.active_slots_count >= 2:
                await ctx.send("There are already 2 slots games running. Please wait.", ephemeral=True)
                return
            # Reserve a slot for this user
            self.active_slots_users.add(user_id_str)
            self.active_slots_count += 1

        logger.info(f'Slots game reserved for {player.name} with a bet of {bet} credits.')

        # Deduct bet (if this fails, release the reservation)
        if not self.credits_cog.subtract_credits(user_id, guild_id, bet, "slot_machine_bet"):
            async with self.slots_lock:
                self.active_slots_users.discard(user_id_str)
                if self.active_slots_count > 0:
                    self.active_slots_count -= 1
            await ctx.send(f"{player.mention}, you do not have enough credits to place a bet of {bet}.")
            return
        
        # Initial message before animation
        initial_message_content = f"{player.mention} bets {bet} credits on the slots!"
        reels = ["?", "?", "?"] # Initial state
        message = await ctx.send(initial_message_content + "\n" + _get_reels_display(reels))

        animation_duration = 4  # seconds for the entire animation
        frames_per_second = 2

        animation_duration_per_reel = animation_duration / 3  # Each reel animates for ~1 second
        total_frames_per_reel = int(animation_duration_per_reel * frames_per_second)

        # Ensure at least one frame per reel to avoid zero-frame animations
        if total_frames_per_reel < 1:
            total_frames_per_reel = 1

        total_frames = total_frames_per_reel * 3
        final_reels = [secrets.choice(SLOT_EMOJIS) for _ in range(3)]

        # Single loop: update all three reels and the spinner once per frame
        started = True
        try:
            for i in range(total_frames):
                # Determine current symbol for each reel: spinning until its stop frame
                if i < total_frames_per_reel:
                    r1 = secrets.choice(SLOT_EMOJIS)
                else:
                    r1 = final_reels[0]

                if i < total_frames_per_reel * 2:
                    r2 = secrets.choice(SLOT_EMOJIS)
                else:
                    r2 = final_reels[1]

                if i < total_frames_per_reel * 3:
                    r3 = secrets.choice(SLOT_EMOJIS)
                else:
                    r3 = final_reels[2]

                animation_char = SLOT_ANIMATION_FRAMES[i % len(SLOT_ANIMATION_FRAMES)]
                current_reels = [r1, r2, r3]
                animation_frame_content = initial_message_content + f"\n{_get_reels_display(current_reels)} {animation_char}"
                await message.edit(content=animation_frame_content)
                await asyncio.sleep(1 / frames_per_second)

            # Final display with settled reels
            await message.edit(content=initial_message_content + f"\n{_get_reels_display(final_reels)}")
            await asyncio.sleep(0.2)  # Short pause after last reel

            # Final spin result and payout calculation
            multiplier = _check_win(final_reels)

            result_message = initial_message_content + "\n"
            result_message += f"**{_get_reels_display(final_reels)}**\n\n"

            if multiplier > 0:
                winnings = int(bet * multiplier)
                self.credits_cog.add_credits(user_id, guild_id, winnings, "slot_machine_win")
                result_message += f"🎉 **{player.mention} wins {winnings} credits!** (Multiplier: {multiplier:.1f}x)"
            else:
                result_message += f"😔 {player.mention} didn't win this time. Better luck next spin!"

            await message.edit(content=result_message)
        finally:
            # Release reservation for this user's slots game
            async with self.slots_lock:
                self.active_slots_users.discard(user_id_str)
                if self.active_slots_count > 0:
                    self.active_slots_count -= 1

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
