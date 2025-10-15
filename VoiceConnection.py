import discord
import os
import tempfile
import openai
from discord.ext import voice_recv
import STTConnection
from datetime import datetime
import asyncio


class VoiceConnection:
    """Manages voice connection, STT, and TTS for a guild"""
    
    def __init__(self, current_voice, guild_id, voice_client, conversation_history, bot):
        self.guild_id = guild_id
        self.voice_client = voice_client
        self.stt_connections = {}  # user_id: STTConnection
        self.is_listening = False
        self.conversation_history = conversation_history
        self.bot = bot
        self.voice = current_voice
        
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
            self.stt_connections[user.id] = STTConnection(user, self.on_speech_recognized, self.bot.loop)
        
        # Send audio data to STT
        self.stt_connections[user.id].process_audio(data.pcm)
    
    async def on_speech_recognized(self, user, text):
        """Handle recognized speech"""
        if not text.strip():
            return
            
        print(f"{user.display_name}: {text}")
        
        # Add to conversation history
        self.conversation_history[self.guild_id].append({
            "user": user.display_name,
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate response
        response = await self.generate_response(text, user)
        
        if response:
            # Add bot response to history
            self.conversation_history[self.guild_id].append({
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
            for msg in list(self.conversation_history[self.guild_id])[-10:]:  # Last 10 messages
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
                voice=self.voice,
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