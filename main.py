import discord
import os
from dotenv import load_dotenv
import asyncio
from discord.ext import commands
from discord import opus
from discord.sinks import Sink
import wave

load_dotenv()

# Safely ensure Opus is loaded (required for voice receive)
try:
    if not opus.is_loaded():
        opus.load_opus('libopus.so.0')
except Exception as e:
    print(f"Warning: Could not load Opus library: {e}")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command()
async def join(ctx):
    """Joins a voice channel and starts recording to output.wav."""
    if not ctx.message.author.voice:
        await ctx.send(f'{ctx.message.author.name} is not connected to a voice channel.')
        return

    channel = ctx.message.author.voice.channel
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)

    vc = await channel.connect()

    # The file where the audio will be saved.
    output_file = 'output.wav'

    sink = WaveSink(output_file)

    print("Starting recording...")
    vc.start_recording(
        sink,
        lambda e: print(f"Error in recording: {e}" if e else "Recording finished."),
    )
    
    connections[ctx.guild.id] = vc
    await ctx.send(f"Joined and now recording to `{output_file}`. Use `$stop` to finish.")

@bot.command()
async def stop(ctx):
    """Stops recording and leaves the voice channel."""
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        
        # Stop the recording. This will trigger the sink's cleanup() method.
        vc.stop_recording()
        
        await vc.disconnect()
        del connections[ctx.guild.id]
        await ctx.send("Stopped recording and left the channel. Your file is ready.")
    else:
        await ctx.send("The bot is not currently recording.")

bot.run(os.getenv('DISCORD_TOKEN'))
