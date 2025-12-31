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
        Falls back to gTTS if ElevenLabs fails or is unconfigured.
        """
        clean_text = re.sub(r"[*#`]", "", text)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        if len(clean_text) < 2: 
            return b"" # Quiet failure for empty text
            
        # 1. Try ElevenLabs
        if settings.elevenlabs_api_key:
            try:
                print(f"DEBUG: Attempting ElevenLabs TTS (Voice: {settings.elevenlabs_voice_id})")
                from elevenlabs.client import ElevenLabs
                client = ElevenLabs(api_key=settings.elevenlabs_api_key)
                
                audio_generator = client.text_to_speech.convert(
                    voice_id=settings.elevenlabs_voice_id,
                    optimize_streaming_latency="0",
                    output_format="mp3_44100_128",
                    text=clean_text,
                    model_id=settings.elevenlabs_model_id,
                )
                
                audio_bytes = b"".join(chunk for chunk in audio_generator)
                if len(audio_bytes) > 100:
                    print(f"ELEVENLABS SUCCESS. Bytes: {len(audio_bytes)}")
                    return audio_bytes
                else:
                    print("ElevenLabs returned suspiciously small response, falling back...")
            except Exception as e:
                print(f"ELEVENLABS ERROR: {str(e)}")
                # Continue to gTTS fallback

        # 2. Fallback to gTTS
        try:
            print("Falling back to gTTS...")
            tts = gTTS(text=clean_text, lang=language, slow=False)
            audio_bytes_io = io.BytesIO()
            tts.write_to_fp(audio_bytes_io)
            audio_bytes_io.seek(0)
            return audio_bytes_io.read()
        except Exception as e:
            print(f"gTTS ERROR: {str(e)}")
            raise Exception(f"All TTS engines failed: {str(e)}")