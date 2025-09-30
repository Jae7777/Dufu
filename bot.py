import discord
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True

bot = discord.Bot(intents=intents)

async def finished_callback(sink, *args):
    """Called when recording finishes."""
    print(f"Recording finished. Callback args: {args}")
    print(f"Audio data items: {list(sink.audio_data.keys())}")
    print(f"Number of users recorded: {len(sink.audio_data)}")
    
    if not sink.audio_data:
        print("WARNING: No audio data was captured!")
        return
    
    # Save each user's audio to a separate file
    for user_id, audio in sink.audio_data.items():
        filename = f"{user_id}.{sink.encoding}"
        print(f"Attempting to save {filename}...")
        print(f"Current working directory: {os.getcwd()}")
        
        with open(filename, "wb") as f:
            audio_bytes = audio.file.getvalue()
            f.write(audio_bytes)
            print(f"Saved audio for user {user_id} to {filename} ({len(audio_bytes)} bytes)")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.slash_command(name="record", description="Join and start recording")
async def record(ctx: discord.ApplicationContext):
    """Starts recording audio."""
    if not ctx.author.voice:
        return await ctx.respond("You need to be in a voice channel.", ephemeral=True)
    
    voice = ctx.author.voice.channel
    
    await ctx.defer()
    
    try:
        # Check permissions first
        print(f"Bot permissions in {voice.name}: {voice.permissions_for(ctx.guild.me)}")
        if not voice.permissions_for(ctx.guild.me).connect:
            return await ctx.followup.send("I don't have permission to connect to that voice channel!")
        
        # Connect to voice channel with timeout
        print(f"Attempting to connect to {voice.name}...")
        try:
            vc = await asyncio.wait_for(voice.connect(), timeout=10.0)
        except asyncio.TimeoutError:
            return await ctx.followup.send("Connection timed out. Please check bot permissions and try again.")
        
        print(f"Connected successfully. Voice client: {vc}")
        print(f"Is connected: {vc.is_connected()}")
        
        # Use the built-in WaveSink
        sink = discord.sinks.WaveSink()
        print(f"Created sink: {sink}")
        
        # Start recording (callback is positional, not keyword)
        print("Starting recording...")
        vc.start_recording(sink, finished_callback)
        print("Recording started!")
        
        await ctx.followup.send("🎙️ Recording! Use `/stop` to finish.")
    except Exception as e:
        print(f"Error in record command: {e}")
        import traceback
        traceback.print_exc()
        await ctx.followup.send(f"Error: {e}")

@bot.slash_command(name="stop", description="Stop recording")
async def stop(ctx: discord.ApplicationContext):
    """Stops recording."""
    if ctx.voice_client:
        await ctx.respond("Stopping recording...")
        ctx.voice_client.stop_recording()
        await ctx.voice_client.disconnect()
    else:
        await ctx.respond("Not recording.", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))