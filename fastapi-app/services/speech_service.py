import speech_recognition as sr
from gtts import gTTS
import io, re, os
from typing import Optional
from config import settings

# Set FFmpeg path for pydub
FFMPEG_PATH = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe", "ffmpeg-8.0.1-full_build", "bin")
if os.path.exists(FFMPEG_PATH):
    os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ.get("PATH", "")

class SpeechService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def _convert_to_wav(self, input_path: str) -> str:
        """Convert any audio to WAV using pydub/ffmpeg"""
        output_path = input_path.rsplit(".", 1)[0] + "_converted.wav"
        try:
            # Check file size
            if os.path.getsize(input_path) == 0:
                print("Error: Input audio file is empty")
                raise Exception("Input audio file is empty")

            from pydub import AudioSegment
            
            # Explicitly set ffmpeg path if strict dependency issues occur
            # AudioSegment.converter = FFMPEG_PATH + "\\ffmpeg.exe" 
            
            audio = AudioSegment.from_file(input_path)
            
            # Normalize for SpeechRecognition (16kHz, Mono, 16bit)
            audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
            
            # Boost volume slightly if too quiet
            if audio.dBFS < -50:
                audio = audio + 20
                
            audio.export(output_path, format="wav")
            print(f"Audio converted successfully: {output_path}")
            return output_path
        except Exception as e:
            print(f"Audio conversion error: {e}")
            # Identify if it's an ffmpeg issue
            if "ffmpeg" in str(e).lower() or "converter" in str(e).lower():
                print("CRITICAL: FFmpeg not found or not executable. Please install FFmpeg.")
            return input_path
    
    async def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
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
                try: os.unlink(converted_path)
                except: pass
    
    async def text_to_speech(self, text: str, language: str = "bn") -> bytes:
        """
        Convert text to speech.
        Prioritizes ElevenLabs for high-quality conversational audio.
        Falls back to gTTS.
        """
        try:
            clean_text = re.sub(r"[*#`]", "", text)
            clean_text = re.sub(r"\s+", " ", clean_text).strip()
            if len(clean_text) < 2: raise Exception("Text too short")

            print(f"DEBUG: SERVICE KEY: {settings.elevenlabs_api_key}")
            # Try ElevenLabs first (Conversational Voice)
            if settings.elevenlabs_api_key:
                print("STARTING ELEVENLABS REQUEST...")
                from elevenlabs.client import ElevenLabs
                
                client = ElevenLabs(api_key=settings.elevenlabs_api_key)
                
                # Ensure generator is consumed to bytes
                audio_generator = client.text_to_speech.convert(
                    voice_id=settings.elevenlabs_voice_id,
                    optimize_streaming_latency="0",
                    output_format="mp3_44100_128",
                    text=clean_text,
                    model_id=settings.elevenlabs_model_id,
                )
                
                # Convert generator to bytes
                audio_bytes = b"".join(chunk for chunk in audio_generator)
                print(f"ELEVENLABS SUCCESS. Bytes: {len(audio_bytes)}")
                return audio_bytes

            # Fallback to gTTS (Only if no key provided)
            print("Using gTTS (No Key)...")
            tts = gTTS(text=clean_text, lang=language, slow=False)
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            return audio_bytes.read()
            
        except Exception as e:
            raise Exception(f"Voice error: {str(e)}")