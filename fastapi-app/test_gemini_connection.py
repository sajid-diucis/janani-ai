
import os
import asyncio
from openai import AsyncOpenAI

# Configuration derived from config.py and retrieved .env
API_KEY = "sk-OneBrain-5b3a2c89f1d440adbb8bea2464525a53"
BASE_URL = "https://dev.onebrain.app/onebrain-api/v1"
MODEL_ID = "google/gemini-2.0-flash-exp" # Trying a known valid model, or the one from config?
# Config said: google/gemini-2.5-flash. That sounds made up or very new.
# Let's try the config one first.
MODEL_ID_CONFIG = "google/gemini-2.5-flash"

async def test_gemini():
    print(f"Testing Gemini via Proxy: {BASE_URL}")
    print(f"Model: {MODEL_ID_CONFIG}")
    print(f"Key Prefix: {API_KEY[:5]}...")
    
    client = AsyncOpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        timeout=30.0
    )
    
    try:
        response = await client.chat.completions.create(
            model=MODEL_ID_CONFIG,
            messages=[{"role": "user", "content": "Hello, are you working?"}],
            max_tokens=50
        )
        print("\nSUCCESS!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"\nFAILED!")
        print(f"Error: {e}")
        
        # If it fails, let's try a fallback model name in case 2.5 is invalid
        print("\nRetrying with 'google/gemini-2.0-flash-exp'...")
        try:
           response = await client.chat.completions.create(
                model="google/gemini-2.0-flash-exp",
                messages=[{"role": "user", "content": "Hello, are you working?"}],
                max_tokens=50
            ) 
           print("\nSUCCESS with fallback model!")
           print(f"Response: {response.choices[0].message.content}")
        except Exception as e2:
           print(f"Fallback also failed: {e2}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
