import asyncio
import discord
from dotenv import load_dotenv
import os

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


async def start_recording(source):
    """
    Starts recording audio from a ctx or interaction.
    Works with both slash commands and button clicks.
    """
    # takes values from interaction and ctx
    user = getattr(source, "user", None) or getattr(source, "author", None)
    guild = getattr(source, "guild", None)

    if not user or not user.voice:
        if hasattr(source, "response"):
            return await source.response.send_message("❌ You need to be in a voice channel.", ephemeral=True)
        else:
            return await source.respond("❌ You need to be in a voice channel.", ephemeral=True)

    voice_channel = user.voice.channel

    # Defer depending on context type
    if hasattr(source, "defer"):
        await source.defer()
    elif hasattr(source, "response"):
        await source.response.defer()

    try:
        # Check permissions
        me = guild.me if guild else None
        if me and not voice_channel.permissions_for(me).connect:
            msg = "🚫 I don't have permission to connect to that voice channel!"
            if hasattr(source, "followup"):
                return await source.followup.send(msg)
            elif hasattr(source, "response"):
                return await source.response.send_message(msg)
            else:
                return

        print(f"Attempting to connect to {voice_channel.name}...")
        try:
            vc = await asyncio.wait_for(voice_channel.connect(), timeout=10.0)
        except asyncio.TimeoutError:
            msg = "⏰ Connection timed out. Please check bot permissions and try again."
            if hasattr(source, "followup"):
                return await source.followup.send(msg)
            elif hasattr(source, "response"):
                return await source.response.send_message(msg)
            else:
                return

        print(f"Connected successfully to {voice_channel.name}")

        # 🎙️ Create sink
        sink = discord.sinks.WaveSink()
        print(f"Created sink: {sink}")

        # 🔴 Start recording
        vc.start_recording(sink, finished_callback)
        print("Recording started!")

        # 💬 Notify user
        msg = "🎙️ Recording started! Use `/stop` or the Stop button to finish."
        if hasattr(source, "followup"):
            await source.followup.send(msg)
        elif hasattr(source, "response"):
            await source.response.send_message(msg)
        else:
            await source.send(msg)

    except Exception as e:
        print(f"Error in start_recording: {e}")
        import traceback
        traceback.print_exc()
        msg = f"⚠️ Error: {e}"
        if hasattr(source, "followup"):
            await source.followup.send(msg)
        elif hasattr(source, "response"):
            await source.response.send_message(msg)
        else:
            await source.send(msg)
            
async def stop_recording(ctx: discord.ApplicationContext):
    """Actually stops the recording and disconnects the bot."""
    if ctx.voice_client:
        ctx.voice_client.stop_recording()  # triggers finished_callback
        await ctx.voice_client.disconnect()
        return True
    return False