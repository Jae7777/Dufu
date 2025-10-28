import discord

class Buttons(discord.ui.View):
    """Interactive buttons for controlling the Voice AI Bot."""

    def __init__(self, commands_handler, bot, timeout=180):
        super().__init__(timeout=timeout)
        self.commands_handler = commands_handler  # <-- pass BotCommands instance
        self.bot = bot

    @discord.ui.button(label="Join Voice", style=discord.ButtonStyle.green, emoji="🎙️")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await self.commands_handler.join_voice(interaction, self.bot)
        button.disabled = False

    @discord.ui.button(label="Leave Voice", style=discord.ButtonStyle.red, emoji="🛑")
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await self.commands_handler.leave_voice(interaction)
        button.disabled = False

    @discord.ui.button(label="Show History", style=discord.ButtonStyle.blurple, emoji="💬")
    async def history_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await self.commands_handler.show_history(interaction)
        button.disabled = False

    @discord.ui.button(label="Voice Status", style=discord.ButtonStyle.gray, emoji="🤖")
    async def status_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await self.commands_handler.show_status(interaction)
        button.disabled = False

