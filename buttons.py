import discord
import bot_commands as commands

class Buttons(discord.ui.View):
    """Interactive buttons for controlling the Voice AI Bot"""

    def __init__(self, ctx, *, timeout=180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.bot = ctx.bot

    @discord.ui.button(label="Join Voice", style=discord.ButtonStyle.green, emoji="🎙️")
    async def join_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await commands.join_voice(interaction)
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Leave Voice", style=discord.ButtonStyle.red, emoji="🛑")
    async def leave_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await commands.leave_voice(interaction)
        button.disabled = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Show History", style=discord.ButtonStyle.blurple, emoji="💬")
    async def history_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await commands.show_history(interaction)

    @discord.ui.button(label="Voice Status", style=discord.ButtonStyle.gray, emoji="🤖")
    async def status_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await commands.show_status(interaction)
