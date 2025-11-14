import asyncio
import discord
from datetime import datetime
from discord.ext import voice_recv
from VoiceConnection import VoiceConnection
from buttons import Menu, VoiceSelect

class BotCommands:
    """Encapsulates all voice-related command logic."""

    def __init__(self, active_connections, conversation_history, available_voices, current_voice="default"):
        self.active_connections = active_connections
        self.conversation_history = conversation_history
        self.available_voices = available_voices
        self.current_voice = current_voice
        self.default_personality = "You are Dufu, a cute and friendly anime-style AI assistant in a Discord voice channel. Speak in a cheerful, energetic way like an anime character. Keep responses brief (1-2 sentences) and very engaging. You're speaking out loud, so avoid markdown formatting. Be enthusiastic and kawaii!"

    # -----------------------------
    # Helper Methods
    # -----------------------------
    async def delayed_disconnect(self, guild_id, delay=300):
        """Disconnect after delay if channel is still empty"""
        await asyncio.sleep(delay)

        if guild_id in self.active_connections:
            connection = self.active_connections[guild_id]
            if connection.voice_client.channel:
                members = [m for m in connection.voice_client.channel.members if not m.bot]
                if not members:
                    await self.leave_voice_channel(guild_id)

    async def leave_voice_channel(self, guild_id):
        """Clean up and leave voice channel"""
        if guild_id in self.active_connections:
            connection = self.active_connections[guild_id]

            await connection.cleanup()

            if connection.voice_client.is_connected():
                await connection.voice_client.disconnect()

            del self.active_connections[guild_id]
            print(f"🚪 Left voice channel in guild {guild_id}")

    # -----------------------------
    # Command Logic
    # -----------------------------
    async def join_voice(self, interaction: discord.Interaction, bot):
        """Join the user's voice channel and start AI conversation"""
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ You need to be in a voice channel first!", ephemeral=True)

        guild_id = interaction.guild.id

        if guild_id in self.active_connections:
            return await interaction.response.send_message(
                "🎙️ I'm already active in a voice channel! Use `/leave` to disconnect first.",
                ephemeral=True
            )

        voice_channel = interaction.user.voice.channel
        await interaction.response.defer()

        try:
            # Permission check
            permissions = voice_channel.permissions_for(interaction.guild.me)
            if not permissions.connect or not permissions.speak:
                return await interaction.followup.send("❌ I need permission to connect and speak in that voice channel!")

            print(f"🔗 Connecting to {voice_channel.name} in {interaction.guild.name}...")

            try:
                voice_client = await asyncio.wait_for(
                    voice_channel.connect(cls=voice_recv.VoiceRecvClient),
                    timeout=15.0
                )
            except asyncio.TimeoutError:
                return await interaction.followup.send("❌ Connection timed out. Please try again.")
            except Exception as e:
                return await interaction.followup.send(f"❌ Failed to connect: {str(e)}")

            connection = VoiceConnection(
                self.current_voice,
                guild_id,
                voice_client,
                self.conversation_history,
                interaction.client,
                self.default_personality
            )
            self.active_connections[guild_id] = connection

            await connection.start_listening()
            print(f"✅ Connected and listening in {voice_channel.name}")

            embed = discord.Embed(
                title="🎙️ Voice AI Active!",
                description=(
                    f"I'm now listening in **{voice_channel.name}**\n\n"
                    "💬 Just speak naturally and I'll respond!\n"
                    "🚪 Use `/leave` when you're done"
                ),
                color=0x00ff00
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"❌ Error in join command: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(f"❌ Error: {str(e)}")

    async def leave_voice(self, interaction: discord.Interaction):
        """Leave the voice channel and save conversation"""
        guild_id = interaction.guild.id
        if guild_id not in self.active_connections:
            return await interaction.response.send_message("❌ I'm not in a voice channel!", ephemeral=True)

        try:
            history = self.conversation_history.get(guild_id, [])
            message_count = len(history)

            await self.leave_voice_channel(guild_id)

            embed = discord.Embed(
                title="👋 Left Voice Channel",
                description=f"💾 Saved conversation with **{message_count}** messages\n📊 Use `/history` to view recent conversations",
                color=0xff9900
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"Error leaving voice channel: {e}")
            await interaction.response.send_message(f"❌ Error leaving channel: {str(e)}")

    async def show_history(self, interaction: discord.Interaction):
        """Show recent conversation history"""
        guild_id = interaction.guild.id
        history = self.conversation_history.get(guild_id, [])
        if not history:
            return await interaction.response.send_message("📝 No conversation history found.", ephemeral=True)

        embed = discord.Embed(
            title="💬 Recent Conversation History",
            color=0x0099ff,
            timestamp=datetime.now()
        )

        recent_messages = list(history)[-10:]
        history_text = ""
        for msg in recent_messages:
            timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M")
            history_text += f"**{msg['user']}** ({timestamp}): {msg['text']}\n"

        if len(history_text) > 4000:
            history_text = history_text[:4000] + "...\n*[Truncated]*"

        embed.description = history_text or "No recent messages"
        embed.set_footer(text=f"Total messages: {len(history)}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def show_status(self, interaction: discord.Interaction):
        """Show current voice connection status"""
        guild_id = interaction.guild.id
        embed = discord.Embed(title="🤖 Voice Status", color=0x0099ff)

        if guild_id in self.active_connections:
            connection = self.active_connections[guild_id]
            channel = connection.voice_client.channel

            embed.add_field(
                name="📡 Connection Status",
                value=f"✅ Connected to **{channel.name}**\n"
                      f"🎧 Listening: {'Yes' if connection.is_listening else 'No'}\n"
                      f"👥 Users in channel: {len([m for m in channel.members if not m.bot])}",
                inline=False
            )

            if connection.stt_connections:
                users = ", ".join([f"<@{uid}>" for uid in connection.stt_connections.keys()])
                embed.add_field(name="🎙️ Active Speakers", value=users, inline=False)

            history = self.conversation_history.get(guild_id, [])
            if history:
                embed.add_field(
                    name="💬 Conversation Stats",
                    value=f"Messages: {len(history)}\n"
                          f"Last activity: <t:{int(datetime.fromisoformat(history[-1]['timestamp']).timestamp())}:R>",
                    inline=False
                )
        else:
            embed.add_field(
                name="📡 Connection Status",
                value="❌ Not connected to any voice channel\nUse `/vc` to join your voice channel",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def change_voice(self, interaction: discord.Interaction, voice: str = None):
        """Change TTS voice or show a selector UI."""
        # Direct set if valid key provided
        if voice:
            key = str(voice).lower()
            if key in self.available_voices:
                self.current_voice = key
                
                return
            else:
                info = f"❌ Unknown voice '{voice}'. Choose from the menu below:"
        else:
            info = "Select a TTS voice from the menu below:"

        # Show dropdown selector
        view = discord.ui.View(timeout=120)
        view.add_item(VoiceSelect(self, self.available_voices))
        try:
            if interaction.response.is_done():
                await interaction.followup.send(info, view=view, ephemeral=True)
            else:
                await interaction.response.send_message(info, view=view, ephemeral=True)
        except Exception as e:
            if interaction.response.is_done():
                await interaction.followup.send(f"❌ Failed to show selector: {e}", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ Failed to show selector: {e}", ephemeral=True)
        
        
    
    async def menu(self, interaction: discord.Interaction):
        """Show the Voice AI control menu buttons."""
        embed = discord.Embed(
            title="🎛️ Voice AI Control Panel",
            description="Use the buttons below to manage the Voice AI bot.",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Use these buttons to control the voice system.")
        
        view = Menu(self, interaction.client)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    

    async def set_personality(self, interaction: discord.Interaction, prompt: str):
        guild = interaction.guild
        guild_id = guild.id if guild else None

        prompt = str(prompt).strip()
        if not prompt:
            try:
                await interaction.response.send_message("❌ Empty prompt provided.", ephemeral=True)
            except Exception:
                if interaction.response.is_done():
                    await interaction.followup.send("❌ Empty prompt provided.", ephemeral=True)
            return

        # If there's an active connection for this guild, update it directly
        if guild_id and guild_id in self.active_connections:
            connection = self.active_connections[guild_id]
            connection.personality_prompt = prompt

            # record system message in history
            self.conversation_history[guild_id].append({
                "user": "System",
                "text": f"Personality changed to: {prompt}",
                "timestamp": datetime.now().isoformat()
            })

            msg = f"✅ Prompt:\n'{prompt}'\nupdated for the active call and added to conversation history."
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(msg, ephemeral=True)
                else:
                    await interaction.response.send_message(msg, ephemeral=True)
            except Exception:
                pass
            return

        # No active connection: save as default for future sessions (on this handler)
        self.default_personality = prompt
        msg = f"✅ Prompt:\n'{prompt}'\nsaved as the default for future voice sessions."

        try:
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except Exception:
            pass
