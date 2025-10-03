import discord
from discord.ext import commands
import os
import asyncio
import io
import wave
import tempfile
from collections import defaultdict, deque
from datetime import datetime
from discord.ext import voice_recv
from dotenv import load_dotenv
import openai

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

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

class VoiceConnection:
    """Manages voice connection, STT, and TTS for a guild"""
    
    def __init__(self, guild_id, voice_client):
        self.guild_id = guild_id
        self.voice_client = voice_client
        self.stt_connections = {}  # user_id: STTConnection
        self.is_listening = False
        
    async def start_listening(self):
        """Start listening to voice channel"""
        if not self.is_listening:
            self.voice_client.listen(voice_recv.BasicSink(self.process_voice_packet))
            self.is_listening = True
            print(f"Started listening in guild {self.guild_id}")
    
    def process_voice_packet(self, user, data):
        """Process incoming voice packets"""
        if user.bot:  # Ignore bot's own voice
            return
            
        # Get or create STT connection for this user
        if user.id not in self.stt_connections:
            self.stt_connections[user.id] = STTConnection(user, self.on_speech_recognized, bot.loop)
        
        # Send audio data to STT
        self.stt_connections[user.id].process_audio(data.pcm)
    
    async def on_speech_recognized(self, user, text):
        """Handle recognized speech"""
        if not text.strip():
            return
            
        print(f"{user.display_name}: {text}")
        
        # Add to conversation history
        conversation_history[self.guild_id].append({
            "user": user.display_name,
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate response
        response = await self.generate_response(text, user)
        
        if response:
            # Add bot response to history
            conversation_history[self.guild_id].append({
                "user": "Bot",
                "text": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Speak the response
            await self.speak_response(response)
    
    async def generate_response(self, text, user):
        """Generate AI response using OpenAI GPT"""
        try:
            # Build context from conversation history
            messages = [
                {"role": "system", "content": "You are Dufu, a cute and friendly anime-style AI assistant in a Discord voice channel. Speak in a cheerful, energetic way like an anime character. Use casual expressions like 'quack~' occasionally. Keep responses brief (1-2 sentences) and very engaging. You're speaking out loud, so avoid markdown formatting. Be enthusiastic and kawaii!"}
            ]
            
            # Add recent conversation history
            for msg in list(conversation_history[self.guild_id])[-10:]:  # Last 10 messages
                if msg["user"] == "Bot":
                    messages.append({"role": "assistant", "content": msg["text"]})
                else:
                    messages.append({"role": "user", "content": f"{msg['user']}: {msg['text']}"})
            
            # Add current message
            messages.append({"role": "user", "content": f"{user.display_name}: {text}"})
            
            response = await asyncio.to_thread(
                openai.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
    
    async def speak_response(self, text):
        """Convert text to speech using OpenAI TTS with anime-style voice"""
        print(f"Bot response: {text}")
        
        try:
            # Generate TTS using OpenAI with selected voice
            response = await asyncio.to_thread(
                openai.audio.speech.create,
                model="tts-1",  # Use tts-1-hd for higher quality but slower generation
                voice=current_voice,  # Use the globally configured voice
                input=text,
                response_format="mp3"
            )
            
            # Get audio data
            audio_data = response.content
            print(f"Generated OpenAI TTS: {len(audio_data)} bytes")
            
            # Save to temporary file for FFmpeg
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Create FFmpeg audio source from MP3
            audio_source = discord.FFmpegPCMAudio(temp_file_path)
            
            # Stop any currently playing audio
            if self.voice_client.is_playing():
                self.voice_client.stop()
            
            # Play the TTS response with cleanup callback
            def after_playing(error):
                if error:
                    print(f"Playback error: {error}")
                else:
                    print(f"✅ Finished playing anime TTS: {text}")
                
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                    print(f"🗑️ Cleaned up TTS file")
                except Exception as cleanup_error:
                    print(f"Warning: Could not delete TTS file: {cleanup_error}")
            
            # Play the audio in the voice channel
            self.voice_client.play(audio_source, after=after_playing)
            print(f"🎌 Playing anime-style TTS in voice channel: {text}")
            
        except Exception as e:
            print(f"Error in OpenAI TTS: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: send to text channel as before
            try:
                guild = self.voice_client.guild
                text_channel = None
                
                for channel in guild.text_channels:
                    if channel.name.lower() in ['general', 'bot-testing', 'chat', 'bot']:
                        text_channel = channel
                        break
                
                if not text_channel and guild.text_channels:
                    text_channel = guild.text_channels[0]
                
                if text_channel:
                    await text_channel.send(f"🎌 **Anime Bot says:** {text}", tts=True)
                    print(f"🔊 Fallback TTS sent to #{text_channel.name}")
                    
            except Exception as fallback_error:
                print(f"Fallback TTS also failed: {fallback_error}")
                print(f"Bot response (all TTS failed): {text}")
    
    async def cleanup(self):
        """Clean up connections"""
        self.is_listening = False
        for stt_conn in self.stt_connections.values():
            stt_conn.cleanup()
        self.stt_connections.clear()

class STTConnection:
    """Handles speech-to-text for individual users"""
    
    def __init__(self, user, callback, loop):
        self.user = user
        self.callback = callback
        self.loop = loop  # Store the event loop reference
        self.audio_buffer = io.BytesIO()
        self.sample_rate = 48000  # Discord's sample rate
        self.channels = 2
        self.silence_threshold = 500  # ms of silence before processing
        self.last_audio_time = None
        self.processing_audio = False
        
    def process_audio(self, pcm_data):
        """Process incoming PCM audio data"""
        if not pcm_data:
            return
            
        # Write to buffer
        self.audio_buffer.write(pcm_data)
        self.last_audio_time = datetime.now()
        
        # Debug: Show audio data info occasionally
        buffer_size = self.audio_buffer.tell()
        if buffer_size % 32000 == 0:  # Every ~2 seconds
            print(f"Audio buffer for {self.user.display_name}: {buffer_size} bytes")
        
        # If we have enough audio and there's a pause, process it
        if not self.processing_audio and buffer_size > 48000:  # ~3 seconds of audio for better transcription
            # Schedule the async task using the stored event loop
            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(self._process_buffered_audio(), self.loop)
    
    async def _process_buffered_audio(self):
        """Process buffered audio with STT"""
        if self.processing_audio:
            return
            
        self.processing_audio = True
        
        try:
            # Get audio data
            audio_data = self.audio_buffer.getvalue()
            self.audio_buffer = io.BytesIO()  # Reset buffer
            
            print(f"Processing {len(audio_data)} bytes of audio from {self.user.display_name}")
            
            if len(audio_data) < 3200:  # Need at least ~0.1 seconds of audio (increased threshold)
                print(f"Audio too short ({len(audio_data)} bytes), skipping")
                self.processing_audio = False
                return
            
            # Convert to format suitable for Whisper STT
            audio_wav = self._convert_to_wav(audio_data)
            
            if audio_wav is None:
                print("Failed to create WAV file, skipping transcription")
                return
            
            # Use OpenAI Whisper for STT
            text = await self._whisper_stt(audio_wav)
            
            if text and len(text.strip()) > 0:
                await self.callback(self.user, text)
                
        except Exception as e:
            print(f"Error processing audio for {self.user.display_name}: {e}")
        finally:
            self.processing_audio = False
    
    def _convert_to_wav(self, pcm_data):
        """Convert PCM data to WAV format"""
        try:
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(pcm_data)
            
            wav_buffer.seek(0)
            
            # Debug: Check if WAV file was created properly
            wav_size = len(wav_buffer.getvalue())
            print(f"Created WAV file: {wav_size} bytes for user {self.user.display_name}")
            
            if wav_size < 44:  # WAV header is 44 bytes minimum
                print(f"Warning: WAV file too small ({wav_size} bytes)")
                return None
            
            wav_buffer.seek(0)
            return wav_buffer
            
        except Exception as e:
            print(f"Error creating WAV file for {self.user.display_name}: {e}")
            return None
    
    async def _whisper_stt(self, audio_wav):
        """Use OpenAI Whisper for speech-to-text"""
        try:
            if audio_wav is None:
                print("Audio WAV is None, skipping transcription")
                return None
                
            audio_wav.seek(0)
            audio_data = audio_wav.read()
            print(f"Sending {len(audio_data)} bytes to Whisper API")
            
            # Create a new BytesIO with proper file-like behavior
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"  # Give it a name with .wav extension
            audio_file.seek(0)
            
            response = await asyncio.to_thread(
                openai.audio.transcriptions.create,
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            
            result = response.strip()
            print(f"Whisper transcription: '{result}'")
            return result
            
        except Exception as e:
            print(f"Whisper STT error: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources"""
        self.audio_buffer.close()

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
        
        # Also sync to each guild for faster updates (optional)
        for guild in bot.guilds:
            try:
                guild_synced = await bot.tree.sync(guild=guild)
                print(f"✅ Synced {len(guild_synced)} command(s) to {guild.name}")
            except Exception as guild_error:
                print(f"❌ Failed to sync to {guild.name}: {guild_error}")
                
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
                asyncio.create_task(delayed_disconnect(guild_id))

async def delayed_disconnect(guild_id, delay=300):  # 5 minutes
    """Disconnect after delay if channel is still empty"""
    await asyncio.sleep(delay)
    
    if guild_id in active_connections:
        connection = active_connections[guild_id]
        if connection.voice_client.channel:
            members = [m for m in connection.voice_client.channel.members if not m.bot]
            if not members:
                await leave_voice_channel(guild_id)

@bot.tree.command(name="vc", description="Join your voice channel and start listening")
async def join_vc(interaction: discord.Interaction):
    """Join the user's voice channel and start AI conversation"""
    if not interaction.user.voice:
        return await interaction.response.send_message("❌ You need to be in a voice channel first!", ephemeral=True)
    
    if interaction.guild.id in active_connections:
        return await interaction.response.send_message("🎙️ I'm already active in a voice channel! Use `/leave` to disconnect first.", ephemeral=True)
    
    voice_channel = interaction.user.voice.channel
    
    await interaction.response.defer()
    
    try:
        # Check permissions
        permissions = voice_channel.permissions_for(interaction.guild.me)
        if not permissions.connect or not permissions.speak:
            return await interaction.followup.send("❌ I need permission to connect and speak in that voice channel!")
        
        print(f"🔗 Connecting to {voice_channel.name} in {interaction.guild.name}...")
        
        # Connect with voice_recv for receiving audio
        try:
            voice_client = await asyncio.wait_for(
                voice_channel.connect(cls=voice_recv.VoiceRecvClient),
                timeout=15.0
            )
        except asyncio.TimeoutError:
            return await interaction.followup.send("❌ Connection timed out. Please try again.")
        except Exception as e:
            return await interaction.followup.send(f"❌ Failed to connect: {str(e)}")
        
        # Create voice connection manager
        connection = VoiceConnection(interaction.guild.id, voice_client)
        active_connections[interaction.guild.id] = connection
        
        # Start listening for voice
        await connection.start_listening()
        
        print(f"✅ Connected and listening in {voice_channel.name}")
        
        embed = discord.Embed(
            title="🎙️ Voice AI Active!",
            description=f"I'm now listening in **{voice_channel.name}**\n\n"
                       "💬 Just speak naturally and I'll respond!\n"
                       "🚪 Use `/leave` when you're done",
            color=0x00ff00
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"❌ Error in join command: {e}")
        import traceback
        traceback.print_exc()
        await interaction.followup.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="leave", description="Leave voice channel and save conversation")
async def leave_vc(interaction: discord.Interaction):
    """Leave the voice channel and save conversation history"""
    guild_id = interaction.guild.id
    
    if guild_id not in active_connections:
        return await interaction.response.send_message("❌ I'm not in a voice channel!", ephemeral=True)
    
    try:
        # Get conversation summary
        history = conversation_history[guild_id]
        message_count = len(history)
        
        # Clean up connection
        await leave_voice_channel(guild_id)
        
        embed = discord.Embed(
            title="👋 Left Voice Channel",
            description=f"💾 Saved conversation with **{message_count}** messages\n"
                       "📊 Use `/history` to view recent conversations",
            color=0xff9900
        )
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        print(f"Error leaving voice channel: {e}")
        await interaction.response.send_message(f"❌ Error leaving channel: {str(e)}")

async def leave_voice_channel(guild_id):
    """Clean up and leave voice channel"""
    if guild_id in active_connections:
        connection = active_connections[guild_id]
        
        # Clean up voice connection
        await connection.cleanup()
        
        # Disconnect from voice
        if connection.voice_client.is_connected():
            await connection.voice_client.disconnect()
        
        # Remove from active connections
        del active_connections[guild_id]
        
        print(f"🚪 Left voice channel in guild {guild_id}")

@bot.tree.command(name="history", description="View recent conversation history")
async def view_history(interaction: discord.Interaction):
    """Show recent conversation history"""
    guild_id = interaction.guild.id
    history = conversation_history[guild_id]
    
    if not history:
        return await interaction.response.send_message("📝 No conversation history found.", ephemeral=True)
    
    # Build history embed
    embed = discord.Embed(
        title="💬 Recent Conversation History",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    # Show last 10 messages
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

@bot.tree.command(name="ping", description="Test if the bot is responding")
async def ping_command(interaction: discord.Interaction):
    """Simple test command"""
    await interaction.response.send_message("🏓 Pong! Bot is working!", ephemeral=True)

@bot.tree.command(name="voice", description="Change the bot's TTS voice")
async def change_voice(interaction: discord.Interaction, voice: str):
    """Change the bot's TTS voice"""
    global current_voice
    
    if voice.lower() not in available_voices:
        voice_list = "\n".join([f"**{v}**: {desc}" for v, desc in available_voices.items()])
        embed = discord.Embed(
            title="❌ Invalid Voice",
            description=f"Available voices:\n{voice_list}",
            color=0xff0000
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    current_voice = voice.lower()
    
    embed = discord.Embed(
        title="🎌 Voice Changed!",
        description=f"Bot voice changed to: **{available_voices[current_voice]}**",
        color=0x00ff00
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="status", description="Check bot voice status")
async def voice_status(interaction: discord.Interaction):
    """Show current voice connection status"""
    guild_id = interaction.guild.id
    
    embed = discord.Embed(title="🤖 Voice Status", color=0x0099ff)
    
    if guild_id in active_connections:
        connection = active_connections[guild_id]
        channel = connection.voice_client.channel
        
        embed.add_field(
            name="📡 Connection Status",
            value=f"✅ Connected to **{channel.name}**\n"
                  f"🎧 Listening: {'Yes' if connection.is_listening else 'No'}\n"
                  f"👥 Users in channel: {len([m for m in channel.members if not m.bot])}",
            inline=False
        )
        
        # Show active STT connections
        if connection.stt_connections:
            users = ", ".join([f"<@{uid}>" for uid in connection.stt_connections.keys()])
            embed.add_field(name="🎙️ Active Speakers", value=users, inline=False)
        
        # Show conversation stats
        history = conversation_history[guild_id]
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
        await leave_voice_channel(guild_id)

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ["DISCORD_TOKEN", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        exit(1)
    
    print("🚀 Starting Discord Voice AI Bot with OpenAI Whisper...")
    bot.run(os.getenv("DISCORD_TOKEN"))