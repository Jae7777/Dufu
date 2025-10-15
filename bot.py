import discord
from discord.ext import commands
import os
import asyncio
import wave
import tempfile
from collections import defaultdict, deque
from datetime import datetime
from dotenv import load_dotenv
import openai
import VoiceConnection
import STTConnection
from bot_commands import BotCommands
from buttons import Buttons

load_dotenv()

# Enhanced intents for full voice functionality
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
# Note: message_content intent is privileged and must be enabled in Discord Developer Portal
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables for managing connections and conversations
active_connections = {}  # guild_id: VoiceConnection
conversation_history = defaultdict(lambda: deque(maxlen=50))  # guild_id: conversation deque

# TTS Configuration
current_voice = "nova"  # Default anime-like voice
available_voices = {
    "alloy": "🤖 Neutral (Alloy)",
    "echo": "🎭 Dramatic (Echo)", 
    "fable": "📚 Storyteller (Fable)",
    "onyx": "🎵 Deep (Onyx)",
    "nova": "🎌 Anime Girl (Nova)",
    "shimmer": "✨ Energetic (Shimmer)"
}


commands_handler = BotCommands(
    active_connections,
    conversation_history,
    available_voices,
    current_voice
)

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")



@bot.event
async def on_ready():
    print(f"🤖 {bot.user.name} is online and ready for voice interactions!")
    print(f"📋 Guilds: {len(bot.guilds)}")
    
    # List guilds for debugging
    for guild in bot.guilds:
        print(f"   - {guild.name} (ID: {guild.id})")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s) globally")
                
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice state changes"""
    # If bot is alone in a voice channel, leave after 5 minutes
    if member == bot.user:
        return
    
    # Check if bot should leave empty channels
    for guild_id, connection in list(active_connections.items()):
        if connection.voice_client.channel:
            members = [m for m in connection.voice_client.channel.members if not m.bot]
            if not members:  # No humans left
                asyncio.create_task(commands_handler.delayed_disconnect(guild_id))

@bot.tree.command(name="vc", description="Join your voice channel and start listening")
async def vc(interaction: discord.Interaction):
    await commands_handler.join_vc(interaction, bot)


@bot.tree.command(name="leave", description="Leave voice channel and save conversation")
async def leave(interaction: discord.Interaction):
    await commands_handler.leave_vc(interaction)


@bot.tree.command(name="history", description="View recent conversation history")
async def history(interaction: discord.Interaction):
    await commands_handler.show_history(interaction)


@bot.tree.command(name="voice", description="Change TTS voice")
async def voice(interaction: discord.Interaction, voice: str):
    await commands_handler.change_voice(interaction, voice)


@bot.tree.command(name="status", description="Check bot status")
async def status(interaction: discord.Interaction):
    await commands_handler.show_status(interaction)


@bot.tree.command(name="ping", description="Check if the bot is alive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! I'm alive!", ephemeral=True)

@bot.tree.command(name="menu", description="Show the Voice AI control menu.")
async def menu(interaction: discord.Interaction):
    """Slash command to display the Voice AI menu buttons."""
    embed = discord.Embed(
        title="🎛️ Voice AI Control Panel",
        description="Use the buttons below to manage the Voice AI bot.",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Use these buttons to control the voice system.")
    
    view = Buttons(commands_handler)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# Error handling
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Handle command errors gracefully"""
    if isinstance(error, discord.app_commands.CommandInvokeError):
        embed = discord.Embed(
            title="❌ Command Error",
            description=f"An error occurred: {str(error.original)}",
            color=0xff0000
        )
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        print(f"Command error in {interaction.command.name}: {error}")
    else:
        print(f"Unhandled error: {error}")

# Graceful shutdown
@bot.event
async def on_disconnect():
    """Clean up on disconnect"""
    for guild_id in list(active_connections.keys()):
        await commands_handler.leave_voice_channel(guild_id)

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ["DISCORD_TOKEN", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        # exit(1)
    
    print("🚀 Starting Discord Voice AI Bot with OpenAI Whisper...")
    bot.run(os.getenv("DISCORD_TOKEN"))