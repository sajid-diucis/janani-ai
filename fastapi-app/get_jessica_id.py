
from elevenlabs.client import ElevenLabs
from config import settings

# Use the key from settings (which we know is working now)
client = ElevenLabs(api_key=settings.elevenlabs_api_key)

try:
    response = client.voices.get_all()
    print(f"Found {len(response.voices)} voices.")
    
    # Search for Jessica
    jessica = next((v for v in response.voices if "Jessica" in v.name), None)
    
    if jessica:
        print(f"FOUND JESSICA: ID={jessica.voice_id}, Name={jessica.name}")
    else:
        print("Jessica not found in stock voices. Listing all Females:")
        for v in response.voices:
            if "female" in v.labels.get("gender", "").lower():
                print(f" - {v.name}: {v.voice_id}")
                
except Exception as e:
    print(f"Error listing voices: {e}")
