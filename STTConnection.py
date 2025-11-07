import asyncio
from datetime import datetime
import audioop
import io
import wave
import os
import tempfile
import threading

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

        # Synchronization primitives to avoid backlog / races
        self._lock = threading.Lock()
        self._silence_future = None  # concurrent.futures.Future for the scheduled silence waiter

    def process_audio(self, pcm_data):
        """Process incoming PCM audio data"""
        if not pcm_data:
            return
            
         # Append to buffer under lock
        with self._lock:
            self.audio_buffer.write(pcm_data)
            self.last_audio_time = datetime.now()
            buffer_size = self.audio_buffer.tell()
        
        # Debug: Show audio data info occasionally
        if buffer_size % 32000 == 0:  # Every ~2 seconds
            print(f"Audio buffer for {self.user.display_name}: {buffer_size} bytes")
        
        # Cancel existing scheduled waiter (if any) to debounce
        try:
            if self._silence_future and not self._silence_future.done():
                self._silence_future.cancel()
        except Exception:
            pass
        
        # Schedule a new silence waiter on the stored loop
        if self.loop and self.loop.is_running():
            self._silence_future = asyncio.run_coroutine_threadsafe(self._silence_waiter(), self.loop)
        else:
            # Fallback: schedule on current loop if possible
            try:
                asyncio.create_task(self._silence_waiter())
            except Exception:
                # If scheduling fails, we simply return — no processing will be done
                print("Failed to schedule silence waiter for STTConnection")

    async def _silence_waiter(self):
        """Wait for silence and then process audio"""
        try:
            await asyncio.sleep(self.silence_threshold / 1000.0)
            await self._process_buffered_audio()
        except asyncio.CancelledError:
            # Expected when new audio arrives and we cancel the waiter to debounce
            return
        except Exception as e:
            print(f"Silence waiter error for {self.user.display_name}: {e}")



    async def _process_buffered_audio(self):
        """Process buffered audio with STT"""
        if self.processing_audio:
            return
            
        # Snapshot buffer under lock and clear it so newer audio is not included
        with self._lock:
            audio_data = self.audio_buffer.getvalue()
            self.audio_buffer = io.BytesIO()

        if not audio_data:
            return

        self.processing_audio = True
        
        try:            
            print(f"Processing {len(audio_data)} bytes of audio from {self.user.display_name}")
            
            if len(audio_data) < 3200:  # Need at least ~0.1 seconds of audio (increased threshold)
                print(f"Audio too short ({len(audio_data)} bytes), skipping")
                return
            
            # Quick duration and energy checks to avoid whisper hallucinations on near-silence
            duration_ms = _pcm_duration_ms(audio_data, self.sample_rate, self.channels)
            try:
                rms = audioop.rms(audio_data, 2)  # 16-bit PCM
            except Exception:
                rms = 0

            if duration_ms < MIN_DURATION_MS:
                print(f"Skipping: audio too short ({duration_ms:.1f} ms)")
                return

            if rms < RMS_THRESHOLD:
                print(f"Skipping: low energy audio (rms={rms})")
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
                
            # Ensure we have bytes to work with
            audio_wav.seek(0)
            audio_data = audio_wav.read()
            print(f"Preparing {len(audio_data)} bytes for Whisper API")

            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_data)
                    tmp.flush()
                    tmp_path = tmp.name

                # Wait briefly and verify the temp file is readable/closed
                for _ in range(10):
                    try:
                        with open(tmp_path, "rb"):
                            break
                    except Exception:
                        await asyncio.sleep(0.05)

                with open(tmp_path, "rb") as f:
                    data = f.read()
                audio_file = io.BytesIO(data)
                audio_file.name = "audio.wav"
                audio_file.seek(0)

            finally:
                # Remove the temporary file if it was created
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        # If deletion fails, ignore — it's a temp file and will be cleaned up later
                        pass

            print(f"Sending {len(audio_file.getvalue())} bytes to Whisper API")

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
        try:
            if self._silence_future and not self._silence_future.done():
                self._silence_future.cancel()
        except Exception:
            pass

        self.audio_buffer.close()
