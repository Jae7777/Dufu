import discord

class Menu(discord.ui.View):
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


    # @discord.ui.button(label="Change Voice", style=discord.ButtonStyle.purple, emoji="🗣️")
    # async def change_voice_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     button.disabled = True
    #     await self.commands_handler.change_voice(interaction)
    #     button.disabled = False
    @discord.ui.button(label="Change Voice", style=discord.ButtonStyle.gray, emoji="🗣️")
    async def change_voice_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await self.commands_handler.change_voice(interaction)
        button.disabled = False

class VoiceSelect(discord.ui.Select):
    """Dropdown menu for selecting TTS voice."""

    def __init__(self, commands_handler, available_voices):
        options = [
            discord.SelectOption(label=label, value=key)
            for key, label in available_voices.items()
        ]
        super().__init__(placeholder="Select TTS Voice", min_values=1, max_values=1, options=options)
        self.commands_handler = commands_handler
        self.available_voices = available_voices

    async def callback(self, interaction: discord.Interaction):
        """Handle a voice selection: call BotCommands.change_voice and confirm to the user."""
        if not self.values:
            try:
                await interaction.response.send_message("No voice selected.", ephemeral=True)
            except Exception:
                if interaction.response.is_done():
                    await interaction.followup.send("No voice selected.", ephemeral=True)
            return

        selected_key = self.values[0]  # e.g. "nova", "alloy"
        friendly_name = self.available_voices.get(selected_key, selected_key)

        # Delegate to the commands handler to perform the change (keeps logic centralized)
        try:
            await self.commands_handler.change_voice(interaction, selected_key)
            msg = f"✅ TTS voice changed to: {friendly_name}"
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except Exception as e:
            err = f"❌ Failed to change voice: {e}"
            if interaction.response.is_done():
                await interaction.followup.send(err, ephemeral=True)
            else:
                await interaction.response.send_message(err, ephemeral=True)
