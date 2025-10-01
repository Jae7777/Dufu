import discord
import commands

class Buttons(discord.ui.View):
    def __init__(self, ctx, *, timeout=180):
        self.ctx = ctx
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Record",style=discord.ButtonStyle.green,emoji="🎙️") # or .success
    async def green_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        self.author = interaction.user
        await commands.start_recording(interaction)
        button.disabled=True
        await interaction.response.edit_message(view=self)
    @discord.ui.button(label="Stop",style=discord.ButtonStyle.gray,emoji="🛑") # or .danger
    async def red_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        self.author = interaction.user
        await commands.stop_recording(interaction)
        button.disabled=True
        await interaction.response.edit_message(view=self)