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

import buttons as b
import bot_commands as commands  # Import shared command functions

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------------------------
# Discord Intents
# ---------------------------
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.message_content = True

# ---------------------------
# Initialize Bot
# ---------------------------
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------------
# Global Variables
# ---------------------------
active_connections = {}  # guild_id: VoiceConnection
conversation_history = defaultdict(lambda: deque(maxlen=50))  # guild_id: deque
current_voice = "nova"  # default voice

# ---------------------------
# Voice Connection Classes
# ---------------------------
class VoiceConnection:
    """Manages voice connection, STT, and TTS for a guild"""
    def __init__(self, guild_id, voice_client):
        self.guild_id = guild_id
        self.voice_client = voice_client
        self.stt_connections = {}  # user_id: STTConnection
        self.is_listening = False

    async def start_listening(self):
        if not self.is_listening:
            self.voice_client.listen(voice_recv.BasicSink(self.process_voice_packet))
            self.is_listening = True
            print(f"Started listening in guild {self.guild_id}")

    def process_voice_packet(self, user, data):
        if user.bot:
            return
        if user.id not in self.stt_connections:
            self.stt_connections[user.id] = STTConnection(user, self.on_speech_recognized, bot.loop)
        self.stt_connections[user.id].process_audio(data.pcm)

    async def on_speech_recognized(self, user, text):
        if not text.strip():
            return
        print(f"{user.display_name}: {text}")
        conversation_history[self.guild_id].append({
            "user": user.display_name,
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        response = await self.generate_response(text, user)
        if response:
            conversation_history[self.guild_id].append({
                "user": "Bot",
                "text": response,
                "timestamp": datetime.now().isoformat()
            })
            await self.speak_response(response)

    async def generate_response(self, text, user):
        try:
            messages = [{"role": "system", "content": (
                "You are Dufu, a cute anime-style assistant. Keep replies cheerful, casual, 1-2 sentences."
            )}]
            for msg in list(conversation_history[self.guild_id])[-10:]:
                role = "assistant" if msg["user"] == "Bot" else "user"
                content = msg["text"] if role == "assistant" else f"{msg['user']}: {msg['text']}"
                messages.append({"role": role, "content": content})
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
        print(f"Bot response: {text}")
        try:
            response = await asyncio.to_thread(
                openai.audio.speech.create,
                model="tts-1",
                voice=current_voice,
                input=text,
                response_format="mp3"
            )
            audio_data = response.content
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name

            audio_source = discord.FFmpegPCMAudio(temp_path)
            if self.voice_client.is_playing():
                self.voice_client.stop()

            def after_playing(error):
                if error:
                    print(f"Playback error: {error}")
                try:
                    os.unlink(temp_path)
                except:
                    pass

            self.voice_client.play(audio_source, after=after_playing)
        except Exception as e:
            print(f"TTS error: {e}")

    async def cleanup(self):
        self.is_listening = False
        for stt in self.stt_connections.values():
            stt.cleanup()
        self.stt_connections.clear()


class STTConnection:
    """Handles speech-to-text for individual users"""
    def __init__(self, user, callback, loop):
        self.user = user
        self.callback = callback
        self.loop = loop
        self.audio_buffer = io.BytesIO()
        self.sample_rate = 48000
        self.channels = 2
        self.processing_audio = False

    def process_audio(self, pcm_data):
        if not pcm_data:
            return
        self.audio_buffer.write(pcm_data)
        if not self.processing_audio and self.audio_buffer.tell() > 48000:
            if self.loop.is_running():
                asyncio.run_coroutine_threadsafe(self._process_buffered_audio(), self.loop)

    async def _process_buffered_audio(self):
        if self.processing_audio:
            return
        self.processing_audio = True
        try:
            audio_data = self.audio_buffer.getvalue()
            self.audio_buffer = io.BytesIO()
            if len(audio_data) < 3200:
                return
            wav = self._convert_to_wav(audio_data)
            if wav:
                text = await self._whisper_stt(wav)
                if text:
                    await self.callback(self.user, text)
        finally:
            self.processing_audio = False

    def _convert_to_wav(self, pcm_data):
        try:
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(pcm_data)
            wav_buffer.seek(0)
            return wav_buffer if len(wav_buffer.getvalue()) >= 44 else None
        except Exception as e:
            print(f"WAV conversion error: {e}")
            return None

    async def _whisper_stt(self, audio_wav):
        try:
            audio_wav.seek(0)
            audio_file = io.BytesIO(audio_wav.read())
            audio_file.name = "audio.wav"
            audio_file.seek(0)
            response = await asyncio.to_thread(
                openai.audio.transcriptions.create,
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            return response.strip()
        except Exception as e:
            print(f"Whisper STT error: {e}")
            return None

    def cleanup(self):
        self.audio_buffer.close()


# ---------------------------
# Slash Commands
# ---------------------------
from discord import app_commands

@bot.tree.command(name="vc", description="Join your voice channel")
async def vc(interaction: discord.Interaction):
    await commands.join_voice(interaction)

@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    await commands.leave_voice(interaction)

@bot.tree.command(name="history", description="Show recent conversation history")
async def history(interaction: discord.Interaction):
    await commands.show_history(interaction)

@bot.tree.command(name="status", description="Show bot connection status")
async def status(interaction: discord.Interaction):
    await commands.show_status(interaction)
    
@bot.tree.command(name="menu", description="Show the interactive control buttons")
async def menu(interaction: discord.Interaction):
    """Send a message with interactive buttons"""
    view = b.Buttons(interaction)
    await interaction.response.send_message(
        "🎛️ Control your voice bot using the buttons below:", 
        view=view,
        ephemeral=True  # only visible to the user
    )


# ---------------------------
# Bot Events
# ---------------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        await bot.tree.sync()
        print("Slash commands synced ✅")
    except Exception as e:
        print(f"Error syncing commands: {e}")


# ---------------------------
# Run Bot
# ---------------------------
bot.run(os.getenv("DISCORD_TOKEN"))
