import discord
import asyncio
import os
import tempfile
from collections import defaultdict, deque
from datetime import datetime
import openai
from bot import active_connections, conversation_history, current_voice

openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------------------------
# Voice Command Functions
# ---------------------------
async def join_voice(interaction: discord.Interaction):
    """Join the user's voice channel"""
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message(
            "❌ You need to be in a voice channel first!", ephemeral=True
        )
        return

    channel = interaction.user.voice.channel
    guild_id = interaction.guild.id

    if guild_id in active_connections:
        await interaction.response.send_message("✅ Already connected!", ephemeral=True)
        return

    voice_client = await channel.connect()
    active_connections[guild_id] = voice_client
    await interaction.response.send_message(f"🎙️ Joined {channel.name}!", ephemeral=True)


async def leave_voice(interaction: discord.Interaction):
    """Leave the current voice channel"""
    guild_id = interaction.guild.id
    if guild_id not in active_connections:
        await interaction.response.send_message("❌ Not connected to any channel!", ephemeral=True)
        return

    voice_client = active_connections[guild_id]
    await voice_client.disconnect()
    del active_connections[guild_id]
    await interaction.response.send_message("🛑 Left the voice channel!", ephemeral=True)


async def show_history(interaction: discord.Interaction):
    """Show last 5 messages of conversation"""
    guild_id = interaction.guild.id
    history = conversation_history.get(guild_id)
    if not history or len(history) == 0:
        await interaction.response.send_message("💬 No conversation history yet.", ephemeral=True)
        return

    last_messages = list(history)[-5:]
    formatted = "\n".join(f"**{msg['user']}**: {msg['text']}" for msg in last_messages)
    await interaction.response.send_message(f"💬 Last messages:\n{formatted}", ephemeral=True)


async def show_status(interaction: discord.Interaction):
    """Show bot connection status"""
    guild_id = interaction.guild.id
    if guild_id in active_connections:
        vc = active_connections[guild_id]
        await interaction.response.send_message(f"✅ Connected to **{vc.channel.name}**", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Not connected to any voice channel", ephemeral=True)
