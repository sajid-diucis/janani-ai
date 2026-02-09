
from elevenlabs.client import ElevenLabs
from config import settings
import json

client = ElevenLabs(api_key=settings.elevenlabs_api_key)

try:
    user = client.user.get()
    subscription = client.user.get_subscription()
    
    usage = {
        "character_count": subscription.character_count,
        "character_limit": subscription.character_limit,
        "status": subscription.status,
        "tier": subscription.tier,
        "can_use_multilingual": subscription.can_use_delayed_v2_models
    }
    
    print("--- ELEVENLABS DIAGNOSTICS ---")
    print(f"User Character Usage: {usage['character_count']} / {usage['character_limit']}")
    print(f"Subscription Status: {usage['status']}")
    print(f"Tier: {usage['tier']}")
    print(f"Multilingual v2 Support: {usage['can_use_multilingual']}")
    
    if usage['character_count'] >= usage['character_limit']:
        print("ALERT: Characters exhausted! Fallen back to gTTS.")
except Exception as e:
    print(f"Error checking ElevenLabs: {e}")
