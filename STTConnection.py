import asyncio
from datetime import datetime
import audioop
import io
import wave

import openai


MIN_DURATION_MS = 250        # minimum audio duration to consider (ms)
RMS_THRESHOLD = 600          # adjust: lower -> more sensitive, higher -> stricter

def _pcm_duration_ms(pcm_bytes, sample_rate, channels, sample_width=2):
    samples = len(pcm_bytes) // (sample_width * channels)
    return (samples / sample_rate) * 1000.0

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
            
            # Quick duration and energy checks to avoid whisper hallucinations on near-silence
            duration_ms = _pcm_duration_ms(audio_data, self.sample_rate, self.channels)
            try:
                rms = audioop.rms(audio_data, 2)  # 16-bit PCM
            except Exception:
                rms = 0

            if duration_ms < MIN_DURATION_MS:
                print(f"Skipping: audio too short ({duration_ms:.1f} ms)")
                self.processing_audio = False
                return

            if rms < RMS_THRESHOLD:
                print(f"Skipping: low energy audio (rms={rms})")
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
