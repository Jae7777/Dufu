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

# In-memory store for active recordings
connections = {}

class WaveSink(Sink):
    def __init__(self, destination):
        self.destination = destination
        self.file = None

    def write(self, data, user):
        # This is our debug print. If this doesn't show up, the bot isn't receiving audio.
        print(f"Received {len(data)} bytes of audio data from user {user}.")
        
        # We receive PCM 16-bit 48kHz stereo data.
        # Initialize the wave file on the first write.
        if not self.file:
            print(f"First audio packet received. Creating file: {self.destination}")
            self.file = wave.open(self.destination, 'wb')
            self.file.setnchannels(2)  # Stereo
            self.file.setsampwidth(2)  # 16-bit
            self.file.setframerate(48000)
        self.file.writeframes(data)

    def cleanup(self):
        # This is called when the recording is stopped.
        if self.file:
            self.file.close()
            self.file = None

@bot.command()
async def join(ctx):
    """Joins a voice channel and starts recording to output.wav."""
    if not ctx.message.author.voice:
        await ctx.send(f'{ctx.message.author.name} is not connected to a voice channel.')
        return

    channel = ctx.message.author.voice.channel
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)

    # By setting self_deaf=True, we tell Discord we will not be speaking.
    # This is a good practice for listening bots.
    vc = await channel.connect(self_deaf=True)

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
