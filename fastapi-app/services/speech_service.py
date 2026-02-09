import io
import re
import os
import asyncio
from typing import Optional
import speech_recognition as sr
from config import settings

# Set FFmpeg path for pydub
FFMPEG_PATH = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe", "ffmpeg-8.0.1-full_build", "bin")
if os.path.exists(FFMPEG_PATH):
    os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ.get("PATH", "")


class SpeechService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Bengali female voice (Microsoft Neural - high quality)
        self.tts_voice = "bn-IN-TanishaaNeural"
    
    def _convert_to_wav(self, input_path: str) -> str:
        """Convert any audio to WAV using pydub/ffmpeg"""
        output_path = input_path.rsplit(".", 1)[0] + "_converted.wav"
        try:
            if os.path.getsize(input_path) == 0:
                print("Error: Input audio file is empty")
                raise Exception("Input audio file is empty")

            from pydub import AudioSegment
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
            
            if audio.dBFS < -50:
                audio = audio + 20
                
            audio.export(output_path, format="wav")
            print(f"Audio converted successfully: {output_path}")
            return output_path
        except Exception as e:
            print(f"Audio conversion error: {e}")
            if "ffmpeg" in str(e).lower() or "converter" in str(e).lower():
                print("CRITICAL: FFmpeg not found. Please install FFmpeg.")
            return input_path
    
    async def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio to text using Google Speech Recognition"""
        converted_path = None
        try:
            converted_path = self._convert_to_wav(audio_file_path)
            with sr.AudioFile(converted_path) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)
            return self.recognizer.recognize_google(audio_data, language=settings.speech_recognition_language)
        except sr.UnknownValueError:
            return "Sorry, could not understand audio."
        except Exception as e:
            raise Exception(f"Transcription error: {str(e)}")
        finally:
            if converted_path and converted_path != audio_file_path and os.path.exists(converted_path):
                try:
                    os.unlink(converted_path)
                except:
                    pass
    
    async def text_to_speech(self, text: str, language: str = "bn") -> bytes:
        """
        Convert text to speech using edge-tts (Microsoft Neural Voices).
        Uses high-quality Bengali female voice: Tanishaa
        """
        try:
            import edge_tts
            
            # Clean text
            clean_text = re.sub(r"[*#`]", "", text)
            clean_text = re.sub(r"\s+", " ", clean_text).strip()
            
            if len(clean_text) < 2:
                raise Exception("Text too short")
            
            print(f"🗣️ Using edge-tts with voice: {self.tts_voice}")
            
            # Use edge-tts with Bengali female voice
            communicate = edge_tts.Communicate(clean_text, self.tts_voice)
            
            # Collect audio chunks
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            print(f"✅ edge-tts SUCCESS. Bytes: {len(audio_data)}")
            return audio_data
            
        except ImportError:
            print("⚠️ edge-tts not installed. Falling back to gTTS...")
            return await self._fallback_gtts(text, language)
        except Exception as e:
            print(f"⚠️ edge-tts error: {e}. Falling back to gTTS...")
            return await self._fallback_gtts(text, language)
    
    async def _fallback_gtts(self, text: str, language: str = "bn") -> bytes:
        """Fallback to gTTS if edge-tts fails"""
        from gtts import gTTS
        
        clean_text = re.sub(r"[*#`]", "", text)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        
        tts = gTTS(text=clean_text, lang=language, slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes.read()

    async def stream_elevenlabs_audio(self, text: str, stability: float = 0.5, style: float = 0.0):
        """
        Stream audio from ElevenLabs with dynamic emotional settings.
        Yields chunks of audio bytes.
        """
        try:
            from elevenlabs.client import ElevenLabs
            from elevenlabs import VoiceSettings
            
            if not settings.elevenlabs_api_key:
                print("❌ ElevenLabs API Key missing")
                return

            client = ElevenLabs(api_key=settings.elevenlabs_api_key)
            
            # Dynamic Voice Settings
            voice_settings = VoiceSettings(
                stability=stability,
                similarity_boost=0.75,
                style=style,
                use_speaker_boost=True
            )

            print(f"🎙️ Streaming ElevenLabs: '{text[:20]}...' (Stability: {stability}, Style: {style})")

            # Use client.text_to_speech.convert for v3 SDK
            audio_stream = client.text_to_speech.convert(
                text=text,
                voice_id=settings.elevenlabs_voice_id,
                model_id=settings.elevenlabs_model_id,
                voice_settings=voice_settings
            )

            for chunk in audio_stream:
                if chunk:
                    yield chunk

        except Exception as e:
            print(f"⚠️ ElevenLabs Streaming Error: {e}")
            # Fallback to edge-tts if ElevenLabs fails
            # Note: edge-tts is not a generator in our wrapper, so we yield once
            fallback_audio = await self.text_to_speech(text)
            yield fallback_audio


# Singleton instance
speech_service = SpeechService()