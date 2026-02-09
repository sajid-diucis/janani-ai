
from elevenlabs.client import ElevenLabs
from config import settings
import os

def test_generation():
    print(f"Testing ElevenLabs Generation with Key: {settings.elevenlabs_api_key[:5]}...")
    
    client = ElevenLabs(api_key=settings.elevenlabs_api_key)
    
    try:
        print("Attempting client.text_to_speech.convert()...")
        audio_generator = client.text_to_speech.convert(
            text="This is a test of the Eleven Labs API.",
            voice_id=settings.elevenlabs_voice_id,
            model_id=settings.elevenlabs_model_id
        )
        
        # Consume the generator to get bytes
        if hasattr(audio_generator, '__iter__') and not isinstance(audio_generator, (bytes, str)):
             audio_bytes = b"".join(audio_generator)
        else:
             audio_bytes = audio_generator
        
        if len(audio_bytes) > 0:
            print(f"SUCCESS: Generated {len(audio_bytes)} bytes of audio.")
            with open("test_eleven_output.mp3", "wb") as f:
                f.write(audio_bytes)
            print("Saved to test_eleven_output.mp3")
        else:
            print("FAILURE: Generated audio is empty.")
            
    except Exception as e:
        print(f"FAILURE: Generation Error: {e}")

if __name__ == "__main__":
    test_generation()
